"""Wayfarer interior surfaces: 1:25 FDM test sheet (Claude, 13 Nov 2026). ALL bodies. ALL sponsors. 2026-2226.
Printer: Bambu Lab A2L (FDM). Print FLAT, detail face up, 0.08-0.12 mm layers. Rules: stock 0.4 nozzle -> raised >=0.45 mm,
grooves >=0.5 mm, slots >=0.6 mm; 0.2 nozzle -> raised >=0.25, grooves >=0.3. Tiles are drawn to the 0.4 rules; tile L tests both.
Builds a piecewise-constant heightmap (0.05 mm cells, 0.04 mm height quanta) and meshes it into one closed STL."""
import numpy as np, math, struct, sys
from PIL import Image, ImageDraw, ImageFont
S=0.05; Q=0.04                                 # cell (mm), height quantum (mm)
T=40.0; G=5.0; COLS,ROWS=4,3; LAB=7.0          # tile size, gap, label strip under each tile
W=COLS*T+(COLS-1)*G; Hh=ROWS*(T+LAB)+(ROWS-1)*G
nx,ny=int(round(W/S)),int(round(Hh/S))
H=np.zeros((ny,nx),np.float32)
BASE=1.6
X=(np.arange(nx)+0.5)*S; Y=(np.arange(ny)+0.5)*S
class Tile:
    def __init__(s,c,r): s.x0=c*(T+G); s.y0=r*(T+LAB+G)+LAB
    def sl(s,x0,y0,x1,y1):
        return slice(int(round((s.y0+y0)/S)),int(round((s.y0+y1)/S))),slice(int(round((s.x0+x0)/S)),int(round((s.x0+x1)/S)))
    def rect(s,x0,y0,x1,y1,h,mode='set'):
        sy,sx=s.sl(x0,y0,x1,y1)
        if mode=='set': H[sy,sx]=h
        elif mode=='add': H[sy,sx]+=h
        elif mode=='max': H[sy,sx]=np.maximum(H[sy,sx],h)
        elif mode=='min': H[sy,sx]=np.minimum(H[sy,sx],h)
    def field(s,f,x0=0,y0=0,x1=T,y1=T,mode='max'):
        sy,sx=s.sl(x0,y0,x1,y1)
        xx=X[sx]-s.x0; yy=Y[sy]-s.y0; XX,YY=np.meshgrid(xx,yy); v=f(XX,YY)
        cur=H[sy,sx]
        H[sy,sx]=np.maximum(cur,v) if mode=='max' else (np.minimum(cur,v) if mode=='min' else np.where(np.isnan(v),cur,v))
    def rrect(s,x0,y0,x1,y1,rad,h,mode='max'):
        def f(XX,YY):
            cx=np.clip(XX,x0+rad,x1-rad); cy=np.clip(YY,y0+rad,y1-rad)
            ins=(XX>=x0)&(XX<=x1)&(YY>=y0)&(YY<=y1)&(np.hypot(XX-cx,YY-cy)<=rad)
            return np.where(ins,h,-1e9 if mode=='max' else 1e9)
        s.field(f,x0,y0,x1,y1,mode)
    def pipe_x(s,y,x0,x1,dia,top):     # half-cylinder along x, stepped by layers
        r=dia/2
        s.field(lambda XX,YY: np.where(np.abs(YY-y)<r, top-r+np.sqrt(np.clip(r*r-(YY-y)**2,0,None)), -1e9),x0,y-r,x1,y+r)
    def pipe_y(s,x,y0,y1,dia,top):
        r=dia/2
        s.field(lambda XX,YY: np.where(np.abs(XX-x)<r, top-r+np.sqrt(np.clip(r*r-(XX-x)**2,0,None)), -1e9),x-r,y0,x+r,y1)
    def disc(s,cx,cy,rad,h,mode='max'):
        s.field(lambda XX,YY: np.where(np.hypot(XX-cx,YY-cy)<=rad,h,-1e9 if mode=='max' else 1e9),cx-rad,cy-rad,cx+rad,cy+rad,mode)
    def label(s,text,h=BASE+0.4):
        img=Image.new('L',(int(T/S),int((LAB-1.0)/S)),0); d=ImageDraw.Draw(img)
        f=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf',int(3.6/S))
        d.text((int(0.6/S),int(0.4/S)),text,fill=255,font=f)
        a=np.array(img)[::-1]>128
        sy=slice(int(round((s.y0-LAB+0.5)/S)),int(round((s.y0-LAB+0.5)/S))+a.shape[0]); sx=slice(int(round(s.x0/S)),int(round(s.x0/S))+a.shape[1])
        H[sy,sx]=np.where(a,h,BASE*0.75)    # label strip: thinner base with raised letters (strokes ~0.55 mm)
def base(t): t.rect(0,0,T,T,BASE)
tiles={}
def tile(c,r,code,title):
    t=Tile(c,r); base(t); t.label(code+' '+title); tiles[code]=(t,title); return t
# ---------------- WALLS (row 0, top of the sheet when the print is viewed label-down) ----------------
r=2
t=tile(0,r,'A','HABITAT')          # lined, light strip, padded panels, slatted lower panel
t.rrect(2,2,38,38,1.6,BASE+0.24)                        # raised lining field
t.rrect(5,33,35,35.6,1.0,BASE-0.36,'min')               # recessed light strip (0.6 deep reveal, 2.6 wide)
for y0 in (24.5,17.5):
    t.rrect(4,y0,36,y0+6.2,1.6,BASE+0.48); t.rrect(4.6,y0+0.6,35.4,y0+5.6,1.2,BASE+0.6)   # padded panels, 2-step edge
t.rrect(4,3.5,36,15.5,1.4,BASE+0.16)                    # wood-slat panel field
for x in np.arange(5.6,35.0,1.6): t.rect(x,4.3,x+0.5,14.7,BASE-0.08,'min')   # 0.5 mm slat grooves
t=tile(1,r,'B','SERVICE')
t.rrect(2,2,38,38,1.6,BASE+0.16)
for i,y in enumerate((33,29.4,25.8)): t.rrect(4,y,36,y+1.4,0.6,BASE+0.56)               # routing ribs 1.4 wide
for y in (21.4,17.8,14.2,10.6,7.0): t.rrect(4,y,17,y+1.4,0.6,BASE+0.56)
t.rrect(20,4,36,21.5,1.2,BASE+0.4); t.rrect(21,5,35,20.5,0.8,BASE+0.36,'min')           # access panel frame + face
for cx,cy in ((22.6,6.6),(33.4,6.6),(22.6,18.9),(33.4,18.9)): t.disc(cx,cy,0.55,BASE+0.6)   # fasteners 1.1 dia
t=tile(2,r,'C','UTILITY')
t.rrect(2,2,38,38,1.6,BASE+0.08)
t.pipe_x(34,3,37,2.6,BASE+1.6); t.pipe_x(29.5,3,19.5,2.6,BASE+1.6)                       # two service pipes
t.pipe_y(19.5,4,29.5,2.6,BASE+1.6)
for x in (9,19,31): t.rrect(x,32.0,x+1.4,36.0,0.4,BASE+1.8)                              # pipe clamps
t.rrect(4,4,16.8,22,1.0,BASE+0.6); t.rrect(5,5,15.8,21,0.6,BASE+0.4,'min')                   # small service panel
t.rrect(22.2,4,36,20,1.0,BASE+0.64)                                                        # louvre box
for y in np.arange(6.0,18.5,2.0): t.rrect(24,y,34.2,y+0.9,0.3,BASE+0.16,'min')            # 0.9 louvre slots
t=tile(3,r,'D','BULKHEAD')
oct_=lambda XX,YY,R: (np.abs(XX-20)<=R)&(np.abs(YY-20)<=R)&(np.abs(XX-20)+np.abs(YY-20)<=R*1.42)
t.field(lambda XX,YY: np.where(oct_(XX,YY,17)&~oct_(XX,YY,13.4),BASE+0.8,-1e9))          # octagonal frame 3.6 wide
t.field(lambda XX,YY: np.where(oct_(XX,YY,12.6),BASE-0.32,1e9),mode='min')               # sealing-face recess
t.field(lambda XX,YY: np.where(oct_(XX,YY,10.0),BASE-0.16,-1e9))
for cx,cy in ((4.5,4.5),(35.5,4.5),(4.5,35.5),(35.5,35.5)): t.rrect(cx-3,cy-3,cx+3,cy+3,1.0,BASE+0.48)   # corner gussets
for cx,cy in ((20,2.6),(20,37.4),(2.6,20),(37.4,20)): t.rrect(cx-1.6 if cx in (2.6,37.4) else cx-4,cy-4 if cx in (2.6,37.4) else cy-1.6,cx+1.6 if cx in (2.6,37.4) else cx+4,cy+4 if cx in (2.6,37.4) else cy+1.6,0.6,BASE+0.48)
# ---------------- FLOORS (row 1) ----------------
r=1
t=tile(0,r,'F1','SMOOTH')
for v in (0.5,20,39.5):
    t.rect(v-0.25 if v not in (0.5,39.5) else (0 if v==0.5 else 39.5),0,v+0.25 if v not in (0.5,39.5) else (0.5 if v==0.5 else 40),40,BASE-0.24,'min'); t.rect(0,v-0.25 if v not in (0.5,39.5) else (0 if v==0.5 else 39.5),40,v+0.25 if v not in (0.5,39.5) else (0.5 if v==0.5 else 40),BASE-0.24,'min')
for cx in (3,17,23,37):
    for cy in (3,17,23,37): t.disc(cx,cy,0.6,BASE-0.2,'min')
t=tile(1,r,'F2','RIBBED')
for x in np.arange(2.0,38.0,1.8): t.rrect(x,2,x+0.9,38,0.45,BASE+0.32)                   # 0.9 ribs, 0.9 gaps
t=tile(2,r,'F3','GRATED')
t.rect(0,0,T,T,BASE+0.2)
for row in range(5):
    for col in range(3):
        x0=3+col*11.8; y0=3+row*7.0
        for k in range(4): t.rrect(x0+k*2.6,y0,x0+k*2.6+1.0,y0+5.4,0.45,BASE-0.6,'min')   # 1.0 x 5.4 slots, 0.8 deep
t=tile(3,r,'F4','WALKWAY')
for x0 in (6,30):
    t.rect(x0,0,x0+4,40,BASE-0.36,'min')                                                 # recessed wear strip
    for y in np.arange(1.0,40,2.0): t.rect(x0+0.5,y,x0+3.5,y+0.8,BASE-0.12)              # tread bars inside the strip
t.rect(19.75,0,20.25,40,BASE-0.24,'min')
# ---------------- CEILINGS + DETAIL LADDER (row 2) ----------------
r=0
t=tile(0,r,'K1','LIVING')
t.field(lambda XX,YY: np.where(YY>30, BASE+0.4*np.clip((YY-30)/10,0,1)**0.5*1.0, -1e9))   # cove sweep (stepped)
t.rect(0,29.0,40,30.0,BASE-0.36,'min')                                                    # continuous cove light reveal
for x in (6.5,20,33.5): t.rect(x-0.3,0,x+0.3,29,BASE-0.24,'min')                         # radial seams 0.6
t=tile(1,r,'K2','CORRIDOR')
t.rrect(6,10,34,30,1.4,BASE+0.48); t.rrect(8,12,32,28,1.0,BASE-0.4,'min')                # light panel frame + recessed diffuser
t.pipe_x(5.0,0,40,2.4,BASE+1.2); t.pipe_x(35.0,0,40,2.4,BASE+1.2)                        # overhead handrails
for x in (8,32): t.rrect(x-0.8,3.0,x+0.8,7.0,0.3,BASE+1.0); t.rrect(x-0.8,33.0,x+0.8,37.0,0.3,BASE+1.0)
t=tile(2,r,'K3','TECH')
t.rect(0,0,T,T,BASE)
for y0 in (6,22): t.rect(2,y0,38,y0+10,BASE+0.16); t.rect(3.5,y0+1.2,36.5,y0+8.8,BASE-0.24,'min')   # cable trays
for y0 in (6,22):
    for x in np.arange(5,36,4.5): t.rect(x,y0+1.2,x+0.8,y0+8.8,BASE+0.16)                # tray rungs 0.8
t=tile(3,r,'L','LADDER')
widths=[0.20,0.25,0.30,0.35,0.40,0.45,0.50,0.60,0.80]
for i,w in enumerate(widths):
    x=2.0+i*4.0
    t.rect(x,21,x+w,38,BASE+0.4)                       # raised lines
    t.rect(x,3,x+w,19,BASE-0.4,'min')                  # grooves
    for k in range(i+1): t.disc(x+w/2,20.0 if False else 20.0,0,0)   # (index by position)
t.rect(0,19.6,40,20.4,BASE+0.0)
for i,d in enumerate([0.08,0.12,0.16,0.24,0.32,0.48,0.64]):   # relief depth steps along the bottom edge
    t.rect(1.0+i*5.4,0.6,1.0+i*5.4+4.6,2.4,BASE+d)
# ---------------- quantise and mesh ----------------
Hq=np.round(H/Q).astype(np.int32)
def mesh(Hq):
    ny,nx=Hq.shape; F=[]
    def quad(a,b,c,d): F.append((a,b,c)); F.append((a,c,d))
    # top faces: runs per row merged vertically
    active={}
    def flush(key,y0,y1):
        x0,x1,h=key; z=h*Q
        quad((x0*S,y0*S,z),(x1*S,y0*S,z),(x1*S,y1*S,z),(x0*S,y1*S,z))
    def runs(row):
        b=np.flatnonzero(np.diff(row))+1; st=np.r_[0,b]; en=np.r_[b,len(row)]
        return [(int(s),int(e),int(row[s])) for s,e in zip(st,en) if row[s]>0]
    prev={}
    for j in range(ny):
        cur={}
        for s,e,h in runs(Hq[j]):
            k=(s,e,h); cur[k]=prev.pop(k,j)
        for k,y0 in prev.items(): flush(k,y0,j)
        prev=cur
    for k,y0 in prev.items(): flush(k,y0,ny)
    # bottom faces (z=0) where material exists
    B=(Hq>0).astype(np.int32); prev={}
    def bflush(key,y0,y1):
        x0,x1,_=key; quad((x0*S,y0*S,0),(x0*S,y1*S,0),(x1*S,y1*S,0),(x1*S,y0*S,0))
    for j in range(ny):
        cur={}
        for s,e,h in runs(B[j]): k=(s,e,h); cur[k]=prev.pop(k,j)
        for k,y0 in prev.items(): bflush(k,y0,j)
        prev=cur
    for k,y0 in prev.items(): bflush(k,y0,ny)
    # x-walls: between column i-1 and i (incl. borders), merged along y
    P=np.pad(Hq,((0,0),(1,1)))
    prev={}
    def xflush(key,y0,y1):
        i,ha,hb=key; x=i*S; za,zb=ha*Q,hb*Q
        if ha>hb: quad((x,y0*S,zb),(x,y1*S,zb),(x,y1*S,za),(x,y0*S,za))     # face +x
        else: quad((x,y0*S,za),(x,y0*S,zb),(x,y1*S,zb),(x,y1*S,za))         # face -x
    for j in range(ny):
        a=P[j,:-1]; b=P[j,1:]; idx=np.flatnonzero(a!=b); cur={}
        for i in idx: k=(int(i),int(a[i]),int(b[i])); cur[k]=prev.pop(k,j)
        for k,y0 in prev.items(): xflush(k,y0,j)
        prev=cur
    for k,y0 in prev.items(): xflush(k,y0,ny)
    # y-walls: between row j-1 and j, runs along x
    P=np.pad(Hq,((1,1),(0,0)))
    for j in range(ny+1):
        a=P[j]; b=P[j+1]; d=(a!=b)
        if not d.any(): continue
        key=np.where(d,a.astype(np.int64)*100000+b,-1)
        bnd=np.flatnonzero(np.diff(key))+1; st=np.r_[0,bnd]; en=np.r_[bnd,len(key)]
        y=j*S
        for s,e in zip(st,en):
            if key[s]<0: continue
            ha,hb=int(a[s]),int(b[s]); za,zb=ha*Q,hb*Q
            if ha>hb: quad((s*S,y,zb),(s*S,y,za),(e*S,y,za),(e*S,y,zb))      # face +y
            else: quad((s*S,y,za),(e*S,y,za),(e*S,y,zb),(s*S,y,zb))
    return np.array(F,np.float32)
Fs=mesh(Hq)
n=np.cross(Fs[:,1]-Fs[:,0],Fs[:,2]-Fs[:,0]); n/=np.linalg.norm(n,axis=1,keepdims=True)+1e-12
out=sys.argv[1] if len(sys.argv)>1 and not sys.argv[1].startswith('--') else 'wayfarer_1to25_surface_test_sheet.stl'
with open(out,'wb') as fh:
    fh.write(b'Wayfarer 1:25 surface test sheet (Claude)'.ljust(80,b' ')); fh.write(struct.pack('<I',len(Fs)))
    rec=np.zeros(len(Fs),dtype=[('n','<f4',3),('v','<f4',(3,3)),('a','<u2')]); rec['n']=n; rec['v']=Fs; fh.write(rec.tobytes())
print('triangles',len(Fs),'sheet mm',round(W,1),'x',round(Hh,1),'max h',Hq.max()*Q)
np.save(out.rsplit('.',1)[0]+'_heightmap.npy',Hq) if '--npy' in sys.argv else None
