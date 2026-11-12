"""Wayfarer L2 Common deck furniture: Japandi x spaceship (Claude, 12 Nov 2026; kT approved layout).
ALL bodies. ALL sponsors. 2026-2226.
Run from repo root: python wayfarer/lab/l2_japandi_generator.py -> wayfarer/render/out/proposal_L2_japandi.glb
Frame: source angle a (Y=r cos a, Z=r sin a); glTF = [X, Z, -Y]; h = height above L2 floor top (X=5.6); ceiling h=2.3."""
import json,struct,math,os,sys,numpy as np
OUT=sys.argv[1] if len(sys.argv)>1 else os.path.join("wayfarer","render","out","proposal_L2_japandi.glb")
def srgb(hx): c=[int(hx[i:i+2],16)/255 for i in (1,3,5)]; return [((x+0.055)/1.055)**2.4 if x>0.04045 else x/12.92 for x in c]+[1.0]
MAT={'oak':('#C8A27A',0,.65),'walnut':('#6B4F3A',0,.6),'linen':('#E8E1D3',0,.9),'stone':('#A39E93',0,.5),'charcoal':('#2E2E2C',.2,.5),
     'sage':('#8A9A7B',0,.85),'leaf':('#5E7D4E',0,.8),'paper':('#F1ECE0',0,.95),'glow':('#F3E3C3',0,.3),'teal':('#3FA79A',.3,.4),'belt':('#1A1A19',0,.8)}
X0=5.6
def P(r,a,h): t=math.radians(a); return [X0-h, r*math.sin(t), -r*math.cos(t)]
def L(rc,ac,u,v,h): # local radial u, tangential v (m) about (rc,ac)
    t=math.radians(ac); Y=rc*math.cos(t)+u*math.cos(t)-v*math.sin(t); Z=rc*math.sin(t)+u*math.sin(t)+v*math.cos(t); return [X0-h,Z,-Y]
def quads(c):  # c: 8 corners in order bottom(0..3) top(4..7), CCW
    f=[(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)]; T=[]
    for q in f: T+= [c[q[0]],c[q[1]],c[q[2]],c[q[0]],c[q[2]],c[q[3]]]
    return T
def box(rc,ac,d,w,h0,h1,du=0,dv=0):
    cs=[(-d/2,-w/2),(d/2,-w/2),(d/2,w/2),(-d/2,w/2)]
    return quads([L(rc,ac,du+u,dv+v,h0) for u,v in cs]+[L(rc,ac,du+u,dv+v,h1) for u,v in cs])
def sector(a0,a1,r0,r1,h0,h1,n=None):
    n=n or max(2,int(abs(a1-a0)/3)+1); A=np.linspace(a0,a1,n); T=[]
    for i in range(n-1):
        a,b=A[i],A[i+1]
        T+=quads([P(r0,a,h0),P(r1,a,h0),P(r1,b,h0),P(r0,b,h0),P(r0,a,h1),P(r1,a,h1),P(r1,b,h1),P(r0,b,h1)])
    return T
def cyl(rc,ac,rad,h0,h1,n=16):
    T=[]; c=[L(rc,ac,rad*math.cos(2*math.pi*k/n),rad*math.sin(2*math.pi*k/n),0) for k in range(n)]
    for k in range(n):
        p=c[k];q=c[(k+1)%n]
        a=[p[0]-0+X0*0,p[1],p[2]]
        pb=[X0-h0,p[1],p[2]];qb=[X0-h0,q[1],q[2]];pt=[X0-h1,p[1],p[2]];qt=[X0-h1,q[1],q[2]];cb=[X0-h0]+L(rc,ac,0,0,0)[1:];ct=[X0-h1]+L(rc,ac,0,0,0)[1:]
        T+=[pb,qb,qt,pb,qt,pt, cb,qb,pb, ct,pt,qt]
    return T
def shoji(a,r0,r1,h0,h1,th=0.04):
    """Radial screen at angle a: paper panel + oak frame and lattice (purpose: privacy with light)."""
    rc=(r0+r1)/2; d=r1-r0; parts=[('paper',box(rc,a,d,th*0.5,h0+0.04,h1-0.04))]
    fr=[]; fr+=box(rc,a,d,th,h0,h0+0.04)+box(rc,a,d,th,h1-0.04,h1)
    for u in np.linspace(-d/2+0.02,d/2-0.02,int(d/0.5)+2): fr+=box(rc,a,0.035,th,h0,h1,du=u)
    for hh in np.arange(h0+0.45,h1-0.2,0.45): fr+=box(rc,a,d,th,hh,hh+0.025)
    parts.append(('oak',fr)); return parts
def arcwall(a0,a1,r,h0,h1,th=0.04):
    parts=[('paper',sector(a0,a1,r-th/4,r+th/4,h0+0.04,h1-0.04))]; fr=sector(a0,a1,r-th/2,r+th/2,h0,h0+0.04)+sector(a0,a1,r-th/2,r+th/2,h1-0.04,h1)
    for aa in np.linspace(a0,a1,int((a1-a0)*math.pi/180*r/0.5)+2): fr+=sector(aa-0.6,aa+0.6,r-th/2,r+th/2,h0,h1,2)
    for hh in np.arange(h0+0.45,h1-0.2,0.45): fr+=sector(a0,a1,r-th/2,r+th/2,hh,hh+0.025)
    parts.append(('oak',fr)); return parts
U={}
# ---------- GALLEY (room_L2-galley 2.047 t)
def counter(a_part,sgn,name,tall_mat,sink=False):
    ac=a_part+sgn*math.degrees(0.325/2.95)
    P_=[('charcoal',box(2.95,ac,2.0,0.55,0,0.1,du=0.05)),('oak',box(2.95,ac,1.5,0.65,0.1,0.88,du=0.3)),('stone',box(2.95,ac,1.5,0.67,0.88,0.92,du=0.3)),
        (tall_mat,box(2.225,ac,0.55,0.65,0.1,2.2)),                                   # tall column at the corridor end, away from the glass
        ('linen',box(2.95,a_part+sgn*math.degrees(0.175/2.95),1.5,0.35,1.45,2.2,du=0.3))]  # flush upper cupboards on the partition
    if sink: P_+= [('charcoal',box(2.95,ac,0.5,0.4,0.85,0.921,du=0.35)),('teal',box(2.95,ac,0.05,0.05,0.92,1.15,du=0.35,dv=-0.22*sgn))]
    else: P_+= [('belt',box(2.95,ac,0.6,0.5,0.921,0.925,du=0.5)),('charcoal',box(2.95,ac,0.6,0.02,0.2,0.8,du=0.0,dv=0.335*sgn))]
    U[name]=P_
counter(300,1,'G1_cook_run','linen')          # fridge-freezer column, rehydrator/oven, induction hob
counter(30,-1,'G2_water_run','oak',sink=True)  # pantry column, sink, cleaner, compactor
U['G3_prep_island']=[('oak',box(3.05,345,0.6,1.2,0.1,0.88)),('charcoal',box(3.05,345,0.5,1.1,0,0.1)),('stone',box(3.05,345,0.62,1.22,0.88,0.92))]
# ---------- WARDROOM (room_L2-wardroom 1.228 t)
U['W1_table']=[('oak',box(3.0,90,1.0,2.8,0.72,0.76)),('charcoal',box(3.0,90,0.7,0.06,0,0.72,dv=-1.0)),('charcoal',box(3.0,90,0.7,0.06,0,0.72,dv=1.0)),
               ('teal',box(3.0,90,0.02,2.2,0.70,0.72,du=-0.4)),('teal',box(3.0,90,0.02,2.2,0.70,0.72,du=0.4))]   # under-edge restraint rails
U['W2_banquette']=[('oak',sector(62,118,3.6,4.05,0.02,0.40)),('charcoal',sector(62.5,117.5,3.65,4.0,0,0.02)),('linen',sector(62,118,3.6,3.98,0.40,0.47)),('linen',sector(62,118,3.94,4.07,0.47,1.02)),('oak',sector(62,118,4.0,4.08,1.02,1.05))]
st=[]; cu=[]
for k in range(5): st+=cyl(2.25,90+(k-2)*13,0.18,0,0.42); cu+=cyl(2.25,90+(k-2)*13,0.17,0.42,0.47)
U['W3_stools']=[('oak',st),('sage',cu)]
U['W4_serving_pass']=[('oak',box(3.3,38.5,1.4,0.45,0.05,0.95)),('charcoal',box(3.3,38.5,1.3,0.4,0,0.05)),('stone',box(3.3,38.5,1.42,0.47,0.95,0.98))]
U['W5_briefing_screen']=[('charcoal',box(3.25,146,1.3,0.04,2.12,2.26))]   # stowed flat at the ceiling, folds down
U['W6_living_niche']=[('walnut',box(3.7,147.2,0.7,0.24,0.35,1.65)),('oak',box(3.7,146.7,0.6,0.2,0.4,1.6)),('leaf',box(3.7,146.4,0.5,0.1,0.55,1.35)),('stone',box(3.7,146.6,0.55,0.16,0.4,0.5))]
# ---------- OBSERVATION (room_L2-observation 0.614 t)
lo=[];cs=[];bk=[]
for a in (162,180,198):
    lo+=box(3.25,a,1.7,0.7,0.05,0.25); cs+=box(3.25,a,1.66,0.64,0.25,0.36); bk+=box(3.25,a,0.35,0.6,0.36,0.72,du=-0.62)
U['O1_loungers']=[('oak',lo),('linen',cs),('linen',bk),('charcoal',sum((box(3.25,a,1.6,0.6,0,0.05) for a in (162,180,198)),[]))]
U['O2_telescope']=[('charcoal',cyl(3.9,207,0.05,0,1.25)),('charcoal',box(3.9,207,0.35,0.16,1.25,1.42,du=-0.05)),('teal',box(3.9,207,0.05,0.1,1.30,1.37,du=0.14))]
# ---------- EXERCISE (room_L2-exercise 1.638 t)
U['E1_treadmill']=[('charcoal',box(3.1,223,2.0,0.85,0,0.2)),('belt',box(3.1,223,1.8,0.55,0.2,0.22)),('oak',box(3.1,223,1.0,0.04,0.95,0.99,du=-0.2,dv=0.38)),('oak',box(3.1,223,1.0,0.04,0.95,0.99,du=-0.2,dv=-0.38)),
                   ('charcoal',box(3.1,223,0.06,0.06,0.2,0.97,du=0.3,dv=0.38)),('charcoal',box(3.1,223,0.06,0.06,0.2,0.97,du=0.3,dv=-0.38)),('charcoal',box(3.1,223,0.06,0.06,0.2,0.97,du=-0.7,dv=0.38)),('charcoal',box(3.1,223,0.06,0.06,0.2,0.97,du=-0.7,dv=-0.38))]
U['E2_resistance']=[('charcoal',box(3.15,240,1.5,0.9,0,0.08)),('charcoal',box(3.15,240,0.1,0.1,0.08,2.05,du=0.6,dv=0.38)),('charcoal',box(3.15,240,0.1,0.1,0.08,2.05,du=0.6,dv=-0.38)),
                    ('oak',box(3.15,240,0.12,0.9,1.9,2.0,du=0.6)),('linen',box(3.15,240,0.9,0.45,0.35,0.45,du=-0.2)),('teal',box(3.15,240,0.05,0.7,1.2,1.25,du=0.4))]
U['E3_cycle']=[('charcoal',box(3.35,258,1.1,0.5,0,0.08)),('charcoal',box(3.35,258,0.12,0.12,0.08,0.75,du=-0.25)),('linen',box(3.35,258,0.3,0.22,0.75,0.82,du=-0.25)),
               ('charcoal',box(3.35,258,0.12,0.12,0.08,1.0,du=0.35)),('oak',box(3.35,258,0.08,0.5,1.0,1.04,du=0.35)),('charcoal',cyl(3.35,258,0.18,0.2,0.3))]
U['E4_shoji_screen']=shoji(210.6,1.95,4.1,0,2.25)
# ---------- WASHROOM (room_L2-hygiene 0.614 t)
U['H0_walls_door']=shoji(270.6,1.95,4.1,0,2.25)+shoji(299.4,1.95,4.1,0,2.25)+arcwall(271.2,298.8,1.97,0,2.25)
U['H1_toilet']=[('stone',box(3.85,285,0.55,0.45,0,0.42)),('charcoal',box(3.85,285,0.2,0.5,0.42,0.9,du=0.17))]
U['H2_shower']=[('oak',box(3.05,285,0.95,0.95,0,0.05)),('linen',box(3.05,285,0.95,0.05,0.05,2.2,dv=0.45)),('linen',box(3.05,285,0.95,0.05,0.05,2.2,dv=-0.45)),('linen',box(3.05,285,0.05,0.85,0.05,2.2,du=0.45)),('teal',box(3.05,285,0.05,0.05,1.9,2.1,du=0.4))]
U['H3_basin']=[('oak',box(2.25,285,0.45,0.7,0.05,0.8)),('stone',box(2.25,285,0.47,0.72,0.8,0.86)),('charcoal',box(2.25,285,0.4,0.6,0,0.05))]
# ---------- DECK-WIDE (outfit_L2 0.819 t)
U['D1_cove_light']=[('glow',sector(0,360,3.86,4.0,2.2,2.25,120))]
U['D2_overhead_rail']=[('oak',sector(14,166,1.62,1.67,1.98,2.03)+sector(194,346,1.62,1.67,1.98,2.03))]
# ---------- GLB write
mats=list(MAT); mi={k:i for i,k in enumerate(mats)}; buf=bytearray(); bvs=[]; accs=[]; meshes=[]; nodes=[]
def add(arr):
    global buf
    while len(buf)%4: buf+=b'\0'
    o=len(buf); buf+=arr.tobytes(); bvs.append({'buffer':0,'byteOffset':o,'byteLength':arr.nbytes,'target':34962}); return len(bvs)-1
for name,parts in U.items():
    prims=[]; bym={}
    for m,t in parts: bym.setdefault(m,[]).extend(t)
    for m,t in bym.items():
        V=np.array(t,np.float32).reshape(-1,3,3); N=np.cross(V[:,1]-V[:,0],V[:,2]-V[:,0]); N/=np.linalg.norm(N,axis=1,keepdims=True)+1e-12
        V=V.reshape(-1,3); N=np.repeat(N,3,0).astype(np.float32)
        a=len(accs); accs.append({'bufferView':add(V),'componentType':5126,'count':len(V),'type':'VEC3','min':V.min(0).tolist(),'max':V.max(0).tolist()})
        accs.append({'bufferView':add(N),'componentType':5126,'count':len(N),'type':'VEC3'}); prims.append({'attributes':{'POSITION':a,'NORMAL':a+1},'material':mi[m]})
    meshes.append({'name':name,'primitives':prims})
    nodes.append({'name':'proposal:L2_'+name,'mesh':len(meshes)-1,'extras':{'proposal':'L2 Japandi furniture, Claude 2026-11-12','status':'kT approved layout; style for review; not built; no D9 yet','mass_rebooking_t':0}})
nodes.append({'name':'L2_JAPANDI_PROPOSAL','children':list(range(len(nodes)))})
gl={'asset':{'version':'2.0','generator':'Claude L2 Japandi proposal'},'scene':0,'scenes':[{'nodes':[len(nodes)-1]}],'nodes':nodes,'meshes':meshes,
    'materials':[{'name':'PROPOSAL/L2_japandi/'+k,'doubleSided':True,'pbrMetallicRoughness':{'baseColorFactor':srgb(v[0]),'metallicFactor':v[1],'roughnessFactor':v[2]},**({'emissiveFactor':srgb(v[0])[:3]} if k=='glow' else {})} for k,v in MAT.items()],
    'accessors':accs,'bufferViews':bvs,'buffers':[{'byteLength':len(buf)}]}
js=json.dumps(gl).encode(); js+=b' '*(-len(js)%4); buf+=b'\0'*(-len(buf)%4)
open(OUT,'wb').write(struct.pack('<III',0x46546C67,2,12+8+len(js)+8+len(buf))+struct.pack('<II',len(js),0x4E4F534A)+js+struct.pack('<II',len(buf),0x004E4942)+bytes(buf))
allv=np.concatenate([np.array(t,float) for p in U.values() for _,t in p]); h=X0-allv[:,0]; r=np.hypot(allv[:,1],allv[:,2])
print('vertices',len(allv),'r max',r.max().round(3),'r min',r.min().round(3),'h',h.min().round(3),h.max().round(3),'bytes',os.path.getsize(OUT))
