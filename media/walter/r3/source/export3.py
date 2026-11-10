import json, struct, zipfile, time
import numpy as np
from scipy.sparse import coo_matrix
from scipy.sparse.csgraph import connected_components
from scipy import ndimage
import model3
t0=time.time()
v=np.load('m3_v.npy').astype(np.float64); f=np.load('m3_f.npy').astype(np.int64)
meta=json.load(open('g3_hi.json')); G=np.load('g3_hi.npy'); h=meta['h']; lo=np.array(meta['lo'])
R={}
e=np.concatenate([f[:,[0,1]],f[:,[1,2]],f[:,[2,0]]])
und=np.sort(e,1); _,cnt=np.unique(und[:,0]*len(v)+und[:,1],return_counts=True)
_,dcnt=np.unique(e[:,0]*len(v)+e[:,1],return_counts=True)
ncomp,_=connected_components(coo_matrix((np.ones(len(e)),(e[:,0],e[:,1])),shape=(len(v),)*2),directed=False)
a,b,c=v[f[:,0]],v[f[:,1]],v[f[:,2]]; cr=np.cross(b-a,c-a); ar=0.5*np.linalg.norm(cr,axis=1); fn=cr/np.maximum(2*ar,1e-12)[:,None]
chi=len(v)-len(cnt)+len(f)
R.update(faces=int(len(f)),vertices=int(len(v)),non_manifold_edges=int((cnt!=2).sum()),orientation_errors=int((dcnt!=1).sum()),
 shells=int(ncomp),genus=int((2*ncomp-chi)//2),degenerate_faces=int((ar<1e-9).sum()),
 volume_mm3=round(float(np.einsum('ij,ij->i',a,np.cross(b,c)).sum()/6),1),surface_area_mm2=round(float(ar.sum()),1))
mn,mx=v.min(0),v.max(0); R['bbox_min_mm']=mn.round(2).tolist(); R['bbox_max_mm']=mx.round(2).tolist(); R['size_LxWxH_mm']=(mx-mn).round(1).tolist()
cz=(a[:,2]+b[:,2]+c[:,2])/3; base=(cz<0.05)&(fn[:,2]<-0.99)
R['base_contact_mm2']=round(float(ar[base].sum()),1)
R['overhang_gt45_mm2']=round(float(ar[(fn[:,2]<-0.7071)&~base].sum()),1)
ins=G<0; isl=[]
for k in range(1,ins.shape[2]):
    cur=ins[:,:,k]
    if not cur.any(): continue
    below=ndimage.binary_dilation(ins[:,:,k-1],np.ones((3,3),bool))
    lab,nl=ndimage.label(cur)
    if not nl: continue
    sup=ndimage.sum(below,lab,index=np.arange(1,nl+1))
    for j in np.nonzero(sup==0)[0]:
        p=np.argwhere(lab==j+1); xy=lo[:2]+p.mean(0)*h
        isl.append([round(float(xy[0]),1),round(float(xy[1]),1),round(float(lo[2]+k*h),1),int(len(p))])
R['support_islands_above_base']=[i for i in isl if i[2]>0.6]
for r_mm in (0.4,):
    r=int(round(r_mm/h)); zz,yy,xx=np.mgrid[-r:r+1,-r:r+1,-r:r+1]; ball=(xx**2+yy**2+zz**2)<=r*r
    thin=ins&~ndimage.binary_opening(ins,structure=ball)
    R['thin_fraction_below_0.8mm']=round(float(thin.sum()/ins.sum()),5)
print('checks',f'{time.time()-t0:.0f}s',flush=True)
# materials per face
mid=model3.walter_material_ids(v); fm=mid[f]
fmat=np.where(fm[:,0]==fm[:,1],fm[:,0],np.where(fm[:,1]==fm[:,2],fm[:,1],fm[:,0]))
COL={'hull':(0.20,0.21,0.23),'struct':(0.30,0.31,0.33),'joint':(0.50,0.51,0.53),'pad':(0.05,0.05,0.055),
     'glass':(0.06,0.08,0.10),'accent':(0.86,0.42,0.10),'repl':(0.62,0.62,0.60)}
NAME={'hull':'Hull graphite','struct':'Leg/neck structure gunmetal','joint':'Actuator housings steel','pad':'Wear pads and soles black',
      'glass':'Sensor glass','accent':'EVA handrails and tail lamp, safety orange','repl':'Replacement shank bare titanium'}
R['material_faces']={k:int((fmat==i).sum()) for i,k in enumerate(model3.MATS)}
base='out3/Walter_R3_1-12'
# STL
dt=np.dtype([('n','<f4',3),('v','<f4',(3,3)),('a','<u2')]); rec=np.zeros(len(f),dt); rec['n']=fn; rec['v']=np.stack([a,b,c],1)
with open(base+'.stl','wb') as fh:
    fh.write(b'WALTER R3 1:12 LOOM 2226 units mm'.ljust(80,b' ')); fh.write(struct.pack('<I',len(f))); fh.write(rec.tobytes())
# OBJ + MTL (mm, z-up, groups per material)
with open(base+'.mtl','w') as fh:
    for k in model3.MATS: fh.write(f'newmtl {k}\nKd {COL[k][0]:.3f} {COL[k][1]:.3f} {COL[k][2]:.3f}\n# {NAME[k]}\n\n')
with open(base+'.obj','w') as fh:
    fh.write('# WALTER R3 1:12 - units mm, Z up\nmtllib Walter_R3_1-12.mtl\no Walter_R3\n')
    np.savetxt(fh,v,fmt='v %.4f %.4f %.4f')
    for i,k in enumerate(model3.MATS):
        sel=f[fmat==i]
        if len(sel)==0: continue
        fh.write(f'g {k}\nusemtl {k}\n'); np.savetxt(fh,sel+1,fmt='f %d %d %d')
# 3MF
hexes=['#%02X%02X%02XFF'%tuple(int(x*255) for x in COL[k]) for k in model3.MATS]
mats='\n'.join(f'<base name="{NAME[k]}" displaycolor="{hexes[i]}"/>' for i,k in enumerate(model3.MATS))
vs='\n'.join(f'<vertex x="{p[0]:.4f}" y="{p[1]:.4f}" z="{p[2]:.4f}"/>' for p in v)
ts='\n'.join(f'<triangle v1="{t[0]}" v2="{t[1]}" v3="{t[2]}" pid="1" p1="{m}"/>' for t,m in zip(f,fmat))
xml=f'''<?xml version="1.0" encoding="UTF-8"?>
<model unit="millimeter" xml:lang="en-US" xmlns="http://schemas.microsoft.com/3dmanufacturing/core/2015/02">
<metadata name="Title">WALTER R3 1:12 - LOOM 2226</metadata>
<resources><basematerials id="1">
{mats}
</basematerials>
<object id="2" type="model" name="Walter_R3" pid="1" pindex="0"><mesh><vertices>
{vs}
</vertices><triangles>
{ts}
</triangles></mesh></object></resources>
<build><item objectid="2"/></build></model>'''
with zipfile.ZipFile(base+'.3mf','w',zipfile.ZIP_DEFLATED) as z:
    z.writestr('[Content_Types].xml','<?xml version="1.0" encoding="UTF-8"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="model" ContentType="application/vnd.ms-package.3dmanufacturing-3dmodel+xml"/></Types>')
    z.writestr('_rels/.rels','<?xml version="1.0" encoding="UTF-8"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Target="/3D/3dmodel.model" Id="rel0" Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel"/></Relationships>')
    z.writestr('3D/3dmodel.model',xml)
# GLB: plain glTF 2.0 - metres, Y-up, float32 POSITION+NORMAL, uint32 indices, one primitive per material, plain PBR colours
vg=(np.stack([v[:,0],v[:,2],-v[:,1]],1)*0.001).astype(np.float32)
vn=np.zeros_like(v)
for i in range(3): np.add.at(vn,f[:,i],cr)
vn/=np.maximum(np.linalg.norm(vn,axis=1,keepdims=True),1e-12); ng=np.stack([vn[:,0],vn[:,2],-vn[:,1]],1).astype(np.float32)
blobs=[vg.tobytes(),ng.tobytes()]; prims=[]; mats_gl=[]; acc=[
 {'bufferView':0,'componentType':5126,'count':len(v),'type':'VEC3','min':vg.min(0).tolist(),'max':vg.max(0).tolist()},
 {'bufferView':1,'componentType':5126,'count':len(v),'type':'VEC3'}]
views=[]
for i,k in enumerate(model3.MATS):
    sel=f[fmat==i].astype(np.uint32)
    if len(sel)==0: continue
    blobs.append(sel.tobytes()); acc.append({'bufferView':len(blobs)-1,'componentType':5125,'count':int(sel.size),'type':'SCALAR'})
    mats_gl.append({'name':k,'pbrMetallicRoughness':{'baseColorFactor':[*COL[k],1.0],'metallicFactor':0.3 if k not in('pad','glass') else 0.0,'roughnessFactor':0.55}})
    prims.append({'attributes':{'POSITION':0,'NORMAL':1},'indices':len(acc)-1,'material':len(mats_gl)-1,'mode':4})
binb=b''; offs=[]
for bb in blobs: offs.append(len(binb)); binb+=bb+b'\x00'*((4-len(bb)%4)%4)
for i,bb in enumerate(blobs): views.append({'buffer':0,'byteOffset':offs[i],'byteLength':len(bb),'target':34962 if i<2 else 34963})
gl={'asset':{'version':'2.0','generator':'Walter R3 SDF build'},'scene':0,'scenes':[{'nodes':[0]}],'nodes':[{'mesh':0,'name':'Walter_R3'}],
    'meshes':[{'name':'Walter_R3','primitives':prims}],'materials':mats_gl,'buffers':[{'byteLength':len(binb)}],'bufferViews':views,'accessors':acc}
js=json.dumps(gl).encode(); js+=b' '*((4-len(js)%4)%4)
with open(base+'.glb','wb') as fh:
    fh.write(struct.pack('<III',0x46546C67,2,12+8+len(js)+8+len(binb)))
    fh.write(struct.pack('<II',len(js),0x4E4F534A)); fh.write(js); fh.write(struct.pack('<II',len(binb),0x004E4942)); fh.write(binb)
# round-trips
raw=open(base+'.stl','rb').read(); rr=np.frombuffer(raw[84:],dt); P=rr['v'].reshape(-1,3)
u,inv=np.unique(P,axis=0,return_inverse=True); fe=inv.reshape(-1,3)
e2=np.sort(np.concatenate([fe[:,[0,1]],fe[:,[1,2]],fe[:,[2,0]]]),1); _,c2=np.unique(e2[:,0]*len(u)+e2[:,1],return_counts=True)
R['stl_reload']={'faces':int(len(rr)),'non_manifold_after_weld':int((c2!=2).sum())}
g=open(base+'.glb','rb').read(); L=struct.unpack('<I',g[12:16])[0]; J=json.loads(g[20:20+L])
R['glb_reload']={'primitives':len(J['meshes'][0]['primitives']),'total_indices':sum(J['accessors'][p['indices']]['count'] for p in J['meshes'][0]['primitives']),'length':struct.unpack('<I',g[8:12])[0]==len(g)}
ov=sum(1 for l in open(base+'.obj') if l.startswith('v ')); of=sum(1 for l in open(base+'.obj') if l.startswith('f '))
R['obj_reload']={'v':ov,'f':of}
json.dump(R,open('out3/report.json','w'),indent=1)
print(json.dumps({k:v for k,v in R.items() if k!='support_islands_above_base'},indent=1)); print('islands',R['support_islands_above_base'])
