"""Install read-only spatial-state and qualification-view HTTP exposure."""
from __future__ import annotations

from pathlib import Path
from typing import Any
from urllib.parse import urlparse
import json

from .sqlite_source import SQLiteSpatialStateSource

SPATIAL_ENDPOINT = "/spatial-state.json"
SPATIAL_3D_ENDPOINT = "/3d"
SPATIAL_3D_JS_ENDPOINT = "/3d.js"


def install_spatial_state_endpoint(
    solar_gis_module: Any,
    *,
    source: SQLiteSpatialStateSource,
    scene_epoch_utc: str,
    campaign_revision: int | None,
    campaign_epoch_utc: str | None,
    epoch_source: str,
    web_root: Path | str | None = None,
) -> None:
    """Add/update read-only spatial API and optional C3 qualification viewer.

    The 3D viewer is presentation-only. It consumes ``/spatial-state.json`` and
    cannot mutate campaign or world state.
    """
    handler = solar_gis_module.SolarHandler
    handler._loom_spatial_source = source
    handler._loom_spatial_scene_epoch_utc = scene_epoch_utc
    handler._loom_spatial_campaign_revision = campaign_revision
    handler._loom_spatial_campaign_epoch_utc = campaign_epoch_utc
    handler._loom_spatial_epoch_source = epoch_source
    handler._loom_spatial_web_root = Path(web_root).expanduser().resolve() if web_root else None

    marker = "_loom_spatial_endpoint_installed"
    if getattr(handler, marker, False):
        return

    original_do_get = handler.do_GET

    def _static(self, filename: str, content_type: str) -> bool:
        root = getattr(type(self), "_loom_spatial_web_root", None)
        if root is None:
            return False
        target = root / filename
        if not target.is_file():
            return False
        self._send(200, content_type, target.read_bytes())
        return True

    def do_GET(self):
        path = urlparse(self.path).path
        if path == SPATIAL_ENDPOINT:
            try:
                payload = type(self)._loom_spatial_source.snapshot(
                    type(self)._loom_spatial_scene_epoch_utc,
                    campaign_revision=type(self)._loom_spatial_campaign_revision,
                    campaign_epoch_utc=type(self)._loom_spatial_campaign_epoch_utc,
                    epoch_source=type(self)._loom_spatial_epoch_source,
                )
                body = (json.dumps(payload, separators=(",", ":")) + "\n").encode("utf-8")
                self._send(200, "application/json; charset=utf-8", body)
            except Exception as exc:
                body = (json.dumps({
                    "contract": "LOOM_SPATIAL_STATE_SNAPSHOT_V1",
                    "error": f"{type(exc).__name__}: {exc}",
                }, separators=(",", ":")) + "\n").encode("utf-8")
                self._send(500, "application/json; charset=utf-8", body)
            return
        if path in {SPATIAL_3D_ENDPOINT, SPATIAL_3D_ENDPOINT + "/"}:
            if _static(self, "solar3d.html", "text/html; charset=utf-8"):
                return
        if path == SPATIAL_3D_JS_ENDPOINT:
            if _static(self, "solar3d.js", "application/javascript; charset=utf-8"):
                return
        return original_do_get(self)

    handler.do_GET = do_GET
    setattr(handler, marker, True)
