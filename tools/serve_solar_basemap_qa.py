#!/usr/bin/env python3
"""Loopback-only static publication and QA shell server; no authority routes."""
import argparse
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import unquote
import hashlib
import mimetypes
import os
import json
import base64
import gzip

ROOT = Path(__file__).resolve().parents[1]
EXPECTED_THREE = "8a5f7249903b54d30f79f708699d2fed2d6a1d0741a4cd41377d1f01bb5a2271"


def make_handler(product, three, temporal=None):
    class Handler(SimpleHTTPRequestHandler):
        def __init__(self, *args, **kwargs): self.product=product; self.three=three; self.temporal=temporal; super().__init__(*args,directory=str(ROOT/"web/solar-basemap"),**kwargs)
        def translate_path(self, path):
            path=unquote(path.split("?",1)[0])
            if path=="/" or path=="/index.html": return str(ROOT/"web/solar-basemap/index.html")
            if path=="/three.min.js": return str(self.three)
            if path.startswith("/design/"):
                relative=Path(path[len("/design/"):])
                if relative.is_absolute() or ".." in relative.parts: return str(ROOT/"__blocked__")
                return str(ROOT/"design"/relative)
            if path.startswith("/temporal/") and self.temporal:
                relative=Path(path[len("/temporal/"):])
                if relative.is_absolute() or ".." in relative.parts: return str(ROOT/"__blocked__")
                return str(self.temporal/relative)
            if path.startswith("/product/"):
                relative=Path(path[len("/product/"):])
                if relative.as_posix()=="current.json":
                    pointer=json.loads((self.product/"current.json").read_text())
                    return str(self.product/pointer["manifest_uri"])
                if relative.is_absolute() or ".." in relative.parts: return str(ROOT/"__blocked__")
                return str(self.product/relative)
            return str(ROOT/"web/solar-basemap"/path.lstrip("/"))
        def end_headers(self):
            self.send_header("X-Content-Type-Options","nosniff")
            self.send_header("Referrer-Policy","no-referrer")
            super().end_headers()
        def do_GET(self):
            if self.path.split("?",1)[0]=="/product/current.json" and "delivery=monolithic" in self.path:
                import gzip
                pointer=json.loads((self.product/"current.json").read_text()); manifest_path=self.product/pointer["manifest_uri"]
                manifest=json.loads(manifest_path.read_bytes()); root_path=self.product/manifest["root"]["uri"]
                root=json.loads((self.product/root_path).read_bytes()); resources={}
                descriptors=[manifest["root"],manifest["provenance"],manifest["generation"]["spec"]]
                descriptors += [level["resource"] for node in root["nodes"] for level in node["levels"]]
                descriptors += [curve["audit"] for curve in root["curves"]]
                provenance=json.loads((self.product/manifest["provenance"]["uri"]).read_bytes())
                descriptors += provenance.get("sample_resources",[])
                for desc in descriptors:
                    raw=(self.product/desc["uri"]).read_bytes();
                    if hashlib.sha256(raw).hexdigest()!=desc["sha256"]: self.send_error(500,"stored resource hash mismatch"); return
                    resources[desc["uri"]]=base64.b64encode(raw).decode("ascii")
                envelope=json.dumps({"manifest":manifest,"resources":resources},sort_keys=True,separators=(",",":"),ensure_ascii=False).encode()
                payload=gzip.compress(envelope,mtime=0) if "gzip" in self.headers.get("Accept-Encoding","") else envelope
                self.send_response(200);self.send_header("Content-Type","application/json");self.send_header("Vary","Accept-Encoding")
                if payload is not envelope:self.send_header("Content-Encoding","gzip")
                self.send_header("Cache-Control","no-store");self.send_header("Content-Length",str(len(payload)));self.end_headers();self.wfile.write(payload);return
            path=self.translate_path(self.path)
            if self.path.split("?",1)[0].startswith("/product/") and self.headers.get("Accept-Encoding"," ").find("gzip")>=0:
                gz=Path(path+".gz")
                if gz.is_file():
                    raw=Path(path).read_bytes(); digest=hashlib.sha256(raw).hexdigest()
                    self.send_response(200); self.send_header("Content-Type","application/json")
                    self.send_header("Content-Encoding","gzip"); self.send_header("Vary","Accept-Encoding")
                    self.send_header("Content-Length",str(gz.stat().st_size)); self.send_header("ETag",f'"{digest}"')
                    self.send_header("Cache-Control","public, max-age=31536000, immutable" if "/objects/" in path or "/provenance/" in path else "no-cache")
                    self.end_headers(); self.wfile.write(gz.read_bytes()); return
            return super().do_GET()
        def log_message(self, fmt, *args): print("[static] "+fmt%args)
    return Handler


def main():
    p=argparse.ArgumentParser(); p.add_argument("--product-root",type=Path,required=True); p.add_argument("--port",type=int,default=8770)
    p.add_argument("--temporal-root",type=Path); p.add_argument("--three-js",type=Path,default=ROOT/"web/three/three.min.js"); a=p.parse_args()
    three=a.three_js.resolve()
    if not three.is_file() or hashlib.sha256(three.read_bytes()).hexdigest()!=EXPECTED_THREE: p.error("pinned Three.js r149 asset missing or hash mismatch")
    product=a.product_root.resolve()
    if not (product/"current.json").is_file(): p.error("product-root has no current.json")
    temporal=a.temporal_root.resolve() if a.temporal_root else None
    if temporal and not (temporal/"current.json").is_file(): p.error("temporal-root has no current.json")
    server=ThreadingHTTPServer(("127.0.0.1",a.port),make_handler(product,three,temporal))
    print(f"Serving QA shell and static product on http://127.0.0.1:{a.port}; no Solar authority API",flush=True)
    server.serve_forever()


if __name__=="__main__": main()
