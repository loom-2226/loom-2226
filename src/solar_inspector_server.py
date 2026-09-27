"""Loopback-only, single-process qualification inspector. No runtime network fetches."""
import argparse
import hashlib
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
import mimetypes
from pathlib import Path
from urllib.parse import parse_qs, urlsplit

from src.loom_solar_inspector import Inspector

ROOT = Path(__file__).resolve().parents[1]
THREE_SHA256 = '8a5f7249903b54d30f79f708699d2fed2d6a1d0741a4cd41377d1f01bb5a2271'


def handler_for(inspector, three_path):
    static = {
        '/': ROOT / 'web/solar-inspector/index.html',
        '/inspector.js': ROOT / 'web/solar-inspector/inspector.js',
        '/presentation.js': ROOT / 'web/solar-inspector/presentation.js',
        '/inspector.css': ROOT / 'web/solar-inspector/inspector.css',
        '/three.min.js': Path(three_path),
        '/design/loom-tokens.css': ROOT / 'design/loom-tokens.css',
        '/design/loom-wordmark-white.svg': ROOT / 'design/loom-wordmark-white.svg',
    }
    font = ROOT / 'design/Montserrat-VF.woff2'
    if font.is_file():
        static['/design/Montserrat-VF.woff2'] = font

    class Handler(BaseHTTPRequestHandler):
        def do_GET(self):
            url = urlsplit(self.path)
            query = parse_qs(url.query)
            def value(key, default=None):
                return query.get(key, [default])[0]
            try:
                if url.path == '/api/state':
                    body_ids = (inspector.preview_ids(value('epoch'), value('center', 'SUN')) if value('preview') == '1'
                                else tuple(value('bodies').split(',')) if value('bodies') else None)
                    result = (inspector.scene_snapshot(value('epoch'), value('center', 'SUN'), body_ids)
                              if value('view') == 'scene' else inspector.snapshot(value('epoch'), value('center', 'SUN')))
                elif url.path == '/api/catalog':
                    result = inspector.catalog(value('epoch'))
                elif url.path == '/api/object':
                    result = inspector.at(value('body'), value('epoch'), value('center', 'SUN'))
                    projection = inspector.scene_row(result)
                    result['catalog_only'] = projection['catalog_only']
                    result['partial_catalog'] = projection['partial_catalog']
                elif url.path == '/api/trajectory':
                    if value('view') == 'auto':
                        result = inspector.automatic_path(value('body'), value('start'), value('center', 'SUN'))
                    else:
                        method = inspector.path if value('view') == 'path' else inspector.trajectory
                        result = method(value('body'), value('start'), value('end'),
                                        value('center', 'SUN'), int(value('samples', '96')))
                elif url.path in static:
                    path = static[url.path]
                    if not path.is_file():
                        self.send_error(404)
                        return
                    self.respond(200, path.read_bytes(), mimetypes.guess_type(path)[0] or 'application/octet-stream')
                    return
                else:
                    self.send_error(404)
                    return
                self.respond(200, json.dumps(result, allow_nan=False).encode(), 'application/json')
            except (BrokenPipeError, ConnectionResetError):
                return
            except Exception as exc:
                self.respond(400, json.dumps({'error': str(exc)}).encode(), 'application/json')

        def respond(self, status, content, content_type):
            self.send_response(status)
            self.send_header('Content-Type', content_type + ('; charset=utf-8' if content_type.startswith('text/') else ''))
            self.send_header('Content-Length', str(len(content)))
            self.send_header('Cache-Control', 'no-store')
            self.send_header('X-Content-Type-Options', 'nosniff')
            self.send_header('Content-Security-Policy', "default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'; img-src 'self' data:; connect-src 'self'")
            self.end_headers()
            self.wfile.write(content)

    return Handler


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--database', default='loom_dev', help='libpq database name or DSN (read-only transaction)')
    parser.add_argument('--asset-root', type=Path, default=Path('/home/ubuntu/loom_solar_assets'))
    parser.add_argument('--three-js', type=Path, default=ROOT / 'web/three/three.min.js')
    parser.add_argument('--port', type=int, default=8765)
    parser.add_argument('--max-orbit-years', type=float, default=100,
                        help='maximum automatic bound-object horizon in Julian years (default: 100)')
    args = parser.parse_args()
    if not args.three_js.is_file():
        parser.error('local Three.js r149 required; see docs/solar_ephemeris_inspector_v0.1.md setup')
    if hashlib.sha256(args.three_js.read_bytes()).hexdigest() != THREE_SHA256:
        parser.error('Three.js asset hash mismatch; install the documented r149 build')
    inspector = Inspector.connect(args.database, args.asset_root, args.max_orbit_years)
    with ThreadingHTTPServer(('127.0.0.1', args.port), handler_for(inspector, args.three_js)) as server:
        print(f'Solar inspector: http://127.0.0.1:{args.port} | {len(inspector.bodies)} catalog objects', flush=True)
        server.serve_forever()


if __name__ == '__main__':
    main()
