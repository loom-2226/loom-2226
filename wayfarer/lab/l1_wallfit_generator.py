"""L1 wall fit-out proposal generator (Claude, 12 Nov 2026; kT approved for modelling).
ALL bodies. ALL sponsors. 2026-2226.
Run from repo root: python wayfarer/lab/l1_wallfit_generator.py
Writes wayfarer/render/out/proposal_L1_wallfit.glb and prints the shell-margin screen.
Dome profile: X_shell(r)=3.0431182268-3.3431182268*sqrt(1-(r/4.30)^2) (source pressure_vessel, outer).
Frame: glTF = [X, Z, -Y]; plan angle a from +(-Y) toward +Z; h = height above L1 floor top (X=3.0)."""
import json,struct,math,os,numpy as np
OUT=os.path.join("wayfarer","render","out","proposal_L1_wallfit.glb")  # run from repo root
def srgb(hx): c=[int(hx[i:i+2],16)/255 for i in (1,3,5)]; return [((x+0.055)/1.055)**2.4 if x>0.04045 else x/12.92 for x in c]+[1.0]
MAT={'shell':('#ACBBBD',.1,.6),'slate':('#607A84',.2,.55),'teal':('#3FA79A',.3,.4),'ivory':('#D8D8CD',0,.8),
     'red':('#B5473F',.1,.5),'dark':('#1D2A33',.2,.35),'yellow':('#E3B23C',.1,.5),'vault':('#4A5A63',.6,.35),'lining':('#C4CBC6',0,.9)}
def P(r,a,h): t=math.radians(a); return [3.0-h, r*math.sin(t), r*math.cos(t)]
def sector(a0,a1,r0,r1,h0,h1,n=None):
    n=n or max(2,int(abs(a1-a0)/2)+1); A=np.linspace(a0,a1,n); tris=[]
    def q(p0,p1,p2,p3): tris.extend([p0,p1,p2,p0,p2,p3])
    for i in range(n-1):
        a,b=A[i],A[i+1]
        q(P(r0,a,h0),P(r0,b,h0),P(r0,b,h1),P(r0,a,h1)); q(P(r1,b,h0),P(r1,a,h0),P(r1,a,h1),P(r1,b,h1))
        q(P(r0,a,h1),P(r0,b,h1),P(r1,b,h1),P(r1,a,h1)); q(P(r1,a,h0),P(r1,b,h0),P(r0,b,h0),P(r0,a,h0))
    for a,s in ((a0,1),(a1,-1)):
        c=[P(r0,a,h0),P(r1,a,h0),P(r1,a,h1),P(r0,a,h1)]
        q(*(c if s>0 else c[::-1]))
    return tris
def dome_r(h): return 4.3*math.sqrt(max(0,1-((h+0.043)/3.343)**2))
def lining(a0,a1,h0,h1,off=0.06,th=0.015):
    A=np.linspace(a0,a1,int((a1-a0)/3)+2); H=np.linspace(h0,h1,8); tris=[]
    for o in (off,off+th):
        for i in range(len(A)-1):
            for k in range(len(H)-1):
                p=[P(dome_r(H[k])-o,A[i],H[k]),P(dome_r(H[k])-o,A[i+1],H[k]),P(dome_r(H[k+1])-o,A[i+1],H[k+1]),P(dome_r(H[k+1])-o,A[i],H[k+1])]
                if o==off: p=p[::-1]
                tris.extend([p[0],p[1],p[2],p[0],p[2],p[3]])
    return tris
R0,R1=3.77,4.00   # body
DOOR=(3.755,3.77); HAND=(3.742,3.755)
def doors(a0,a1,n,rows,mat,hmat='teal'):
    parts=[]; g=0.5; w=(a1-a0)/n
    for i in range(n):
        for (h0,h1) in rows:
            s,e=a0+i*w+g/2,a0+(i+1)*w-g/2
            parts.append((mat,sector(s,e,*DOOR,h0,h1,3)))
            mid=(s+e)/2; dh=0.06/3.75*180/math.pi
            parts.append((hmat,sector(mid-dh,mid+dh,*HAND,h1-0.06,h1-0.035,2)))
    return parts
def body(a0,a1,mat='shell'):
    return [(mat,sector(a0,a1,R0,R1,0.08,0.95)),('slate',sector(a0+0.3,a1-0.3,3.82,R1,0.0,0.08)),('slate',sector(a0,a1,R0-0.01,R1,0.93,0.95))]
U={}
U['u1_spares_tools']=body(27,66)+doors(27,66,6,[(0.12,0.48),(0.52,0.91)],'shell')
U['u2_watch_galley']=body(113,126,'ivory')+[('dark',sector(114,125,3.755,3.77,0.55,0.90,4)),('teal',sector(118.8,120.2,3.70,3.755,0.80,0.86,2)),
   ('slate',sector(114,125,3.70,3.77,0.52,0.55,4))]+doors(113,126,2,[(0.12,0.48)],'ivory')
U['u3_courier_strongbox']=body(234,242,'vault')+[('vault',sector(234.6,241.4,3.74,3.77,0.14,0.86,3)),('teal',sector(237.2,238.8,3.725,3.74,0.70,0.80,2)),
   ('slate',sector(235,241,3.735,3.74,0.45,0.48,3))]
U['u4_emergency_left']=body(242,250)+doors(242,250,1,[(0.12,0.91)],'red','ivory')
U['u5_backup_panel']=body(295,305,'slate')+[('yellow',sector(295.8,304.2,3.755,3.77,0.40,0.92,3)),('dark',sector(296.6,303.4,3.745,3.765,0.45,0.87,3))]+doors(295,305,1,[(0.12,0.36)],'slate')
U['u6_emergency_right']=body(354,370)+doors(354,370,2,[(0.12,0.91)],'red','ivory')
L=[]
gaps=[(27,66),(113,126),(234,250),(295,305),(354,370)]
# lining on the free wall between units (dome-following, h 0.30-1.30, below windows)
segs=[(66,113),(126,234),(250,295),(305,354),(10,27)]
for a,b in segs: L+=lining(a,b,0.30,1.30)
U['u7_wall_lining']=[('lining',L)]
# ---- GLB write
mats=list(MAT); mi={k:i for i,k in enumerate(mats)}
buf=bytearray(); bvs=[]; accs=[]; meshes=[]; nodes=[]
def add(arr,target=34962):
    global buf
    while len(buf)%4: buf+=b'\0'
    o=len(buf); buf+=arr.tobytes(); bvs.append({'buffer':0,'byteOffset':o,'byteLength':arr.nbytes,'target':target}); return len(bvs)-1
for name,parts in U.items():
    prims=[]; bym={}
    for m,t in parts: bym.setdefault(m,[]).extend(t)
    for m,t in bym.items():
        V=np.array(t,np.float32).reshape(-1,3,3); N=np.cross(V[:,1]-V[:,0],V[:,2]-V[:,0]); N/=np.linalg.norm(N,axis=1,keepdims=True)+1e-12
        V=V.reshape(-1,3); N=np.repeat(N,3,0).astype(np.float32)
        a=len(accs); accs.append({'bufferView':add(V),'componentType':5126,'count':len(V),'type':'VEC3','min':V.min(0).tolist(),'max':V.max(0).tolist()})
        accs.append({'bufferView':add(N),'componentType':5126,'count':len(N),'type':'VEC3'})
        prims.append({'attributes':{'POSITION':a,'NORMAL':a+1},'material':mi[m]})
    meshes.append({'name':name,'primitives':prims})
    nodes.append({'name':'proposal:'+name,'mesh':len(meshes)-1,'extras':{'proposal':'L1 wall fit-out, Claude 2026-11-12','status':'kT approved for modelling; not built; no D9 by Sol yet','mass_owner':'outfit_L1','mass_rebooking_t':0}})
root={'name':'L1_WALLFIT_PROPOSAL','children':list(range(len(nodes)))}
nodes.append(root)
gl={'asset':{'version':'2.0','generator':'Claude L1 wall fit-out proposal'},'scene':0,'scenes':[{'nodes':[len(nodes)-1]}],'nodes':nodes,'meshes':meshes,
    'materials':[{'name':'PROPOSAL/L1_wall/'+k,'doubleSided':True,'pbrMetallicRoughness':{'baseColorFactor':srgb(v[0]),'metallicFactor':v[1],'roughnessFactor':v[2]}} for k,v in MAT.items()],
    'accessors':accs,'bufferViews':bvs,'buffers':[{'byteLength':len(buf)}]}
js=json.dumps(gl).encode(); js+=b' '*(-len(js)%4); buf+=b'\0'*(-len(buf)%4)
out=struct.pack('<III',0x46546C67,2,12+8+len(js)+8+len(buf))+struct.pack('<II',len(js),0x4E4F534A)+js+struct.pack('<II',len(buf),0x004E4942)+bytes(buf)
open(OUT,'wb').write(out)
# checks: containment (2.5 cm inside 30 mm shell) and AABB vs existing fixtures
allv=np.concatenate([np.array(t,float) for p in U.values() for _,t in p])
h=3.0-allv[:,0]; r=np.hypot(allv[:,1],allv[:,2]); margin=np.array([dome_r(x) for x in h])-0.03-r
print('vertices',len(allv),'min shell margin m',margin.min().round(3),'min h',h.min().round(3))
print('glb bytes',len(out))
