import math
# Tangential corridor into radial medical bay at angle 210 degrees.
# Exact swept collision of stretcher rectangle with circular inner wall r=1.9;
# medical sector 165..255 and outer wall r=4.15. 0.6x2.0m.
# Search continuous rigid poses with center at radius rc, angle phi, and stretcher
# orientation theta (0=tangent, pi/2=radial outward). Discrete C-space BFS.
from collections import deque
RIN,ROUT=1.9,4.15
W,L=.6,1.4
# Door opening is arc angular half-width corresponding to door width at inner wall
# For a point at r>1.9, it must be within medical sector. For a point at r<1.9,
# it is in corridor. Points crossing r=1.9 must be within door angular opening.
# All corners and grid of rectangle tested.
def allowed(rc,theta,door_width):
 a=math.radians(210)
 cx,cy=rc*math.cos(a),rc*math.sin(a)
 ux,uy=math.cos(a+math.pi/2+theta),math.sin(a+math.pi/2+theta)
 vx,vy=-uy,ux
 for i in range(9):
  s=(i/8-.5)*L
  for j in range(5):
   t=(j/4-.5)*W
   x,y=cx+s*ux+t*vx,cy+s*uy+t*vy
   r=math.hypot(x,y)
   if r<.9 or r>ROUT: return False
   ang=(math.degrees(math.atan2(y,x))-210+180)%360-180
   if r>RIN and abs(ang)>45: return False
   if abs(r-RIN)<.11 and abs(ang)>math.degrees(door_width/2/RIN):return False
 return True
for width in (.8,1.,1.2,1.4,1.6,1.8,2.,2.2,2.4):
 # center r grid, orientation 0..90deg
 dr=.05; da=math.radians(5)
 nr=int((3.1-1.15)/dr)+1;na=19
 ok={(i,j) for i in range(nr) for j in range(na) if allowed(1.15+i*dr,j*da,width)}
 starts=[(i,0) for i in range(nr) if (i,0) in ok and 1.15+i*dr<1.45]
 ends={(i,j) for i,j in ok if j>=16 and 1.15+i*dr>2.65}
 q=deque(starts); seen=set(starts); reached=None
 while q:
  u=q.popleft()
  if u in ends:reached=u;break
  for v in ((u[0]+1,u[1]),(u[0]-1,u[1]),(u[0],u[1]+1),(u[0],u[1]-1)):
   if v in ok and v not in seen:seen.add(v);q.append(v)
 print('door_width',width,'valid_poses',len(ok),'path',bool(reached),'initial',bool(starts),'endposes',len(ends),flush=True)
