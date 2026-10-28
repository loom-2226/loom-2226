"""Count direct ray occlusion by 16 identical moving rigid sectors.

Only the moving protective material is tested; glazing, frames, pressure
aperture and room contents remain separate from this metric.
"""
import json,math
from pathlib import Path
import numpy as np
import l1_single_gore_sweep as W
import l1_design_search as D

ROOT=Path(__file__).resolve().parent.parent

def mesh(shape,crown,ang,nr=19,na=6):
    rs=np.linspace(.005,crown,nr)
    fs=np.linspace(-W.HALF,W.HALF,na)
    pts=[]
    for r in rs:
        x=W.profile_x(float(r),shape)
        for f in fs:
            pts.append([x,r*math.cos(f),r*math.sin(f)])
    src=np.array(pts)
    dst=W.rotate_panel(src,W.pivot(shape,crown),ang).reshape(nr,na,3)
    triangles=[]
    for k in range(16):
        az=2*math.pi*k/16;c,s=math.cos(az),math.sin(az)
        v=dst.copy()
        y=v[:,:,1].copy();z=v[:,:,2].copy()
        v[:,:,1]=c*y-s*z;v[:,:,2]=s*y+c*z
        for i in range(nr-1):
            for j in range(na-1):
                a,b,c_,dd=v[i,j],v[i+1,j],v[i,j+1],v[i+1,j+1]
                triangles.extend([[a,b,c_],[b,dd,c_]])
    return np.array(triangles)

def hits(eye,rays,triangles):
    a=triangles[:,0,:];e1=triangles[:,1,:]-a;e2=triangles[:,2,:]-a
    tvec=eye-a
    qvec=np.cross(tvec,e1)
    numerator=np.einsum('ij,ij->i',e2,qvec)
    out=[]
    for ray in rays:
        pvec=np.cross(np.broadcast_to(ray,e2.shape),e2)
        det=np.einsum('ij,ij->i',e1,pvec)
        mask=np.abs(det)>1e-8
        safe=np.where(mask,det,1)
        u=np.einsum('ij,ij->i',tvec,pvec)/safe
        v=np.einsum('j,ij->i',ray,qvec)/safe
        t=numerator/safe
        out.append(bool(np.any(mask&(u>=-1e-7)&(v>=-1e-7)&(u+v<=1+1e-7)&(t>1e-5))))
    return np.array(out)

def main():
    data={'source':'single rigid hinge sector rotated around every 22.5 degree azimuth','metric':'fraction of forward cone directly occluded by petal mesh only','sample_count_per_eye':len(D.CONE),'angles':[-30,-45,-60,-75,-85,-90],'cases':[],'limitations':['No crew/furniture/window aperture mask in this measure','The triangle surface is thin for ray occlusion, not ballistic panel thickness','Collisions with other petals not tested']}
    for name,shape,crown in [('Rev7',None,2.8),('compact',(.8,1.2,35),3.2),('panorama',(1.2,2.0,50),3.5)]:
        result={'design':name,'results':[]}
        for ang in data['angles']:
            tri=mesh(shape,crown,ang)
            blocked=[float(hits(eye,D.CONE,tri).mean()) for eye in D.EYES[:2]]
            result['results'].append({'angle_deg':ang,'pilot_cone_occluded_fraction':round(blocked[0],4),
              'nav_cone_occluded_fraction':round(blocked[1],4)})
        data['cases'].append(result)
        print(name,result['results'],flush=True)
    (ROOT/'command/l1_gore_occlusion_results.json').write_text(json.dumps(data,indent=2))
if __name__=='__main__':main()
