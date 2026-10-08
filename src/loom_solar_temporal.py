"""Derived temporal publication. Governed resolver remains physical authority."""
from __future__ import annotations
from dataclasses import dataclass
import hashlib,json,math

SCHEMA='loom.solar-temporal/1.0'


def hermite_position(a,b,et):
    t0,t1=a['epoch_et'],b['epoch_et']
    if not t0 <= et <= t1 or t1 <= t0: raise ValueError('epoch outside interpolation bracket')
    h=t1-t0; u=(et-t0)/h; u2=u*u; u3=u2*u
    h00=2*u3-3*u2+1; h10=u3-2*u2+u; h01=-2*u3+3*u2; h11=u3-u2
    return [h00*p0+h10*h*v0+h01*p1+h11*h*v1 for p0,v0,p1,v1 in zip(a['position_km'],a['velocity_km_s'],b['position_km'],b['velocity_km_s'])]


def _sample(inspector,body,center,et):
    row=inspector.at(body,et,center)
    if 'relative' not in row: return {'epoch_et':et,'resolution':'UNRESOLVED','reason':row.get('presentation_reason') or row.get('reason')}
    rel=row['relative']; prov=row['state']['provenance']; cp=inspector.record(center,et)['state']['provenance']
    return {'epoch_et':et,'resolution':'RESOLVED','authority_class':row['authority_class'],
            'position_km':rel['position_km'],'velocity_km_s':rel['velocity_km_s'],
            'source_ref':prov['ephemeris_source_id'],'center_source_ref':cp['ephemeris_source_id']}


def adaptive_samples(inspector,body,center,start_et,end_et,error_km,max_depth=18):
    cache={}
    def exact(t):
        if t not in cache: cache[t]=_sample(inspector,body,center,t)
        return cache[t]
    exact(start_et); exact(end_et)
    def split(a,b,depth):
        A,B=exact(a),exact(b); m=(a+b)/2; M=exact(m)
        if any(x['resolution']!='RESOLVED' for x in (A,M,B)):
            if depth>=max_depth:return
            split(a,m,depth+1); split(m,b,depth+1); return
        same=(A['authority_class'],A['source_ref'],A['center_source_ref'])==(B['authority_class'],B['source_ref'],B['center_source_ref'])==(M['authority_class'],M['source_ref'],M['center_source_ref'])
        err=math.dist(hermite_position(A,B,m),M['position_km']) if same else math.inf
        if err>error_km and depth<max_depth:
            split(a,m,depth+1); split(m,b,depth+1)
    split(start_et,end_et,0)
    rows=[cache[t] for t in sorted(cache)]
    max_probe=0.0
    for A,B in zip(rows,rows[1:]):
        if A['resolution']=='RESOLVED' and B['resolution']=='RESOLVED' and (A['source_ref'],A['center_source_ref'],A['authority_class'])==(B['source_ref'],B['center_source_ref'],B['authority_class']):
            m=(A['epoch_et']+B['epoch_et'])/2; M=exact(m)
            if M['resolution']=='RESOLVED': max_probe=max(max_probe,math.dist(hermite_position(A,B,m),M['position_km']))
    return rows,max_probe


def compile_chunk(inspector,body_ids,start_et,end_et,center_for,error_km_for):
    objects=[]
    for body in sorted(body_ids):
        center=center_for(body); samples,err=adaptive_samples(inspector,body,center,start_et,end_et,error_km_for(body))
        objects.append({'body_id':body,'center_id':center,'reference_frame':'ECLIPJ2000','units':'km,km/s','interpolation':'CUBIC_HERMITE_POSVEL',
                        'declared_error_km':error_km_for(body),'observed_midpoint_error_km':err,'samples':samples})
    core={'schema':SCHEMA,'start_et':start_et,'end_et':end_et,'objects':objects}
    core['content_sha256']=hashlib.sha256(json.dumps(core,sort_keys=True,separators=(',',':')).encode()).hexdigest()
    return core
