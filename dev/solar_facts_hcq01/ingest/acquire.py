from __future__ import annotations

import hashlib
import shutil
from datetime import datetime, timezone
from pathlib import Path
from urllib.request import Request, urlopen

from .models import RawArtifact


def _retrieved_at() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def acquire(source: str, destination: Path, *, retrieved_at: str | None = None) -> RawArtifact:
    """Acquire bytes once and record enough identity to audit them later."""
    destination.parent.mkdir(parents=True, exist_ok=True)
    if source.startswith("file://"):
        with open(source[7:], "rb") as handle, destination.open("wb") as output:
            shutil.copyfileobj(handle, output)
        content_type = "application/json"
        provider = "local"
    elif source.startswith(("http://", "https://")):
        request = Request(source, headers={"User-Agent": "LOOM-HCQ01/1.0"})
        with urlopen(request, timeout=30) as response, destination.open("wb") as output:
            content_type = response.headers.get_content_type()
            provider = response.headers.get("Server") or response.headers.get("Via")
            shutil.copyfileobj(response, output)
    else:
        raise ValueError(f"unsupported source identifier: {source}")
    data = destination.read_bytes()
    return RawArtifact(
        artifact_id=destination.stem,
        original_url=source,
        retrieved_at=retrieved_at or _retrieved_at(),
        sha256=hashlib.sha256(data).hexdigest(),
        byte_count=len(data),
        content_type=content_type,
        provider=provider,
        path=str(destination),
    )
