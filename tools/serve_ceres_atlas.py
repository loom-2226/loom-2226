#!/usr/bin/env python3
"""Serve the private, offline Ceres Atlas on loopback. No SQLite or writes."""
from __future__ import annotations

import argparse
import hashlib
import json
import re
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[1]
MANIFEST_SHA256 = "6ae473bf6b6063b17a08e876d7b0057166135d397ce56e276423d319a44ccd81"
FIELDS = (
    "node_id", "name", "facility_type", "noun_id", "asset_id", "role",
    "is_current", "review_status", "media_key", "export_status", "filename",
    "sha256", "byte_length",
)
STATIC = {
    "/": ("index.html", "text/html; charset=utf-8"),
    "/index.html": ("index.html", "text/html; charset=utf-8"),
    "/style.css": ("style.css", "text/css; charset=utf-8"),
    "/app.mjs": ("app.mjs", "text/javascript; charset=utf-8"),
    "/model.mjs": ("model.mjs", "text/javascript; charset=utf-8"),
}
CSP = (
    "default-src 'none'; script-src 'self'; style-src 'self'; img-src 'self'; "
    "connect-src 'self'; base-uri 'none'; frame-ancestors 'none'; form-action 'none'"
)


def load_manifest(root: Path) -> dict:
    raw = (root / "docs/ceres/manifest.json").read_bytes()
    if hashlib.sha256(raw).hexdigest() != MANIFEST_SHA256:
        raise ValueError("Ceres manifest differs from the verified slice-1 snapshot")
    records = json.loads(raw)
    expected = {f"CER-P{i:02}" for i in range(1, 6)}
    if len(records) != 5 or {r["node_id"] for r in records} != expected:
        raise ValueError("Expected exactly the five verified Ceres facilities")
    for record in records:
        if (record["role"], record["is_current"], record["review_status"], record["export_status"]) != (
            "HERO", 1, "APPROVED_REFERENCE", "VERIFIED"
        ):
            raise ValueError("Unapproved Ceres image record")
        filename = f'{record["node_id"]}_{record["asset_id"]}.png'
        if record["filename"] != filename or not re.fullmatch(r"CER-P0[1-5]_[a-f0-9-]+\.png", filename):
            raise ValueError("Invalid Ceres asset filename")
    return {
        "schema_version": 1,
        "source": "docs/ceres/manifest.json",
        "source_sha256": MANIFEST_SHA256,
        "facilities": [{key: r[key] for key in FIELDS} for r in records],
    }


def read_image(root: Path, record: dict) -> bytes:
    directory = (root / "docs/ceres").resolve()
    path = directory / record["filename"]
    if path.is_symlink() or path.resolve().parent != directory:
        raise ValueError("Image must be a local gallery file")
    content = path.read_bytes()
    if len(content) != record["byte_length"] or hashlib.sha256(content).hexdigest() != record["sha256"]:
        raise ValueError("Image failed manifest verification")
    return content


def create_server(port: int = 8768, root: Path = ROOT) -> ThreadingHTTPServer:
    root = root.resolve()
    manifest = load_manifest(root)
    payload = json.dumps(manifest, ensure_ascii=False).encode("utf-8")
    images = {"/images/" + r["filename"]: r for r in manifest["facilities"]}

    class Handler(BaseHTTPRequestHandler):
        def respond(self, status: int, content_type: str, content: bytes) -> None:
            self.send_response(status)
            self.send_header("Content-Type", content_type)
            self.send_header("Content-Length", str(len(content)))
            self.send_header("Cache-Control", "no-store")
            self.send_header("Content-Security-Policy", CSP)
            self.send_header("X-Content-Type-Options", "nosniff")
            self.send_header("Referrer-Policy", "no-referrer")
            self.end_headers()
            if self.command != "HEAD":
                self.wfile.write(content)

        def do_GET(self) -> None:
            # Reject foreign Host headers (including DNS rebinding); no CORS grant.
            allowed_hosts = {f"127.0.0.1:{self.server.server_port}", f"localhost:{self.server.server_port}"}
            if self.headers.get("Host") not in allowed_hosts:
                self.respond(403, "text/plain", b"Loopback access only")
                return
            path = urlsplit(self.path).path
            try:
                if path == "/manifest.json":
                    self.respond(200, "application/json; charset=utf-8", payload)
                elif path in STATIC:
                    filename, mime = STATIC[path]
                    directory = root / "web/ceres-atlas"
                    file = directory / filename
                    if file.is_symlink() or file.resolve().parent != directory.resolve():
                        raise ValueError("Application file must be local")
                    self.respond(200, mime, file.read_bytes())
                elif path in images:
                    self.respond(200, "image/png", read_image(root, images[path]))
                else:
                    self.respond(404, "text/plain", b"Not found")
            except (OSError, ValueError):
                self.respond(404, "text/plain", b"Local resource unavailable or unverified")

        do_HEAD = do_GET

        def log_message(self, *_args) -> None:
            pass

    return ThreadingHTTPServer(("127.0.0.1", port), Handler)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--port", type=int, default=8768)
    args = parser.parse_args()
    try:
        server = create_server(args.port)
    except (OSError, ValueError) as error:
        parser.exit(1, f"Cannot start Ceres Atlas: {error}\n")
    print(f"Private Ceres Atlas: http://127.0.0.1:{server.server_port}/", flush=True)
    print("Offline local use. Ctrl+C to stop.", flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
