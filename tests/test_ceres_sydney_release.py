from __future__ import annotations

import json
import copy
import hashlib
import os
import socket
import time
from pathlib import Path

import deploy.ceres_sydney_release as subject
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
                     "uid": os.getuid(), "gid": os.getgid(), "backup": {"sha256": digest, "restore_tested": True, "path": f"/backup/{name}.sqlite3"}}
    return {"schema_version": 1, "target": "SYDNEY", "approval": APPROVAL,
            "source_sha": "a" * 40, "image": IMAGE1, "successful_ci_run_ids": [123, 456],
            "provenance": {"source_sha": "a" * 40, "image": IMAGE1},
            "hostname": "ceres.private.example", "host_identity": socket.gethostname(), "window_end_unix": time.time() + 600, "minimum_free_bytes": 100,
            "databases": dbs, "checks": {"world_identity": "CER", "civstate_identity": "BODY:CERES:CERES@2226",
            "media_path": "/assets/ceres-world-hero.png", "media_sha256": "f" * 64}}


@pytest.fixture
def evidence(release):
    mounts, files, backups, env = [], {}, {}, []
    for index, (name, item) in enumerate(release["databases"].items()):
        source = f"/srv/ceres/db{index}.sqlite3"
        mounts.append({"Type": "bind", "Source": source, "Destination": item["container_path"], "RW": False, "Mode": "ro", "Propagation": "rprivate"})
        files[source] = {"sha256": item["sha256"], "readable": True, "writable": False, "uid": os.getuid(), "gid": os.getgid()}
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
            "public_listeners": [], "listeners": "LISTEN 0 4096 127.0.0.1:8768 0.0.0.0:*\n",
            "tailscale": {"TCP": {"443": {"HTTPS": True}}, "Web": {"ceres.private.example:443": {"Handlers": {"/": {"Proxy": "http://127.0.0.1:8768"}}}}, "AllowFunnel": {}},
            "files": files, "backups": backups, "current_health": health,
            "container": {"Name": "/ceres-atlas", "Id": "c" * 64, "Image": "sha256:" + "d" * 64, "State": {"Running": True}, "NetworkSettings": {"Networks": {"bridge": {"IPAMConfig": None, "Links": None, "Aliases": None, "DriverOpts": None}}}, "Config": {"Image": IMAGE0, "Env": env, "Hostname": "c" * 12}, "Mounts": mounts,
              "HostConfig": {"AutoRemove": False, "NetworkMode": "bridge", "LogConfig": {"Type": "json-file", "Config": {}},
              "Privileged": False, "PublishAllPorts": False, "CapAdd": None, "CapDrop": None, "SecurityOpt": None,
              "Memory": 0, "MemorySwap": 0, "MemorySwappiness": None, "CpuShares": 0, "CpuPeriod": 0,
              "Runtime": "runc", "IpcMode": "private", "PidMode": "", "Devices": [], "DeviceRequests": None,
              "Dns": [], "DnsOptions": [], "DnsSearch": [], "ExtraHosts": None, "ShmSize": 67108864, "Binds": [f"{m['Source']}:{m['Destination']}:ro" for m in mounts], "ReadonlyRootfs": True, "RestartPolicy": {"Name": "unless-stopped", "MaximumRetryCount": 0},
              "Tmpfs": {"/tmp": "rw,nosuid,nodev,size=64m"},
              "PortBindings": {"8768/tcp": [{"HostIp": "127.0.0.1", "HostPort": "8768"}]}}}}


def test_positive_offline_dry_run(tmp_path, release, evidence, capsys):
    rp, ep = tmp_path / "release.json", tmp_path / "evidence.json"
    rp.write_text(json.dumps(release)); ep.write_text(json.dumps(evidence))
    assert main(["--release", str(rp), "--evidence", str(ep)]) == 0
    report = json.loads(capsys.readouterr().out)
    assert report["mutation_performed"] is False
    assert report["result"] == "OFFLINE_PLAN_ONLY"
    assert report["provenance"] == "UNVERIFIED"


@pytest.mark.parametrize("mutation, message", [
    (lambda r, e: r.update(image="ghcr.io/loom-2226/ceres-atlas:latest"), "immutable"),
    (lambda r, e: r["provenance"].update(source_sha="b" * 40), "provenance"),
    (lambda r, e: e["container"]["Mounts"].pop(), "mount absent"),
    (lambda r, e: e["container"]["Mounts"][0].update(RW=True), "writable"),
    (lambda r, e: e["files"]["/srv/ceres/db0.sqlite3"].update(uid=0), "owner"),
    (lambda r, e: e["files"]["/srv/ceres/db0.sqlite3"].update(writable=True), "permissions"),
    (lambda r, e: e["backups"]["CERES_WORLD_DB"].update(restore_tested=False), "restore-test"),
    (lambda r, e: e["public_listeners"].append("443"), "public"),
    (lambda r, e: e["container"]["HostConfig"]["PortBindings"]["8768/tcp"][0].update(HostIp="0.0.0.0"), "127.0.0.1"),
    (lambda r, e: e["tailscale"]["AllowFunnel"].update({"ceres.private.example:443": True}), "Funnel"),
    (lambda r, e: e.update(disk_free_bytes=1), "disk"),
])
def test_preflight_negative(release, evidence, mutation, message):
    mutation(release, evidence)
    with pytest.raises(ReleaseError, match=message):
        validate_release(release); validate_runtime(release, evidence)


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


class Authority:
    """Authenticated-command boundary double. Never connects to GitHub or GHCR."""
    def __init__(self, release):
        self.commands = []
        self.responses = {
            "user": {"login": "operator"},
            f"repos/{subject.REPO}/commits/{release['source_sha']}": {"sha": release["source_sha"]},
            "users/loom-2226/packages/container/ceres-atlas": {"name": "ceres-atlas", "visibility": "private", "repository": {"full_name": subject.REPO}},
        }
        for run_id in release["successful_ci_run_ids"]:
            self.responses[f"repos/{subject.REPO}/actions/runs/{run_id}"] = {
                "id": run_id, "head_sha": release["source_sha"], "repository": {"full_name": subject.REPO},
                "head_repository": {"full_name": subject.REPO}, "path": subject.WORKFLOW,
                "status": "completed", "conclusion": "success", "event": "push", "run_attempt": 1}
        self.statement = {"predicateType": "https://slsa.dev/provenance/v1",
                          "subject": [{"digest": {"sha256": "1" * 64}}],
                          "predicate": {"runDetails": {"metadata": {"invocationId":
                              f"https://github.com/{subject.REPO}/actions/runs/123/attempts/1"}}}}
        self.responses["attestation"] = [{"verificationResult": {"statement": self.statement}}]

    def __call__(self, args, **kwargs):
        self.commands.append(args)
        key = "attestation" if args[1] == "attestation" else args[-1]
        value = self.responses.get(key)
        return CompletedProcess(args, 0 if value is not None else 1, json.dumps(value), "secret must not leak")


def test_authenticated_provenance(release):
    fake = Authority(release)
    proof = validate_provenance(release, Runner(fake))
    assert proof["ci_run_ids"] == [123, 456]
    args = fake.commands[-1]
    assert "oci://" + IMAGE1 in args
    for flag in ("--source-digest", "--signer-digest"):
        assert args[args.index(flag) + 1] == release["source_sha"]
    assert args[args.index("--signer-workflow") + 1] == subject.REPO + "/" + subject.WORKFLOW
    assert "--deny-self-hosted-runners" in args


def test_forged_assertions_never_authorize(release, evidence):
    with pytest.raises(ReleaseError, match="not assertions"):
        validate_provenance(release, evidence)


@pytest.mark.parametrize("field,value", [
    ("id", 999), ("head_sha", "b" * 40), ("status", "in_progress"), ("conclusion", "failure"),
    ("conclusion", "cancelled"), ("path", ".github/workflows/other.yml"), ("event", "pull_request_target"),
    ("repository", {"full_name": "attacker/repo"}), ("head_repository", {"full_name": "attacker/repo"}),
])
def test_rejects_invalid_authenticated_ci(release, field, value):
    fake = Authority(release)
    fake.responses[f"repos/{subject.REPO}/actions/runs/123"][field] = value
    with pytest.raises(ReleaseError, match="authenticated CI"):
        validate_provenance(release, Runner(fake))


@pytest.mark.parametrize("key", ["user", "commit", "ci", "attestation", "package"])
def test_missing_authentication_fails_closed(release, key):
    fake = Authority(release)
    key = {"commit": f"repos/{subject.REPO}/commits/{release['source_sha']}",
           "ci": f"repos/{subject.REPO}/actions/runs/123",
           "package": "users/loom-2226/packages/container/ceres-atlas"}.get(key, key)
    fake.responses[key] = None
    with pytest.raises(ReleaseError, match="output withheld") as error:
        validate_provenance(release, Runner(fake))
    assert "secret" not in str(error.value)


@pytest.mark.parametrize("defect", ["digest", "source", "attempt", "run", "empty", "public", "package"])
def test_mismatched_signed_provenance(release, defect):
    fake = Authority(release)
    if defect == "digest": fake.statement["subject"][0]["digest"]["sha256"] = "0" * 64
    if defect == "source": fake.responses[f"repos/{subject.REPO}/commits/{release['source_sha']}"]["sha"] = "b" * 40
    if defect == "attempt": fake.responses[f"repos/{subject.REPO}/actions/runs/123"]["run_attempt"] = 2
    if defect == "run": fake.statement["predicate"]["runDetails"]["metadata"]["invocationId"] = f"https://github.com/{subject.REPO}/actions/runs/999/attempts/1"
    if defect == "empty": fake.responses["attestation"] = []
    if defect == "public": fake.responses["users/loom-2226/packages/container/ceres-atlas"]["visibility"] = "public"
    if defect == "package": fake.responses["users/loom-2226/packages/container/ceres-atlas"]["repository"] = {"full_name": "evil/elsewhere"}
    with pytest.raises(ReleaseError):
        validate_provenance(release, Runner(fake))


def test_listener_accepts_exact_loopback_and_separate_ssh(evidence):
    output = evidence["listeners"] + "LISTEN 0 128 [::]:22 [::]:*\n"
    assert ("127.0.0.1", 8768) in subject.parse_listeners(output)
    assert ("::", 22) in subject.parse_listeners(output)


@pytest.mark.parametrize("endpoint", ["0.0.0.0:8768", "[::]:8768", "[::1]:8768", "*:8768", "10.0.0.5:8768", "[::ffff:127.0.0.1]:8768", "127.0.0.2:8768", "0.0.0.0:443", "[::]:80"])
def test_rejects_public_or_unauthorized_listener(evidence, endpoint):
    with pytest.raises(ReleaseError):
        subject.parse_listeners(evidence["listeners"] + f"LISTEN 0 128 {endpoint} *:*\n")


@pytest.mark.parametrize("output", ["", "nonsense", "LISTEN 0 128 bad:8768 *:*", "LISTEN 0 128 127.0.0.1:x *:*", "LISTEN 0 128 [::1:8768 *:*", "LISTEN 0 128 127.0.0.1:98768 *:*", "State Recv-Q Send-Q Local Address Peer"])
def test_rejects_malformed_or_absent_listeners(output):
    with pytest.raises(ReleaseError): subject.parse_listeners(output)


class DockerDouble(Authority):
    """Stateful engine simulator; no host access. Original ID survives rollback."""
    def __init__(self, release, evidence, fail=None):
        super().__init__(release)
        self.original = copy.deepcopy(evidence["container"])
        self.candidate = None
        self.fail = fail
        self.fail_used = False
        self.evidence = evidence

    def __call__(self, args, **kwargs):
        if args[0] == "gh": return super().__call__(args, **kwargs)
        self.commands.append(args)
        assert args[:3] == subject.DOCKER
        action, rest = args[3], args[4:]
        if self.fail == action and not self.fail_used:
            self.fail_used = True
            return CompletedProcess(args, 1, "", "sensitive failure")
        output = ""
        if action == "inspect":
            if rest[:2] == ["--type", "image"]:
                image = rest[2]
                config = copy.deepcopy(self.evidence["container"]["Config"])
                output = json.dumps([{"RepoDigests": [image], "Id": self.original["Image"], "Config": config}])
            else:
                value = self.candidate if self.candidate and rest[0] == self.candidate["Id"] else self.original
                output = json.dumps([value])
        elif action == "ps":
            output = (self.candidate["Id"] if self.candidate else "") if "--filter" in rest else self.original["Name"].lstrip("/")
        elif action == "stop": self.original["State"]["Running"] = False
        elif action == "rename":
            assert rest[0] == self.original["Id"]
            self.original["Name"] = "/" + rest[1]
        elif action == "run":
            self.candidate = copy.deepcopy(self.original)
            self.candidate.update(Id="e" * 64, Name="/ceres-atlas")
            self.candidate["Config"]["Image"] = IMAGE1
            self.candidate["State"]["Running"] = True
        elif action == "rm":
            assert rest == ["--force", "e" * 64]  # NEVER original ID/name.
            self.candidate = None
        elif action == "start": self.original["State"]["Running"] = True
        elif action != "pull": raise AssertionError(args)
        return CompletedProcess(args, 0, output, "")


@pytest.fixture
def execution(monkeypatch, release, evidence, tmp_path):
    monkeypatch.delenv("CI", raising=False)
    monkeypatch.delenv("GITHUB_ACTIONS", raising=False)
    fake = DockerDouble(release, evidence)
    # Independent preflight tests below exercise real refresh with local files.
    def refresh(runner, approved, reviewed):
        assert fake.commands[-1][3] == "inspect"  # image validation completed
        fake.commands.append(["final-live-refresh"])
        return copy.deepcopy(evidence["container"])
    monkeypatch.setattr(subject, "refresh_host_state", refresh)
    return fake, tmp_path / "recovery.json"


def test_candidate_succeeds_and_retains_original(release, evidence, execution):
    fake, record = execution
    assert replace(Runner(fake), release, evidence, lambda phase: True, .01, record) == "UPDATED_ORIGINAL_RETAINED"
    assert fake.original["Name"].startswith("/ceres-atlas-rollback-")
    assert fake.original["Id"] == evidence["container"]["Id"]
    assert fake.original["State"]["Running"] is False
    assert record.stat().st_mode & 0o777 == 0o600
    stop = next(i for i, command in enumerate(fake.commands) if command[3:4] == ["stop"])
    assert fake.commands[stop - 1] == ["final-live-refresh"]
    assert not any(c[3:4] == ["rm"] for c in fake.commands)


@pytest.mark.parametrize("failure", ["run", "timeout", "rename", "stop"])
def test_failed_candidate_exact_original_rollback(release, evidence, execution, failure):
    fake, record = execution
    fake.fail = failure
    with pytest.raises(ReleaseError, match="exact original container rollback verified"):
        replace(Runner(fake), release, evidence, lambda phase: phase != "candidate", .001, record)
    assert subject.stable_container(fake.original) == subject.stable_container(evidence["container"])
    assert fake.original["State"]["Running"] is True
    assert json.loads(record.read_text())["prior"]["inspect"] == evidence["container"]
    assert all(c[3:4] != ["rm"] or c[-1] != fake.original["Id"] for c in fake.commands)


@pytest.mark.parametrize("failure", ["health", "start", "rm"])
def test_failed_rollback_preserves_all_evidence(release, evidence, execution, failure):
    fake, record = execution
    fake.fail = failure
    with pytest.raises(ReleaseError, match="ROLLBACK FAILED.*retained"):
        replace(Runner(fake), release, evidence, lambda phase: phase == "current", .001, record)
    assert record.exists()
    assert json.loads(record.read_text())["prior"]["inspect"]["Id"] == fake.original["Id"]
    assert fake.original["Image"] == evidence["container"]["Image"]


@pytest.mark.parametrize("key,value", [("AutoRemove", True), ("SecurityOpt", ["no-new-privileges"]), ("NewDockerOption", False), ("Privileged", True), ("NetworkMode", "host")])
def test_unsupported_docker_config_rejected_before_any_commands(release, evidence, execution, key, value):
    fake, record = execution
    evidence["container"]["HostConfig"][key] = value
    with pytest.raises(ReleaseError): replace(Runner(fake), release, evidence, lambda phase: True, .01, record)
    assert fake.commands == []
    assert not record.exists()


def test_full_config_drift_blocks_rollback_success(release, evidence, execution):
    fake, record = execution
    def verify(phase):
        if phase == "candidate": fake.original["HostConfig"]["CpuShares"] = 20
        return phase != "candidate"
    with pytest.raises(ReleaseError, match="ROLLBACK FAILED"):
        replace(Runner(fake), release, evidence, verify, .001, record)
    assert record.exists()


def test_refresh_failure_never_stops_existing(release, evidence, execution, monkeypatch):
    fake, record = execution
    def reject(*args): raise ReleaseError("host drift")
    monkeypatch.setattr(subject, "refresh_host_state", reject)
    with pytest.raises(ReleaseError, match="host drift"):
        replace(Runner(fake), release, evidence, lambda phase: True, .01, record)
    assert not any(c[3:4] in (["stop"], ["run"], ["rm"]) for c in fake.commands)
    assert record.exists()


def test_ci_cannot_execute(release, evidence, execution, monkeypatch):
    fake, record = execution
    monkeypatch.setenv("CI", "true")
    with pytest.raises(ReleaseError, match="forbidden in CI"):
        replace(Runner(fake), release, evidence, lambda phase: True, .01, record)
    assert fake.commands == []


def test_existing_recovery_record_never_overwritten(tmp_path, release, evidence):
    path = tmp_path / "recovery.json"
    path.write_text("previous")
    with pytest.raises(FileExistsError): subject.save_recovery(path, release, evidence, {})
    assert path.read_text() == "previous"


@pytest.fixture
def local_host(tmp_path, release, evidence, monkeypatch):
    """Disposable filesystem; mocked processes never contact a host."""
    # Simulate the Linux host disk; Android root is a read-only system partition.
    from types import SimpleNamespace
    monkeypatch.setattr(subject.shutil, "disk_usage", lambda path: SimpleNamespace(free=10**10))
    for index, name in enumerate(subject.DATABASE_ENVS):
        wanted = release['databases'][name]
        content = ('disposable-' + name).encode()
        source, backup = tmp_path / f'{index}.sqlite3', tmp_path / f'{index}.backup'
        source.write_bytes(content); backup.write_bytes(content)
        source.chmod(0o400); backup.chmod(0o400)
        wanted.update(sha256=hashlib.sha256(content).hexdigest(), uid=os.getuid(), gid=os.getgid())
        wanted['backup'].update(path=str(backup), sha256=wanted['sha256'])
        evidence['container']['Mounts'][index]['Source'] = str(source)
    evidence['container']['HostConfig']['Binds'] = [f"{m['Source']}:{m['Destination']}:ro" for m in evidence['container']['Mounts']]
    class Host:
        def __init__(self): self.commands, self.change = [], None
        def __call__(self, args, **kwargs):
            self.commands.append(args)
            if args == subject.DOCKER + ['inspect', 'ceres-atlas']:
                value = copy.deepcopy(evidence['container'])
            elif args == ['ss', '-H', '-ltn']: value = evidence['listeners']
            elif args == ['tailscale', 'serve', 'status', '--json']: value = copy.deepcopy(evidence['tailscale'])
            else: raise AssertionError(f'unexpected process {args}')
            if self.change: value = self.change(args, value)
            return CompletedProcess(args, 0, value if isinstance(value, str) else json.dumps([value] if args[0] == 'docker' else value), '')
    return Host()


def test_live_refresh_restores_independent_backup_copies(release, evidence, local_host, monkeypatch):
    inspected = []
    def schemas(world, civstate, media, manifest):
        paths = [world, civstate, media]
        inspected.append(paths)
        for name, path in zip(subject.DATABASE_ENVS, paths):
            assert hashlib.sha256(path.read_bytes()).hexdigest() == release['databases'][name]['sha256']
        return {'status': 'ok'}
    monkeypatch.setattr(subject, 'verify_runtime', schemas)
    assert subject.refresh_host_state(Runner(local_host), release, evidence) == evidence['container']
    assert len(inspected) == 2
    assert all(a != b for a, b in zip(*inspected))
    assert all(not p.exists() for p in inspected[1])
    assert len(local_host.commands) == 6  # before/after Docker, ss and Serve


@pytest.mark.parametrize('defect', ['hash', 'writable', 'owner', 'missing', 'wal', 'backup', 'backup_alias', 'schema', 'host', 'expired', 'disk'])
def test_live_files_and_readiness_fail_closed(release, evidence, local_host, monkeypatch, defect):
    item = release['databases']['CERES_WORLD_DB']
    path = Path(evidence['container']['Mounts'][0]['Source'])
    monkeypatch.setattr(subject, 'verify_runtime', lambda *args: {'status': 'ok'})
    if defect == 'hash': item['sha256'] = '0' * 64
    if defect == 'writable': path.chmod(0o600)
    if defect == 'owner': item['uid'] += 1
    if defect == 'missing': path.unlink()
    if defect == 'wal': Path(str(path) + '-wal').write_bytes(b'mutable')
    if defect == 'backup': Path(item['backup']['path']).unlink()
    if defect == 'backup_alias': item['backup']['path'] = str(path)
    if defect == 'schema':
        def reject(*args): raise ValueError('incompatible actual schema')
        monkeypatch.setattr(subject, 'verify_runtime', reject)
    if defect == 'host': release['host_identity'] = 'different-host'
    if defect == 'expired': release['window_end_unix'] = 1
    if defect == 'disk': release['minimum_free_bytes'] = 10**25
    with pytest.raises((ReleaseError, OSError, ValueError)):
        subject.refresh_host_state(Runner(local_host), release, evidence)
    assert all(c[3:4] != ['stop'] for c in local_host.commands)


@pytest.mark.parametrize('defect', ['inspect', 'listener', 'tailscale', 'malformed', 'during_preflight'])
def test_actual_host_state_drift(release, evidence, local_host, monkeypatch, defect):
    monkeypatch.setattr(subject, 'verify_runtime', lambda *args: {'status': 'ok'})
    def change(args, value):
        if args[0] == 'docker':
            if defect == 'inspect' or (defect == 'during_preflight' and len(local_host.commands) > 3):
                value['HostConfig']['CpuShares'] = 10
            if defect == 'malformed': return '{}'
        if args[0] == 'ss' and defect == 'listener': value += 'LISTEN 0 128 0.0.0.0:9999 *:*\n'
        if args[0] == 'tailscale' and defect == 'tailscale': value['AllowFunnel']['ceres.private.example:443'] = True
        return value
    local_host.change = change
    with pytest.raises(ReleaseError): subject.refresh_host_state(Runner(local_host), release, evidence)


def test_readonly_checks_reject_symlink(tmp_path, release):
    target, link = tmp_path / 'target', tmp_path / 'link'
    target.write_bytes(b'x'); target.chmod(0o400); link.symlink_to(target)
    with pytest.raises(ReleaseError, match='unsafe'):
        subject.checked_file(link, release['databases']['CERES_WORLD_DB'])


def test_real_compatibility_and_restored_media(tmp_path, release, evidence, local_host):
    """Real existing SQL adapter + six approved blobs; only disposable DB writes."""
    import importlib.util
    import shutil
    spec = importlib.util.spec_from_file_location('media_fixture', Path(__file__).parent / 'create_ceres_media_fixture.py')
    fixture = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(fixture)
    media = tmp_path / 'media-fixture.sqlite3'
    fixture.create_fixture(media)
    sources = [subject.ROOT / 'data/LOOM_2226.sqlite3', subject.ROOT / 'data/LOOM_2226_CIVSTATE.sqlite3', media]
    for name, mount, source in zip(subject.DATABASE_ENVS, evidence['container']['Mounts'], sources):
        live = Path(mount['Source'])
        live.chmod(0o600)
        shutil.copyfile(source, live)
        live.chmod(0o400)
        wanted = release['databases'][name]
        wanted['sha256'] = hashlib.sha256(live.read_bytes()).hexdigest()
        backup = Path(wanted['backup']['path'])
        backup.chmod(0o600); shutil.copyfile(live, backup); backup.chmod(0o400)
        wanted['backup']['sha256'] = wanted['sha256']
    assert subject.refresh_host_state(Runner(local_host), release, evidence)['State']['Running'] is True


@pytest.mark.parametrize('mutation', [
    lambda c: c['Config'].update(User='0'),
    lambda c: c['Config'].update(Entrypoint=['sh']),
    lambda c: c['Config'].update(Env=c['Config']['Env'] + ['PATH=/attacker']),
])
def test_prior_image_overrides_stop_before_stop(release, evidence, execution, mutation):
    fake, record = execution
    original_config = copy.deepcopy(evidence['container']['Config'])
    mutation(evidence['container'])
    # The real image inspect is immutable; it must not inherit the forged
    # container configuration, unlike an operator-provided matching snapshot.
    process = fake.__call__
    def commands(args, **kwargs):
        result = process(args, **kwargs)
        if args[3:6] == ['inspect', '--type', 'image']:
            value = json.loads(result.stdout)
            value[0]['Config'] = original_config
            return CompletedProcess(args, 0, json.dumps(value), '')
        return result
    with pytest.raises(ReleaseError, match='override'):
        replace(Runner(commands), release, evidence, lambda phase: True, .01, record)
    assert not any(c[3:4] == ['stop'] for c in fake.commands)
    assert not record.exists()


def test_inherited_image_configuration_is_supported(release, evidence, execution):
    fake, record = execution
    # PR #251 image-inherited fields must not be rejected as unknown overrides.
    evidence['container']['Config'].update(
        User='65532:65532', WorkingDir='/app',
        Entrypoint=['python', '-B', 'tools/serve_ceres_atlas.py'],
        Cmd=['--host', '0.0.0.0', '--port', '8768', '--verify-startup'],
        Labels={'org.opencontainers.image.source': 'https://github.com/loom-2226/loom-2226'},
    )
    evidence['container']['Config']['Env'] += ['PATH=/usr/local/bin:/usr/bin:/bin', 'PYTHON_VERSION=3.13.7', 'PYTHONDONTWRITEBYTECODE=1', 'PYTHONUNBUFFERED=1']
    fake.original = copy.deepcopy(evidence['container'])
    assert replace(Runner(fake), release, evidence, lambda phase: True, .01, record) == 'UPDATED_ORIGINAL_RETAINED'


def test_execute_cli_rejects_noninteractive_input(tmp_path, release, evidence, monkeypatch, capsys):
    rp, ep = tmp_path / 'release.json', tmp_path / 'evidence.json'
    rp.write_text(json.dumps(release)); ep.write_text(json.dumps(evidence))
    monkeypatch.delenv('CI', raising=False)
    monkeypatch.delenv('GITHUB_ACTIONS', raising=False)
    monkeypatch.setattr(subject.sys.stdin, 'isatty', lambda: False)
    assert main(['--release', str(rp), '--evidence', str(ep), '--execute']) == 2
    assert 'interactive terminal' in capsys.readouterr().err


def test_duplicate_recovery_name_fails_before_stop(release, evidence, execution):
    fake, record = execution
    fake.original['Name'] = '/ceres-atlas-rollback-' + fake.original['Id'][:12]
    with pytest.raises(ReleaseError, match='already occupied'):
        replace(Runner(fake), release, evidence, lambda phase: True, .01, record)
    assert not any(c[3:4] == ['stop'] for c in fake.commands)


def test_malformed_json_provenance_never_stops(release, evidence, execution):
    fake, record = execution
    def corrupt(args, **kwargs):
        fake.commands.append(args)
        return CompletedProcess(args, 0, 'not-json', '')
    with pytest.raises(ValueError):
        replace(Runner(corrupt), release, evidence, lambda phase: True, .01, record)
    assert len(fake.commands) == 1
    assert not record.exists()
