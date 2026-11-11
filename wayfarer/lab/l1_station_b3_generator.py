"""Wayfarer L1 station design B3 (split halo) -- PROPOSAL generator.
Approved as a concept by kT (and Nicole) 12 Nov 2026; geometry by Claude.
Status: PROPOSED. Not canon until Sol imports it, runs D9 + containment, and reconciles mass.
Run from the repo root:  python3 L1_station_B3_generator.py
Reads  wayfarer/render/out/interior_L1.glb  (uses the six i4_seat_* node transforms unchanged)
Writes wayfarer/render/out/proposal_L1_stations_B3.glb
Station frame: u head->feet (0..1.58 m), v across (+-0.35 m), h up from couch base; mapped to couch local x=-h, y=-v, z=-u.
"""
SRC='wayfarer/render/out/interior_L1.glb'
OUT='wayfarer/render/out/proposal_L1_stations_B3.glb'
import numpy as np, json, struct, sys
# ---------- mesh helpers (station frame: u along body head->feet, v across, h up from couch base) ----------
class Mesh:
    def __init__(s): s.P=[]; s.T=[]
    def add(s,P,T):
        o=sum(len(p) for p in s.P); s.P.append(np.asarray(P,float)); s.T.append(np.asarray(T)+o)
    def arrays(s):
        if not s.P: return np.zeros((0,3)),np.zeros((0,3),int)
        return np.vstack(s.P),np.vstack(s.T)
BOXT=[[0,2,1],[0,3,2],[4,5,6],[4,6,7],[0,1,5],[0,5,4],[1,2,6],[1,6,5],[2,3,7],[2,7,6],[3,0,4],[3,4,7]]
def obox(m,c,a,b,n,ha,hb,hn):
    c=np.array(c,float);a=np.array(a,float);b=np.array(b,float);n=np.array(n,float)
    a/=np.linalg.norm(a);b/=np.linalg.norm(b);n/=np.linalg.norm(n)
    P=[c+sa*ha*a+sb*hb*b+sn*hn*n for sn in(-1,1) for (sa,sb) in((-1,-1),(1,-1),(1,1),(-1,1))]
    m.add(P,BOXT)
def box(m,u0,u1,v0,v1,h0,h1):
    obox(m,[(u0+u1)/2,(v0+v1)/2,(h0+h1)/2],[1,0,0],[0,1,0],[0,0,1],(u1-u0)/2,(v1-v0)/2,(h1-h0)/2)
def seg(m,p,q,w,t,up=(0,0,1)):
    p=np.array(p,float);q=np.array(q,float);a=q-p;L=np.linalg.norm(a);a/=L
    up=np.array(up,float);b=np.cross(up,a);
    if np.linalg.norm(b)<1e-6:b=np.cross([1,0,0],a)
    b/=np.linalg.norm(b);n=np.cross(a,b)
    obox(m,(p+q)/2,a,b,n,L/2,w/2,t/2)
def prism(m,c,r,h0,h1,k=8):
    ang=np.linspace(0,2*np.pi,k,endpoint=False);P=[];T=[]
    for z in(h0,h1):
        for t in ang:P.append([c[0]+r*np.cos(t),c[1]+r*np.sin(t),z])
    P.append([c[0],c[1],h0]);P.append([c[0],c[1],h1])
    for i in range(k):
        j=(i+1)%k;T+= [[i,j,k+j],[i,k+j,k+i],[2*k,j,i],[2*k+1,k+i,k+j]]
    m.add(P,T)
def extrude(m,us,top,bot,v0,v1):
    # quad strips: profile in (u,h), extruded across v
    P=[];T=[];n=len(us)
    for v in(v0,v1):
        for i in range(n):P.append([us[i],v,top[i]]);P.append([us[i],v,bot[i]])
    def idx(side,i,tb):return side*2*n+2*i+tb
    for i in range(n-1):
        for side in(0,1):
            a,b,c,d=idx(side,i,0),idx(side,i+1,0),idx(side,i+1,1),idx(side,i,1)
            T+=[[a,b,c],[a,c,d]] if side else [[a,c,b],[a,d,c]]
        for tb in(0,1):
            a,b,c,d=idx(0,i,tb),idx(0,i+1,tb),idx(1,i+1,tb),idx(1,i,tb)
            T+=[[a,c,b],[a,d,c]] if tb==0 else [[a,b,c],[a,c,d]]
    for i,tb in((0,0),(n-1,0)):
        a,b,c,d=idx(0,i,0),idx(1,i,0),idx(1,i,1),idx(0,i,1);T+=[[a,b,c],[a,c,d]]
    m.add(P,T)
# ---------- the station ----------
M={k:Mesh() for k in['upholstery','shell','surround','screen','strap','metal','accent']}
us =[0.00,0.10,0.28,0.55,0.82,0.92,1.05,1.16,1.30,1.45,1.58]
top=[0.24,0.22,0.17,0.16,0.14,0.13,0.25,0.31,0.27,0.22,0.22]
extrude(M['upholstery'],us,top,[0.08]*len(us),-0.26,0.26)
# side bolsters (shell) along back and thighs
ub=us[1:8];tb=top[1:8]
for s in(-1,1):
    extrude(M['shell'],ub,[t+0.035 for t in tb],[0.07]*len(ub),0.26 if s>0 else -0.29,0.29 if s>0 else -0.26)
extrude(M['shell'],us,[0.08]*len(us),[0.06]*len(us),-0.27,0.27)
# headrest with side wings
box(M['upholstery'],0.00,0.09,-0.13,0.13,0.22,0.36)
for s in(-1,1): box(M['shell'],0.00,0.16,s*0.13-(0.04 if s>0 else 0),s*0.13+(0 if s>0 else 0)+ (0.04 if s>0 else 0) if False else s*0.17,0.20,0.34) if False else box(M['shell'],0.00,0.16,min(s*0.13,s*0.17),max(s*0.13,s*0.17),0.20,0.33)
# base frame, attenuators
box(M['metal'],0.15,1.40,-0.24,0.24,0.04,0.08)
for uu in(0.25,1.25):
    for vv in(-0.18,0.18): seg(M["metal"],[uu,vv,0.03],[uu+0.06,vv,0.07],0.05,0.05)
box(M['metal'],0.18,0.32,-0.24,0.24,0.0,0.02);box(M['metal'],1.18,1.32,-0.24,0.24,0.0,0.02)
# armrests both sides
for s in(-1,1):
    box(M['shell'],0.42,0.82,min(s*0.28,s*0.35),max(s*0.28,s*0.35),0.12,0.25)
    box(M['upholstery'],0.44,0.80,min(s*0.285,s*0.345),max(s*0.285,s*0.345),0.25,0.27)
# harness: shoulders -> buckle, lap, crotch
bk=[0.62,0.0,0.18]
for s in(-1,1):
    seg(M['strap'],[0.26,s*0.12,0.20],bk,0.045,0.008)
    seg(M['strap'],[0.86,s*0.25,0.16],bk,0.045,0.008)
seg(M['strap'],[0.98,0,0.17],bk,0.04,0.008)
prism(M['metal'],[0.62,0.0],0.04,0.17,0.20,10)
# foot restraint
box(M['shell'],1.50,1.57,-0.17,0.17,0.20,0.34);box(M['strap'],1.47,1.50,-0.15,0.15,0.26,0.30)
# halo: two posts behind head, arch beam, centre panel (curved, lifts back), two wings
HV=0.31;HT=0.98
for s in(-1,1):
    seg(M['metal'],[0.02,s*HV,0.20],[0.02,s*HV,HT],0.035,0.035)
seg(M['metal'],[0.02,-HV,HT],[0.02,HV,HT],0.035,0.035,up=(1,0,0))
# centre panel: curved across v (wraps the face), u 0.06..0.36
vs=np.linspace(-0.22,0.22,9)
hc=lambda v:0.93-0.10*(v/0.22)**2
for i in range(len(vs)-1):
    a=np.array([0.21,vs[i],hc(vs[i])]);b=np.array([0.21,vs[i+1],hc(vs[i+1])])
    up=np.cross(b-a,[1,0,0]);up=up/np.linalg.norm(up)
    if up[2]<0: up=-up
    seg(M['shell'],a+up*0.012,b+up*0.012,0.30,0.022,up=up) if False else None
    d=b-a;n=up
    obox(M['surround'],(a+b)/2+n*0.010,[1,0,0],d,n,0.15,np.linalg.norm(d)/2+0.002,0.010)
    obox(M['screen'],(a+b)/2-n*0.004,[1,0,0],d,n,0.14,np.linalg.norm(d)/2,0.004)
# hinge arms from arch to centre panel
for s in(-1,1): seg(M['metal'],[0.02,s*0.18,HT],[0.10,s*0.18,hc(0.18)+0.03],0.02,0.02)
# wings: hinged on posts, angled down to wrap the face
for s in(-1,1):
    a=np.array([0.21,s*0.235,0.85]);b=np.array([0.21,s*0.305,0.75])
    d=b-a;n=np.cross([1,0,0],d)*s;n=n/np.linalg.norm(n)
    if n[2]<0:n=-n
    obox(M['surround'],(a+b)/2+n*0.008,[1,0,0],d,n,0.11,np.linalg.norm(d)/2+0.002,0.008)
    obox(M['screen'],(a+b)/2-n*0.003,[1,0,0],d,n,0.10,np.linalg.norm(d)/2,0.003)
    seg(M['metal'],[0.02,s*HV,0.84],[0.10,s*0.29,0.81],0.018,0.018)
# ---------- role add-ons (on armrest tops, h 0.27) ----------
def keypad(m,s): box(m['shell'],0.56,0.74,min(s*0.29,s*0.34),max(s*0.29,s*0.34),0.27,0.29); box(m['screen'],0.575,0.725,min(s*0.295,s*0.335),max(s*0.295,s*0.335),0.29,0.295)
def stick(m,s,big=True):
    c=[0.70,s*0.315];prism(m['metal'],c,0.022,0.27,0.30,8);seg(m['accent'],[0.70,s*0.315,0.29],[0.69,s*0.315,0.40 if big else 0.36],0.03,0.03)
def throttle(m,s):
    seg(m['metal'],[0.66,s*0.315,0.27],[0.62,s*0.315,0.34],0.02,0.02);seg(m['accent'],[0.62,s*0.29,0.345],[0.62,s*0.34,0.345],0.025,0.025,up=(1,0,0))
def trackball(m,s): box(m['shell'],0.58,0.74,min(s*0.29,s*0.34),max(s*0.29,s*0.34),0.27,0.29);prism(m['accent'],[0.66,s*0.315],0.02,0.29,0.31,10)
def guarded(m,s):
    box(m['shell'],0.56,0.76,min(s*0.29,s*0.34),max(s*0.29,s*0.34),0.27,0.30)
    for uu in(0.59,0.645,0.70): box(m['accent'],uu,uu+0.035,min(s*0.297,s*0.333),max(s*0.297,s*0.333),0.30,0.325)
def comms(m,s): keypad(m,s);seg(m['metal'],[0.47,s*0.315,0.27],[0.52,s*0.315,0.33],0.035,0.03)
ROLES={'PILOT':[('throttle',-1),('stick',1)],'S1':[('keypad',-1),('stick_small',1)],'NAV':[('keypad',-1),('trackball',1)],
       'S2':[('keypad',-1),('guarded',1)],'S3':[('trackball',-1),('trackball',1)],'S4':[('keypad',-1),('comms',1)]}
LABEL={'PILOT':'Pilot','S1':'Captain','NAV':'Navigator','S2':'Engineering','S3':'Sensors / EW','S4':'Mission Ops'}
def addon(role):
    m={k:Mesh() for k in M}
    for f,s in ROLES[role]:
        {'throttle':lambda:throttle(m,s),'stick':lambda:stick(m,s),'stick_small':lambda:stick(m,s,False),'keypad':lambda:keypad(m,s),
         'trackball':lambda:trackball(m,s),'guarded':lambda:guarded(m,s),'comms':lambda:comms(m,s)}[f]()
    return m
# station frame (u,v,h) -> couch local (x=-h, y=-v, z=-u)
def tolocal(P): return np.c_[-P[:,2],-P[:,1],-P[:,0]]

import json,struct
src=json.loads(open(SRC,'rb').read()[20:20+struct.unpack('<I',open(SRC,'rb').read()[12:16])[0]])
seat={n['name'].split('i4_seat_')[1]:n for n in src['nodes'] if 'i4_seat_' in n.get('name','')}
# Finish: PR #516 (Sol) proposed L1 palette, sRGB hex -> linear. Screens dark with teal emissive.
MAT={'upholstery':([0.6867, 0.6867, 0.6105],0.0,0.8,None),'shell':([0.4125, 0.4969, 0.5089],0.2,0.55,None),'surround':([0.4793, 0.5841, 0.5583],0.2,0.5,None),'screen':([0.01,0.02,0.025],0.1,0.25,[0.03,0.22,0.26]),
     'strap':([0.0802, 0.1301, 0.15],0.0,0.9,None),'metal':([0.117, 0.1946, 0.2307],0.6,0.4,None),'accent':([0.1651, 0.3185, 0.3278],0.2,0.5,None)}
names=list(MAT)
bin_=bytearray();views=[];accs=[]
def add(arr,target,typ,ct,mm=False):
    o=len(bin_);bin_.extend(arr.tobytes())
    while len(bin_)%4:bin_.append(0)
    views.append({"buffer":0,"byteOffset":o,"byteLength":arr.nbytes,"target":target})
    a={"bufferView":len(views)-1,"componentType":ct,"count":int(arr.shape[0]) if arr.ndim>1 else int(arr.size),"type":typ}
    if mm:a["min"]=arr.min(0).tolist();a["max"]=arr.max(0).tolist()
    accs.append(a);return len(accs)-1
def mesh_of(mm,name):
    prims=[];ntri=0
    for k in names:
        P,T=mm[k].arrays()
        if not len(T):continue
        ntri+=len(T)
        prims.append({"attributes":{"POSITION":add(tolocal(P).astype(np.float32),34962,'VEC3',5126,True)},"indices":add(T.astype(np.uint32).ravel(),34963,'SCALAR',5125),"material":names.index(k)})
    return {"name":name,"primitives":prims},ntri
meshes=[];m0,t0=mesh_of(M,'station_B3');meshes.append(m0)
nodes=[]
ex=lambda r,what:{"id":f"station_{r}" if what=='s' else f"controls_{r}","system":"HABITAT","deck":"L1","state":"PROPOSED (kT/Nicole B3 halo concept, 12 Nov 2026)",
  "tag":"NON-CANON proposal: not BRep, not D9-checked, not mass-booked. Replaces the i4_seat proxy only for viewing.","source":"Claude L1 station design B3","role":LABEL[r]}
for r in ROLES:
    mm,tt=mesh_of(addon(r),'controls_'+r);meshes.append(mm)
    s=seat[r];T={k:s[k] for k in('translation','rotation') if k in s}
    nodes.append({"name":"proposal:station_"+r,"mesh":0,**T,"extras":ex(r,'s')})
    nodes.append({"name":"proposal:controls_"+r,"mesh":len(meshes)-1,**T,"extras":ex(r,'c')})
gl={"asset":{"version":"2.0","generator":"Claude L1 station B3 proposal"},"scene":0,"scenes":[{"nodes":list(range(len(nodes)))}],"nodes":nodes,"meshes":meshes,
 "materials":[{"name":"PROPOSED/"+k,"pbrMetallicRoughness":{"baseColorFactor":v[0]+[1],"metallicFactor":v[1],"roughnessFactor":v[2]},**({"emissiveFactor":v[3]} if v[3] else {})} for k,v in MAT.items()],
 "buffers":[{"byteLength":len(bin_)}],"bufferViews":views,"accessors":accs}
js=json.dumps(gl).encode();js+=b' '*((4-len(js)%4)%4)
out=struct.pack('<III',0x46546C67,2,28+len(js)+len(bin_))+struct.pack('<II',len(js),0x4E4F534A)+js+struct.pack('<II',len(bin_),0x004E4942)+bytes(bin_)
open(OUT,'wb').write(out);print(len(out),'bytes, base tris',t0)
