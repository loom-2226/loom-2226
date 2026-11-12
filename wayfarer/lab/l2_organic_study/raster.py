import numpy as np, math
from PIL import Image, ImageFilter
def hexrgb(h): return np.array([int(h[i:i+2],16)/255 for i in (1,3,5)])
def smooth_normals(V, thr=0.80):
    """V: (n,3,3) triangles -> per-corner normals, averaged across neighbours within angle threshold"""
    N=np.cross(V[:,1]-V[:,0],V[:,2]-V[:,0]); A=np.linalg.norm(N,axis=1,keepdims=True); N=N/(A+1e-12)
    P=V.reshape(-1,3); key=np.round(P*2000).astype(np.int64)
    k=key[:,0]*73856093 ^ key[:,1]*19349663 ^ key[:,2]*83492791
    order=np.argsort(k); ks=k[order]; Nf=np.repeat(N,3,0); out=Nf.copy()
    starts=np.r_[0,np.nonzero(np.diff(ks))[0]+1,len(ks)]
    for s,e in zip(starts[:-1],starts[1:]):
        if e-s<2: continue
        idx=order[s:e]; G=Nf[idx]; D=G@G.T; M=(D>thr).astype(float); S=M@G; S/=np.linalg.norm(S,axis=1,keepdims=True)+1e-12; out[idx]=S
    return N,out.reshape(-1,3,3)
def render(T, MAT, eye, tgt, fov, W=1100, H=800, ss=2, out='x.png', fog=None):
    Wp,Hp=W*ss,H*ss
    eye=np.array(eye,float); tgt=np.array(tgt,float); up=np.array([-1.,0,0])
    f=tgt-eye; f/=np.linalg.norm(f); s=np.cross(f,up); s/=np.linalg.norm(s); u=np.cross(s,f)
    F=1/math.tan(math.radians(fov/2))
    zb=np.full((Hp,Wp),np.inf); img=np.zeros((Hp,Wp,3)); img[:]=np.array([0.06,0.07,0.09])
    L1=-f*0.5+u*0.9+s*0.3; L1/=np.linalg.norm(L1); L2=f*0.2+u*0.3-s*0.6; L2/=np.linalg.norm(L2)
    for m,tris in T.items():
        V=np.array(tris,float).reshape(-1,3,3); col,em=MAT[m]; C=hexrgb(col)**2.2
        Nf,Nv=smooth_normals(V)
        Q=V-eye; x=Q@s; y=Q@u; z=Q@f
        keep=(z>0.08).all(1); 
        for i in np.nonzero(keep)[0]:
            zz=z[i]; px=(F*x[i]/zz*Hp/2+Wp/2); py=(-F*y[i]/zz*Hp/2+Hp/2)
            x0=max(int(np.floor(px.min())),0); x1=min(int(np.ceil(px.max())),Wp-1); y0=max(int(np.floor(py.min())),0); y1=min(int(np.ceil(py.max())),Hp-1)
            if x1<x0 or y1<y0: continue
            gx,gy=np.meshgrid(np.arange(x0,x1+1)+0.5,np.arange(y0,y1+1)+0.5)
            d=(py[1]-py[2])*(px[0]-px[2])+(px[2]-px[1])*(py[0]-py[2])
            if abs(d)<1e-9: continue
            w0=((py[1]-py[2])*(gx-px[2])+(px[2]-px[1])*(gy-py[2]))/d; w1=((py[2]-py[0])*(gx-px[2])+(px[0]-px[2])*(gy-py[2]))/d; w2=1-w0-w1
            ins=(w0>=-1e-6)&(w1>=-1e-6)&(w2>=-1e-6)
            if not ins.any(): continue
            iz=w0/zz[0]+w1/zz[1]+w2/zz[2]; depth=1/iz
            sub=zb[y0:y1+1,x0:x1+1]; vis=ins&(depth<sub-1e-5)
            if not vis.any(): continue
            n=(w0[...,None]*Nv[i,0]/zz[0]+w1[...,None]*Nv[i,1]/zz[1]+w2[...,None]*Nv[i,2]/zz[2])*depth[...,None]
            n/=np.linalg.norm(n,axis=-1,keepdims=True)+1e-12
            if (n@(-f)).mean()<0: n=-n   # double-sided: face the camera
            if em: c=np.broadcast_to(C*1.15,n.shape)
            else:
                dif=0.30+0.62*np.clip(n@L1,0,1)+0.22*np.clip(n@L2,0,1)
                spec=0.10*np.clip(n@((L1-f)/np.linalg.norm(L1-f)),0,1)**24
                c=C[None,None,:]*dif[...,None]+spec[...,None]
            if fog: c=c*np.exp(-depth[...,None]/fog)+ (1-np.exp(-depth[...,None]/fog))*0.03
            sub[vis]=depth[vis]; img[y0:y1+1,x0:x1+1][vis]=c[vis]
    img=np.clip(img,0,1)**(1/2.2)
    im=Image.fromarray((img*255).astype(np.uint8)).resize((W,H),Image.LANCZOS)
    im.save(out); return out
