"""Canonical LOOM runtime identity and authority-root resolution.

Resolution is deliberately side-effect free: this module never creates, moves,
deletes, or mutates runtime data. Physical migration is a separate operation.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Mapping
import os


@dataclass(frozen=True)
class RuntimeRoots:
    app_root: Path
    data_root: Path
    campaign_root: Path
    app_source: str
    data_source: str
    campaign_source: str

    def to_dict(self) -> dict[str, str]:
        return {
            "contract": "LOOM_RUNTIME_ROOTS_V1",
            "app_root": str(self.app_root),
            "data_root": str(self.data_root),
            "campaign_root": str(self.campaign_root),
            "app_source": self.app_source,
            "data_source": self.data_source,
            "campaign_source": self.campaign_source,
        }


def _clean(path: str | Path) -> Path:
    return Path(path).expanduser().resolve()


def _is_android(environ: Mapping[str, str]) -> bool:
    """Detect Android from the same environment supplied to the resolver."""
    return bool(environ.get("ANDROID_ROOT") or environ.get("TERMUX_VERSION"))


def resolve_runtime_roots(
    *,
    app_root: str | Path | None = None,
    data_root: str | Path | None = None,
    campaign_root: str | Path | None = None,
    env: Mapping[str, str] | None = None,
    cwd: str | Path | None = None,
) -> RuntimeRoots:
    """Resolve LOOM authority roots without touching the filesystem.

    Precedence is explicit argument -> dedicated LOOM_*_ROOT environment value ->
    compatibility/default. LOOM_HOME is compatibility input for APP_ROOT only.

    The Android data default reflects the physically audited Pixel authority at
    /storage/emulated/0/Documents/LOOM/data. Campaign state remains at APP_ROOT
    by default for Phase-6 compatibility until an explicit migration is activated.
    """
    environ = os.environ if env is None else env
    here = _clean(cwd or Path.cwd())

    if app_root is not None:
        app, app_source = _clean(app_root), "explicit"
    elif environ.get("LOOM_APP_ROOT"):
        app, app_source = _clean(environ["LOOM_APP_ROOT"]), "env:LOOM_APP_ROOT"
    elif environ.get("LOOM_HOME"):
        app, app_source = _clean(environ["LOOM_HOME"]), "compat:LOOM_HOME"
    else:
        app, app_source = here, "default:cwd"

    if data_root is not None:
        data, data_source = _clean(data_root), "explicit"
    elif environ.get("LOOM_DATA_ROOT"):
        data, data_source = _clean(environ["LOOM_DATA_ROOT"]), "env:LOOM_DATA_ROOT"
    elif _is_android(environ):
        # Resolution must remain deterministic and side-effect free. Do not make
        # authority depend on whether a directory happens to exist at this moment.
        data = _clean("/storage/emulated/0/Documents/LOOM/data")
        data_source = "default:android-documents"
    else:
        data, data_source = _clean(app / "data"), "default:app/data"

    if campaign_root is not None:
        campaign, campaign_source = _clean(campaign_root), "explicit"
    elif environ.get("LOOM_CAMPAIGN_ROOT"):
        campaign = _clean(environ["LOOM_CAMPAIGN_ROOT"])
        campaign_source = "env:LOOM_CAMPAIGN_ROOT"
    else:
        campaign, campaign_source = app, "compat:app-root"

    return RuntimeRoots(app, data, campaign, app_source, data_source, campaign_source)


def export_runtime_environment(
    roots: RuntimeRoots, *, env: dict[str, str] | None = None
) -> None:
    """Publish resolved roots for legacy/current consumers in this process."""
    target = os.environ if env is None else env
    target["LOOM_APP_ROOT"] = str(roots.app_root)
    target["LOOM_DATA_ROOT"] = str(roots.data_root)
    target["LOOM_CAMPAIGN_ROOT"] = str(roots.campaign_root)
    # Preserve legacy Navigator behavior during convergence.
    target["LOOM_HOME"] = str(roots.app_root)
