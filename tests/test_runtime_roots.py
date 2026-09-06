from pathlib import Path

from loom.runtime import export_runtime_environment, resolve_runtime_roots


def test_explicit_roots_win(tmp_path):
    roots = resolve_runtime_roots(
        app_root=tmp_path / "app",
        data_root=tmp_path / "world",
        campaign_root=tmp_path / "campaign",
        env={"LOOM_APP_ROOT": "/wrong", "LOOM_HOME": "/also-wrong"},
        cwd=tmp_path,
    )
    assert roots.app_root == (tmp_path / "app").resolve()
    assert roots.data_root == (tmp_path / "world").resolve()
    assert roots.campaign_root == (tmp_path / "campaign").resolve()
    assert roots.app_source == "explicit"


def test_dedicated_environment_precedes_loom_home(tmp_path):
    roots = resolve_runtime_roots(
        env={
            "LOOM_APP_ROOT": str(tmp_path / "app"),
            "LOOM_DATA_ROOT": str(tmp_path / "data"),
            "LOOM_CAMPAIGN_ROOT": str(tmp_path / "campaign"),
            "LOOM_HOME": str(tmp_path / "legacy"),
        },
        cwd=tmp_path,
    )
    assert roots.app_root == (tmp_path / "app").resolve()
    assert roots.data_root == (tmp_path / "data").resolve()
    assert roots.campaign_root == (tmp_path / "campaign").resolve()
    assert roots.app_source == "env:LOOM_APP_ROOT"


def test_loom_home_compatibility_keeps_phase6_campaign_at_app_root(tmp_path):
    legacy = tmp_path / "LOOM_TEST"
    roots = resolve_runtime_roots(env={"LOOM_HOME": str(legacy)}, cwd=tmp_path)
    assert roots.app_root == legacy.resolve()
    assert roots.campaign_root == legacy.resolve()
    assert roots.campaign_source == "compat:app-root"


def test_default_is_non_mutating_and_derived_from_cwd(tmp_path):
    roots = resolve_runtime_roots(env={}, cwd=tmp_path)
    assert roots.app_root == tmp_path.resolve()
    assert roots.data_root == (tmp_path / "data").resolve()
    assert roots.campaign_root == tmp_path.resolve()
    assert not (tmp_path / "data").exists()


def test_export_sets_new_contract_and_legacy_home(tmp_path):
    roots = resolve_runtime_roots(app_root=tmp_path / "app", data_root=tmp_path / "data", campaign_root=tmp_path / "campaign", env={}, cwd=tmp_path)
    env = {}
    export_runtime_environment(roots, env=env)
    assert env["LOOM_APP_ROOT"] == str((tmp_path / "app").resolve())
    assert env["LOOM_DATA_ROOT"] == str((tmp_path / "data").resolve())
    assert env["LOOM_CAMPAIGN_ROOT"] == str((tmp_path / "campaign").resolve())
    assert env["LOOM_HOME"] == env["LOOM_APP_ROOT"]
