"""Wayfarer L3 Quarters furniture: organic Japandi x working spacecraft (Claude, 12 Nov 2026; kT approved layout).
ALL bodies. ALL sponsors. 2026-2226.  Reuses the approved L2 language (geom.py helpers).
Frame: source angle a (Y=r cos a, Z=r sin a); world=[X,Z,-Y]; h above L3 floor top X=8.2; ceiling h=2.30 (X=5.9)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'l2_organic_study'))
import math,numpy as np, geom as G
G.X0=8.2
G.MAT['linen']=('#EFE9DD',0)
W,Lc,add,item,quad,sweep,soft_block,loft2,tube,dock,rounded_rect=G.W,G.Lc,G.add,G.item,G.quad,G.sweep,G.soft_block,G.loft2,G.tube,G.dock,G.rounded_rect
HC=2.30; RO=4.07          # room outer wall = inner face of the berth water ring
ROOMS={'CAPT':(0,60),'CA':(60,120),'HG':(120,150),'GUEST':(150,240),'CB':(240,330),'HC':(330,360)}
DOORS={'CAPT':45,'CA':105,'GUEST':195,'CB':285,'HG':135,'HC':345}
BERTHS=[('CAPT',15,1),('CA',75,2),('GUEST',169,2),('GUEST',221,2),('CB',259,2),('CB',311,1)]
WIN=[(15,.66),(75,.66),(79,1.55),(169,.66),(173,1.55),(221,.66),(217,1.55),(259,.66),(263,1.55),(311,.66)]   # source windows (angle, centre h)
def architecture():
    item('CTX')
    for a in np.arange(0,360,3): add('floor',quad(W(1.25,a,0),W(RO,a,0),W(RO,a+3,0),W(1.25,a+3,0))[::-1])
    for a in np.arange(0,360,4): add('core',quad(W(1.25,a,0),W(1.25,a+4,0),W(1.25,a+4,HC),W(1.25,a,HC)))
    for a in np.arange(0,360,3): add('hull',quad(W(1.25,a,HC),W(RO,a,HC),W(RO,a+3,HC),W(1.25,a+3,HC)))
    item('D3_lining')
    # outer lining on the water ring with berth viewport cut-outs (Ø0.5 m per SPEC; WWS-1 0.8 m is a draft position)
    for a in np.arange(0,360,1.5):
        for h0 in np.arange(0,HC,0.10):
            cut=any(abs(((a+0.75-wa+180)%360)-180)*math.pi/180*RO<0.27 and abs(h0+0.05-wh)<0.27 for wa,wh in WIN)
            if not cut: add('hull',quad(W(RO,a,h0),W(RO,a,h0+0.1),W(RO,a+1.5,h0+0.1),W(RO,a+1.5,h0)))
    item('CTX')
    for wa,wh in WIN:   # dark glass + titanium ring (source viewports, shown only)
        loft2('space',RO+0.06,wa,[(wh-0.25,0.005,0.25,2,0,0)]*0+[(wh-0.25,0.01,0.01,2,0,0),(wh-0.25,0.01,0.01,2,0,0)]) if False else None
        n=24; pts=[(0.25*math.cos(2*math.pi*k/n),0.25*math.sin(2*math.pi*k/n)) for k in range(n)]
        c=Lc(RO+0.05,wa,0,0,wh); add('space',[(c,Lc(RO+0.05,wa,0,pts[k][0],wh+pts[k][1]),Lc(RO+0.05,wa,0,pts[(k+1)%n][0],wh+pts[(k+1)%n][1])) for k in range(n)])
        for k in range(n):
            p,q=pts[k],pts[(k+1)%n]
            add('titanium',quad(Lc(RO-0.02,wa,0,p[0],wh+p[1]),Lc(RO-0.02,wa,0,q[0],wh+q[1]),Lc(RO+0.05,wa,0,q[0],wh+q[1]),Lc(RO+0.05,wa,0,p[0],wh+p[1])))
            add('titanium',quad(Lc(RO-0.02,wa,0,p[0]*1.14,wh+p[1]*1.14),Lc(RO-0.02,wa,0,q[0]*1.14,wh+q[1]*1.14),Lc(RO-0.02,wa,0,q[0],wh+q[1]),Lc(RO-0.02,wa,0,p[0],wh+p[1])))
    item('D3_lining')
    cove=[(RO-0.25,HC)]+[(RO-0.25+0.25*math.sin(math.radians(t)),HC-0.25+0.25*math.cos(math.radians(t))) for t in range(0,91,10)]
    for a in np.arange(0,360,2):
        for k in range(len(cove)-1):
            (r0,h0),(r1,h1)=cove[k],cove[k+1]; add('hull',quad(W(r0,a,h0),W(r1,a,h1),W(r1,a+2,h1),W(r0,a+2,h0)))
    for a in np.arange(0,360,7.5):
        d=min(abs(((a+180)%360)-180),abs(((a-180+180)%360)-180)); r_in=2.05 if d<=16 else 1.30
        sweep('reveal',[(r_in,HC-0.002),(RO-0.25,HC-0.002),(RO-0.25,HC-0.006),(r_in,HC-0.006)],a-0.07,a+0.07,0.14,caps=False)
    sweep('reveal',[(RO-0.04,0.0),(RO,0.0),(RO,0.09),(RO-0.04,0.09)],0,360,2,caps=False)
    item('D1_lighting')
    sweep('warm',[(RO-0.27,2.268),(RO-0.24,2.268),(RO-0.24,2.28),(RO-0.27,2.28)],0,360,2,caps=False)
    sweep('warm',[(RO-0.055,0.09),(RO-0.04,0.09),(RO-0.04,0.10),(RO-0.055,0.10)],0,360,2,caps=False)
    item('D2_overhead_rail')
    sweep('oak',[(1.62,1.98),(1.67,1.98),(1.67,2.03),(1.62,2.03)],14,166,2); sweep('oak',[(1.62,1.98),(1.67,1.98),(1.67,2.03),(1.62,2.03)],194,346,2)
def walls():
    # inner partition r 1.88-1.92 (sandwich, source) with 0.80 x 2.05 sliding doors; radial cabin walls
    item('P0_partitions')
    for rid,(a0,a1) in ROOMS.items():
        dc=DOORS[rid]; dh=math.degrees(0.40/1.90)
        for s0,s1 in ((a0,dc-dh),(dc+dh,a1)):
            sweep('sand',rounded_rect(1.88,1.92,0,HC,0.008,2),s0,s1,1.0)
        sweep('sand',rounded_rect(1.88,1.92,2.05,HC,0.008,2),dc-dh,dc+dh,1.0)
        # sliding door leaf parked closed, oak-look, titanium track, lock/occupied indicator, recessed pull
        sweep('oak',rounded_rect(1.875,1.885,0.01,2.04,0.004,2),dc-dh+0.3,dc+dh-0.3,0.8)
        sweep('titanium',[(1.86,2.05),(1.875,2.05),(1.875,2.08),(1.86,2.08)],dc-dh-4,dc+dh+4,1.0)
        sweep('ind',[(1.871,1.12),(1.876,1.12),(1.876,1.15),(1.871,1.15)],dc+dh-2.2,dc+dh-1.6,0.6)
        sweep('reveal',[(1.870,0.95),(1.877,0.95),(1.877,1.25),(1.870,1.25)],dc+dh-3.4,dc+dh-3.0,0.4)
    for a in (0,60,120,150,240,330):
        sweep('sand',rounded_rect(1.92,RO,0,HC,0.01,2),a-math.degrees(0.02/3.0),a+math.degrees(0.02/3.0),0.4)
def berth(a,tiers):
    rc,L,Wd=2.975,2.10,0.70
    for t in range(tiers):
        h0=t*1.08
        soft_block('oak',rc,a,L/2,Wd/2,h0+0.0 if t else 0.0,h0+0.14,0.03,nexp=6)                   # frame (source 0.14)
        soft_block('sand',rc,a,L/2-0.03,Wd/2-0.03,h0+0.14,h0+0.26,0.05,nexp=5)                       # mattress (source 0.12)
        soft_block('linen',rc,a,0.20,0.26,h0+0.26,h0+0.33,0.04,nexp=4,du=-L/2+0.25)                 # pillow at the head (inner) end
        for du in (-0.45,0.10,0.65):                                                                   # 5 g restraint straps
            soft_block('teal',rc,a,0.025,Wd/2+0.005,h0+0.255,h0+0.27,0.004,nexp=6,du=du)
        # privacy screen: one long side solid (sand), other side linen screen drawn half open
        soft_block('sand',rc,a,L/2,0.012,h0+0.14,h0+1.06 if (tiers==2 and t==0) else min(h0+1.08,HC-0.02),0.008,nexp=8,dv=-Wd/2-0.012)
        soft_block('linen',rc,a,L/4,0.006,h0+0.30,h0+1.04,0.004,nexp=8,du=L/4-0.02,dv=Wd/2+0.01)
        soft_block('titanium',rc,a,L/2,0.008,h0+1.045,h0+1.06,0.003,nexp=8,dv=Wd/2+0.01)
        # head end: headboard with reading light, vent, personal display
        soft_block('oak',rc,a,0.02,Wd/2,h0+0.14,h0+1.0,0.01,nexp=6,du=-L/2+0.02)
        soft_block('task',rc,a,0.006,0.10,h0+0.82,h0+0.84,0.003,nexp=6,du=-L/2+0.045)
        soft_block('glass',rc,a,0.006,0.13,h0+0.50,h0+0.66,0.006,nexp=8,du=-L/2+0.045,dv=0.12)
        soft_block('vent',rc,a,0.006,0.10,h0+0.40,h0+0.44,0.004,nexp=8,du=-L/2+0.045,dv=-0.15)
        soft_block('ind',rc,a,0.004,0.006,h0+0.70,h0+0.712,0.002,nexp=2,du=-L/2+0.046,dv=-0.25)
    if tiers==2:  # upper canopy and access rungs at the head end
        soft_block('oak',rc,a,L/2,Wd/2,2.16,2.20,0.02,nexp=6)
        for hh in (0.45,0.80,1.15,1.50): tube('oak',rc,a,[(-L/2+0.12,Wd/2+0.03,hh),(-L/2+0.30,Wd/2+0.03,hh)],0.016,samples=3)
    else:
        soft_block('oak',rc,a,L/2,Wd/2,1.08,1.12,0.02,nexp=6)
        soft_block('task',rc,a,0.4,0.02,1.065,1.075,0.003,nexp=6)
def wallrun(a_wall,sgn,r0,r1,w=0.55,h1=2.20):
    rc=(r0+r1)/2; ac=a_wall+sgn*math.degrees((w/2+0.03)/rc); A=(r1-r0)/2
    soft_block('reveal',rc,ac,A-0.03,w/2-0.03,0,0.09,0.02,nexp=8)
    soft_block('oak',rc,ac,A,w/2,0.09,h1,0.05,nexp=7,bulge=0.03)
    face=-sgn*(w/2)
    n=max(1,int(round(2*A/0.6)))
    for k in range(1,n): G.panel_line('reveal',rc,ac,-A+k*2*A/n,-A+k*2*A/n+0.006,face*1.01,0.14,h1-0.06) if False else G.vline('reveal',rc,ac,-A+k*2*A/n,face*0.99,face*1.012,0.14,h1-0.06)
    for k in range(n):
        uu=-A+(k+0.5)*2*A/n
        soft_block('ind',rc,ac,0.002,0.006,1.10,1.112,0.001,nexp=2,du=uu,dv=face*1.02)
        soft_block('vent',rc,ac,0.12,0.003,0.15,0.19,0.002,nexp=8,du=uu,dv=face*1.012)
def seat(rc,ac):
    dock(rc,ac,0.15,0.15)
    st=[(0.006+t*0.38,0.085+0.035*t**2+0.04*t**6,(0.085+0.035*t**2+0.04*t**6)*0.92,2.2,-0.035*math.sin(math.pi*t)*(1-t*0.3),0) for t in np.linspace(0,1,9)]
    loft2('oak',rc,ac,st,cap_top=False)
    loft2('sage',rc,ac,[(0.386,0.16,0.147,2.2,0,0),(0.425,0.198,0.188,2.2,0,0),(0.458,0.186,0.176,2.2,0,0),(0.455,0.11,0.10,2.2,0,0),(0.447,0.0,0.0,2.2,0,0)],cap_top=False)
    loft2('teal',rc,ac,[(0.10,0.0935,0.086,2.2,-0.012,0),(0.115,0.0945,0.087,2.2,-0.013,0)],cap_top=False,cap_bot=False)
def desk(rc,ac,w,d=0.50,h=0.74):
    soft_block('oak',rc,ac,d/2,w/2,h-0.035,h,0.012,nexp=7)
    soft_block('titanium',rc,ac,0.04,w/2-0.06,h-0.20,h-0.035,0.01,nexp=6,du=d/2-0.05)       # wall bracket (folds)
    soft_block('task',rc,ac,0.02,w/2-0.1,h-0.045,h-0.038,0.003,nexp=6,du=d/2-0.08)
def washroom(a0,a1,ad):
    a=(a0+a1)/2
    rc=3.75; dock(rc,a,0.24,0.20)
    loft2('worktop',rc,a,[(0.006,0.17,0.15,2.4,0.02,0),(0.25,0.22,0.18,2.4,0,0),(0.40,0.27,0.21,2.4,-0.01,0),(0.42,0.26,0.20,2.4,-0.01,0)])
    loft2('sand',rc,a,[(0.42,0.25,0.19,2.4,-0.01,0),(0.445,0.24,0.18,2.4,-0.01,0)])
    soft_block('sand',rc,a,0.06,0.24,0.42,0.95,0.04,nexp=4,du=0.22)
    for sv in (-1,1): tube('teal',rc,a,[(0.10,sv*0.24,0.55),(0.0,sv*0.27,0.62),(-0.12,sv*0.24,0.55)],0.014)
    rc=2.95
    soft_block('reveal',rc,a,0.45,0.45,0.0,0.03,0.012,nexp=5)
    for k in range(9): soft_block('oak',rc,a,0.40,0.04,0.03,0.055,0.008,nexp=6,dv=-0.38+k*0.095)
    for sv in (-1,1): soft_block('sand',rc,a,0.455,0.025,0.03,2.22,0.02,nexp=6,dv=sv*0.445)
    soft_block('sand',rc,a,0.025,0.45,0.03,2.22,0.02,nexp=6,du=0.445)
    loft2('titanium',rc,a,[(2.05,0.06,0.06,2,0.28,0),(2.08,0.08,0.08,2,0.28,0)])
    soft_block('teal',rc,a,0.01,0.04,1.15,1.30,0.01,nexp=4,du=0.41,dv=0.25)
    rc=2.2
    soft_block('reveal',rc,a,0.17,0.27,0.0,0.10,0.03,nexp=5); soft_block('oak',rc,a,0.20,0.30,0.10,0.80,0.05,nexp=5,bulge=0.04)
    soft_block('worktop',rc,a,0.215,0.31,0.80,0.84,0.02,nexp=5); loft2('glass',rc,a,[(0.842,0.11,0.15,2.2,0.02,0),(0.845,0.11,0.15,2.2,0.02,0)])
    loft2('titanium',rc,a,[(0.84,0.015,0.015,2,0.18,0),(1.0,0.012,0.012,2,0.18,0)])
def furniture():
    for rid,a,t in BERTHS: item(f'B_{rid}_{a}'); berth(a,t)
    item('C1_captain_wardrobe'); wallrun(60,-1,2.55,3.95)
    item('C2_captain_desk'); desk(3.72,37,1.15,0.55); soft_block('glass',RO-0.03,37,0.004,0.32,1.05,1.30,0.01,nexp=8); seat(3.12,37)
    item('C3_captain_visitor_seat'); seat(2.6,30)
    item('A1_crewA_lockers'); wallrun(120,-1,2.55,3.95)
    item('A2_crewA_desk'); desk(3.75,97,1.0); seat(3.2,97)
    item('G1_guest_lockers'); wallrun(150,1,2.6,3.95); wallrun(240,-1,2.6,3.95)
    item('G2_guest_table'); 
    soft_block('reveal',3.6,195,0.16,0.40,0.0,0.10,0.02,nexp=3); loft2('oak_dk',3.6,195,[(0.10,0.10,0.34,2.6,0,0),(0.40,0.07,0.30,2.6,0,0),(0.68,0.12,0.40,2.6,0,0)])
    loft2('oak',3.6,195,[(0.68,0.27,0.52,2.4,0,0),(0.70,0.30,0.55,2.4,0,0),(0.735,0.30,0.55,2.4,0,0),(0.745,0.29,0.54,2.4,0,0)])
    for k in (-1,1): seat(3.0,195+k*8)
    item('B1_crewB_lockers'); wallrun(240,1,2.6,3.95); wallrun(330,-1,3.4,4.0)
    item('B2_crewB_desk'); desk(3.75,287,1.0); seat(3.2,287)
    item('H1_guest_washroom'); washroom(120,150,135)
    item('H2_crew_washroom'); washroom(330,360,345)
def build():
    G.T.clear(); architecture(); walls(); furniture(); return G.T
def by_material():
    M={}
    for (it,m),t in G.T.items(): M.setdefault(m,[]).extend(t)
    return M
