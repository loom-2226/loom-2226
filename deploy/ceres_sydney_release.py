#!/usr/bin/env python3
"""Manual, fail-closed Ceres update/rollback orchestrator for the Sydney host.

The default is an offline evidence check.  ``--execute`` is deliberately local-only:
the tool has no SSH client and never changes Tailscale configuration.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import sys
import time
import urllib.request
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable

CONTAINER = "ceres-atlas"
PORT = "127.0.0.1:8768:8768"
DATABASE_ENVS = ("CERES_WORLD_DB", "CERES_CIVSTATE_DB", "CERES_MEDIA_DB")
REQUIRED_ENDPOINTS = ("/healthz", "/", "/atlas-data.json")
DIGEST = re.compile(r"^ghcr\.io/loom-2226/ceres-atlas@sha256:[0-9a-f]{64}$")
SHA = re.compile(r"^[0-9a-f]{40}$")
APPROVAL = "I APPROVE THE SYDNEY CERES RELEASE DESCRIBED BY THIS FILE"


class ReleaseError(RuntimeError):
    """A release gate failed closed."""


def load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ReleaseError(f"{path}: expected a JSON object")
    return value


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise ReleaseError(message)


def validate_release(release: dict[str, Any]) -> None:
    """Validate explicit immutable authorization without contacting a host."""
    _require(release.get("schema_version") == 1, "unsupported release schema")
    _require(release.get("target") == "SYDNEY", "approval must name SYDNEY")
    _require(release.get("approval") == APPROVAL, "explicit operator approval is absent")
    _require(bool(SHA.fullmatch(str(release.get("source_sha", "")))), "invalid source SHA")
    _require(bool(DIGEST.fullmatch(str(release.get("image", "")))), "private image must use an immutable GHCR digest")
    runs = release.get("successful_ci_run_ids")
    _require(isinstance(runs, list) and runs and all(isinstance(x, int) and x > 0 for x in runs),
             "successful CI run IDs are required")
    _require(release.get("provenance", {}).get("source_sha") == release.get("source_sha"),
             "provenance source SHA mismatch")
    _require(release.get("provenance", {}).get("image") == release.get("image"),
             "provenance digest mismatch")
    _require(release.get("hostname"), "CERES_ALLOWED_HOSTS hostname is required")
    _require(release.get("minimum_free_bytes", 0) > 0, "minimum disk requirement is required")
    expected = release.get("databases", {})
    _require(set(expected) == set(DATABASE_ENVS), "exactly three database identities are required")
    for name, item in expected.items():
        _require(item.get("container_path", "").startswith("/data/"), f"{name}: invalid container path")
        _require(bool(re.fullmatch(r"[0-9a-f]{64}", str(item.get("sha256", "")))), f"{name}: invalid SHA-256")
        _require(item.get("backup", {}).get("restore_tested") is True, f"{name}: restore-tested backup required")
        _require(item["backup"].get("sha256") == item.get("sha256"), f"{name}: backup hash mismatch")


def _env(inspect: dict[str, Any]) -> dict[str, str]:
    return dict(item.split("=", 1) for item in inspect["Config"].get("Env", []) if "=" in item)


def validate_runtime(release: dict[str, Any], evidence: dict[str, Any]) -> dict[str, Any]:
    """Validate a redacted host snapshot and return exact rollback configuration."""
    inspect = evidence.get("container", {})
    _require(inspect.get("Name") == f"/{CONTAINER}", "unexpected container identity")
    image = inspect.get("Config", {}).get("Image", "")
    _require(bool(DIGEST.fullmatch(image)), "running image is not an immutable private digest")
    ports = inspect.get("HostConfig", {}).get("PortBindings", {})
    _require(set(ports) == {"8768/tcp"}, "unexpected published container ports")
    bindings = ports.get("8768/tcp") or []
    _require(bindings == [{"HostIp": "127.0.0.1", "HostPort": "8768"}], "Ceres must bind only 127.0.0.1:8768")
    _require(not any(p in {"80", "443", "8768"} for p in evidence.get("public_listeners", [])),
             "public Ceres/HTTP listener detected")
    host = inspect.get("HostConfig", {})
    _require(host.get("ReadonlyRootfs") is True, "image filesystem must be read-only")
    _require(host.get("RestartPolicy") == {"Name": "unless-stopped", "MaximumRetryCount": 0},
             "restart policy mismatch")
    _require("/tmp" in host.get("Tmpfs", {}), "required /tmp tmpfs is absent")
    mounts = inspect.get("Mounts", [])
    by_destination = {m.get("Destination"): m for m in mounts}
    env = _env(inspect)
    for name, wanted in release["databases"].items():
        destination = wanted["container_path"]
        mount = by_destination.get(destination)
        _require(mount is not None, f"{name}: mount absent")
        _require(mount.get("RW") is False and mount.get("Type") == "bind", f"{name}: mount is writable or not a bind")
        _require(env.get(name) == destination, f"{name}: environment/mount mismatch")
        actual = evidence.get("files", {}).get(mount.get("Source"), {})
        _require(actual.get("sha256") == wanted["sha256"], f"{name}: database identity mismatch")
        _require(actual.get("readable") is True and actual.get("writable") is False, f"{name}: database permissions unsafe")
        _require(actual.get("uid") == wanted.get("uid") and actual.get("gid") == wanted.get("gid"), f"{name}: database owner mismatch")
        backup = evidence.get("backups", {}).get(name, {})
        _require(backup.get("sha256") == wanted["sha256"] and backup.get("readable") is True,
                 f"{name}: consistent backup evidence absent")
        _require(backup.get("restore_tested") is True and backup.get("restore_test_id"),
                 f"{name}: restore-test evidence absent")
    _require(env.get("CERES_ALLOWED_HOSTS") == release["hostname"], "CERES_ALLOWED_HOSTS mismatch")
    _require(evidence.get("disk_free_bytes", 0) >= release["minimum_free_bytes"], "insufficient disk space")
    tailscale = evidence.get("tailscale", {})
    _require(tailscale.get("funnel") is False, "Tailscale Funnel must be off")
    _require(tailscale.get("serve_target") == "http://127.0.0.1:8768", "Tailscale Serve target mismatch")
    return {"prior_image": image, "inspect": inspect, "database_hashes": evidence["files"]}


def validate_provenance(release: dict[str, Any], evidence: dict[str, Any]) -> None:
    auth = evidence.get("authentication", {})
    _require(auth.get("source_commit_verified") is True, "source commit is not independently authenticated")
    _require(auth.get("image_digest_verified") is True, "image digest is not independently authenticated")
    _require(auth.get("ci_runs_verified") is True, "successful CI provenance is not independently authenticated")
    registry = evidence.get("registry", {})
    _require(registry.get("available") is True, "private registry unavailable")
    _require(registry.get("resolved_image") == release["image"], "registry digest mismatch")
    _require(registry.get("source_sha") == release["source_sha"], "image/source provenance mismatch")
    _require(set(registry.get("successful_ci_run_ids", [])) >= set(release["successful_ci_run_ids"]),
             "successful CI provenance mismatch")


def validate_health(release: dict[str, Any], health: dict[str, Any]) -> None:
    for path in REQUIRED_ENDPOINTS:
        _require(health.get(path, {}).get("status") == 200, f"{path}: unhealthy")
    atlas = health["/atlas-data.json"]
    _require(atlas.get("world_identity") == release["checks"]["world_identity"], "wrong WORLD result")
    _require(atlas.get("civstate_identity") == release["checks"]["civstate_identity"], "wrong CIVSTATE result")
    media = health.get(release["checks"]["media_path"], {})
    _require(media.get("status") == 200 and media.get("sha256") == release["checks"]["media_sha256"],
             "approved MEDIA result mismatch")
    _require(health.get("private_browser_verified") is True, "manual private-browser gate is incomplete")


@dataclass
class Runner:
    run: Callable[..., subprocess.CompletedProcess[str]] = subprocess.run

    def command(self, args: list[str]) -> None:
        result = self.run(args, text=True, capture_output=True, timeout=120)
        if result.returncode:
            raise ReleaseError(f"command failed ({args[0]}): {result.stderr.strip()}")

    def capture(self, args: list[str]) -> str:
        result = self.run(args, text=True, capture_output=True, timeout=120)
        if result.returncode:
            raise ReleaseError(f"inspection failed ({args[0]}): {result.stderr.strip()}")
        return result.stdout


def refresh_host_state(runner: Runner, evidence: dict[str, Any]) -> None:
    """Re-read mutable host state immediately before mutation and reject drift."""
    live = json.loads(runner.capture(["docker", "inspect", CONTAINER]))[0]
    expected = evidence.get("container", {})
    _require(live == expected, "host Docker configuration drifted since evidence collection")
    free = int(runner.capture(["df", "--output=avail", "/"]).splitlines()[-1].strip()) * 1024
    _require(free >= evidence.get("disk_free_bytes", 0), "host disk state drifted since evidence collection")
    listeners = runner.capture(["ss", "-ltn"]).splitlines()
    _require(not any(f":{p}" in line for p in ("80", "443", "8768") for line in listeners), "host listener state drifted")
    tailscale = json.loads(runner.capture(["tailscale", "serve", "status", "--json"]))
    _require(tailscale == evidence.get("tailscale"), "Tailscale state drifted since evidence collection")


def exact_run_args(release: dict[str, Any], prior: dict[str, Any], image: str) -> list[str]:
    """Reconstruct only the approved, captured single-container configuration."""
    inspect = prior["inspect"]
    host = inspect.get("HostConfig", {})
    _require(set(host) >= {"ReadonlyRootfs", "RestartPolicy", "Tmpfs", "PortBindings"}, "prior runtime configuration is incomplete")
    _require(set(host) <= {"ReadonlyRootfs", "RestartPolicy", "Tmpfs", "PortBindings"}, "unsupported prior Docker configuration prevents exact rollback")
    env = _env(inspect)
    _require(set(env) == set(DATABASE_ENVS) | {"CERES_ALLOWED_HOSTS"}, "unsupported prior environment prevents exact rollback")
    mounts = {m["Destination"]: m for m in inspect["Mounts"]}
    _require(len(mounts) == 3 and set(mounts) == {release["databases"][n]["container_path"] for n in DATABASE_ENVS}, "unsupported prior mounts prevent exact rollback")
    args = ["docker", "run", "--detach", "--name", CONTAINER, "--read-only",
            "--tmpfs", "/tmp:rw,nosuid,nodev,size=64m", "--restart", "unless-stopped",
            "--publish", PORT]
    for name in DATABASE_ENVS:
        destination = release["databases"][name]["container_path"]
        args += ["--volume", f"{mounts[destination]['Source']}:{destination}:ro", "--env", f"{name}={destination}"]
    args += ["--env", f"CERES_ALLOWED_HOSTS={env['CERES_ALLOWED_HOSTS']}", image]
    return args


def replace(runner: Runner, release: dict[str, Any], prior: dict[str, Any],
            verify: Callable[[str], bool], timeout: float) -> str:
    """Replace once, rolling back the exact captured image/config on any failure."""
    candidate = release["image"]
    runner.command(["docker", "pull", candidate])
    stopped = False
    try:
        runner.command(["docker", "stop", CONTAINER])
        stopped = True
        runner.command(["docker", "rm", CONTAINER])
        runner.command(exact_run_args(release, prior, candidate))
        deadline = time.monotonic() + timeout
        while time.monotonic() < deadline:
            if verify("candidate"):
                return "UPDATED"
            time.sleep(min(1, timeout))
        raise ReleaseError("candidate verification timeout")
    except Exception as candidate_error:
        if not stopped:
            raise ReleaseError(f"pre-replacement stop failed; existing container retained: {candidate_error}") from candidate_error
        try:
            removal = runner.run(["docker", "rm", "--force", CONTAINER], text=True,
                                 capture_output=True, timeout=120)
            if removal.returncode and "No such container" not in removal.stderr:
                raise ReleaseError(f"candidate cleanup failed: {removal.stderr.strip()}")
            runner.command(exact_run_args(release, prior, prior["prior_image"]))
            if not verify("rollback"):
                raise ReleaseError("restored runtime verification failed")
        except Exception as rollback_error:
            raise ReleaseError(f"ROLLBACK FAILED; preserve evidence: {rollback_error}") from candidate_error
        raise ReleaseError(f"candidate failed; exact rollback verified: {candidate_error}") from candidate_error


def redact(value: Any) -> Any:
    if isinstance(value, dict):
        return {k: ("[REDACTED]" if any(x in k.lower() for x in ("token", "secret", "password")) else redact(v)) for k, v in value.items()}
    if isinstance(value, list):
        return [redact(v) for v in value]
    return value


def live_verify(release: dict[str, Any], phase: str) -> bool:
    """Verify local bytes/data, then require the operator's private-browser gate."""
    try:
        def get(path: str) -> bytes:
            request = urllib.request.Request(f"http://127.0.0.1:8768{path}",
                                             headers={"Host": release["hostname"]})
            with urllib.request.urlopen(request, timeout=5) as response:
                if response.status != 200:
                    raise ReleaseError(f"{path}: HTTP {response.status}")
                return response.read()

        health = json.loads(get("/healthz"))
        root = get("/")
        atlas = json.loads(get("/atlas-data.json"))
        media = get(release["checks"]["media_path"])
        _require(health.get("status") == "ok", "health body is not ok")
        _require(b"Ceres" in root, "root body does not identify Ceres")
        _require(atlas.get("world", {}).get("entity_id") == release["checks"]["world_identity"],
                 "live WORLD result mismatch")
        _require(atlas.get("body", {}).get("demographic", {}).get("subject_id") ==
                 release["checks"]["civstate_identity"], "live CIVSTATE result mismatch")
        _require(hashlib.sha256(media).hexdigest() == release["checks"]["media_sha256"],
                 "live MEDIA hash mismatch")
        answer = input(f"Verify {phase} in the existing private browser via Tailscale Serve; type VERIFIED: ")
        _require(answer == "VERIFIED", "private-browser verification not confirmed")
        return True
    except (OSError, ValueError, KeyError, ReleaseError):
        return False


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--release", type=Path, required=True)
    parser.add_argument("--evidence", type=Path, required=True, help="offline, nonsecret host/registry/health evidence")
    parser.add_argument("--execute", action="store_true", help="future authorized local maintenance only")
    parser.add_argument("--timeout", type=float, default=60)
    args = parser.parse_args(argv)
    try:
        release, evidence = load_json(args.release), load_json(args.evidence)
        validate_release(release)
        validate_provenance(release, evidence)
        prior = validate_runtime(release, evidence)
        validate_health(release, evidence.get("current_health", {}))
        report = {"result": "DRY_RUN_PASS", "target": "SYDNEY", "candidate": release["image"],
                  "prior_image": prior["prior_image"], "mutation_performed": False,
                  "limitations": "offline evidence validation; not Sydney or end-to-end release qualification"}
        if args.execute:
            confirmation = input("Maintenance window authorized; type the candidate digest to continue: ")
            _require(confirmation == release["image"], "maintenance confirmation mismatch")
            live_runner = Runner()
            refresh_host_state(live_runner, evidence)
            report["result"] = replace(live_runner, release, prior,
                                       lambda phase: live_verify(release, phase), args.timeout)
            report["mutation_performed"] = True
        print(json.dumps(redact(report), sort_keys=True))
        return 0
    except (EOFError, OSError, ValueError, KeyError, ReleaseError) as error:
        print(f"FAIL CLOSED: {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
