"""Install read-only spatial-state HTTP exposure onto the legacy Solar GIS handler."""
from __future__ import annotations

from typing import Any
from urllib.parse import urlparse
import json

from .sqlite_source import SQLiteSpatialStateSource

SPATIAL_ENDPOINT = "/spatial-state.json"


def install_spatial_state_endpoint(
    solar_gis_module: Any,
    *,
    source: SQLiteSpatialStateSource,
    scene_epoch_utc: str,
    campaign_revision: int | None,
    campaign_epoch_utc: str | None,
    epoch_source: str,
) -> None:
    """Add one read-only endpoint without changing legacy scene-generation authority."""
    handler = solar_gis_module.SolarHandler
    marker = "_loom_spatial_endpoint_installed"
    if getattr(handler, marker, False):
        return

    original_do_get = handler.do_GET

    def do_GET(self):
        path = urlparse(self.path).path
        if path == SPATIAL_ENDPOINT:
            try:
                payload = source.snapshot(
                    scene_epoch_utc,
                    campaign_revision=campaign_revision,
                    campaign_epoch_utc=campaign_epoch_utc,
                    epoch_source=epoch_source,
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
        return original_do_get(self)

    handler.do_GET = do_GET
    setattr(handler, marker, True)
