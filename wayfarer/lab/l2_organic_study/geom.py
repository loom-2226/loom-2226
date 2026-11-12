"""L2 Organic Japandi design study geometry (Claude, 12 Nov 2026). PROPOSE ONLY.
ALL bodies. ALL sponsors. 2026-2226.
Frame: source angle a (Y=r cos a, Z=r sin a); glTF/world = [X, Z, -Y]; h above L2 floor top X=5.6; ceiling h=2.30."""
import math,numpy as np
X0=5.6; HC=2.30; RW=4.15
MAT={ # name: (hex, emissive)
 'hull':('#8E9FA8',0),'hull_dk':('#6F818B',0),'titanium':('#B8B4AC',0),'oak':('#CDB28F',0),'oak_dk':('#B39470',0),'sand':('#E6DCC8',0),
 'sage':('#9AA58F',0),'worktop':('#EEE9DF',0),'glass':('#1C2530',0),'graphic':('#5FA8D3',1),'warm':('#FFE2B0',1),'floor':('#9C958A',0),
 'reveal':('#3A3F44',0),'teal':('#3FA79A',0),'leaf':('#6E8B5E',0),'paper':('#F1ECE0',0),'belt':('#1E2124',0),'task':('#F4F1EA',1),'ind':('#4FD1A5',1),'vent':('#262B2F',0),'rib':('#97A8B1',0),'space':('#0B1018',0),'core':('#58646D',0)}
T={}  # (item, material) -> list of triangles (3x3)
CUR=['ARCH']
def item(n): CUR[0]=n
def add(m,tris): T.setdefault((CUR[0],m),[]).extend(tris)
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
def ring(A,B,nexp=4,bulge=0.0,N=None):
    if N is None: N=int(min(48,max(8,round(2*math.pi*max(A,B,1e-3)/0.035/4)*4)))
    pts=[]
    for k in range(N):
        t=2*math.pi*k/N; c,s=math.cos(t),math.sin(t)
        u=A*math.copysign(abs(c)**(2/nexp),c); v=B*math.copysign(abs(s)**(2/nexp),s)
        v*= 1+bulge*max(0,1-(u/A)**2) if A>0 else 1
        pts.append((u,v))
    return pts
def loft(m,rc,ac,rings,du=0,dv=0,cap_top=True,cap_bot=True):
    """rings: list of (h, A, B, nexp, bulge)"""
    N=int(min(48,max(8,round(2*math.pi*max(max(r[1],r[2]) for r in rings)/0.035/4)*4)))
    R=[[(u+du,v+dv) for u,v in ring(A,B,n,b,N)] for (h,A,B,n,b) in rings]; H=[r[0] for r in rings]; out=[]
    for i in range(len(R)-1):
        for k in range(len(R[i])):
            k2=(k+1)%len(R[i])
            out+=quad(Lc(rc,ac,*R[i][k],H[i]),Lc(rc,ac,*R[i][k2],H[i]),Lc(rc,ac,*R[i+1][k2],H[i+1]),Lc(rc,ac,*R[i+1][k],H[i+1]))
    for flag,i in ((cap_bot,0),(cap_top,len(R)-1)):
        if flag:
            c=Lc(rc,ac,du,dv,H[i])
            for k in range(len(R[i])): out.append((c,Lc(rc,ac,*R[i][k],H[i]),Lc(rc,ac,*R[i][(k+1)%len(R[i])],H[i])))
    add(m,out)
def loft2(m,rc,ac,rings,cap_top=True,cap_bot=True,N=None):
    if N is None: N=int(min(48,max(8,round(2*math.pi*max(max(r[1],r[2]) for r in rings)/0.035/4)*4)))
    """rings: (h, A, B, nexp, du, dv)"""
    R=[[(u+du,v+dv) for u,v in ring(A,B,n,0,N)] for (h,A,B,n,du,dv) in rings]; H=[r[0] for r in rings]; out=[]
    for i in range(len(R)-1):
        for k in range(N):
            k2=(k+1)%N; out+=quad(Lc(rc,ac,*R[i][k],H[i]),Lc(rc,ac,*R[i][k2],H[i]),Lc(rc,ac,*R[i+1][k2],H[i+1]),Lc(rc,ac,*R[i+1][k],H[i+1]))
    for flag,i in ((cap_bot,0),(cap_top,len(R)-1)):
        if flag:
            c=Lc(rc,ac,rings[i][4],rings[i][5],H[i]); out+=[(c,Lc(rc,ac,*R[i][k],H[i]),Lc(rc,ac,*R[i][(k+1)%N],H[i])) for k in range(N)]
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
BAND={'galley':(300,390,0.05,2.25),'wardroom':(30,150,1.10,1.70),'observation':(150,210,0.40,2.00),'exercise':(210,270,0.05,2.25)}
def architecture():
    item('CTX')
    # floor with radial seams
    for a in np.arange(0,360,3): add('floor',quad(W(1.25,a,0),W(RW,a,0),W(RW,a+3,0),W(1.25,a+3,0))[::-1])
    # core trunk and racks
    for a in np.arange(0,360,4):
        add('core',quad(W(1.25,a,0),W(1.25,a+4,0),W(1.25,a+4,HC),W(1.25,a,HC)))
    # ceiling (L1 floor underside) with ceiling sweep cove into the wall (large-curvature transition)
    for a in np.arange(0,360,3): add('hull',quad(W(1.25,a,HC),W(3.85,a,HC),W(3.85,a+3,HC),W(1.25,a+3,HC)))
    item('D3_lining')
    item('D3_lining')
    cove=[(3.85,HC)]+[(3.85+0.3*math.sin(math.radians(t)),HC-0.3+0.3*math.cos(math.radians(t))) for t in range(0,91,10)]
    for a in np.arange(0,360,2):
        for k in range(len(cove)-1):
            (r0,h0),(r1,h1)=cove[k],cove[k+1]; add('hull',quad(W(r0,a,h0),W(r1,a,h1),W(r1,a+2,h1),W(r0,a+2,h0)))
    def r_in(a):   # keep ceiling details out of the two ladderway openings / L1-L2 hatch leaves (0 and 180 deg)
        d=min(abs(((a-0+180)%360)-180),abs(((a-180+180)%360)-180)); return 2.05 if d<=16 else 1.30
    for a in np.arange(0,360,7.5):
        sweep('reveal',[(r_in(a),HC-0.002),(3.85,HC-0.002),(3.85,HC-0.006),(r_in(a),HC-0.006)],a-0.07,a+0.07,0.14,caps=False)
    sweep('reveal',[(2.55,HC-0.002),(2.60,HC-0.002),(2.60,HC-0.006),(2.55,HC-0.006)],0,360,2,caps=False)
    # continuous warm light reveal at the cove root and a titanium trim line
    item('D1_lighting'); sweep('warm',[(3.83,2.268),(3.86,2.268),(3.86,2.28),(3.83,2.28)],0,360,2,caps=False)
    item('D3_lining')
    sweep('titanium',[(4.11,1.995),(4.15,1.995),(4.15,2.005),(4.11,2.005)],0,360,2,caps=False)
    # outer wall: lining panels with reveals; band as dark glass between titanium edge rings
    for a in np.arange(-60,300,1.5):
        aa=a%360; inband=None
        for k,(b0,b1,g0,g1) in BAND.items():
            if b0<=a<b1 or b0<=a+360<b1: inband=(g0,g1)
        segs=[(0,2.0)] if not inband else [(0,inband[0]),(inband[1],2.0)]
        for s0,s1 in segs:
            if s1-s0>0.01: item('D3_lining'); add('hull',quad(W(RW,a,s0),W(RW,a,s1),W(RW,a+1.5,s1),W(RW,a+1.5,s0)))
        if inband:
            item('CTX'); add('space',quad(W(RW+0.10,a,inband[0]),W(RW+0.10,a,inband[1]),W(RW+0.10,a+1.5,inband[1]),W(RW+0.10,a+1.5,inband[0])))
    item('CTX')
    for k,(b0,b1,g0,g1) in BAND.items():
        for g in (g0,g1):
            sweep('titanium',[(4.09,g-0.03),(4.16,g-0.03),(4.16,g+0.03),(4.09,g+0.03)],b0,b1,1.5,caps=False)
        for a in np.arange(b0,b1+0.01,(b1-b0)/round((b1-b0)/15)):   # Osteon mullions ~15 deg
            sweep('titanium',[(4.10,g0),(4.16,g0),(4.16,g1),(4.10,g1)],a-0.35,a+0.35,0.7)
    # flush access panels on the lining below the wardroom band (behind/above the banquette) and on dividers (see furniture fns)
    for a0 in np.arange(45,135,15):
        for (h0,h1) in ((1.75,1.84),):
            pass
    item('D3_lining')
    # vertical lining reveals every 7.5 deg where there is lining
    for a in np.arange(0,360,7.5):
        inb=any(b0<=a<b1 or b0<=a+360<b1 for (b0,b1,g0,g1) in BAND.values())
        if not inb: sweep('reveal',[(4.135,0.12),(4.15,0.12),(4.15,1.97),(4.135,1.97)],a-0.08,a+0.08,0.16,caps=False)
    # skirting reveal with floor-wash warm light
    sweep('reveal',[(4.10,0.0),(4.15,0.0),(4.15,0.10),(4.10,0.10)],0,360,2,caps=False)
    item('D1_lighting'); sweep('warm',[(4.095,0.10),(4.11,0.10),(4.11,0.11),(4.095,0.11)],0,360,2,caps=False)
    item('D3_lining')
    def lined(a,h):
        for (b0,b1,g0,g1) in list(BAND.values())+[(150,210,0.40,2.00),(210,270,0.05,2.25)]:
            if (b0<=a<b1 or b0<=a+360<b1) and g0<=h<=g1: return False
        return True
    # structural ribs: shallow pilasters continuing each 15 deg mullion line up the lining and across the ceiling
    for a in np.arange(0,360,15):
        if lined(a,1.9): sweep('rib',[(4.125,1.72),(4.15,1.72),(4.15,2.0),(4.125,2.0)],a-0.3,a+0.3,0.6)
        add('rib',[])
        for k in range(len(cove)-1):
            (r0,h0),(r1,h1)=cove[k],cove[k+1]
            add('rib',quad(W(r0-0.012,a-0.3,h0-0.008),W(r1-0.012,a-0.3,h1-0.008),W(r1-0.012,a+0.3,h1-0.008),W(r0-0.012,a+0.3,h0-0.008)))
        sweep('rib',[(r_in(a),HC-0.002),(3.85,HC-0.002),(3.85,HC-0.014),(r_in(a),HC-0.014)],a-0.25,a+0.25,0.5)
    # full-circle sill/head edge rings at 1.10 and 1.70 m (source: edge_rings full_circle); they cross the tall galley glass as transoms
    item('CTX')
    for g in (1.10,1.70):
        sweep('titanium',[(4.10,g-0.035),(4.16,g-0.035),(4.16,g+0.035),(4.10,g+0.035)],210,510,1.5,caps=False)   # skips the lounge
    sweep('titanium',[(4.10,1.18),(4.16,1.18),(4.16,1.22),(4.10,1.22)],150,210,1.5,caps=False)              # lounge mid transom
    item('D3_lining')
    # linear supply diffuser just below the cove, and a slotted return ring in the ceiling
    for a in np.arange(0,360,0.6):
        if lined(a,1.87): sweep('vent',[(4.120,1.862),(4.128,1.862),(4.128,1.878),(4.120,1.878)],a,a+0.3,0.3,caps=False)
    for a in np.arange(0,360,0.9):
        sweep('vent',[(2.555,HC-0.003),(2.595,HC-0.003),(2.595,HC-0.007),(2.555,HC-0.007)],a,a+0.5,0.5,caps=False)
    # room divider walls (galley/wardroom shared wall at 30 is open; washroom wall at 300)
    sweep('hull',rounded_rect(1.92,4.15,0,HC,0.02),299.2,300.4,0.6)
    item('D2_overhead_rail')
    # overhead handrail (oak)
    sweep('oak',[(1.62,1.98),(1.67,1.98),(1.67,2.03),(1.62,2.03)],14,166,2,caps=True); sweep('oak',[(1.62,1.98),(1.67,1.98),(1.67,2.03),(1.62,2.03)],194,346,2,caps=True)
# =================== WARDROOM ===================
def wardroom():
    item('W1_table')
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
    item('W2_banquette')
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
    item('W3_stools')
    # stools (pass 2): flush floor dock with positive-lock indicator, curved asymmetric stem leaning out of the dock,
    # oak shell flaring into a concave sage seat
    for k in range(5):
        a=90+(k-2)*13
        loft2('titanium',2.25,a,[(0.0,0.15,0.15,2,0,0),(0.006,0.15,0.15,2,0,0),(0.006,0.125,0.125,2,0,0),(0.0,0.125,0.125,2,0,0)])   # flush dock plate
        loft2('ind',2.25,a,[(0.0065,0.012,0.012,2,-0.135,0),(0.0075,0.012,0.012,2,-0.135,0)])   # lock indicator
        st=[]
        for j,t in enumerate(np.linspace(0,1,11)):
            h=0.006+t*0.38; rad=0.085+0.035*t**2+0.04*t**6; du=-0.035*math.sin(math.pi*t)*(1-t*0.3)
            st.append((h,rad,rad*0.92,2.2,du,0))
        loft2('oak',2.25,a,st,cap_top=False)
        loft2('oak',2.25,a,[(0.386,0.16,0.147,2.2,0,0),(0.41,0.19,0.18,2.2,0,0),(0.425,0.198,0.188,2.2,0,0)],cap_bot=False,cap_top=False)
        loft2('sage',2.25,a,[(0.425,0.198,0.188,2.2,0,0),(0.445,0.196,0.186,2.2,0,0),(0.458,0.186,0.176,2.2,0,0),(0.462,0.16,0.15,2.2,0,0),
                             (0.455,0.11,0.10,2.2,0,0),(0.449,0.05,0.045,2.2,0,0),(0.447,0.0,0.0,2.2,0,0)],cap_top=False,cap_bot=False)
        loft2('teal',2.25,a,[(0.10,0.0935,0.086,2.2,-0.012,0),(0.115,0.0945,0.087,2.2,-0.013,0)],cap_top=False,cap_bot=False)   # latch collar
    item('W4_serving_pass')
    # serving pass: radiused plan, convex door face, off-white top with upstand
    soft_block('oak',3.3,38.5,0.70,0.225,0.05,0.93,0.04,nexp=6,bulge=0.06)
    soft_block('worktop',3.3,38.5,0.71,0.235,0.93,0.965,0.015,nexp=6)
    for u in (-0.23,0.23): vline('reveal',3.3,38.5,u,0.20*1.0,0.24,0.08,0.9)
    item('W5_briefing_screen')
    # briefing screen stowed in a ceiling recess (dark glass, cool graphic line)
    soft_block('glass',3.25,146,0.65,0.03,2.13,2.27,0.01,nexp=8)
    item('W6_living_niche')
    wall_details(150,-1,2.30,1.15)
    item('D1_lighting')
    # task light line in the ceiling over the table
    loft2('task',3.0,90,[(HC-0.004,0.30,1.20,2.2,0,0),(HC-0.009,0.30,1.20,2.2,0,0)],cap_top=False)
    loft2('hull',3.0,90,[(HC-0.0045,0.28,1.18,2.2,0,0),(HC-0.0095,0.28,1.18,2.2,0,0)],cap_top=False)
    item('W6_living_niche')
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
    soft_block(tall_mat,2.24,ac,0.31,0.33,0.09,2.295,0.02,nexp=4,bulge=0.03,top=False)   # tall column to the ceiling, broad radius
    # door reveals on the run front (tangential face toward the room)
    face=sgn*0.345
    for u in (-0.36,0.0,0.36): vline('reveal',RC,ac,u,face*0.995,face*1.01,0.14,0.86)
    for u in (-0.54,-0.18,0.18,0.54):
        for hh in (0.46,0.84): soft_block('ind',RC,ac,0.006,0.002,hh-0.006,hh+0.006,0.001,nexp=2,du=u,dv=face*1.018)
    add('reveal',quad(Lc(RC,ac,-0.62,face*1.01,0.50),Lc(RC,ac,0.62,face*1.01,0.50),Lc(RC,ac,0.62,face*1.01,0.506),Lc(RC,ac,-0.62,face*1.01,0.506)))
    # upper cupboards as a soft-bellied form that sweeps into the ceiling cove; task light underneath
    a_up=a_part+sgn*math.degrees(0.19/2.97)
    if sink: a_up=None
    if a_up is not None: loft('sand',3.30,a_up,[(1.50,0.62,0.12,6,0),(1.55,0.68,0.165,6,0.04),(1.66,0.70,0.175,6,0.04),(2.30,0.70,0.175,6,0.0)],cap_top=False)
    if a_up is not None: loft('task',3.30,a_up,[(1.485,0.58,0.10,6,0),(1.50,0.58,0.10,6,0)])
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
def wall_details(a_wall,sgn,r_ctrl,h_ctrl):
    # recessed control panel (dark glass, cool line) + flush access panel outline + low vent grille on a divider wall
    off=sgn*0.016
    ac=a_wall+sgn*math.degrees(0.02/3.0)
    soft_block('glass',r_ctrl,a_wall+sgn*math.degrees(0.018/r_ctrl),0.07,0.004,h_ctrl,h_ctrl+0.18,0.008,nexp=8)
    soft_block('graphic',r_ctrl,a_wall+sgn*math.degrees(0.0225/r_ctrl),0.05,0.0015,h_ctrl+0.13,h_ctrl+0.14,0.002,nexp=8)
    soft_block('ind',r_ctrl,a_wall+sgn*math.degrees(0.0225/r_ctrl),0.006,0.0015,h_ctrl+0.03,h_ctrl+0.045,0.002,nexp=2,du=0.04)
    for (u0,u1,h0,h1) in ((2.45,3.15,0.30,1.25),):
        for (a,b,c,d) in ((u0,u1,h0,h0+0.004),(u0,u1,h1-0.004,h1),(u0,u0+0.004,h0,h1),(u1-0.004,u1,h0,h1)):
            soft_block('reveal',(a+b)/2,a_wall+sgn*math.degrees(0.0115/((a+b)/2)),(b-a)/2,0.0015,c,d,0.0005,nexp=8)
    for k in range(9):
        soft_block('vent',3.55+k*0.05,a_wall+sgn*math.degrees(0.0115/3.75),0.012,0.0015,0.14,0.30,0.004,nexp=8)
def galley():
    item('G0_wall_details'); wall_details(300,-1,2.35,1.15)
    item('G1_cook_run'); galley_run(300,1,'sand',False)
    item('G2_water_run'); galley_run(30,-1,'oak',True)
    item('G3_prep_island')
    # island: elliptical/racetrack plan, tapered plinth, off-white top
    loft2('reveal',3.05,345,[(0.0,0.17,0.43,2.8,0,0),(0.13,0.17,0.43,2.8,0,0)])                      # deep recessed plinth
    loft2('warm',3.05,345,[(0.004,0.172,0.432,2.8,0,0),(0.012,0.172,0.432,2.8,0,0)],cap_top=False)    # toe-kick wash
    body=[(0.13,0.235,0.505,2.8,0,0),(0.135,0.245,0.515,2.8,0,0),(0.15,0.25,0.52,2.8,0,0)]
    body+=[(0.15+t*0.69,0.25+0.035*t,0.52+0.04*t,2.8,0,0) for t in np.linspace(0.05,1,8)]
    body+=[(0.855,0.288,0.562,2.8,0,0),(0.862,0.282,0.556,2.8,0,0)]
    loft2('oak',3.05,345,body)
    loft2('reveal',3.05,345,[(0.862,0.27,0.54,2.8,0,0),(0.878,0.27,0.54,2.8,0,0)])                  # shadow gap
    loft2('worktop',3.05,345,[(0.878,0.30,0.605,2.8,0,0),(0.885,0.31,0.615,2.8,0,0),(0.905,0.315,0.62,2.8,0,0),(0.918,0.31,0.615,2.8,0,0),(0.922,0.30,0.605,2.8,0,0)])
    # flush drawers: two horizontal reveals + centre seam on the long faces, positive-latch indicators
    for hh in (0.36,0.61):
        A=0.25+0.035*(hh-0.15)/0.69+0.001; B=0.52+0.04*(hh-0.15)/0.69+0.001
        loft2('reveal',3.05,345,[(hh,A,B,2.8,0,0),(hh+0.005,A,B,2.8,0,0)],cap_top=False,cap_bot=False)
    for su in (1,-1):
        panel_line('reveal',3.05,345,su*0.262,su*0.300,0.0,0.16,0.85)
        for vv in (-0.16,0.16):
            for hh in (0.33,0.58,0.82):
                A=0.25+0.035*(hh-0.15)/0.69
                soft_block('ind',3.05,345,0.002,0.006,hh-0.006,hh+0.006,0.001,nexp=2,du=su*(A+0.003),dv=vv)
    # handhold bars at the island ends (teal, positive grip)
    for sv in (1,-1): soft_block('teal',3.05,345,0.10,0.012,0.80,0.83,0.008,nexp=4,dv=sv*0.60)
# =================== helpers for the remaining rooms ===================
def extrude_uh(m,rc,ac,top,t,b,dv=0.0,taper=None):
    """extrude a (u,h) top curve with thickness t across v in [-b,b]; taper(u)->half-width scale"""
    bot=[(u,h-t) for u,h in top]; poly=top+bot[::-1]; out=[]
    def hw(u): return b*(taper(u) if taper else 1.0)
    for k in range(len(poly)):
        (u0,h0),(u1,h1)=poly[k],poly[(k+1)%len(poly)]
        out+=quad(Lc(rc,ac,u0,dv-hw(u0),h0),Lc(rc,ac,u1,dv-hw(u1),h1),Lc(rc,ac,u1,dv+hw(u1),h1),Lc(rc,ac,u0,dv+hw(u0),h0))
    for sgn in (-1,1):
        for k in range(len(top)-1):
            (ua,ha),(ub,hb)=top[k],top[k+1]; (uc,hc),(ud,hd)=bot[k+1],bot[k]
            out+=quad(Lc(rc,ac,ua,dv+sgn*hw(ua),ha),Lc(rc,ac,ub,dv+sgn*hw(ub),hb),Lc(rc,ac,uc,dv+sgn*hw(uc),hc),Lc(rc,ac,ud,dv+sgn*hw(ud),hd))
    add(m,out)
def tube(m,rc,ac,pts,rad,n=10,samples=8):
    """smooth tube through local (u,v,h) control points (Catmull-Rom)"""
    P=np.array(pts,float); C=[]
    for i in range(len(P)-1):
        p0=P[max(i-1,0)];p1=P[i];p2=P[i+1];p3=P[min(i+2,len(P)-1)]
        for t in np.linspace(0,1,samples,endpoint=(i==len(P)-2)):
            C.append(0.5*((2*p1)+(-p0+p2)*t+(2*p0-5*p1+4*p2-p3)*t*t+(-p0+3*p1-3*p2+p3)*t**3))
    Wp=np.array([Lc(rc,ac,*c) for c in C]); rings=[]
    for i in range(len(Wp)):
        tg=Wp[min(i+1,len(Wp)-1)]-Wp[max(i-1,0)]; tg/=np.linalg.norm(tg)+1e-12
        ref=np.array([1.0,0,0]) if abs(tg[0])<0.9 else np.array([0,1.0,0])
        a=np.cross(tg,ref); a/=np.linalg.norm(a); bb=np.cross(tg,a)
        rings.append([Wp[i]+rad*(math.cos(2*math.pi*k/n)*a+math.sin(2*math.pi*k/n)*bb) for k in range(n)])
    out=[]
    for i in range(len(rings)-1):
        for k in range(n): out+=quad(tuple(rings[i][k]),tuple(rings[i][(k+1)%n]),tuple(rings[i+1][(k+1)%n]),tuple(rings[i+1][k]))
    add(m,out)
def dock(rc,ac,A,B,du=0,dv=0):
    loft2('titanium',rc,ac,[(0.0,A,B,3,du,dv),(0.006,A,B,3,du,dv)])
    loft2('ind',rc,ac,[(0.0065,0.011,0.011,2,du-A+0.02,dv),(0.0075,0.011,0.011,2,du-A+0.02,dv)])
def shoji2(a,r0,r1,h0=0.0,h1=2.25):
    rc=(r0+r1)/2; A=(r1-r0)/2
    soft_block('paper',rc,a,A-0.02,0.006,h0+0.04,h1-0.04,0.004,nexp=10)
    soft_block('oak',rc,a,A,0.022,h0,h0+0.05,0.012,nexp=10); soft_block('oak',rc,a,A,0.022,h1-0.05,h1,0.012,nexp=10)
    for u in np.linspace(-A+0.02,A-0.02,int(2*A/0.5)+2): soft_block('oak',rc,a,0.017,0.018,h0,h1,0.008,nexp=6,du=u)
    for hh in np.arange(h0+0.45,h1-0.2,0.45): soft_block('oak',rc,a,A,0.014,hh,hh+0.022,0.006,nexp=10)
    soft_block('vent',rc,a,A-0.04,0.008,h0+0.06,h0+0.12,0.004,nexp=10)   # transfer-air slot at the foot
# =================== OBSERVATION ===================
def observation():
    item('O1_loungers')
    top=[(-0.86,0.74),(-0.80,0.70),(-0.68,0.60),(-0.52,0.47),(-0.36,0.37),(-0.18,0.31),(0.0,0.30),(0.18,0.33),(0.34,0.36),(0.50,0.34),(0.66,0.29),(0.80,0.25),(0.86,0.24)]
    for a in (162,180,198):
        extrude_uh('oak',3.25,a,[(u,h-0.055) for u,h in top],0.05,0.33,taper=lambda u: 0.9+0.1*math.cos(u*1.6))
        extrude_uh('sand',3.25,a,[(u*0.97,h) for u,h in top],0.055,0.29,taper=lambda u: 0.9+0.1*math.cos(u*1.6))
        loft2('oak_dk',3.25,a,[(0.006,0.22,0.15,2.6,-0.05,0),(0.12,0.20,0.13,2.6,-0.04,0),(0.24,0.27,0.19,2.6,-0.03,0)])
        dock(3.25,a,0.26,0.19,du=-0.05)
        tube('teal',3.25,a,[(-0.02,-0.31,0.27),(0.0,-0.33,0.24),(0.02,-0.31,0.21)],0.012)   # lap-belt anchors
        tube('teal',3.25,a,[(-0.02,0.31,0.27),(0.0,0.33,0.24),(0.02,0.31,0.21)],0.012)
    item('O2_telescope')
    dock(3.84,207,0.12,0.12)
    loft2('titanium',3.84,207,[(0.006,0.08,0.08,2,0,0),(0.4,0.045,0.045,2,0,0),(1.15,0.035,0.035,2,0,0),(1.2,0.05,0.05,2,0,0)])
    loft2('sand',3.84,207,[(1.2,0.17,0.09,2.4,0.03,0),(1.26,0.20,0.11,2.4,0.03,0),(1.36,0.20,0.11,2.4,0.03,0),(1.42,0.17,0.09,2.4,0.03,0)])
    soft_block('glass',3.84,207,0.02,0.06,1.27,1.35,0.01,nexp=4,du=0.235)
    soft_block('ind',3.84,207,0.004,0.01,1.385,1.395,0.002,nexp=2,du=-0.12)
# =================== EXERCISE ===================
def exercise():
    item('E1_treadmill'); rc,ac=3.1,223
    dock(rc,ac,0.95,0.40)
    loft2('worktop',rc,ac,[(0.006,0.98,0.40,3.2,0,0),(0.12,1.00,0.42,3.2,0,0),(0.17,0.99,0.41,3.2,0,0),(0.19,0.96,0.38,3.2,0,0)])
    loft2('belt',rc,ac,[(0.19,0.86,0.27,4,0,0),(0.205,0.86,0.27,4,0,0)])
    for sv in (-1,1):
        tube('titanium',rc,ac,[(0.70,sv*0.39,0.17),(0.80,sv*0.40,0.55),(0.84,sv*0.39,0.95),(0.80,sv*0.36,1.08)],0.022)
        tube('oak',rc,ac,[(0.80,sv*0.37,1.0),(0.55,sv*0.39,1.0),(0.25,sv*0.39,0.98)],0.024)
        soft_block('teal',rc,ac,0.03,0.015,0.95,1.0,0.008,nexp=4,du=0.2,dv=sv*0.39)   # harness anchor
    tube('titanium',rc,ac,[(0.80,-0.36,1.08),(0.86,0.0,1.13),(0.80,0.36,1.08)],0.022)
    soft_block('glass',rc,ac,0.06,0.20,1.05,1.20,0.02,nexp=6,du=0.84)
    soft_block('graphic',rc,ac,0.003,0.12,1.15,1.16,0.002,nexp=8,du=0.795)
    item('E2_resistance'); rc,ac=3.15,240
    dock(rc,ac,0.72,0.46)
    loft2('worktop',rc,ac,[(0.006,0.72,0.46,3.5,0,0),(0.06,0.70,0.44,3.5,0,0)])
    for sv in (-1,1):
        loft2('worktop',rc,ac,[(0.06,0.10,0.07,2.4,0.55,sv*0.37),(1.0,0.075,0.055,2.4,0.56,sv*0.37),(1.95,0.065,0.05,2.4,0.55,sv*0.37)],cap_top=False)
        soft_block('teal',rc,ac,0.012,0.02,0.4,1.7,0.006,nexp=4,du=0.48,dv=sv*0.37)  # cable guide
    tube('titanium',rc,ac,[(0.55,-0.37,1.93),(0.58,-0.2,2.04),(0.58,0.2,2.04),(0.55,0.37,1.93)],0.035)
    loft2('titanium',rc,ac,[(0.06,0.05,0.05,2,-0.25,0),(0.40,0.04,0.04,2,-0.25,0)],cap_top=False)
    loft2('sand',rc,ac,[(0.40,0.30,0.16,2.6,-0.25,0),(0.45,0.32,0.18,2.6,-0.25,0),(0.48,0.30,0.16,2.6,-0.25,0)])
    soft_block('glass',rc,ac,0.02,0.09,1.30,1.42,0.01,nexp=6,du=0.48)
    item('E3_cycle'); rc,ac=3.35,258
    dock(rc,ac,0.50,0.25)
    loft2('worktop',rc,ac,[(0.006,0.48,0.22,3,0,0),(0.05,0.46,0.20,3,0,0)])
    tube('titanium',rc,ac,[(-0.35,0,0.05),(-0.30,0,0.35),(-0.22,0,0.72)],0.03)
    tube('titanium',rc,ac,[(0.38,0,0.05),(0.30,0,0.45),(0.33,0,0.85),(0.38,0,1.0)],0.03)
    tube('titanium',rc,ac,[(-0.30,0,0.30),(0.0,0,0.38),(0.30,0,0.45)],0.028)
    soft_block('worktop',rc,ac,0.22,0.07,0.16,0.58,0.06,nexp=2.2,du=0.05)       # flywheel housing
    loft2('sand',rc,ac,[(0.72,0.14,0.08,2.6,-0.22,0),(0.77,0.15,0.09,2.6,-0.22,0),(0.79,0.12,0.07,2.6,-0.22,0)])
    tube('oak',rc,ac,[(0.38,-0.26,1.0),(0.40,0,1.04),(0.38,0.26,1.0)],0.02)
    soft_block('glass',rc,ac,0.05,0.08,1.06,1.14,0.01,nexp=6,du=0.40)
    item('E4_shoji_screen'); shoji2(210.6,1.95,4.1)
# =================== WASHROOM ===================
def washroom():
    item('H0_walls_door')
    shoji2(270.6,1.95,4.1)
    sweep('paper',[(1.966,0.04),(1.974,0.04),(1.974,2.21),(1.966,2.21)],271.3,298.7,1.0)
    sweep('oak',[(1.955,0.0),(1.985,0.0),(1.985,0.05),(1.955,0.05)],271.3,298.7,1.0); sweep('oak',[(1.955,2.20),(1.985,2.20),(1.985,2.25),(1.955,2.25)],271.3,298.7,1.0)
    for a in np.linspace(271.6,298.4,7): sweep('oak',[(1.957,0.0),(1.983,0.0),(1.983,2.25),(1.957,2.25)],a-0.45,a+0.45,0.9)
    for hh in (0.45,0.90,1.35,1.80): sweep('oak',[(1.959,hh),(1.981,hh),(1.981,hh+0.022),(1.959,hh+0.022)],271.3,298.7,1.0)
    sweep('titanium',[(1.94,2.22),(1.955,2.22),(1.955,2.25),(1.94,2.25)],271.3,298.7,1.0)     # sliding-door track
    sweep('ind',[(1.952,1.10),(1.956,1.10),(1.956,1.14),(1.952,1.14)],284.6,285.4,0.4)       # occupied/lock indicator
    sweep('reveal',[(1.950,0.95),(1.958,0.95),(1.958,1.25),(1.950,1.25)],280.0,280.5,0.5)   # recessed pull
    item('H1_toilet'); rc,ac=3.85,285
    dock(rc,ac,0.24,0.20)
    loft2('worktop',rc,ac,[(0.006,0.17,0.15,2.4,0.02,0),(0.25,0.22,0.18,2.4,0,0),(0.40,0.27,0.21,2.4,-0.01,0),(0.42,0.26,0.20,2.4,-0.01,0)])
    loft2('sand',rc,ac,[(0.42,0.25,0.19,2.4,-0.01,0),(0.445,0.24,0.18,2.4,-0.01,0)])
    soft_block('sand',rc,ac,0.06,0.24,0.42,0.95,0.04,nexp=4,du=0.22)
    soft_block('glass',rc,ac,0.004,0.08,0.80,0.88,0.01,nexp=6,du=0.158); soft_block('ind',rc,ac,0.003,0.01,0.86,0.87,0.002,nexp=2,du=0.155,dv=0.05)
    for sv in (-1,1): tube('teal',rc,ac,[(0.10,sv*0.24,0.55),(0.0,sv*0.27,0.62),(-0.12,sv*0.24,0.55)],0.014)   # thigh-restraint grips
    item('H2_shower'); rc,ac=3.05,285
    soft_block('reveal',rc,ac,0.47,0.47,0.0,0.03,0.012,nexp=5)
    for k in range(9): soft_block('oak',rc,ac,0.42,0.04,0.03,0.055,0.008,nexp=6,dv=-0.40+k*0.10)
    for sv in (-1,1): soft_block('sand',rc,ac,0.475,0.025,0.03,2.22,0.02,nexp=6,dv=sv*0.465)
    soft_block('sand',rc,ac,0.025,0.47,0.03,2.22,0.02,nexp=6,du=0.465)
    loft2('titanium',rc,ac,[(2.05,0.06,0.06,2,0.30,0),(2.08,0.08,0.08,2,0.30,0)])
    soft_block('teal',rc,ac,0.01,0.04,1.15,1.30,0.01,nexp=4,du=0.43,dv=0.25)
    soft_block('titanium',rc,ac,0.004,0.36,1.95,1.97,0.004,nexp=6,du=-0.47)    # curtain/door track across the open face
    soft_block('vent',rc,ac,0.30,0.004,0.06,0.12,0.003,nexp=8,du=0.0,dv=0.437)
    item('H3_basin'); rc,ac=2.25,285
    soft_block('reveal',rc,ac,0.19,0.31,0.0,0.10,0.03,nexp=5)
    soft_block('oak',rc,ac,0.22,0.35,0.10,0.80,0.05,nexp=5,bulge=0.04)
    soft_block('worktop',rc,ac,0.235,0.36,0.80,0.84,0.02,nexp=5)
    loft2('glass',rc,ac,[(0.842,0.13,0.17,2.2,0.02,0),(0.845,0.13,0.17,2.2,0.02,0)])
    loft2('titanium',rc,ac,[(0.84,0.015,0.015,2,0.20,0),(1.0,0.012,0.012,2,0.20,0)])
    for hh in (0.45,): panel_line('reveal',rc,ac,-0.225,0.225,-0.36,0.12,0.78)
    soft_block('ind',rc,ac,0.003,0.006,0.70,0.712,0.001,nexp=2,du=-0.223,dv=0.15)
CONTEXT=('floor','core','space')   # visual context only, not exported
def build():
    T.clear(); item('ARCH'); architecture(); wardroom(); galley(); observation(); exercise(); washroom(); return T
def by_material():
    M={}
    for (it,m),t in T.items(): M.setdefault(m,[]).extend(t)
    return M
