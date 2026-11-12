"""L2 Organic Japandi design study geometry (Claude, 12 Nov 2026). PROPOSE ONLY.
ALL bodies. ALL sponsors. 2026-2226.
Frame: source angle a (Y=r cos a, Z=r sin a); glTF/world = [X, Z, -Y]; h above L2 floor top X=5.6; ceiling h=2.30."""
import math,numpy as np
X0=5.6; HC=2.30; RW=4.15
MAT={ # name: (hex, emissive)
 'hull':('#8E9FA8',0),'hull_dk':('#6F818B',0),'titanium':('#B8B4AC',0),'oak':('#CDB28F',0),'oak_dk':('#B39470',0),'sand':('#E6DCC8',0),
 'sage':('#9AA58F',0),'worktop':('#EEE9DF',0),'glass':('#1C2530',0),'graphic':('#5FA8D3',1),'warm':('#FFE2B0',1),'floor':('#9C958A',0),
 'reveal':('#3A3F44',0),'teal':('#3FA79A',0),'leaf':('#6E8B5E',0),'space':('#0B1018',0),'core':('#58646D',0)}
T={}  # material -> list of triangles (3x3)
def add(m,tris): T.setdefault(m,[]).extend(tris)
def W(r,a,h): t=math.radians(a); return (X0-h, r*math.sin(t), -r*math.cos(t))
def Lc(rc,ac,u,v,h):
    t=math.radians(ac); c,s=math.cos(t),math.sin(t); Y=(rc+u)*c-v*s; Z=(rc+u)*s+v*c; return (X0-h,Z,-Y)
def quad(p0,p1,p2,p3): return [(p0,p1,p2),(p0,p2,p3)]
# ---- sweep a closed (r,h) profile around an arc
def sweep(m,prof,a0,a1,step=1.5,caps=True):
    n=max(2,int(abs(a1-a0)/step)+1); A=np.linspace(a0,a1,n); out=[]
    for i in range(n-1):
        for k in range(len(prof)):
            (r0,h0),(r1,h1)=prof[k],prof[(k+1)%len(prof)]
            out+=quad(W(r0,A[i],h0),W(r1,A[i],h1),W(r1,A[i+1],h1),W(r0,A[i+1],h0))
    if caps:
        for a in (a0,a1):
            c=W(np.mean([p[0] for p in prof]),a,np.mean([p[1] for p in prof]))
            for k in range(len(prof)):
                out.append((c,W(*prof[k][:1],a,prof[k][1]) if False else W(prof[k][0],a,prof[k][1]),W(prof[(k+1)%len(prof)][0],a,prof[(k+1)%len(prof)][1])))
    add(m,out)
def sweep_var(m,proff,a0,a1,step=0.5):
    n=max(2,int(abs(a1-a0)/step)+1); A=np.linspace(a0,a1,n); PR=[proff(a) for a in A]; out=[]
    for i in range(n-1):
        p,q=PR[i],PR[i+1]
        for k in range(len(p)):
            k2=(k+1)%len(p); out+=quad(W(*p[k][:1],A[i],p[k][1]) if False else W(p[k][0],A[i],p[k][1]),W(p[k2][0],A[i],p[k2][1]),W(q[k2][0],A[i+1],q[k2][1]),W(q[k][0],A[i+1],q[k][1]))
    for a,p in ((A[0],PR[0]),(A[-1],PR[-1])):
        c=W(np.mean([x[0] for x in p]),a,np.mean([x[1] for x in p])); out+=[(c,W(p[k][0],a,p[k][1]),W(p[(k+1)%len(p)][0],a,p[(k+1)%len(p)][1])) for k in range(len(p))]
    add(m,out)
def rounded_rect(r0,r1,h0,h1,rad,n=5):
    """closed (r,h) profile with rounded corners"""
    pts=[]
    for (cr,ch,s) in ((r1-rad,h0+rad,-90),(r1-rad,h1-rad,0),(r0+rad,h1-rad,90),(r0+rad,h0+rad,180)):
        for k in range(n+1):
            t=math.radians(s+90*k/n); pts.append((cr+rad*math.cos(t),ch+rad*math.sin(t)))
    return pts
# ---- loft of superellipse rings in local (u radial, v tangential) frame
def ring(A,B,nexp=4,bulge=0.0,N=48):
    pts=[]
    for k in range(N):
        t=2*math.pi*k/N; c,s=math.cos(t),math.sin(t)
        u=A*math.copysign(abs(c)**(2/nexp),c); v=B*math.copysign(abs(s)**(2/nexp),s)
        v*= 1+bulge*max(0,1-(u/A)**2) if A>0 else 1
        pts.append((u,v))
    return pts
def loft(m,rc,ac,rings,du=0,dv=0,cap_top=True,cap_bot=True):
    """rings: list of (h, A, B, nexp, bulge)"""
    R=[[(u+du,v+dv) for u,v in ring(A,B,n,b)] for (h,A,B,n,b) in rings]; H=[r[0] for r in rings]; out=[]
    for i in range(len(R)-1):
        for k in range(len(R[i])):
            k2=(k+1)%len(R[i])
            out+=quad(Lc(rc,ac,*R[i][k],H[i]),Lc(rc,ac,*R[i][k2],H[i]),Lc(rc,ac,*R[i+1][k2],H[i+1]),Lc(rc,ac,*R[i+1][k],H[i+1]))
    for flag,i in ((cap_bot,0),(cap_top,len(R)-1)):
        if flag:
            c=Lc(rc,ac,du,dv,H[i])
            for k in range(len(R[i])): out.append((c,Lc(rc,ac,*R[i][k],H[i]),Lc(rc,ac,*R[i][(k+1)%len(R[i])],H[i])))
    add(m,out)
def soft_block(m,rc,ac,A,B,h0,h1,rad=0.03,nexp=5,bulge=0.0,du=0,dv=0,top=True):
    """block with radiused top/bottom edges and superellipse plan"""
    rr=[]; 
    for k in range(5):
        t=math.radians(90*k/4); rr.append((h0+rad*(1-math.cos(t)), A-rad*(1-math.sin(t)), B-rad*(1-math.sin(t))))
    for k in range(5):
        t=math.radians(90*k/4); rr.append((h1-rad+rad*math.sin(t), A-rad*(1-math.cos(t)), B-rad*(1-math.cos(t))))
    loft(m,rc,ac,[(h,a,b,nexp,bulge) for h,a,b in rr],du,dv,top,True)
def panel_line(m,rc,ac,u0,u1,v,h0,h1,w=0.006):
    add(m,quad(Lc(rc,ac,u0,v,h0),Lc(rc,ac,u1,v,h0),Lc(rc,ac,u1,v,h1),Lc(rc,ac,u0,v,h1)))
def vline(m,rc,ac,u,v0,v1,h0,h1):
    add(m,quad(Lc(rc,ac,u,v0,h0),Lc(rc,ac,u,v1,h0),Lc(rc,ac,u,v1,h1),Lc(rc,ac,u,v0,h1)))
# =================== ARCHITECTURE (hull lining, ceiling sweep, floor, band) ===================
BAND={'galley':(300,390,0.05,2.25),'wardroom':(30,150,1.10,1.70)}
def architecture():
    # floor with radial seams
    for a in np.arange(0,360,3): add('floor',quad(W(1.25,a,0),W(RW,a,0),W(RW,a+3,0),W(1.25,a+3,0))[::-1])
    # core trunk and racks
    for a in np.arange(0,360,4):
        add('core',quad(W(1.25,a,0),W(1.25,a+4,0),W(1.25,a+4,HC),W(1.25,a,HC)))
    # ceiling (L1 floor underside) with ceiling sweep cove into the wall (large-curvature transition)
    for a in np.arange(0,360,3): add('hull',quad(W(1.25,a,HC),W(3.85,a,HC),W(3.85,a+3,HC),W(1.25,a+3,HC)))
    cove=[(3.85,HC)]+[(3.85+0.3*math.sin(math.radians(t)),HC-0.3+0.3*math.cos(math.radians(t))) for t in range(0,91,10)]
    for a in np.arange(0,360,2):
        for k in range(len(cove)-1):
            (r0,h0),(r1,h1)=cove[k],cove[k+1]; add('hull',quad(W(r0,a,h0),W(r1,a,h1),W(r1,a+2,h1),W(r0,a+2,h0)))
    for a in np.arange(0,360,7.5):
        sweep('reveal',[(1.30,HC-0.002),(3.85,HC-0.002),(3.85,HC-0.006),(1.30,HC-0.006)],a-0.07,a+0.07,0.14,caps=False)
    sweep('reveal',[(2.55,HC-0.002),(2.60,HC-0.002),(2.60,HC-0.006),(2.55,HC-0.006)],0,360,2,caps=False)
    # continuous warm light reveal at the cove root and a titanium trim line
    sweep('warm',[(3.83,2.268),(3.86,2.268),(3.86,2.28),(3.83,2.28)],0,360,2,caps=False)
    sweep('titanium',[(4.11,1.995),(4.15,1.995),(4.15,2.005),(4.11,2.005)],0,360,2,caps=False)
    # outer wall: lining panels with reveals; band as dark glass between titanium edge rings
    for a in np.arange(-60,300,1.5):
        aa=a%360; inband=None
        for k,(b0,b1,g0,g1) in BAND.items():
            if b0<=a<b1 or b0<=a+360<b1: inband=(g0,g1)
        segs=[(0,2.0)] if not inband else [(0,inband[0]),(inband[1],2.0)]
        for s0,s1 in segs:
            if s1-s0>0.01: add('hull',quad(W(RW,a,s0),W(RW,a,s1),W(RW,a+1.5,s1),W(RW,a+1.5,s0)))
        if inband:
            add('space',quad(W(RW+0.10,a,inband[0]),W(RW+0.10,a,inband[1]),W(RW+0.10,a+1.5,inband[1]),W(RW+0.10,a+1.5,inband[0])))
    for k,(b0,b1,g0,g1) in BAND.items():
        for g in (g0,g1):
            sweep('titanium',[(4.09,g-0.03),(4.16,g-0.03),(4.16,g+0.03),(4.09,g+0.03)],b0,b1,1.5,caps=False)
        for a in np.arange(b0,b1+0.01,(b1-b0)/round((b1-b0)/15)):   # Osteon mullions ~15 deg
            sweep('titanium',[(4.10,g0),(4.16,g0),(4.16,g1),(4.10,g1)],a-0.35,a+0.35,0.7)
    # vertical lining reveals every 7.5 deg where there is lining
    for a in np.arange(0,360,7.5):
        inb=any(b0<=a<b1 or b0<=a+360<b1 for (b0,b1,g0,g1) in BAND.values())
        if not inb: sweep('reveal',[(4.135,0.12),(4.15,0.12),(4.15,1.97),(4.135,1.97)],a-0.08,a+0.08,0.16,caps=False)
    # skirting reveal with floor-wash warm light
    sweep('reveal',[(4.10,0.0),(4.15,0.0),(4.15,0.10),(4.10,0.10)],0,360,2,caps=False)
    sweep('warm',[(4.095,0.10),(4.11,0.10),(4.11,0.11),(4.095,0.11)],0,360,2,caps=False)
    # room divider walls (galley/wardroom shared wall at 30 is open; washroom wall at 300)
    sweep('hull',rounded_rect(1.92,4.15,0,HC,0.02),299.2,300.4,0.6)
    # overhead handrail (oak)
    sweep('oak',[(1.62,1.98),(1.67,1.98),(1.67,2.03),(1.62,2.03)],14,166,2,caps=True); sweep('oak',[(1.62,1.98),(1.67,1.98),(1.67,2.03),(1.62,2.03)],194,346,2,caps=True)
# =================== WARDROOM ===================
def wardroom():
    # table: racetrack top, rounded underside, tapered integrated blade support
    rc,ac=3.0,90
    loft('oak',rc,ac,[(0.70,0.44,1.34,2.0,0),(0.715,0.48,1.38,2.0,0),(0.735,0.50,1.40,2.0,0),(0.755,0.495,1.395,2.0,0),(0.76,0.485,1.385,2.0,0)][::-1][::-1],du=0,dv=0) if False else None
    # stadium: build with superellipse exponent 2 on a stretched ring -> use racetrack ring
    def race(A,B,N=64):  # A radial half (short), B tangential half (long)
        pts=[]; r=A
        for k in range(N//2+1):
            t=math.pi*k/(N//2)-math.pi/2; pts.append((r*math.cos(t+math.pi/2)*-1*0+r*math.sin(t+math.pi), B-r+r*math.cos(t)) )
        pts=[]
        for k in range(N//2+1):
            t=-math.pi/2+math.pi*k/(N//2); pts.append((A*math.sin(t), (B-A)+A*math.cos(t)))
        for k in range(N//2+1):
            t=math.pi/2+math.pi*k/(N//2); pts.append((A*math.sin(t), -(B-A)+A*math.cos(t)))
        return pts
    def loftp(m,rc,ac,rings):
        out=[]; R=[(h,race(A,B)) for h,A,B in rings]
        for i in range(len(R)-1):
            (h0,P0),(h1,P1)=R[i],R[i+1]
            for k in range(len(P0)):
                k2=(k+1)%len(P0); out+=quad(Lc(rc,ac,*P0[k],h0),Lc(rc,ac,*P0[k2],h0),Lc(rc,ac,*P1[k2],h1),Lc(rc,ac,*P1[k],h1))
        for h,P in (R[0],R[-1]):
            c=Lc(rc,ac,0,0,h); out+=[(c,Lc(rc,ac,*P[k],h),Lc(rc,ac,*P[(k+1)%len(P)],h)) for k in range(len(P))]
        add(m,out)
    loftp('oak',rc,ac,[(0.685,0.40,1.30),(0.70,0.455,1.355),(0.72,0.49,1.39),(0.745,0.50,1.40),(0.76,0.49,1.39),(0.765,0.475,1.375)])
    loftp('teal',rc,ac,[(0.675,0.39,1.29),(0.69,0.40,1.30)])     # recessed restraint rail ring under the edge
    loftp('titanium',rc,ac,[(0.0,0.20,0.70),(0.02,0.19,0.69)])    # floor docking plate
    loftp('oak_dk',rc,ac,[(0.02,0.11,0.55),(0.35,0.07,0.62),(0.62,0.08,0.85),(0.685,0.16,1.05)])   # tapered blade support
    # banquette: continuous sweep, backrest leaning to the hull, rounded returns, segmented cushions
    plinth=rounded_rect(3.58,4.05,0.02,0.40,0.04)
    sweep('oak',plinth,64,116,1.0)
    sweep('warm',[(3.60,0.02),(3.63,0.02),(3.63,0.035),(3.60,0.035)],64,116,1.0,caps=False)   # toe-kick light
    for k in range(5):
        a0=64+k*10.4+0.25; a1=a0+10.4-0.5
        sweep('sand',rounded_rect(3.60,3.97,0.40,0.49,0.035),a0,a1,0.8)
        back=[(3.94,0.49),(4.02,0.49),(4.07,1.00),(4.00,1.02),(3.95,0.95)]
        sweep('sand',back,a0,a1,0.8)
    sweep('titanium',[(4.0,1.02),(4.09,1.02),(4.09,1.045),(4.0,1.045)],62,118,1.0)
    def rin(t): return 4.05-0.47*math.sqrt(max(0.0,1-(1-t)**2))
    sweep_var('oak',lambda a: rounded_rect(rin((a-60.6)/3.4),4.06,0.02,1.0,0.04,3),60.6,64.0,0.25)
    sweep_var('oak',lambda a: rounded_rect(rin((119.4-a)/3.4),4.06,0.02,1.0,0.04,3),116.0,119.4,0.25)
    # stools: tapered, domed cushion, teal floor dock ring
    for k in range(5):
        a=90+(k-2)*13
        loft('oak',2.25,a,[(0.02,0.13,0.13,2,0),(0.30,0.155,0.155,2,0),(0.40,0.17,0.17,2,0)])
        loft('sage',2.25,a,[(0.40,0.175,0.175,2,0),(0.43,0.18,0.18,2,0),(0.46,0.165,0.165,2,0),(0.475,0.12,0.12,2,0),(0.48,0.0,0.0,2,0)],cap_top=False)
        loft('teal',2.25,a,[(0.0,0.16,0.16,2,0),(0.012,0.16,0.16,2,0)])
    # serving pass: radiused plan, convex door face, off-white top with upstand
    soft_block('oak',3.3,38.5,0.70,0.225,0.05,0.93,0.04,nexp=6,bulge=0.06)
    soft_block('worktop',3.3,38.5,0.71,0.235,0.93,0.965,0.015,nexp=6)
    for u in (-0.23,0.23): vline('reveal',3.3,38.5,u,0.20*1.0,0.24,0.08,0.9)
    # briefing screen stowed in a ceiling recess (dark glass, cool graphic line)
    soft_block('glass',3.25,146,0.65,0.03,2.13,2.27,0.01,nexp=8)
    # living niche integrated into the 150 divider: arched oak frame, planter
    sweep('hull',rounded_rect(2.0,4.10,0,HC,0.02),149.4,150.6,0.6)
    soft_block('oak',3.7,148.3,0.38,0.12,0.30,1.70,0.06,nexp=6)
    soft_block('glass',3.7,148.0,0.32,0.03,0.40,1.62,0.05,nexp=6)
    soft_block('leaf',3.7,147.8,0.26,0.04,0.55,1.25,0.05,nexp=3)
    sweep('warm',[(3.38,1.64),(4.02,1.64),(4.02,1.655),(3.38,1.655)],147.6,148.1,0.5,caps=False)
# =================== GALLEY ===================
def galley_run(a_part,sgn,tall_mat,sink):
    w=0.65; ac=a_part+sgn*math.degrees((w/2+0.02)/2.95)
    # one continuous curved cabinet run: tall column (corridor end) flowing into base run, broad-radius outer end
    RC=3.29; HA=0.71          # base run r 2.58-4.00
    soft_block('reveal',RC,ac,HA-0.04,0.29,0.0,0.09,0.02,nexp=8)                 # recessed plinth
    soft_block('oak',RC,ac,HA,0.325,0.09,0.90,0.05,nexp=7,bulge=0.035)           # base run, convex fronts
    soft_block('worktop',2.97,ac,1.03,0.34,0.90,0.94,0.018,nexp=7)               # worktop wraps into the column
    soft_block('worktop',RC,ac+sgn*-math.degrees(0.30/3.29),HA,0.035,0.94,1.06,0.015,nexp=8)  # integrated splash upstand at the divider
    soft_block(tall_mat,2.24,ac,0.31,0.33,0.09,2.42,0.12,nexp=4,bulge=0.03,top=False)   # tall column to the ceiling, broad radius
    # door reveals on the run front (tangential face toward the room)
    face=-sgn*0.345
    for u in (-0.36,0.0,0.36): vline('reveal',RC,ac,u,face*0.995,face*1.01,0.14,0.86)
    add('reveal',quad(Lc(RC,ac,-0.62,face*1.01,0.50),Lc(RC,ac,0.62,face*1.01,0.50),Lc(RC,ac,0.62,face*1.01,0.506),Lc(RC,ac,-0.62,face*1.01,0.506)))
    # upper cupboards as a soft-bellied form that sweeps into the ceiling cove; task light underneath
    a_up=a_part+sgn*math.degrees(0.19/2.97)
    if sink: a_up=None
    if a_up is not None: loft('sand',3.30,a_up,[(1.50,0.62,0.12,6,0),(1.55,0.68,0.165,6,0.04),(1.66,0.70,0.175,6,0.04),(2.30,0.70,0.175,6,0.0)],cap_top=False)
    if a_up is not None: loft('warm',3.30,a_up,[(1.485,0.58,0.10,6,0),(1.50,0.58,0.10,6,0)])
    # recessed appliances / controls: dark glass flush panels with cool graphic
    if sink:
        soft_block('glass',2.97,ac,0.30,0.20,0.938,0.942,0.005,nexp=6,du=0.25)
        loft('titanium',2.97,ac,[(0.94,0.025,0.025,2,0),(1.18,0.02,0.02,2,0)],du=0.25,dv=sgn*0.22)
        soft_block('glass',2.97,ac,0.28,0.005,0.30,0.82,0.01,nexp=8,du=-0.35,dv=face*1.012)   # cleaner front
    else:
        soft_block('glass',2.97,ac,0.30,0.24,0.938,0.944,0.01,nexp=8,du=0.25)            # induction field
        soft_block('glass',2.97,ac,0.30,0.005,0.30,0.82,0.01,nexp=8,du=-0.35,dv=face*1.012)   # oven/rehydrator
        soft_block('graphic',2.97,ac,0.10,0.004,0.74,0.76,0.003,nexp=8,du=-0.35,dv=face*1.016)
    soft_block('graphic',2.24,ac,0.08,0.004,1.30,1.32,0.003,nexp=8,dv=-sgn*0.335)   # column status line
def galley():
    galley_run(300,1,'sand',False)
    galley_run(30,-1,'oak',True)
    # island: elliptical/racetrack plan, tapered plinth, off-white top
    loft('reveal',3.05,345,[(0.0,0.18,0.48,2.6,0),(0.10,0.20,0.50,2.6,0)])
    loft('oak',3.05,345,[(0.10,0.22,0.52,2.6,0),(0.50,0.26,0.57,2.6,0),(0.88,0.29,0.59,2.6,0)])
    loft('worktop',3.05,345,[(0.88,0.30,0.61,2.6,0),(0.90,0.315,0.625,2.6,0),(0.925,0.315,0.625,2.6,0),(0.94,0.30,0.61,2.6,0)])
    loft('teal',3.05,345,[(0.86,0.295,0.605,2.6,0),(0.875,0.295,0.605,2.6,0)])   # tether/handhold rail
def build():
    T.clear(); architecture(); wardroom(); galley(); return T
