from __future__ import annotations

import json
from subprocess import CompletedProcess

import pytest

from deploy.ceres_sydney_release import (
    APPROVAL, ReleaseError, Runner, main, replace,
    validate_health, validate_provenance, validate_release, validate_runtime,
)

D0 = "sha256:" + "0" * 64
D1 = "sha256:" + "1" * 64
IMAGE0 = "ghcr.io/loom-2226/ceres-atlas@" + D0
IMAGE1 = "ghcr.io/loom-2226/ceres-atlas@" + D1


@pytest.fixture
def release():
    dbs = {}
    for index, name in enumerate(("CERES_WORLD_DB", "CERES_CIVSTATE_DB", "CERES_MEDIA_DB")):
        digest = str(index + 2) * 64
        dbs[name] = {"container_path": f"/data/{name.lower()}.sqlite3", "sha256": digest,
                     "uid": 1000, "gid": 1000, "backup": {"sha256": digest, "restore_tested": True}}
    return {"schema_version": 1, "target": "SYDNEY", "approval": APPROVAL,
            "source_sha": "a" * 40, "image": IMAGE1, "successful_ci_run_ids": [123, 456],
            "provenance": {"source_sha": "a" * 40, "image": IMAGE1},
            "hostname": "ceres.private.example", "minimum_free_bytes": 100,
            "databases": dbs, "checks": {"world_identity": "CER", "civstate_identity": "BODY:CERES:CERES@2226",
            "media_path": "/assets/ceres-world-hero.png", "media_sha256": "f" * 64}}


@pytest.fixture
def evidence(release):
    mounts, files, backups, env = [], {}, {}, []
    for index, (name, item) in enumerate(release["databases"].items()):
        source = f"/srv/ceres/db{index}.sqlite3"
        mounts.append({"Type": "bind", "Source": source, "Destination": item["container_path"], "RW": False})
        files[source] = {"sha256": item["sha256"], "readable": True, "writable": False, "uid": 1000, "gid": 1000}
        backups[name] = {"sha256": item["sha256"], "readable": True, "restore_tested": True,
                         "restore_test_id": f"restore-{index}"}
        env.append(f"{name}={item['container_path']}")
    env.append("CERES_ALLOWED_HOSTS=ceres.private.example")
    health = {"/healthz": {"status": 200}, "/": {"status": 200},
              "/atlas-data.json": {"status": 200, "world_identity": "CER", "civstate_identity": "BODY:CERES:CERES@2226"},
              "/assets/ceres-world-hero.png": {"status": 200, "sha256": "f" * 64},
              "private_browser_verified": True}
    return {"registry": {"available": True, "resolved_image": IMAGE1, "source_sha": "a" * 40,
                         "successful_ci_run_ids": [123, 456]},
            "authentication": {"source_commit_verified": True, "image_digest_verified": True, "ci_runs_verified": True},
            "disk_free_bytes": 1000,
            "public_listeners": [], "tailscale": {"funnel": False, "serve_target": "http://127.0.0.1:8768"},
            "files": files, "backups": backups, "current_health": health,
            "container": {"Name": "/ceres-atlas", "Config": {"Image": IMAGE0, "Env": env}, "Mounts": mounts,
              "HostConfig": {"ReadonlyRootfs": True, "RestartPolicy": {"Name": "unless-stopped", "MaximumRetryCount": 0},
              "Tmpfs": {"/tmp": "rw,nosuid,nodev,size=64m"},
              "PortBindings": {"8768/tcp": [{"HostIp": "127.0.0.1", "HostPort": "8768"}]}}}}


def test_positive_offline_dry_run(tmp_path, release, evidence, capsys):
    rp, ep = tmp_path / "release.json", tmp_path / "evidence.json"
    rp.write_text(json.dumps(release)); ep.write_text(json.dumps(evidence))
    assert main(["--release", str(rp), "--evidence", str(ep)]) == 0
    assert json.loads(capsys.readouterr().out)["mutation_performed"] is False


@pytest.mark.parametrize("mutation, message", [
    (lambda r, e: r.update(image="ghcr.io/loom-2226/ceres-atlas:latest"), "immutable"),
    (lambda r, e: r["provenance"].update(source_sha="b" * 40), "provenance"),
    (lambda r, e: e["registry"].update(available=False), "registry"),
    (lambda r, e: e["registry"].update(resolved_image=IMAGE0), "digest"),
    (lambda r, e: e["container"]["Mounts"].pop(), "mount absent"),
    (lambda r, e: e["container"]["Mounts"][0].update(RW=True), "writable"),
    (lambda r, e: e["files"]["/srv/ceres/db0.sqlite3"].update(uid=0), "owner"),
    (lambda r, e: e["files"]["/srv/ceres/db0.sqlite3"].update(writable=True), "permissions"),
    (lambda r, e: e["backups"]["CERES_WORLD_DB"].update(restore_tested=False), "restore-test"),
    (lambda r, e: e["public_listeners"].append("443"), "public"),
    (lambda r, e: e["container"]["HostConfig"]["PortBindings"]["8768/tcp"][0].update(HostIp="0.0.0.0"), "127.0.0.1"),
    (lambda r, e: e["tailscale"].update(funnel=True), "Funnel"),
    (lambda r, e: e.update(disk_free_bytes=1), "disk"),
])
def test_preflight_negative(release, evidence, mutation, message):
    mutation(release, evidence)
    with pytest.raises(ReleaseError, match=message):
        validate_release(release); validate_provenance(release, evidence); validate_runtime(release, evidence)


@pytest.mark.parametrize("mutation, message", [
    (lambda h: h["/healthz"].update(status=503), "healthz"),
    (lambda h: h["/"].update(status=500), "unhealthy"),
    (lambda h: h["/atlas-data.json"].update(world_identity="EARTH"), "WORLD"),
    (lambda h: h["/atlas-data.json"].update(civstate_identity="wrong"), "CIVSTATE"),
    (lambda h: h["/assets/ceres-world-hero.png"].update(sha256="0" * 64), "MEDIA"),
    (lambda h: h.update(private_browser_verified=False), "browser"),
])
def test_health_negative(release, evidence, mutation, message):
    mutation(evidence["current_health"])
    with pytest.raises(ReleaseError, match=message):
        validate_health(release, evidence["current_health"])


class FakeCommands:
    def __init__(self, fail_at=None): self.commands, self.fail_at = [], fail_at
    def __call__(self, args, **kwargs):
        self.commands.append(args)
        failed = self.fail_at == len(self.commands)
        return CompletedProcess(args, 1 if failed else 0, "", "injected" if failed else "")


def test_candidate_failure_restores_exact_prior(release, evidence):
    fake = FakeCommands(fail_at=4)  # candidate docker run
    with pytest.raises(ReleaseError, match="exact rollback verified"):
        replace(Runner(fake), release, {"prior_image": IMAGE0, "inspect": evidence["container"]}, lambda phase: phase == "rollback", 0)
    assert fake.commands[-1][-1] == IMAGE0
    assert "127.0.0.1:8768:8768" in fake.commands[-1]


def test_timeout_rolls_back(release, evidence):
    fake = FakeCommands()
    with pytest.raises(ReleaseError, match="timeout"):
        replace(Runner(fake), release, {"prior_image": IMAGE0, "inspect": evidence["container"]}, lambda phase: phase == "rollback", 0)
    assert fake.commands[-1][-1] == IMAGE0


def test_failed_rollback_stops_and_preserves_evidence(release, evidence):
    fake = FakeCommands()
    with pytest.raises(ReleaseError, match="ROLLBACK FAILED; preserve evidence"):
        replace(Runner(fake), release, {"prior_image": IMAGE0, "inspect": evidence["container"]}, lambda phase: False, 0)


def test_release_rejects_inconsistent_backup(release):
    release["databases"]["CERES_MEDIA_DB"]["backup"]["sha256"] = "0" * 64
    with pytest.raises(ReleaseError, match="backup hash"):
        validate_release(release)

def test_provenance_rejects_self_consistent_unverified_evidence(release, evidence):
    evidence["authentication"]["image_digest_verified"] = False
    with pytest.raises(ReleaseError, match="independently authenticated"):
        validate_provenance(release, evidence)

def test_rollback_rejects_unsupported_prior_configuration(release, evidence):
    prior = {"prior_image": IMAGE0, "inspect": json.loads(json.dumps(evidence["container"]))}
    prior["inspect"]["HostConfig"]["SecurityOpt"] = ["no-new-privileges"]
    with pytest.raises(ReleaseError, match="unsupported prior Docker configuration"):
        replace(Runner(FakeCommands()), release, prior, lambda phase: True, 0)
