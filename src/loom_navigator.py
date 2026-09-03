#!/usr/bin/env python3
"""LOOM 2226 unified Navigator entrypoint.

Platform-neutral wrapper around the frozen RC6.1 Navigator core. Runtime root is
selected by LOOM_HOME; CIVSTATE/data may be selected independently with
LOOM_DATA_DIR / LOOM_CIVSTATE_DB. The frozen core is not modified here.
"""
from __future__ import annotations

from pathlib import Path as _Path
import importlib.util
import os
import sys

CORE = _Path(__file__).with_name("loom_navigator_core.py")


def runtime_root() -> _Path:
    explicit = os.environ.get("LOOM_HOME", "").strip()
    if explicit:
        return _Path(explicit).expanduser().resolve()
    legacy = _Path("/storage/emulated/0/Download")
    if legacy.exists():
        return legacy
    return _Path.cwd()


class _RootAwarePath:
    """Path constructor shim used only to redirect the core's legacy Android root."""

    def __new__(cls, *parts):
        p = _Path(*parts)
        if str(p) == "/storage/emulated/0/Download":
            return runtime_root()
        return p

    @staticmethod
    def cwd() -> _Path:
        return _Path.cwd()


def load_core():
    if not CORE.is_file():
        raise RuntimeError(f"Navigator core not found: {CORE}")
    spec = importlib.util.spec_from_file_location("loom_navigator_core", CORE)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Unable to load Navigator core: {CORE}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    module.Path = _RootAwarePath
    return module


def load_navigation_service():
    """Return the canonical Phase-2 service facade over the frozen Navigator core."""
    from loom.navigation.service import LegacyNavigationService

    return LegacyNavigationService(load_core())


def main() -> int:
    core = load_core()
    if "--runtime-root" in sys.argv:
        print(runtime_root())
        return 0
    if "--mvp-self-test" in sys.argv:
        core._mvp_self_test()
        return 0
    if "--k1-self-test" in sys.argv:
        core._k1_self_test()
        return 0
    if "--civstate-self-test" in sys.argv:
        i = sys.argv.index("--civstate-self-test")
        arg = sys.argv[i + 1] if i + 1 < len(sys.argv) and not sys.argv[i + 1].startswith("--") else None
        core._civstate_self_test(arg)
        return 0
    return int(core.main() or 0)


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except KeyboardInterrupt:
        pass
