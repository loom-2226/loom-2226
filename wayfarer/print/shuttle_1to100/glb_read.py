import json,struct,numpy as np
def load(path):
    f=open(path,'rb').read(); L=struct.unpack('<I',f[12:16])[0]; j=json.loads(f[20:20+L]); b0=20+L; BL=struct.unpack('<I',f[b0:b0+4])[0]; buf=f[b0+8:b0+8+BL]
    def acc(i):
        a=j['accessors'][i]; bv=j['bufferViews'][a['bufferView']]; off=bv.get('byteOffset',0)+a.get('byteOffset',0)
        dt={5126:np.float32,5125:np.uint32,5123:np.uint16,5121:np.uint8}[a['componentType']]; n={'SCALAR':1,'VEC3':3,'VEC4':4,'VEC2':2}[a['type']]
        st=bv.get('byteStride',0); isz=np.dtype(dt).itemsize*n
        if st and st!=isz:
            raw=np.frombuffer(buf,np.uint8,count=st*a['count'],offset=off).reshape(a['count'],st)[:,:isz].copy(); return raw.view(dt).reshape(a['count'],n)
        return np.frombuffer(buf,dt,count=a['count']*n,offset=off).reshape(a['count'],n)
    def mat(n):
        if 'matrix' in n: return np.array(n['matrix']).reshape(4,4).T
        T=np.eye(4); t=n.get('translation',[0,0,0]); q=n.get('rotation',[0,0,0,1]); s=n.get('scale',[1,1,1])
        x,y,z,w=q; R=np.array([[1-2*(y*y+z*z),2*(x*y-z*w),2*(x*z+y*w)],[2*(x*y+z*w),1-2*(x*x+z*z),2*(y*z-x*w)],[2*(x*z-y*w),2*(y*z+x*w),1-2*(x*x+y*y)]])
        T[:3,:3]=R*np.array(s); T[:3,3]=t; return T
    out=[]
    def walk(i,M):
        n=j['nodes'][i]; M2=M@mat(n)
        if 'mesh' in n:
            for pr in j['meshes'][n['mesh']]['primitives']:
                V=acc(pr['attributes']['POSITION']).astype(float); I=acc(pr['indices']).reshape(-1) if 'indices' in pr else np.arange(len(V))
                Vw=(np.c_[V,np.ones(len(V))]@M2.T)[:,:3]; out.append((n.get('name',''),Vw[I.reshape(-1,3)]))
        for c in n.get('children',[]): walk(c,M2)
    for r in j['scenes'][j.get('scene',0)]['nodes']: walk(r,np.eye(4))
    return out
