#!/usr/bin/env python3
"""Build a public, media-only Pages snapshot from the existing LOOM databases.

Derived presentation only. Never exports CIVSTATE or arbitrary SQL rows.
"""
import argparse
import hashlib
import json
import mimetypes
import sqlite3
from pathlib import Path

ALLOWED = {'image/png': '.png', 'image/jpeg': '.jpg', 'image/webp': '.webp'}

def connect(path):
    db = sqlite3.connect(Path(path).resolve().as_uri() + '?mode=ro', uri=True)
    db.row_factory = sqlite3.Row
    return db

def build(world_path, media_path, output):
    from importlib.util import spec_from_file_location, module_from_spec
    source = Path(__file__).resolve().parents[1] / 'src' / 'loom_media_library.py'
    spec = spec_from_file_location('loom_media_library', source)
    mod = module_from_spec(spec)
    spec.loader.exec_module(mod)
    entries = mod.load_catalog(world_path, media_path)
    approved = [x for x in entries if x['review_status'] == 'APPROVED_REFERENCE' and x['is_current'] == 1]
    if len(approved) != 182 or len({x['asset_id'] for x in approved}) != 182:
        raise RuntimeError(f'Expected 182 distinct approved/current assets; got {len(approved)}')
    out = Path(output)
    out.mkdir(parents=True, exist_ok=True)
    media = connect(media_path)
    results = []
    try:
        for entry in approved:
            row = media.execute('SELECT mime_type,original_blob,thumbnail_mime_type,thumbnail_blob FROM media_assets WHERE media_key=?', (entry['media_key'],)).fetchone()
            if row is None or row['original_blob'] is None or row['thumbnail_blob'] is None:
                raise RuntimeError(f'Missing original/thumbnail for {entry["asset_id"]}')
            original_mime, thumb_mime = row['mime_type'], row['thumbnail_mime_type'] or row['mime_type']
            if original_mime not in ALLOWED or thumb_mime not in ALLOWED:
                raise RuntimeError(f'Unapproved MIME for {entry["asset_id"]}: {original_mime}/{thumb_mime}')
            item = {k: entry.get(k) for k in ('asset_id','knowledge_entity_id','asset_role','review_status','media_key','width_px','height_px','is_current','canonical_name','noun_class','spatial_entity_id','name','object_type','parent','celestial_object','celestial_id')}
            item['ancestry'] = [{'name': e['name'], 'entity_id': e['entity_id'], 'entity_class': e['entity_class']} for e in mod.ancestry(entry['spatial_entity_id'], mod.entities(world))] if False else []
            for label, blob, mime in (('original', row['original_blob'], original_mime), ('thumbnail', row['thumbnail_blob'], thumb_mime)):
                data = bytes(blob)
                if not data:
                    raise RuntimeError(f'Empty {label} for {entry["asset_id"]}')
                name = hashlib.sha256(data).hexdigest() + ALLOWED[mime]
                relative = f'images/{name}'
                target = out / relative
                target.parent.mkdir(exist_ok=True)
                if not target.exists():
                    target.write_bytes(data)
                item[label] = relative
                item[label + '_bytes'] = len(data)
            results.append(item)
    finally:
        media.close()
    # Publish only explicitly allowlisted fields; never serialize whole SQL rows.
    (out / 'catalog.json').write_text(json.dumps({'status':'APPROVED_FOR_PUBLICATION','source':'WORLD + existing media release; read-only derived export','approved_current_assets':len(results),'sql_inspection':'NOT_EXPORTED','assets':results}, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(f'PASS: {len(results)} approved/current assets, no CIVSTATE or SQL row export')

def main():
    p = argparse.ArgumentParser()
    p.add_argument('--world', required=True)
    p.add_argument('--media', required=True)
    p.add_argument('--output', required=True)
    a = p.parse_args()
    build(a.world, a.media, a.output)

if __name__ == '__main__':
    main()
