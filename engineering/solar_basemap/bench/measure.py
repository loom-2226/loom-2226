"""Read-only decision experiment; no basemap compiler or physical model.
Run with --inspector-root pointing to PR299 checkout and --url to its live server.
Optional legacy HTML is a local archive, measured without trusting its authority.
"""
import argparse, ast, base64, collections, gzip, hashlib, importlib.util, io, json, math
import platform, re, struct, sys, time, urllib.parse, urllib.request, zlib
from contextlib import redirect_stdout
from pathlib import Path


def encoded(x):
    return json.dumps(x, sort_keys=True, separators=(',', ':'), allow_nan=False).encode()


def sizes(b):
    return {'bytes': len(b), 'gzip_bytes': len(gzip.compress(b, mtime=0)), 'sha256': hashlib.sha256(b).hexdigest()}


def dist_segment(p, a, b):
    ab=[y-x for x,y in zip(a,b)]; den=sum(x*x for x in ab)
    t=max(0,min(1,sum((x-y)*v for x,y,v in zip(p,a,ab))/den)) if den else 0
    return math.dist(p,[x+t*v for x,v in zip(a,ab)])


def simplify(points, eps):
    keep={0,len(points)-1}; stack=[(0,len(points)-1)]
    while stack:
        a,b=stack.pop()
        if b-a<2: continue
        e,i=max((dist_segment(points[i],points[a],points[b]),i) for i in range(a+1,b))
        if e>eps:
            keep.add(i); stack.extend(((a,i),(i,b)))
    ids=sorted(keep)
    err=max((dist_segment(points[i],points[a],points[b]) for a,b in zip(ids,ids[1:]) for i in range(a,b+1)),default=0)
    return {'tolerance_km':eps,'vertices':len(ids),'measured_polyline_error_km':err,
            **sizes(encoded([points[i] for i in ids]))}


def main():
    p=argparse.ArgumentParser();p.add_argument('--inspector-root',type=Path,required=True)
    p.add_argument('--url',default='http://127.0.0.1:8765');p.add_argument('--legacy-html',type=Path)
    p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    out={'environment':{'python':platform.python_version(),'platform':platform.platform()},'live':{},'legacy':{}}
    def get(route,**query):
        url=a.url+route+'?'+urllib.parse.urlencode(query); t=time.perf_counter()
        with urllib.request.urlopen(url,timeout=300) as r: b=r.read()
        out['live'][url]={'elapsed_ms':(time.perf_counter()-t)*1000,**sizes(b)}
        return json.loads(b)
    catalog=get('/api/catalog');out['authority']=catalog['authority']
    out['catalog_classes']=dict(collections.Counter(x['body_class'] for x in catalog['objects']))
    scene=get('/api/state',epoch='2226-01-01T00:00:00 TDB',center='SUN',view='scene')
    out['epoch_et']=scene['epoch_et'];out['counts']=scene['counts']
    out['unresolved']=[{'body_id':x['body_id'],'reason':x.get('reason')} for x in scene['objects'] if x['resolution']!='RESOLVED']
    # Size lower bound for root identities/epoch points, not a finished product.
    root=[{k:v for k,v in x.items() if k in ('body_id','canonical_name','body_class','parent_body_id','resolution','reason')} |
          ({'position_km':x['relative']['position_km']} if 'relative' in x else {}) for x in scene['objects']]
    out['root_identity_position_projection']=sizes(encoded(root))
    paths={};out['paths']={}
    for body,center in [('MARS','SUN'),('PHOBOS','MARS'),('DEIMOS','MARS'),('MOON','EARTH'),('CHARON','PLUTO')]:
        path=get('/api/trajectory',body=body,center=center,start=scene['epoch_et'],view='auto')
        dense=get('/api/trajectory',body=body,center=center,start=path['start_et'],end=path['end_et'],samples=512,view='path')
        paths[body]=dense
        points=[v['relative']['position_km'] for v in dense['points'] if 'relative' in v]
        assert len(points)==len(dense['points']) and len(dense['segments'])==1,'experiment only compares continuous segments'
        f64=struct.pack('<'+'d'*len(points)*3,*[x for row in points for x in row]); f32=struct.pack('<'+'f'*len(points)*3,*[x for row in points for x in row])
        rt=list(struct.iter_unpack('<fff',f32))
        out['paths'][body]={'center':center,'horizon':path['horizon'],'auto_vertices':len(path['points']),
            'vertices':len(points),'radius_km':max(math.dist(x,[0,0,0]) for x in points),
            'formats':{'json':sizes(encoded(points)),'f64le':sizes(f64),'f32le':sizes(f32)},
            'f32_max_error_km':max(math.dist(x,y) for x,y in zip(points,rt)),
            'simplifications':[simplify(points,e) for e in ([100000,10000,1000] if body=='MARS' else [100,10,1,.1])],
            'sampling_warning':'Errors are relative to the 512-sample polyline, not a certified continuous orbit bound.'}
    # All fixture generation is in an in-memory legacy database. Never open live SQLite.
    sys.path.insert(0,str(a.inspector_root))
    from src import loom_solar_gis as gis
    t=time.perf_counter()
    with redirect_stdout(io.StringIO()): legacy=gis.build_scene(gis.parse_epoch('2226-01-01T00:00:00Z'),provider=gis.demo_provider)
    data=legacy.to_json_dict();out['legacy']['fixture_build_ms']=(time.perf_counter()-t)*1000
    out['legacy']['fixture_only']=True
    out['legacy']['counts']={k:len(data[k]) for k in ['entities','orbit_tracks','local_body_orbit_tracks','infrastructure_orbit_tracks','context_layers']}
    boot={**data,'atlas':{},'catalog':{},'orbit_tracks':[],'local_body_orbit_tracks':[],'infrastructure_orbit_tracks':[],'context_layers':[]}
    geom={k:data[k] for k in ('orbit_tracks','local_body_orbit_tracks','infrastructure_orbit_tracks','context_layers')}
    out['legacy']['sizes']={k:sizes(encoded(v)) for k,v in [('full',data),('bootstrap',boot),('geometry',geom),('details',{'atlas':data['atlas'],'catalog':data['catalog']})]}
    out['legacy']['client_js']=sizes(gis.CLIENT_JS.encode())
    if a.legacy_html:
        raw=a.legacy_html.read_bytes();s=raw.decode();parts={}
        for name,body in re.findall(r'<script[^>]*id="([^"]+)"[^>]*>(.*?)</script>',s,re.S):
            if not name.endswith('Payload'):continue
            b=base64.b64decode(body)
            if b.startswith(b'{'):
                parts[name]={'base64_bytes':len(body),**sizes(b),'encoding':'JSON'};continue
            n=struct.unpack('<I',b[:4])[0];meta=json.loads(b[4:4+n]);parts[name]={'base64_bytes':len(body),**sizes(b),'metadata_bytes':n,'binary_bytes':len(b)-4-n}
            if name=='ephemerisPayload': parts[name].update(frame_count=meta['frame_count'],body_order=meta['body_order'],local_systems=list(meta['local_meta']),tracks=len(meta['tracks']),codec=meta['geometry_codec'])
        out['legacy']['archived_navigator']={'input':str(a.legacy_html),**sizes(raw),'payloads':parts,'archive_not_current_authority':True}
    a.output.write_text(json.dumps(out,indent=2)+'\n')
    a.output.with_name('sample_corpus.json').write_bytes(encoded({'authority':catalog['authority'],'epoch_et':scene['epoch_et'],'paths':paths})+b'\n')
    print(json.dumps({'output':str(a.output),'counts':out['counts'],'paths':{k:v['vertices'] for k,v in out['paths'].items()},'legacy':out['legacy']['counts']}))

if __name__=='__main__':main()
