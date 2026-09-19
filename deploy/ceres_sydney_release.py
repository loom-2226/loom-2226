#!/usr/bin/env python3
"""Manual, fail-closed Ceres update/rollback orchestrator for the Sydney host.

The default is an offline evidence check.  ``--execute`` is deliberately local-only:
the tool has no SSH client and never changes Tailscale configuration.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import ipaddress
import os
import shutil
import socket
import stat
import tempfile
import math
import select
import re
import subprocess
import sys
import time
import urllib.request
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from tools.serve_ceres_atlas import ROOT, load_manifest, verify_runtime

CONTAINER = "ceres-atlas"
PORT = "127.0.0.1:8768:8768"
DATABASE_ENVS = ("CERES_WORLD_DB", "CERES_CIVSTATE_DB", "CERES_MEDIA_DB")
REQUIRED_ENDPOINTS = ("/healthz", "/", "/atlas-data.json")
DIGEST = re.compile(r"^ghcr\.io/loom-2226/ceres-atlas@sha256:[0-9a-f]{64}$")
SHA = re.compile(r"^[0-9a-f]{40}$")
REPO = "loom-2226/loom-2226"
WORKFLOW = ".github/workflows/ceres-atlas-docker.yml"
DOCKER = ["docker", "--host", "unix:///var/run/docker.sock"]
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
    _require(isinstance(runs, list) and runs and all(type(x) is int and x > 0 for x in runs) and len(set(runs)) == len(runs),
             "successful CI run IDs are required")
    _require(release.get("provenance", {}).get("source_sha") == release.get("source_sha"),
             "provenance source SHA mismatch")
    _require(release.get("provenance", {}).get("image") == release.get("image"),
             "provenance digest mismatch")
    _require(re.fullmatch(r"[a-zA-Z0-9.-]+", str(release.get("host_identity", ""))), "local host identity required")
    _require(type(release.get("window_end_unix")) in (int, float) and math.isfinite(release["window_end_unix"]), "finite maintenance window required")
    _require(re.fullmatch(r"[a-zA-Z0-9][a-zA-Z0-9.-]*", str(release.get("hostname", ""))), "valid CERES_ALLOWED_HOSTS hostname required")
    _require(release.get("minimum_free_bytes", 0) > 0, "minimum disk requirement is required")
    expected = release.get("databases", {})
    _require(set(expected) == set(DATABASE_ENVS), "exactly three database identities are required")
    _require(len({item.get("container_path") for item in expected.values()}) == 3, "distinct database mounts required")
    for name, item in expected.items():
        _require(re.fullmatch(r"/data/[a-zA-Z0-9_.-]+", item.get("container_path", "")), f"{name}: invalid container path")
        _require(Path(item.get("backup", {}).get("path", "")).is_absolute(), f"{name}: backup path required")
        _require(bool(re.fullmatch(r"[0-9a-f]{64}", str(item.get("sha256", "")))), f"{name}: invalid SHA-256")
        _require(item.get("backup", {}).get("restore_tested") is True, f"{name}: restore-tested backup required")
        _require(item["backup"].get("sha256") == item.get("sha256"), f"{name}: backup hash mismatch")


def _env(inspect: dict[str, Any]) -> dict[str, str]:
    return dict(item.split("=", 1) for item in inspect["Config"].get("Env", []) if "=" in item)


def validate_runtime(release: dict[str, Any], evidence: dict[str, Any]) -> dict[str, Any]:
    """Validate an untrusted offline snapshot; it never authorizes execution."""
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
    validate_tailscale(evidence.get("tailscale", {}), release["hostname"])
    parse_listeners(evidence["listeners"])
    return {"prior_image": image, "inspect": inspect, "database_hashes": evidence["files"]}


def validate_provenance(release: dict[str, Any], runner: "Runner") -> dict:
    """Authenticate records ourselves. No supplied evidence-file field grants trust.

    gh verifies the OCI bytes, signature, OIDC issuer, repository, workflow and
    source revision. Missing credentials/attestation/permissions fail closed.
    """
    _require(isinstance(runner, Runner), "provenance requires authentication, not assertions")
    def api(path: str) -> Any:
        return json.loads(runner.capture(["gh", "api", "--hostname", "github.com", path]))
    api("user")
    commit = api(f"repos/{REPO}/commits/{release['source_sha']}")
    _require(commit.get("sha") == release["source_sha"], "authenticated source SHA mismatch")
    package = api("users/loom-2226/packages/container/ceres-atlas")
    _require(package.get("visibility") == "private" and package.get("name") == "ceres-atlas"
             and package.get("repository", {}).get("full_name") == REPO,
             "authenticated package privacy/identity unverified")
    runs = []
    for run_id in release["successful_ci_run_ids"]:
        record = api(f"repos/{REPO}/actions/runs/{run_id}")
        _require(record.get("id") == run_id and record.get("head_sha") == release["source_sha"]
                 and record.get("head_repository", {}).get("full_name") == REPO
                 and record.get("repository", {}).get("full_name") == REPO
                 and record.get("path") == WORKFLOW and record.get("status") == "completed"
                 and record.get("conclusion") == "success"
                 and record.get("event") in {"push", "workflow_dispatch"},
                 "authenticated CI identity/source/status mismatch")
        runs.append(record)
    results = json.loads(runner.capture([
        "gh", "attestation", "verify", "oci://" + release["image"],
        "--hostname", "github.com", "--repo", REPO,
        "--signer-workflow", REPO + "/" + WORKFLOW,
        "--source-digest", release["source_sha"], "--signer-digest", release["source_sha"],
        "--cert-oidc-issuer", "https://token.actions.githubusercontent.com",
        "--deny-self-hosted-runners", "--format", "json",
    ]))
    _require(isinstance(results, list) and bool(results), "no verified image attestation")
    digest = release["image"].split("@sha256:")[1]
    invocations = {f"https://github.com/{REPO}/actions/runs/{r['id']}/attempts/{r['run_attempt']}" for r in runs}
    for result in results:
        statement = result.get("verificationResult", {}).get("statement", {})
        invocation = statement.get("predicate", {}).get("runDetails", {}).get("metadata", {}).get("invocationId")
        if (statement.get("predicateType") == "https://slsa.dev/provenance/v1"
                and any(x.get("digest") == {"sha256": digest} for x in statement.get("subject", []))
                and invocation in invocations):
            return {"source_sha": commit["sha"], "image": release["image"],
                    "ci_run_ids": [r["id"] for r in runs], "invocation": invocation}
    raise ReleaseError("verified attestation does not bind digest to approved successful CI attempt")


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
        self.capture(args)

    def capture(self, args: list[str]) -> str:
        try:
            result = self.run(args, text=True, capture_output=True, timeout=120)
        except (OSError, subprocess.SubprocessError):
            raise ReleaseError("external verification/operation failed; output withheld") from None
        if result.returncode:
            raise ReleaseError("external verification/operation failed; output withheld")
        return result.stdout


def parse_listeners(output: str) -> set[tuple[str, int]]:
    """Parse ss -H -ltn strictly; no substring or wildcard-to-loopback coercion."""
    listeners = set()
    for line in output.splitlines():
        fields = line.split()
        _require(len(fields) == 5 and fields[0] == "LISTEN" and fields[1].isdigit()
                 and fields[2].isdigit(), "malformed listener evidence")
        address, sep, port = fields[3].rpartition(":")
        _require(bool(sep) and port.isdigit() and 0 < int(port) <= 65535, "malformed listener endpoint")
        if address.startswith("[") and address.endswith("]"):
            address = address[1:-1]
        if address == "*":
            address = "0.0.0.0"
        try:
            address = str(ipaddress.ip_address(address))
        except ValueError:
            raise ReleaseError("malformed listener address") from None
        peer, peer_sep, peer_port = fields[4].rpartition(":")
        _require(bool(peer_sep) and (peer_port == "*" or peer_port.isdigit()), "malformed listener peer")
        try:
            if peer != "*":
                ipaddress.ip_address(peer[1:-1] if peer.startswith("[") and peer.endswith("]") else peer)
        except ValueError:
            raise ReleaseError("malformed listener peer") from None
        _require((address, int(port)) not in listeners, "duplicate listener evidence")
        listeners.add((address, int(port)))
    _require(("127.0.0.1", 8768) in listeners, "required loopback listener absent")
    _require(all(address == "127.0.0.1" for address, port in listeners if port == 8768),
             "unauthorized Ceres listener")
    # A kernel 80/443 listener needs independent qualification; userspace Serve
    # is not a public host socket and is verified separately below.
    _require(not any(port in {80, 443} for _, port in listeners), "unexpected HTTP listener")
    return listeners


def validate_tailscale(value: dict, hostname: str) -> None:
    _require(set(value) <= {"TCP", "Web", "AllowFunnel", "Foreground"}, "unsupported Tailscale evidence")
    _require(not value.get("Foreground"), "unsupported foreground Serve configuration")
    _require(value.get("TCP") == {"443": {"HTTPS": True}} and
             value.get("Web") == {hostname + ":443": {"Handlers": {"/": {"Proxy": "http://127.0.0.1:8768"}}}},
             "Tailscale Serve target/configuration mismatch")
    funnel = value.get("AllowFunnel", {})
    _require(isinstance(funnel, dict) and set(funnel) <= {hostname + ":443"}
             and all(v is False for v in funnel.values()), "Tailscale Funnel must be off")


def stable_container(inspect: dict) -> dict:
    """Compare ALL persistent inspect fields, including full Config/HostConfig.

    The original object is retained, never reconstructed. State/RestartCount and
    runtime network endpoint addresses change on restart, requested network
    configuration is compared separately. Unknown persistent fields stay in.
    """
    result = {k: v for k, v in inspect.items() if k not in {"State", "RestartCount", "NetworkSettings"}}
    networks = inspect.get("NetworkSettings", {}).get("Networks", {})
    result["requested_networks"] = {name: {k: v.get(k) for k in
        ("IPAMConfig", "Links", "Aliases", "DriverOpts", "GwPriority")} for name, v in networks.items()}
    return result


def inspect_one(runner: Runner, *args: str) -> dict:
    values = json.loads(runner.capture(DOCKER + ["inspect", *args]))
    _require(isinstance(values, list) and len(values) == 1 and isinstance(values[0], dict),
             "malformed Docker inspection")
    return values[0]


def checked_file(path: Path, wanted: dict) -> dict:
    _require(path.is_absolute() and path.resolve() == path and not path.is_symlink(), "unsafe database/backup path")
    before = path.stat()
    _require(stat.S_ISREG(before.st_mode) and not before.st_mode & 0o222, "database/backup permissions unsafe")
    _require((before.st_uid, before.st_gid) == (wanted["uid"], wanted["gid"]), "database/backup owner mismatch")
    _require(not any(Path(str(path) + suffix).exists() for suffix in ("-wal", "-shm", "-journal")),
             "database/backup has mutable SQLite sidecars")
    with path.open("rb") as stream:
        digest = hashlib.file_digest(stream, "sha256").hexdigest()
    _require(all(getattr(path.stat(), k) == getattr(before, k) for k in ("st_dev", "st_ino", "st_size", "st_mtime_ns", "st_ctime_ns")) and digest == wanted["sha256"], "database/backup identity drift")
    return {"sha256": digest, "uid": before.st_uid, "gid": before.st_gid, "readable": True, "writable": False}


def refresh_host_state(runner: Runner, release: dict, evidence: dict) -> dict:
    """Inspect real local state; supplied snapshots only detect drift."""
    _require(socket.gethostname() == release["host_identity"], "wrong local host identity")
    live = inspect_one(runner, CONTAINER)
    _require(stable_container(live) == stable_container(evidence["container"]), "host Docker configuration drifted")
    _require(live.get("State", {}).get("Running") is True, "prior container is not running")
    exact_run_args(release, {"inspect": live}, release["image"])
    listeners = parse_listeners(runner.capture(["ss", "-H", "-ltn"]))
    _require(listeners == parse_listeners(evidence["listeners"]), "host listener state drifted")
    tailscale = json.loads(runner.capture(["tailscale", "serve", "status", "--json"]))
    validate_tailscale(tailscale, release["hostname"])
    _require(tailscale == evidence["tailscale"], "Tailscale state drifted")
    _require(shutil.disk_usage("/").free >= release["minimum_free_bytes"], "insufficient disk space")
    sources = {m["Destination"]: m["Source"] for m in live["Mounts"]}
    paths = []
    # Independently restore backup copies, never into live mounts.
    with tempfile.TemporaryDirectory(prefix="ceres-backup-verify-") as directory:
        restored = []
        for name in DATABASE_ENVS:
            wanted = release["databases"][name]
            source, backup = Path(sources[wanted["container_path"]]), Path(wanted["backup"]["path"])
            _require(not source.samefile(backup), "backup aliases live database")
            checked_file(source, wanted)
            checked_file(backup, wanted)
            copy = Path(directory) / (name + ".sqlite3")
            shutil.copyfile(backup, copy)
            copy.chmod(0o400)
            with copy.open("rb") as stream:
                _require(hashlib.file_digest(stream, "sha256").hexdigest() == wanted["sha256"], "restored backup hash mismatch")
            restored.append(copy)
            paths.append(source)
        manifest = load_manifest(ROOT)
        verify_runtime(*paths, manifest)
        verify_runtime(*restored, manifest)
    # Slow schema/media/restore work is followed by final identity and host checks.
    for name, path in zip(DATABASE_ENVS, paths):
        checked_file(path, release["databases"][name])
        checked_file(Path(release["databases"][name]["backup"]["path"]), release["databases"][name])
    final = inspect_one(runner, CONTAINER)
    _require(stable_container(final) == stable_container(live) and final["State"]["Running"] is True,
             "host drifted during preflight")
    _require(parse_listeners(runner.capture(["ss", "-H", "-ltn"])) == listeners, "listener drift during preflight")
    _require(json.loads(runner.capture(["tailscale", "serve", "status", "--json"])) == tailscale,
             "Tailscale drift during preflight")
    _require(shutil.disk_usage("/").free >= release["minimum_free_bytes"], "insufficient disk space")
    _require(time.time() < release["window_end_unix"], "maintenance window expired")
    return final


# Known Docker Engine inspect defaults. Unknown/nondefault options are not
# silently dropped from the candidate. Rollback does NOT depend on this map:
# it restarts the retained original container ID and compares its full config.
HOST_DEFAULTS = {
    "ContainerIDFile": "", "LogConfig": {"Type": "json-file", "Config": {}},
    "NetworkMode": "bridge", "AutoRemove": False, "VolumeDriver": "", "VolumesFrom": None,
    "ConsoleSize": [0, 0], "CapAdd": None, "CapDrop": None, "CgroupnsMode": "private",
    "Dns": [], "DnsOptions": [], "DnsSearch": [], "ExtraHosts": None, "GroupAdd": None,
    "IpcMode": "private", "Cgroup": "", "Links": None, "OomScoreAdj": 0, "PidMode": "",
    "Privileged": False, "PublishAllPorts": False, "SecurityOpt": None, "UTSMode": "",
    "UsernsMode": "", "ShmSize": 67108864, "Runtime": "runc", "Isolation": "",
    "CpuShares": 0, "Memory": 0, "NanoCpus": 0, "CgroupParent": "", "BlkioWeight": 0,
    "BlkioWeightDevice": [], "BlkioDeviceReadBps": [], "BlkioDeviceWriteBps": [],
    "BlkioDeviceReadIOps": [], "BlkioDeviceWriteIOps": [], "CpuPeriod": 0, "CpuQuota": 0,
    "CpuRealtimePeriod": 0, "CpuRealtimeRuntime": 0, "CpusetCpus": "", "CpusetMems": "",
    "Devices": [], "DeviceCgroupRules": None, "DeviceRequests": None, "MemoryReservation": 0,
    "MemorySwap": 0, "MemorySwappiness": None, "OomKillDisable": None, "PidsLimit": None,
    "Ulimits": None, "CpuCount": 0, "CpuPercent": 0, "IOMaximumIOps": 0,
    "IOMaximumBandwidth": 0, "MaskedPaths": ["/proc/asound", "/proc/acpi", "/proc/interrupts",
        "/proc/kcore", "/proc/keys", "/proc/latency_stats", "/proc/timer_list", "/proc/timer_stats",
        "/proc/sched_debug", "/proc/scsi", "/sys/firmware", "/sys/devices/virtual/powercap"],
    "ReadonlyPaths": ["/proc/bus", "/proc/fs", "/proc/irq", "/proc/sys", "/proc/sysrq-trigger"],
    "Init": False, "Mounts": [], "Annotations": {}, "StorageOpt": None, "Sysctls": None,
}


def exact_run_args(release: dict, prior: dict, image: str) -> list[str]:
    """Validate before stopping. Candidate profile only; never reconstruct rollback."""
    inspect = prior["inspect"]
    _require(bool(re.fullmatch(r"[0-9a-f]{64}", inspect.get("Id", ""))), "missing prior container ID")
    _require(bool(re.fullmatch(r"sha256:[0-9a-f]{64}", inspect.get("Image", ""))), "missing prior image ID")
    _require(inspect["Config"].get("Hostname") == inspect["Id"][:12], "unsupported custom container hostname")
    networks = inspect.get("NetworkSettings", {}).get("Networks", {})
    _require(set(networks) == {"bridge"} and all(networks["bridge"].get(k) is None for k in ("IPAMConfig", "Links", "Aliases", "DriverOpts"))
             and networks["bridge"].get("GwPriority", 0) == 0, "unsupported requested network configuration")
    host = inspect["HostConfig"]
    required = {"ReadonlyRootfs": True, "RestartPolicy": {"Name": "unless-stopped", "MaximumRetryCount": 0},
                "Tmpfs": {"/tmp": "rw,nosuid,nodev,size=64m"},
                "PortBindings": {"8768/tcp": [{"HostIp": "127.0.0.1", "HostPort": "8768"}]}}
    _require(all(host.get(k) == v for k, v in required.items()), "unsupported prior Docker configuration")
    for key, value in host.items():
        if key not in required and key != "Binds":
            _require(key in HOST_DEFAULTS and value == HOST_DEFAULTS[key], "unsupported prior Docker configuration")
    _require(host.get("AutoRemove") is False, "AutoRemove must explicitly be false")
    mounts = inspect["Mounts"]
    _require(len(mounts) == 3 and {m["Destination"] for m in mounts} ==
             {release["databases"][n]["container_path"] for n in DATABASE_ENVS}, "unsupported prior mounts")
    for m in mounts:
        _require(m.get("Type") == "bind" and m.get("RW") is False and m.get("Mode") == "ro"
                 and m.get("Propagation") == "rprivate" and Path(m["Source"]).is_absolute()
                 and not any(c in m["Source"] for c in (":", "\n", ",")), "unsupported prior bind")
    _require(sorted(host.get("Binds", [])) == sorted(f"{m['Source']}:{m['Destination']}:ro" for m in mounts),
             "prior bind representation mismatch")
    env = _env(inspect)
    _require(len(env) == len(inspect["Config"].get("Env", [])), "duplicate/malformed environment")
    safe_names = set(DATABASE_ENVS) | {"CERES_ALLOWED_HOSTS", "PATH", "LANG", "GPG_KEY",
        "PYTHON_VERSION", "PYTHON_SHA256", "PYTHONDONTWRITEBYTECODE", "PYTHONUNBUFFERED"}
    _require(set(env) <= safe_names and set(env) >= set(DATABASE_ENVS) | {"CERES_ALLOWED_HOSTS"},
             "unsupported prior environment")
    labels = inspect["Config"].get("Labels") or {}
    _require(set(labels) <= {"org.opencontainers.image." + n for n in ("title", "description", "source", "revision")},
             "unsupported prior labels")
    by_destination = {m["Destination"]: m for m in mounts}
    args = DOCKER + ["run", "--detach", "--name", CONTAINER, "--read-only",
            "--tmpfs", "/tmp:rw,nosuid,nodev,size=64m", "--restart", "unless-stopped", "--publish", PORT]
    for name in DATABASE_ENVS:
        destination = release["databases"][name]["container_path"]
        _require(env[name] == destination, "database environment mismatch")
        args += ["--volume", f"{by_destination[destination]['Source']}:{destination}:ro", "--env", f"{name}={destination}"]
    _require(env["CERES_ALLOWED_HOSTS"] == release["hostname"], "allowlist mismatch")
    args += ["--env", f"CERES_ALLOWED_HOSTS={release['hostname']}", image]
    return args


def validate_image_configuration(runner: Runner, release: dict, prior: dict) -> None:
    original = prior["inspect"]
    for image in (prior["prior_image"], release["image"]):
        inspected = inspect_one(runner, "--type", "image", image)
        _require(image in inspected.get("RepoDigests", []), "image digest not present locally")
        if image == prior["prior_image"]:
            _require(inspected["Id"] == original["Image"], "prior image identity mismatch")
            expected, actual = dict(inspected["Config"]), dict(original["Config"])
            # Container-generated hostname and explicit image/env overrides only.
            for key in ("Hostname", "Image", "Env"):
                expected.pop(key, None); actual.pop(key, None)
            # Engine adds these default fields to container Config. Any other
            # schema/config difference requires qualification before execution.
            for key, default in {"Domainname": "", "AttachStdin": False, "AttachStdout": False,
                                 "AttachStderr": False, "Tty": False, "OpenStdin": False,
                                 "StdinOnce": False}.items():
                expected.setdefault(key, default)
                actual.setdefault(key, default)
            _require(actual == expected, "unsupported prior image/configuration override")
            excluded = set(DATABASE_ENVS) | {"CERES_ALLOWED_HOSTS"}
            _require({k: v for k, v in _env(original).items() if k not in excluded} ==
                     {k: v for k, v in _env(inspected).items() if k not in excluded},
                     "unsupported inherited environment override")


def save_recovery(path: Path, release: dict, prior: dict, provenance: dict) -> None:
    _require(path.is_absolute() and path.parent.resolve() == path.parent, "unsafe recovery-record directory")
    # Exclusive creation and fsync. Never overwritten/deleted during recovery.
    directory = path.parent.stat()
    _require(directory.st_uid == os.getuid() and not directory.st_mode & 0o077, "recovery directory must be private and operator-owned")
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600)
    with os.fdopen(fd, "w") as stream:
        json.dump({"release": release, "prior": prior, "provenance": provenance}, stream, sort_keys=True)
        stream.flush()
        os.fsync(stream.fileno())
    parent = os.open(path.parent, os.O_RDONLY | os.O_DIRECTORY)
    try:
        os.fsync(parent)
    finally:
        os.close(parent)


def replace(runner: Runner, release: dict, evidence: dict, verify: Callable[[str], bool],
            timeout: float, recovery_path: Path) -> str:
    """Retain the exact original object; never remove/recreate it for rollback."""
    _require(not os.environ.get("CI") and not os.environ.get("GITHUB_ACTIONS"), "execution forbidden in CI")
    _require(0 < timeout <= 300, "invalid verification timeout")
    prior = validate_runtime(release, evidence)
    args = exact_run_args(release, prior, release["image"])  # Before pull and stop.
    provenance = validate_provenance(release, runner)
    runner.command(DOCKER + ["pull", release["image"]])
    original = prior["inspect"]
    original_id = original["Id"]
    retained_name = CONTAINER + "-rollback-" + original_id[:12]
    names = runner.capture(DOCKER + ["ps", "--all", "--format", "{{.Names}}"])
    _require(retained_name not in names.splitlines(), "rollback name already occupied")
    validate_image_configuration(runner, release, prior)
    _require(verify("current"), "current runtime/private access verification failed")
    save_recovery(recovery_path, release, prior, provenance)
    fresh = refresh_host_state(runner, release, evidence)  # After pull and durable evidence write.
    _require(stable_container(fresh) == stable_container(original), "final prior identity drift")
    _require(time.time() + timeout < release["window_end_unix"], "insufficient remaining maintenance window")
    stopped = renamed = False
    try:
        runner.command(DOCKER + ["stop", original_id])
        stopped = True
        runner.command(DOCKER + ["rename", original_id, retained_name])
        renamed = True
        runner.command(args)
        deadline = time.monotonic() + timeout
        while time.monotonic() < deadline:
            if verify("candidate") and time.monotonic() <= deadline:
                return "UPDATED_ORIGINAL_RETAINED"
            time.sleep(min(1, max(0, deadline - time.monotonic())))
        raise ReleaseError("candidate verification timeout")
    except (Exception, KeyboardInterrupt):
        # stop/rename may have succeeded despite a lost client response.
        try:
            retained = inspect_one(runner, original_id)
            _require(retained["Id"] == original_id and retained["Image"] == original["Image"], "prior object identity changed")
            compared = dict(retained, Name=original["Name"])
            _require(stable_container(compared) == stable_container(original), "retained configuration drifted; manual recovery required")
            if renamed or retained["Name"] == "/" + retained_name:
                ids = runner.capture(DOCKER + ["ps", "--all", "--filter", "name=^/" + CONTAINER + "$",
                                               "--format", "{{.ID}}", "--no-trunc"]).splitlines()
                _require(len(ids) <= 1, "ambiguous candidate identity")
                if ids:
                    candidate = inspect_one(runner, ids[0])
                    _require(candidate["Id"] != original_id and candidate["Config"]["Image"] == release["image"],
                             "refusing to remove unrelated container")
                    runner.command(DOCKER + ["rm", "--force", candidate["Id"]])
                runner.command(DOCKER + ["rename", original_id, CONTAINER])
            if stopped or retained["State"]["Running"] is not True:
                runner.command(DOCKER + ["start", original_id])
            restored = inspect_one(runner, original_id)
            _require(stable_container(restored) == stable_container(original) and restored["State"]["Running"] is True,
                     "restored configuration does not exactly match")
            _require(verify("rollback"), "restored runtime verification failed")
        except (Exception, KeyboardInterrupt):
            raise ReleaseError("ROLLBACK FAILED; original container, image, backups and recovery record retained") from None
        raise ReleaseError("candidate failed; exact original container rollback verified; recovery record retained") from None


def redact(value: Any) -> Any:
    if isinstance(value, dict):
        return {k: ("[REDACTED]" if any(x in k.lower() for x in ("token", "secret", "password")) else redact(v)) for k, v in value.items()}
    if isinstance(value, list):
        return [redact(v) for v in value]
    return value


def live_verify(release: dict[str, Any], phase: str, timeout: float = 60) -> bool:
    """Verify local bytes/data, then require the operator's private-browser gate."""
    try:
        deadline = time.monotonic() + timeout
        def get(path: str) -> bytes:
            request = urllib.request.Request(f"http://127.0.0.1:8768{path}",
                                             headers={"Host": release["hostname"]})
            with urllib.request.urlopen(request, timeout=max(.001, min(5, deadline - time.monotonic()))) as response:
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
        print(f"Verify {phase} in the existing private browser via Tailscale Serve; type VERIFIED: ", end="", flush=True)
        ready, _, _ = select.select([sys.stdin], [], [], max(0, deadline - time.monotonic()))
        _require(bool(ready), "private-browser verification timed out")
        answer = sys.stdin.readline().strip()
        _require(answer == "VERIFIED", "private-browser verification not confirmed")
        return True
    except (OSError, ValueError, KeyError, ReleaseError):
        return False


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--release", type=Path, required=True)
    parser.add_argument("--evidence", type=Path, required=True, help="offline, nonsecret host/registry/health evidence")
    parser.add_argument("--execute", action="store_true", help="future authorized local maintenance only")
    parser.add_argument("--recovery-record", type=Path, help="new secure file, required for execution")
    parser.add_argument("--verify-provenance", action="store_true", help="read-only authenticated GitHub/GHCR check")
    parser.add_argument("--timeout", type=float, default=60)
    args = parser.parse_args(argv)
    try:
        release, evidence = load_json(args.release), load_json(args.evidence)
        validate_release(release)
        prior = validate_runtime(release, evidence)
        validate_health(release, evidence.get("current_health", {}))
        report = {"result": "OFFLINE_PLAN_ONLY", "target": "SYDNEY", "candidate": release["image"],
                  "prior_image": prior["prior_image"], "mutation_performed": False,
                  "provenance": "UNVERIFIED",
                  "limitations": "untrusted offline snapshot; not execution authorization or qualification"}
        if args.verify_provenance and not args.execute:
            report["provenance"] = validate_provenance(release, Runner())
        if args.execute:
            _require(not os.environ.get("CI") and not os.environ.get("GITHUB_ACTIONS"), "execution forbidden in CI")
            _require(sys.stdin.isatty(), "execution requires an interactive terminal")
            _require(args.recovery_record is not None, "recovery record required")
            _require(time.time() < release["window_end_unix"], "maintenance window expired")
            confirmation = input("Maintenance window authorized; type the candidate digest to continue: ")
            _require(confirmation == release["image"], "maintenance confirmation mismatch")
            live_runner = Runner()
            report["result"] = replace(live_runner, release, evidence,
                                       lambda phase: live_verify(release, phase, args.timeout), args.timeout, args.recovery_record)
            report["mutation_performed"] = True
            report["provenance"] = "AUTHENTICATED_BY_GITHUB_AND_GHCR"
        print(json.dumps(redact(report), sort_keys=True))
        return 0
    except (EOFError, OSError, ValueError, KeyError, TypeError, AttributeError, ReleaseError) as error:
        message = str(error) if isinstance(error, ReleaseError) else "malformed or unavailable evidence/input"
        print(f"FAIL CLOSED: {message}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
