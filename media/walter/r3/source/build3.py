import json, time, numpy as np
from scipy import ndimage
from skimage.measure import marching_cubes
import sdf, model3
h=0.25; lo=np.array([-3.0,-30.0,-0.75]); hi=np.array([102.5,30.0,61.0])
sdf.CHUNK_SCALE=model3.GS
t0=time.time()
G=sdf.build_grid(model3.walter,lo,hi,h,block=48,verbose=False); G=np.minimum(G,10).astype(np.float32)
print('grid',G.shape,f'{time.time()-t0:.0f}s',flush=True)
G=ndimage.gaussian_filter(G,0.5).astype(np.float32)
ins=G<0; lab,n=ndimage.label(ins); sz=np.bincount(lab.ravel()); sz[0]=0; keep=lab==sz.argmax()
out=~keep; lab2,n2=ndimage.label(out); void=out&(lab2!=lab2[0,0,-1])
print('solid comps',n,'voids',n2-1)
small=np.sort(sz)[::-1][1:]*h**3
print('removed part volumes mm3',small[:5])
assert (small<0.05).all(), 'real part would be discarded'
G[ins&~keep]=np.abs(G[ins&~keep])+0.01; G[void]=-np.abs(G[void])-0.01
z=np.abs(G)<2e-4; G[z]=np.where(G[z]<0,-2e-4,2e-4)
np.save('g3_hi.npy',G); json.dump({'lo':lo.tolist(),'h':h},open('g3_hi.json','w'))
v,f,_,_=marching_cubes(np.pad(G,1,constant_values=10.0),0.0,spacing=(h,h,h),allow_degenerate=False)
v=v+(lo-h); f=f.astype(np.int64)
a,b,c=v[f[:,0]],v[f[:,1]],v[f[:,2]]
if np.einsum('ij,ij->i',a,np.cross(b,c)).sum()<0: f=f[:,::-1]
np.save('m3_v.npy',v.astype(np.float32)); np.save('m3_f.npy',f.astype(np.int32))
print(len(v),len(f),f'{time.time()-t0:.0f}s')
