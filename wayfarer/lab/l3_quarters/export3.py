"""Export the L3 Quarters organic Japandi proposal GLB (Claude). PROPOSE ONLY. Usage: python export3.py out.glb"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'l2_organic_study'))
import json,struct,sys,os,numpy as np, geom, raster, l3geom
OUT=sys.argv[1] if len(sys.argv)>1 else 'proposal_L3_quarters.glb'
l3geom.build()
def srgb(hx): c=[int(hx[i:i+2],16)/255 for i in (1,3,5)]; return [((x+0.055)/1.055)**2.4 if x>0.04045 else x/12.92 for x in c]+[1.0]
items={}
for (it,m),t in geom.T.items():
    if it in ('CTX','ARCH') or not t: continue
    items.setdefault(it,{})[m]=t
mats=sorted({m for d in items.values() for m in d}); mi={m:i for i,m in enumerate(mats)}
buf=bytearray(); bvs=[]; accs=[]; meshes=[]; nodes=[]
def add(arr,target):
    global buf
    while len(buf)%4: buf+=b'\0'
    o=len(buf); buf+=arr.tobytes(); bvs.append({'buffer':0,'byteOffset':o,'byteLength':arr.nbytes,'target':target}); return len(bvs)-1
for it in sorted(items):
    prims=[]
    for m,t in items[it].items():
        V=np.array(t,float).reshape(-1,3,3); _,Nv=raster.smooth_normals(V)
        P=V.reshape(-1,3).astype(np.float32); N=Nv.reshape(-1,3).astype(np.float32)
        key=np.round(np.c_[P*5000,N*100]).astype(np.int64)
        _,first,inv=np.unique(key,axis=0,return_index=True,return_inverse=True)
        Pu=P[first]; Nu=N[first]/ (np.linalg.norm(N[first],axis=1,keepdims=True)+1e-9); I=inv.astype(np.uint32).ravel()
        a=len(accs)
        accs.append({'bufferView':add(Pu,34962),'componentType':5126,'count':len(Pu),'type':'VEC3','min':Pu.min(0).tolist(),'max':Pu.max(0).tolist()})
        accs.append({'bufferView':add(Nu.astype(np.float32),34962),'componentType':5126,'count':len(Nu),'type':'VEC3'})
        accs.append({'bufferView':add(I,34963),'componentType':5125,'count':len(I),'type':'SCALAR'})
        prims.append({'attributes':{'POSITION':a,'NORMAL':a+1},'indices':a+2,'material':mi[m]})
    meshes.append({'name':it,'primitives':prims})
    nodes.append({'name':'proposal:L3_'+it,'mesh':len(meshes)-1,'extras':{'proposal':'L3 Quarters organic Japandi furniture, Claude 2026-11-12','status':'PROPOSE ONLY; kT approves before build; no D9 yet','mass_rebooking_t':0}})
nodes.append({'name':'L3_QUARTERS_PROPOSAL','children':list(range(len(nodes)))})
gl={'asset':{'version':'2.0','generator':'Claude L3 Quarters organic Japandi'},'scene':0,'scenes':[{'nodes':[len(nodes)-1]}],'nodes':nodes,'meshes':meshes,
    'materials':[{'name':'PROPOSAL/L3_organic/'+m,'doubleSided':True,'pbrMetallicRoughness':{'baseColorFactor':srgb(geom.MAT[m][0]),'metallicFactor':0.6 if m=='titanium' else 0.0,'roughnessFactor':0.35 if m in('titanium','glass') else 0.7},**({'emissiveFactor':srgb(geom.MAT[m][0])[:3]} if geom.MAT[m][1] else {})} for m in mats],
    'accessors':accs,'bufferViews':bvs,'buffers':[{'byteLength':len(buf)}]}
js=json.dumps(gl).encode(); js+=b' '*(-len(js)%4); buf+=b'\0'*(-len(buf)%4)
open(OUT,'wb').write(struct.pack('<III',0x46546C67,2,12+8+len(js)+8+len(buf))+struct.pack('<II',len(js),0x4E4F534A)+js+struct.pack('<II',len(buf),0x004E4942)+bytes(buf))
allv=np.concatenate([np.array(t,float).reshape(-1,3) for d in items.values() for t in d.values()]); h=geom.X0-allv[:,0]; r=np.hypot(allv[:,1],allv[:,2])
print('items',len(items),'bytes',os.path.getsize(OUT),'r',r.min().round(3),r.max().round(3),'h',h.min().round(3),h.max().round(3))
