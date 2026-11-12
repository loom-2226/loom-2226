"""Wayfarer L5 Mission, EVA and transfer: organic Japandi x working spacecraft (Claude, 12 Nov 2026; kT approved layout).
ALL bodies. ALL sponsors. 2026-2226.  Reuses the approved L2 language (geom.py helpers).
Frame: source angle a (Y=r cos a, Z=r sin a); world=[X,Z,-Y]; h above L5 floor (aft bulkhead fore face X=13.4); ceiling h=2.30 (X=11.1).
Assumes kT decisions l5_decisions_2026_11_12: EVA hatch 1.0 m at 0 deg (centre h 1.1); 1.2 m floor hatch to tunnel_0 at r 3.0, 270 deg."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'l2_organic_study'))
import math,numpy as np, geom as G
G.X0=13.4
G.MAT['linen']=('#EFE9DD',0); G.MAT['vault']=('#4A5A63',0); G.MAT['suit']=('#F2F0EA',0)
W,Lc,add,item,quad,sweep,soft_block,loft2,tube,dock,rounded_rect=G.W,G.Lc,G.add,G.item,G.quad,G.sweep,G.soft_block,G.loft2,G.tube,G.dock,G.rounded_rect
HC=2.30; RO=4.15
WIN=[(50,0.95,0.225),(102.5,0.95,0.225),(147.5,0.95,0.225),(270,0.95,0.225)]
EVA=(0,1.10,0.50)
ROOMW=(-20,20,80,170,200,250,290,340)
DOORS={50:'s',125:'s',225:'s',270:'s',315:'s'}
def vdisc(m,rc,ac,u,v0,h0,rad,n=28,ring=None):
    pts=[(rad*math.cos(2*math.pi*k/n),rad*math.sin(2*math.pi*k/n)) for k in range(n)]
    c=Lc(rc,ac,u,v0,h0); add(m,[(c,Lc(rc,ac,u,v0+pts[k][0],h0+pts[k][1]),Lc(rc,ac,u,v0+pts[(k+1)%n][0],h0+pts[(k+1)%n][1])) for k in range(n)])
    if ring:
        mm,w=ring
        for k in range(n):
            p,q=pts[k],pts[(k+1)%n]; f=1+w/rad
            add(mm,quad(Lc(rc,ac,u-0.002,v0+p[0]*f,h0+p[1]*f),Lc(rc,ac,u-0.002,v0+q[0]*f,h0+q[1]*f),Lc(rc,ac,u-0.002,v0+q[0],h0+q[1]),Lc(rc,ac,u-0.002,v0+p[0],h0+p[1])))
def hdisc(m,rc,ac,du,dv,h,rad,n=32):   # horizontal disc
    pts=[(rad*math.cos(2*math.pi*k/n),rad*math.sin(2*math.pi*k/n)) for k in range(n)]
    c=Lc(rc,ac,du,dv,h); add(m,[(c,Lc(rc,ac,du+pts[k][0],dv+pts[k][1],h),Lc(rc,ac,du+pts[(k+1)%n][0],dv+pts[(k+1)%n][1],h)) for k in range(n)])
def ctx():
    item('CTX')
    for a in np.arange(0,360,3):
        add('floor',quad(W(1.25,a,0),W(RO,a,0),W(RO,a+3,0),W(1.25,a+3,0))[::-1])
        add('core',quad(W(1.25,a,0),W(1.25,a+3,0),W(1.25,a+3,HC),W(1.25,a,HC)))
        add('hull',quad(W(1.25,a,HC),W(RO,a,HC),W(RO,a+3,HC),W(1.25,a+3,HC)))
    for wa,wh,wr in WIN: vdisc('space',RO+0.04,wa,0,0,wh,wr,ring=('titanium',0.04))
def lining():
    item('D3_lining')
    holes=[(wa,wh,wr+0.06) for wa,wh,wr in WIN]+[(EVA[0],EVA[1],EVA[2]+0.12)]
    def hole(a,h): return any(abs(((a-ha+180)%360)-180)*math.pi/180*RO<hr and abs(h-hh)<hr for ha,hh,hr in holes)
    for a in np.arange(0,360,1.5):
        for h0 in np.arange(0,HC,0.1):
            if not hole(a+0.75,h0+0.05): add('hull',quad(W(RO,a,h0),W(RO,a,h0+0.1),W(RO,a+1.5,h0+0.1),W(RO,a+1.5,h0)))
    cove=[(RO-0.28,HC)]+[(RO-0.28+0.28*math.sin(math.radians(t)),HC-0.28+0.28*math.cos(math.radians(t))) for t in range(0,91,10)]
    for a in np.arange(0,360,2):
        for k in range(len(cove)-1):
            (r0,h0),(r1,h1)=cove[k],cove[k+1]; add('hull',quad(W(r0,a,h0),W(r1,a,h1),W(r1,a+2,h1),W(r0,a+2,h0)))
    for a in np.arange(0,360,7.5):
        d=min(abs(((a+180)%360)-180),abs(((a-180+180)%360)-180)); r_in=2.05 if d<=16 else 1.30
        sweep('reveal',[(r_in,HC-0.002),(RO-0.28,HC-0.002),(RO-0.28,HC-0.006),(r_in,HC-0.006)],a-0.07,a+0.07,0.14,caps=False)
    item('D1_lighting'); sweep('warm',[(RO-0.30,2.268),(RO-0.27,2.268),(RO-0.27,2.28),(RO-0.30,2.28)],0,360,2,caps=False)
    item('D2_overhead_rail'); sweep('oak',[(1.62,1.98),(1.67,1.98),(1.67,2.03),(1.62,2.03)],14,166,2); sweep('oak',[(1.62,1.98),(1.67,1.98),(1.67,2.03),(1.62,2.03)],194,346,2)
def walls():
    item('P0_walls')
    dh=math.degrees(0.40/1.90)
    gaps=sorted([(a-dh,a+dh) for a in DOORS]+[(0-dh,0+dh),(185-dh,185+dh)])
    edges=[-20]+[x for g in gaps for x in g]+[340]
    for k in range(0,len(edges),2): sweep('sand',rounded_rect(1.88,1.92,0,HC,0.008,2),edges[k],edges[k+1],1.0)
    for a,_ in DOORS.items():
        sweep('sand',rounded_rect(1.88,1.92,2.05,HC,0.008,2),a-dh,a+dh,1.0)
        sweep('oak',rounded_rect(1.875,1.885,0.01,2.04,0.004,2),a-dh+0.3,a+dh-0.3,0.8)
        sweep('titanium',[(1.86,2.05),(1.875,2.05),(1.875,2.08),(1.86,2.08)],a-dh-4,a+dh+4,1.0)
        sweep('ind',[(1.871,1.12),(1.876,1.12),(1.876,1.15),(1.871,1.15)],a+dh-2.2,a+dh-1.6,0.6)
    for a in ROOMW: sweep('sand',rounded_rect(1.92,RO,0,HC,0.01,2),a-math.degrees(0.02/3.0),a+math.degrees(0.02/3.0),0.4)
def airlock():
    item('A0_inner_pressure_hatch')   # pressure-rated hatch from the corridor (0 deg, beside the ladder)
    dh=math.degrees(0.40/1.90)
    sweep('sand',rounded_rect(1.88,1.92,1.70,HC,0.008,2),-dh,dh,1.0)
    sweep('vault',rounded_rect(1.86,1.94,0.05,1.70,0.03,3),-dh+0.5,dh-0.5,0.5)
    for a0,a1 in ((-dh-1.2,-dh+0.6),(dh-0.6,dh+1.2)): sweep('titanium',rounded_rect(1.85,1.95,0.0,1.75,0.01,2),a0,a1,0.4)
    tube('titanium',1.85,0,[(0,-0.12,0.95),(-0.02,0,1.07),(0,0.12,0.95),(-0.02,0,0.83),(0,-0.12,0.95)],0.014,samples=5)
    soft_block('ind',1.85,0,0.004,0.01,1.40,1.42,0.002,nexp=2,dv=0.25)
    item('A1_control_panel')     # depress/repress control (dark glass + manual equalisation valve) on the -20 wall
    rc=3.0; ac=-20+math.degrees(0.04/rc)
    soft_block('worktop',rc,ac,0.55,0.02,0.75,1.75,0.02,nexp=8)
    soft_block('glass',rc,ac,0.35,0.004,1.20,1.60,0.01,nexp=8,dv=0.022)
    soft_block('graphic',rc,ac,0.25,0.003,1.52,1.53,0.002,nexp=8,dv=0.026)
    vdisc('titanium',rc,ac,0,0,0,0.0) if False else None
    tube('teal',rc,ac,[(0.35,0.03,0.95),(0.42,0.08,1.0),(0.35,0.13,1.05),(0.28,0.08,1.0),(0.35,0.03,0.95)],0.012,samples=5)
    for hh in (1.05,1.12): soft_block('ind',rc,ac,0.004,0.004,hh,hh+0.012,0.001,nexp=2,du=-0.40,dv=0.025)
    item('A2_tether_tool_board')
    rc=3.0; ac=20-math.degrees(0.04/rc)
    soft_block('oak',rc,ac,0.55,0.02,0.60,1.80,0.02,nexp=8)
    for du in (-0.35,-0.12,0.12,0.35): loft2('titanium',rc,ac,[(1.45,0.05,0.05,2,du,-0.06),(1.52,0.06,0.06,2,du,-0.06)])   # tether reels
    for du in (-0.3,0.0,0.3): soft_block('teal',rc,ac,0.04,0.015,0.85,1.15,0.008,nexp=4,du=du,dv=-0.03)
    item('A3_handhold_station')
    for k in range(4):
        a=-9+k*6
        tube('teal',3.1,0,[(-0.35,-0.35+k*0.233,0.0),(-0.35,-0.35+k*0.233,1.0)],0.016,samples=3) if False else None
    n=24; pts=[(0.42*math.cos(2*math.pi*k/n),0.42*math.sin(2*math.pi*k/n),1.0) for k in range(n+1)]
    tube('teal',3.1,0,pts,0.018,samples=3)
    for k in range(4):
        t=2*math.pi*(k+0.5)/4; tube('titanium',3.1,0,[(0.42*math.cos(t),0.42*math.sin(t),0.0),(0.42*math.cos(t),0.42*math.sin(t),1.0)],0.02,samples=3)
    item('A4_EVA_hatch')   # kT decision: 1.0 m outer hatch at 0 deg, centre h 1.1, between the EVA rails
    wa,wh,wr=EVA
    vdisc('vault',RO-0.05,wa,0,0,wh,wr-0.03,ring=('titanium',0.10))
    tube('titanium',RO-0.05,wa,[(0,-0.2*math.cos(t),wh+0.2*math.sin(t)) for t in np.linspace(0,2*math.pi,25)],0.016,samples=3)
    for t in np.linspace(0,2*math.pi,7)[:-1]: tube('titanium',RO-0.05,wa,[(0,0,wh),(0,-0.2*math.cos(t),wh+0.2*math.sin(t))],0.01,samples=2)
    soft_block('ind',RO-0.06,wa,0.004,0.012,wh+0.62,wh+0.64,0.002,nexp=2)
    soft_block('ind',RO-0.06,wa,0.004,0.012,wh+0.66,wh+0.68,0.002,nexp=2)
def suit_room():
    item('U1_EVA_suit_stands')
    for a in (32,44,56,68):
        rc=3.6
        dock(rc,a,0.22,0.22)
        loft2('titanium',rc,a,[(0.006,0.05,0.05,2,0,0),(0.95,0.04,0.04,2,0,0)],cap_top=False)
        for sv in (-1,1): tube('suit',rc,a,[(0.0,sv*0.12,0.10),(0.02,sv*0.12,0.55),(0.0,sv*0.11,0.95)],0.075)   # legs
        loft2('suit',rc,a,[(0.95,0.16,0.20,2.4,0,0),(1.20,0.19,0.24,2.4,0,0),(1.50,0.20,0.26,2.4,0,0),(1.62,0.15,0.22,2.4,0,0)])   # hard upper torso
        for sv in (-1,1): tube('suit',rc,a,[(0,sv*0.27,1.50),(-0.04,sv*0.32,1.25),(-0.06,sv*0.31,1.02)],0.06)
        loft2('glass',rc,a,[(1.62,0.10,0.10,2,0,0),(1.70,0.15,0.15,2,0,0),(1.80,0.16,0.16,2,0,0),(1.90,0.12,0.12,2,0,0),(1.95,0.0,0.0,2,0,0)],cap_top=False)
        soft_block('sand',rc,a,0.12,0.20,1.05,1.50,0.04,nexp=4,du=0.20)                     # life-support pack
        tube('teal',rc,a,[(0.30,0.0,1.25),(0.45,0.05,1.6),(0.52,0.05,2.0)],0.02)          # service umbilical to the wall
    item('U2_IVA_lockers')
    rc=2.65; ac=20+math.degrees(0.28/rc)
    soft_block('reveal',rc,ac,0.32,0.22,0,0.09,0.02,nexp=8); soft_block('oak',rc,ac,0.35,0.25,0.09,2.20,0.05,nexp=7,bulge=0.03)
    for k in range(1,5): G.vline('reveal',rc,ac,0.35*(2*k/5-1),-0.255,-0.262,0.14,2.14) if False else None
    for hh in np.linspace(0.5,1.9,5): soft_block('reveal',rc,ac,0.34,0.002,hh,hh+0.005,0.001,nexp=8,dv=-0.252)
    for hh in np.linspace(0.28,2.05,10): soft_block('ind',rc,ac,0.004,0.002,hh,hh+0.01,0.001,nexp=2,du=0.25,dv=-0.254)
    item('U3_donning_bench')
    soft_block('oak_dk',2.55,62,0.20,0.40,0.0,0.40,0.04,nexp=4); soft_block('sand',2.55,62,0.24,0.44,0.40,0.47,0.03,nexp=4)
def workshop():
    item('W1_workbench'); rc,ac=3.58,125
    soft_block('reveal',rc,ac,0.29,1.25,0,0.09,0.02,nexp=8)
    soft_block('worktop',rc,ac,0.31,1.28,0.09,0.86,0.04,nexp=8)
    for dv in np.linspace(-0.96,0.96,4):
        for hh in (0.32,0.58): soft_block('reveal',rc,ac,0.002,0.3,hh,hh+0.005,0.001,nexp=8,du=-0.312,dv=dv)
        soft_block('ind',rc,ac,0.002,0.006,0.80,0.812,0.001,nexp=2,du=-0.313,dv=dv)
    soft_block('oak',rc,ac,0.34,1.30,0.86,0.92,0.012,nexp=8)
    soft_block('titanium',rc,ac,0.08,0.10,0.92,1.02,0.01,nexp=6,du=-0.24,dv=0.9)          # vise
    sweep('sand',[(4.12,1.10),(4.14,1.10),(4.14,1.95),(4.12,1.95)],ac-15,ac+15,1.0)                 # tool shadow board on the wall
    for a in np.linspace(ac-12,ac+12,9): sweep('reveal',[(4.112,1.25),(4.12,1.25),(4.12,1.75),(4.112,1.75)],a-0.25,a+0.25,0.5)
    sweep('task',[(3.98,1.98),(4.0,1.98),(4.0,1.99),(3.98,1.99)],ac-14,ac+14,1.0)
    item('W2_3D_printer'); rc,ac=2.6,100
    soft_block('reveal',rc,ac,0.32,0.32,0,0.08,0.02,nexp=8); soft_block('worktop',rc,ac,0.35,0.35,0.08,1.50,0.05,nexp=7)
    soft_block('glass',rc,ac,0.004,0.25,0.65,1.30,0.02,nexp=8,du=-0.352)
    soft_block('task',rc,ac,0.003,0.2,1.27,1.28,0.002,nexp=6,du=-0.355)
    soft_block('glass',rc,ac,0.003,0.12,1.36,1.44,0.01,nexp=8,du=-0.352,dv=0.18)
    item('W3_mill_lathe'); rc,ac=2.6,150
    soft_block('reveal',rc,ac,0.32,0.37,0,0.08,0.02,nexp=8); soft_block('worktop',rc,ac,0.35,0.40,0.08,1.0,0.05,nexp=7)
    soft_block('titanium',rc,ac,0.25,0.30,1.0,1.45,0.06,nexp=4)
    soft_block('glass',rc,ac,0.003,0.26,1.05,1.40,0.02,nexp=8,du=-0.252)
    soft_block('glass',rc,ac,0.003,0.10,0.70,0.85,0.01,nexp=8,du=-0.352,dv=0.25)
    item('W4_W5_parts_walls')
    for aw,sg in ((80,1),(170,-1)):
        rc=3.1; ac=aw+sg*math.degrees(0.255/rc)
        soft_block('reveal',rc,ac,0.77,0.195,0,0.09,0.02,nexp=8); soft_block('oak',rc,ac,0.80,0.225,0.09,2.20,0.05,nexp=7,bulge=0.03)
        for hh in np.linspace(0.3,2.0,8): soft_block('reveal',rc,ac,0.78,0.002,hh,hh+0.005,0.001,nexp=8,dv=-sg*0.228)
    item('W6_stools')
    for a in (115,135):
        dock(3.15,a,0.15,0.15)
        loft2('oak',3.15,a,[(0.006+t*0.58,0.085+0.03*t**2+0.03*t**6,0.08+0.03*t**2+0.03*t**6,2.2,-0.03*math.sin(math.pi*t),0) for t in np.linspace(0,1,8)],cap_top=False)
        loft2('sage',3.15,a,[(0.586,0.15,0.14,2.2,0,0),(0.62,0.17,0.16,2.2,0,0),(0.645,0.16,0.15,2.2,0,0),(0.64,0.0,0.0,2.2,0,0)],cap_top=False)
def custody():
    item('V1_custody_vault'); rc,ac=3.3,185
    soft_block('reveal',rc,ac,0.72,0.40,0,0.08,0.02,nexp=8); soft_block('vault',rc,ac,0.75,0.425,0.08,1.90,0.06,nexp=6)
    for dv in (-0.2,0.2): G.panel_line('reveal',rc,ac,-0.76,-0.75,dv,0.15,1.85) if False else soft_block('reveal',rc,ac,0.002,0.003,0.15,1.85,0.001,nexp=8,du=0.0,dv=dv) if False else None
    for u in (-0.38,0.38): soft_block('reveal',rc,ac,0.002,0.42,0.15,1.85,0.001,nexp=8,du=u) if False else None
    for dv in (-0.43,0.43):
        for hh in (0.5,1.0,1.5): soft_block('ind',rc,ac,0.05,0.003,hh,hh+0.012,0.002,nexp=2,du=-0.3,dv=dv*1.005)
    soft_block('glass',rc,ac,0.004,0.06,1.20,1.32,0.005,nexp=8,du=-0.755)
    soft_block('teal',rc,ac,0.004,0.18,1.0,1.03,0.005,nexp=6,du=-0.755)
    item('V2_vault_door')   # heavier door at 185 deg (custody)
    dh=math.degrees(0.40/1.90)
    sweep('sand',rounded_rect(1.88,1.92,2.05,HC,0.008,2),185-dh,185+dh,1.0)
    sweep('vault',rounded_rect(1.865,1.885,0.01,2.04,0.006,2),185-dh+0.3,185+dh-0.3,0.8)
    tube('titanium',1.86,185,[(0,-0.13*math.cos(t),1.05+0.13*math.sin(t)) for t in np.linspace(0,2*math.pi,21)],0.012,samples=3)
    soft_block('glass',1.86,185,0.004,0.05,1.35,1.45,0.005,nexp=8,dv=0.25); soft_block('ind',1.858,185,0.003,0.01,1.50,1.515,0.002,nexp=2,dv=0.25)
def stores():
    for nm,angs in (('S1_stores_racks',(210,225,240)),('S2_stores_racks',(300,315,330))):
        item(nm)
        for a in angs:
            rc=3.15
            for du in (-0.92,0.92):
                for dv in (-0.25,0.25): loft2('titanium',rc,a,[(0.0,0.02,0.02,2,du,dv),(2.20,0.02,0.02,2,du,dv)],cap_top=True)
            for hh in (0.05,0.48,0.91,1.34,1.77,2.18): soft_block('oak',rc,a,0.94,0.27,hh,hh+0.025,0.008,nexp=8)
            for hh in (0.10,0.53,0.96,1.39,1.82):
                for du in (-0.46,0.46): soft_block('linen',rc,a,0.42,0.24,hh+0.03,hh+0.36,0.04,nexp=3,du=du)   # stowage bags
                soft_block('teal',rc,a,0.93,0.004,hh+0.20,hh+0.22,0.002,nexp=8,dv=0.272); soft_block('teal',rc,a,0.93,0.004,hh+0.20,hh+0.22,0.002,nexp=8,dv=-0.272)
def vestibule():
    item('T1_tunnel_floor_hatch')   # kT decision: 1.2 m hatch to tunnel_0 in the vestibule floor (r 3.0, 270 deg)
    rc,ac=3.0,270
    loft2('titanium',rc,ac,[(0.0,0.70,0.70,2,0,0),(0.02,0.70,0.70,2,0,0),(0.03,0.66,0.66,2,0,0)],cap_bot=False)
    loft2('vault',rc,ac,[(0.0,0.60,0.60,2,0,0),(0.025,0.60,0.60,2,0,0)],cap_bot=False)
    tube('titanium',rc,ac,[(0.2*math.cos(t),0.2*math.sin(t),0.05) for t in np.linspace(0,2*math.pi,25)],0.016,samples=3)
    for t in np.linspace(0,2*math.pi,7)[:-1]: tube('titanium',rc,ac,[(0,0,0.05),(0.2*math.cos(t),0.2*math.sin(t),0.05)],0.01,samples=2)
    for k in range(6):
        t=2*math.pi*k/6; soft_block('ind',rc,ac,0.01,0.01,0.032,0.036,0.002,nexp=2,du=0.68*math.cos(t),dv=0.68*math.sin(t))
    item('T2_handrails_panel')
    for t0,t1 in ((0.35,2.8),(3.5,5.9)):
        pts=[(0.95*math.cos(t),0.95*math.sin(t),0.95) for t in np.linspace(t0,t1,12)]
        tube('oak',rc,ac,pts,0.022,samples=3)
        for t in (t0,t1): tube('titanium',rc,ac,[(0.95*math.cos(t),0.95*math.sin(t),0.0),(0.95*math.cos(t),0.95*math.sin(t),0.95)],0.018,samples=2)
    ac2=290-math.degrees(0.04/3.0)
    soft_block('worktop',3.0,ac2,0.30,0.02,1.0,1.7,0.02,nexp=8)
    soft_block('glass',3.0,ac2,0.22,0.004,1.25,1.60,0.01,nexp=8,dv=-0.022)
    soft_block('ind',3.0,ac2,0.004,0.004,1.15,1.162,0.001,nexp=2,du=0.1,dv=-0.025)
def build():
    G.T.clear(); ctx(); lining(); walls(); airlock(); suit_room(); workshop(); custody(); stores(); vestibule(); return G.T
def by_material():
    M={}
    for (it,m),t in G.T.items(): M.setdefault(m,[]).extend(t)
    return M
