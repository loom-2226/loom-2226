"""Wayfarer L4: storm shelter / wellness room, medical bay, life support. Organic Japandi x working spacecraft (Claude, 12 Nov 2026; kT approved layout).
ALL bodies. ALL sponsors. 2026-2226.  Reuses the approved L2 language (geom.py helpers).
Frame: source angle a (Y=r cos a, Z=r sin a); world=[X,Z,-Y]; h above L4 floor top X=10.8; ceiling h=2.30 (X=8.5).
Assumes kT decisions l4_decisions_2026_11_12: shelter plug door at 90 deg, medical ports centred h 1.50, hatch_L3L4_0 (180 deg) sliding."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'l2_organic_study'))
import math,numpy as np, geom as G
G.X0=10.8
G.MAT['linen']=('#EFE9DD',0); G.MAT['scene']=('#6E9A93',1); G.MAT['water']=('#2F6F8F',0)
W,Lc,add,item,quad,sweep,soft_block,loft2,tube,dock,rounded_rect=G.W,G.Lc,G.add,G.item,G.quad,G.sweep,G.soft_block,G.loft2,G.tube,G.dock,G.rounded_rect
HC=2.30; RO=4.15
SH=(18.79,161.21); SF,SC=0.20,2.10      # shelter interior angles, floor and ceiling heights (inside the jacket)
PORTS=[180,210,240]; PH=1.50; PR=0.775
def vdisc(m,rc,ac,u,v0,h0,rad,n=28,ring=None):
    pts=[(rad*math.cos(2*math.pi*k/n),rad*math.sin(2*math.pi*k/n)) for k in range(n)]
    c=Lc(rc,ac,u,v0,h0); add(m,[(c,Lc(rc,ac,u,v0+pts[k][0],h0+pts[k][1]),Lc(rc,ac,u,v0+pts[(k+1)%n][0],h0+pts[(k+1)%n][1])) for k in range(n)])
    if ring:
        mm,w=ring
        for k in range(n):
            p,q=pts[k],pts[(k+1)%n]
            add(mm,quad(Lc(rc,ac,u-0.002,v0+p[0]*(1+w/rad),h0+p[1]*(1+w/rad)),Lc(rc,ac,u-0.002,v0+q[0]*(1+w/rad),h0+q[1]*(1+w/rad)),Lc(rc,ac,u-0.002,v0+q[0],h0+q[1]),Lc(rc,ac,u-0.002,v0+p[0],h0+p[1])))
def ctx():
    item('CTX')
    for a in np.arange(0,360,3):
        add('floor',quad(W(1.25,a,0),W(RO,a,0),W(RO,a+3,0),W(1.25,a+3,0))[::-1])
        add('core',quad(W(1.25,a,0),W(1.25,a+3,0),W(1.25,a+3,HC),W(1.25,a,HC)))
        add('hull',quad(W(1.25,a,HC),W(RO,a,HC),W(RO,a+3,HC),W(RO,a+3,HC)) if False else quad(W(1.25,a,HC),W(RO,a,HC),W(RO,a+3,HC),W(1.25,a+3,HC)))
    # 20 cm water jacket round the shelter (source), with the kT plug-door opening at 90 deg
    dh=math.degrees(0.40/2.0)
    for s0,s1 in ((15,90-dh),(90+dh,165)): sweep('water',[(1.9,0),(2.1,0),(2.1,HC),(1.9,HC)],s0,s1,1.5)
    sweep('water',[(1.9,SC),(2.1,SC),(2.1,HC),(1.9,HC)],90-dh,90+dh,1.0)
    sweep('water',[(3.95,0),(RO,0),(RO,HC),(3.95,HC)],15,165,1.5)
    sweep('water',[(2.1,0),(3.95,0),(3.95,SF),(2.1,SF)],15,165,1.5); sweep('water',[(2.1,SC),(3.95,SC),(3.95,HC),(2.1,HC)],15,165,1.5)
    for a0,a1 in ((15,18.79),(161.21,165)): sweep('water',[(2.1,SF),(3.95,SF),(3.95,SC),(2.1,SC)],a0,a1,1.0)
    # source shelter backup unit (box at r 2.8-3.2, a 90, h 0.95-1.35) and rescue kit
    soft_block('titanium',3.0,90,0.2,0.2,0.95,1.35,0.02,nexp=8)
    soft_block('teal',3.55,230,0.15,0.15,1.0,1.3,0.02,nexp=8)
    # medical ports (lowered, kT): dark glass discs with titanium rings
    for wa in PORTS:
        n=28; pts=[(PR*math.cos(2*math.pi*k/n),PR*math.sin(2*math.pi*k/n)) for k in range(n)]
        c=Lc(RO+0.04,wa,0,0,PH); add('space',[(c,Lc(RO+0.04,wa,0,pts[k][0],PH+pts[k][1]),Lc(RO+0.04,wa,0,pts[(k+1)%n][0],PH+pts[(k+1)%n][1])) for k in range(n)])
        for k in range(n):
            p,q=pts[k],pts[(k+1)%n]
            add('titanium',quad(Lc(RO-0.03,wa,0,p[0]*1.08,PH+p[1]*1.08),Lc(RO-0.03,wa,0,q[0]*1.08,PH+q[1]*1.08),Lc(RO-0.03,wa,0,q[0],PH+q[1]),Lc(RO-0.03,wa,0,p[0],PH+p[1])))
            add('titanium',quad(Lc(RO-0.03,wa,0,p[0],PH+p[1]),Lc(RO-0.03,wa,0,q[0],PH+q[1]),Lc(RO+0.04,wa,0,q[0],PH+q[1]),Lc(RO+0.04,wa,0,p[0],PH+p[1])))
    # L3/L4 hatch leaf at 0 deg (hatch_L3L4_1, source) hanging into L4; the 180 deg leaf slides into the slab (kT)
    soft_block('hull_dk',1.86,0,0.03,0.46,1.68,HC,0.005,nexp=10)
def lining():
    item('D3_lining')
    def inport(a,h): return any(abs(((a-p+180)%360)-180)*math.pi/180*RO<PR+0.06 and abs(h-PH)<PR+0.06 for p in PORTS)
    for a in np.arange(165,375,1.5):
        for h0 in np.arange(0,HC,0.1):
            if not inport(a+0.75,h0+0.05): add('hull',quad(W(RO,a,h0),W(RO,a,h0+0.1),W(RO,a+1.5,h0+0.1),W(RO,a+1.5,h0)))
    cove=[(RO-0.28,HC)]+[(RO-0.28+0.28*math.sin(math.radians(t)),HC-0.28+0.28*math.cos(math.radians(t))) for t in range(0,91,10)]
    for a in np.arange(165,375,2):
        if not any(abs(((a+1-p+180)%360)-180)<12 for p in PORTS):
            for k in range(len(cove)-1):
                (r0,h0),(r1,h1)=cove[k],cove[k+1]; add('hull',quad(W(r0,a,h0),W(r1,a,h1),W(r1,a+2,h1),W(r0,a+2,h0)))
    for a in np.arange(0,360,7.5):
        d=min(abs(((a+180)%360)-180),abs(((a-180+180)%360)-180)); r_in=2.05 if d<=16 else 1.30
        r_out=1.9 if 15<=a<=165 else RO-0.28
        sweep('reveal',[(r_in,HC-0.002),(r_out,HC-0.002),(r_out,HC-0.006),(r_in,HC-0.006)],a-0.07,a+0.07,0.14,caps=False)
    item('D1_lighting')
    sweep('warm',[(RO-0.30,2.268),(RO-0.27,2.268),(RO-0.27,2.28),(RO-0.30,2.28)],165,375,2,caps=False)
    sweep('warm',[(3.86,SC-0.03),(3.90,SC-0.03),(3.90,SC-0.02),(3.86,SC-0.02)],20,160,2,caps=False)   # shelter cove light
    item('D2_overhead_rail')
    sweep('oak',[(1.62,1.98),(1.67,1.98),(1.67,2.03),(1.62,2.03)],14,166,2); sweep('oak',[(1.62,1.98),(1.67,1.98),(1.67,2.03),(1.62,2.03)],194,346,2)
def walls():
    item('P0_walls')
    # medical: radial wall at 255 and short inner partition stubs either side of the 2.4 m bi-parting entrance (source, 202 deg)
    sweep('sand',rounded_rect(1.92,RO,0,HC,0.01,2),254.6,255.4,0.4)
    dh=math.degrees(1.2/1.9)
    for s0,s1 in ((165,202-dh),(202+dh,255)): sweep('sand',rounded_rect(1.88,1.92,0,HC,0.008,2),s0,s1,0.8)
    sweep('sand',rounded_rect(1.88,1.92,2.10,HC,0.008,2),202-dh,202+dh,1.0)
    sweep('titanium',[(1.86,2.10),(1.88,2.10),(1.88,2.13),(1.86,2.13)],202-dh-3,202+dh+3,1.0)
    for s in (-1,1): sweep('linen',rounded_rect(1.875,1.885,0.01,2.09,0.004,2),202+s*dh-(0 if s>0 else -0.0)-(4 if s>0 else -4)*0+((-1 if s>0 else 1)*0)+(0),202+s*dh+(0.0),0.6) if False else None
    for a0,a1 in ((202-dh,202-dh+3.5),(202+dh-3.5,202+dh)): sweep('linen',rounded_rect(1.874,1.886,0.01,2.09,0.004,2),a0,a1,0.5)   # bi-parting leaves parked open
    sweep('ind',[(1.871,1.15),(1.876,1.15),(1.876,1.19),(1.871,1.19)],202+dh+1.2,202+dh+1.8,0.6)
    # life support: acoustic inner partition with a 1.2 m sliding maintenance door at 315 deg (room-booking item, not a pressure boundary)
    dm=math.degrees(0.6/1.9)
    for s0,s1 in ((255,315-dm),(315+dm,344)): sweep('sand',rounded_rect(1.88,1.92,0,HC,0.008,2),s0,s1,1.0)
    sweep('sand',rounded_rect(1.88,1.92,2.05,HC,0.008,2),315-dm,315+dm,1.0)
    sweep('oak',rounded_rect(1.875,1.885,0.01,2.04,0.004,2),315-dm+0.3,315+dm-0.3,0.8)
    sweep('titanium',[(1.86,2.05),(1.875,2.05),(1.875,2.08),(1.86,2.08)],315-dm-4,315+dm+4,1.0)
    sweep('ind',[(1.871,1.12),(1.876,1.12),(1.876,1.15),(1.871,1.15)],315+dm-2.2,315+dm-1.6,0.6)
def shelter():
    item('S0_shelter_plug_door')   # kT decision: 0.8 m water-filled sliding plug door in jacket_inner at 90 deg
    dh=math.degrees(0.40/2.0)
    sweep('sand',rounded_rect(1.91,2.09,SF+0.01,SC-0.01,0.03,3),90-dh+0.4,90+dh-0.4,0.8)
    sweep('titanium',rounded_rect(1.885,1.91,SF,SC,0.005,2),90-dh-0.8,90-dh+0.4,0.4); sweep('titanium',rounded_rect(1.885,1.91,SF,SC,0.005,2),90+dh-0.4,90+dh+0.8,0.4)
    sweep('ind',[(1.882,1.10),(1.887,1.10),(1.887,1.16),(1.882,1.16)],90+dh+1.0,90+dh+1.6,0.6)
    sweep('reveal',[(1.882,0.85),(1.889,0.85),(1.889,1.25),(1.882,1.25)],90-dh+1.5,90-dh+2.0,0.5)
    item('S7_shelter_lining')   # warm interior faces on the water jacket: oak-look floor, linen walls and ceiling
    sweep('oak',[(2.1,SF),(3.95,SF),(3.95,SF+0.004),(2.1,SF+0.004)],SH[0],SH[1],1.5,caps=False)
    sweep('linen',[(2.1,SC-0.004),(3.95,SC-0.004),(3.95,SC),(2.1,SC)],SH[0],SH[1],1.5,caps=False)
    dh2=math.degrees(0.40/2.0)
    for s0,s1 in ((SH[0],90-dh2),(90+dh2,SH[1])): sweep('linen',[(2.1,SF),(2.104,SF),(2.104,SC),(2.1,SC)],s0,s1,1.5,caps=False)
    sweep('linen',[(3.946,SF),(3.95,SF),(3.95,SC),(3.946,SC)],SH[0],SH[1],1.5,caps=False)
    for a in SH: sweep('linen',[(2.1,SF),(3.95,SF),(3.95,SC),(2.1,SC)],a-0.05 if a>90 else a,a if a>90 else a+0.05,0.05)
    item('S1_living_wall')
    sweep('scene',[(3.918,0.45),(3.93,0.45),(3.93,1.75),(3.918,1.75)],28,152,1.0,caps=False)
    for g in (0.43,1.75): sweep('titanium',[(3.91,g),(3.94,g),(3.94,g+0.02),(3.91,g+0.02)],27.5,152.5,1.0)
    for a in np.arange(28,153,15.5): sweep('reveal',[(3.914,0.45),(3.919,0.45),(3.919,1.75),(3.914,1.75)],a-0.1,a+0.1,0.2,caps=False)
    item('S2_wellness_loungers')
    top=[(-0.80,0.70),(-0.74,0.66),(-0.62,0.56),(-0.47,0.44),(-0.32,0.35),(-0.15,0.30),(0.0,0.29),(0.17,0.32),(0.32,0.35),(0.47,0.33),(0.62,0.28),(0.75,0.24),(0.80,0.23)]
    for a in (60,120):
        G.extrude_uh('oak',3.0,a,[(u,h+SF-0.055) for u,h in top],0.05,0.31,taper=lambda u: 0.9+0.1*math.cos(u*1.6))
        G.extrude_uh('sand',3.0,a,[(u*0.97,h+SF) for u,h in top],0.055,0.27,taper=lambda u: 0.9+0.1*math.cos(u*1.6))
        loft2('oak_dk',3.0,a,[(SF+0.006,0.2,0.14,2.6,-0.05,0),(SF+0.12,0.18,0.12,2.6,-0.04,0),(SF+0.24,0.25,0.18,2.6,-0.03,0)])
        loft2('titanium',3.0,a,[(SF,0.24,0.17,3,-0.05,0),(SF+0.006,0.24,0.17,3,-0.05,0)])
        tube('teal',3.0,a,[(-0.02,-0.29,SF+0.27),(0.0,-0.31,SF+0.24),(0.02,-0.29,SF+0.21)],0.012); tube('teal',3.0,a,[(-0.02,0.29,SF+0.27),(0.0,0.31,SF+0.24),(0.02,0.29,SF+0.21)],0.012)
    item('S3_soft_floor')
    for a0 in (70,75,80,96,101,106):
        sweep('sand',rounded_rect(2.35,3.55,SF,SF+0.06,0.02,3),a0+0.15,a0+4.85,1.0)
    item('S4_backup_stand')
    loft2('oak',3.0,90,[(SF,0.16,0.16,2.4,0,0),(SF+0.02,0.16,0.16,2.4,0,0),(0.6,0.07,0.07,2.4,0,0),(0.95,0.12,0.12,2.4,0,0)],cap_top=False)
    item('S5_shelter_seats')    # ten fold-flat restraint seats on the inner jacket wall (storm mode)
    for a in (24,36,48,60,72,108,120,132,144,156):
        soft_block('oak',2.13,a,0.02,0.22,0.55,1.25,0.02,nexp=6)
        soft_block('teal',2.15,a,0.004,0.18,1.12,1.14,0.002,nexp=6)
        soft_block('ind',2.152,a,0.002,0.006,1.20,1.212,0.001,nexp=2)
    item('S6_storm_lockers')
    for a,sg in ((18.79,1),(161.21,-1)):
        rc=3.0; ac=a+sg*math.degrees(0.18/rc)
        soft_block('oak',rc,ac,0.80,0.15,SF,SC-0.02,0.04,nexp=7,bulge=0.03)
        for u in (-0.4,0.0,0.4): soft_block('ind',rc,ac,0.002,0.006,1.1,1.112,0.001,nexp=2,du=u,dv=-sg*0.155)
def medical():
    item('M1_treatment_table'); rc,ac=3.05,210
    dock(rc,ac,0.35,0.22)
    loft2('worktop',rc,ac,[(0.006,0.30,0.18,2.6,0,0),(0.40,0.18,0.12,2.6,0,0),(0.62,0.26,0.16,2.6,0,0)])
    soft_block('worktop',rc,ac,1.0,0.35,0.62,0.74,0.03,nexp=6)
    soft_block('sand',rc,ac,0.96,0.31,0.74,0.80,0.04,nexp=5)
    for sv in (-1,1): soft_block('titanium',rc,ac,0.95,0.012,0.70,0.73,0.006,nexp=8,dv=sv*0.36)   # stretcher rails
    for du in (-0.5,0.0,0.5): soft_block('teal',rc,ac,0.025,0.33,0.795,0.81,0.004,nexp=6,du=du)
    loft2('titanium',rc,ac,[(HC-0.03,0.14,0.14,2,0,0),(HC,0.14,0.14,2,0,0)])
    tube('titanium',rc,ac,[(0,0,HC-0.02),(0.05,0.0,2.10),(0.2,0.05,1.98)],0.025)
    loft2('worktop',rc,ac,[(1.98,0.0,0.0,2,0.2,0.05),(1.99,0.22,0.22,2,0.2,0.05),(2.06,0.24,0.24,2,0.2,0.05),(2.08,0.0,0.0,2,0.2,0.05)])
    loft2('task',rc,ac,[(1.975,0.18,0.18,2,0.2,0.05),(1.978,0.18,0.18,2,0.2,0.05)])
    soft_block('glass',rc,ac,0.02,0.30,1.35,1.65,0.02,nexp=8,du=1.02)    # patient display on its arm end
    item('M2_recovery_bed'); rc,ac=3.15,243
    dock(rc,ac,0.6,0.25)
    soft_block('worktop',rc,ac,0.95,0.37,0.06,0.48,0.05,nexp=6,bulge=0.02)
    soft_block('sand',rc,ac,0.92,0.33,0.48,0.56,0.04,nexp=5)
    G.extrude_uh('sand',rc,ac,[(-0.92,0.85),(-0.80,0.80),(-0.62,0.62),(-0.45,0.58)],0.06,0.32)
    for sv in (-1,1): tube('titanium',rc,ac,[(-0.6,sv*0.39,0.56),(-0.55,sv*0.40,0.75),(0.4,sv*0.40,0.75),(0.45,sv*0.39,0.56)],0.015)
    for du in (-0.2,0.35): soft_block('teal',rc,ac,0.025,0.35,0.555,0.57,0.004,nexp=6,du=du)
    item('M3_cabinets_pharmacy')
    rc=3.2; ac=165+math.degrees(0.305/rc); A=0.8
    soft_block('reveal',rc,ac,A-0.03,0.245,0,0.09,0.02,nexp=8); soft_block('oak',rc,ac,A,0.275,0.09,2.20,0.05,nexp=7,bulge=0.03)
    for u in (-0.4,0.0,0.4):
        G.vline('reveal',rc,ac,u,-0.27,-0.285,0.14,2.14)
        soft_block('ind',rc,ac,0.002,0.006,1.10,1.112,0.001,nexp=2,du=u+0.2,dv=-0.285) if u<0.4 else None
    soft_block('glass',rc,ac,0.25,0.003,1.25,1.55,0.01,nexp=8,du=0.4,dv=-0.284)
    item('M5_decon_sink_terminal'); rc,ac=3.75,195
    soft_block('reveal',rc,ac,0.2,0.27,0,0.1,0.03,nexp=5); soft_block('oak',rc,ac,0.22,0.30,0.10,0.86,0.05,nexp=5,bulge=0.04)
    soft_block('worktop',rc,ac,0.235,0.31,0.86,0.90,0.02,nexp=5); loft2('glass',rc,ac,[(0.902,0.11,0.15,2.2,0.02,0),(0.905,0.11,0.15,2.2,0.02,0)])
    loft2('titanium',rc,ac,[(0.90,0.015,0.015,2,0.18,0),(1.08,0.012,0.012,2,0.18,0)])
def life_support():
    item('R_racks')
    labs=['O2','CO2','H2Orec','H2Oproc','airmon','thermal','waste']
    for k,a in enumerate(np.linspace(264,348,7)):
        rc=3.70
        soft_block('reveal',rc,a,0.40,0.49,0,0.08,0.02,nexp=8)
        soft_block('worktop',rc,a,0.43,0.52,0.08,2.0,0.05,nexp=7)
        G.panel_line('reveal',rc,a,-0.44,-0.425,0.0,0.12,1.96)
        for hh in (0.70,1.35): soft_block('reveal',rc,a,0.003,0.5,hh,hh+0.006,0.002,nexp=8,du=-0.433)
        soft_block('glass',rc,a,0.004,0.18,1.55,1.80,0.01,nexp=8,du=-0.433,dv=0.22)
        soft_block('graphic',rc,a,0.003,0.12,1.74,1.75,0.002,nexp=8,du=-0.436,dv=0.22)
        soft_block('ind',rc,a,0.002,0.006,1.62,1.632,0.001,nexp=2,du=-0.437,dv=0.36)
        soft_block('vent',rc,a,0.003,0.40,0.14,0.24,0.004,nexp=8,du=-0.433)
        for sv in (-1,1): tube('titanium',rc,a,[(-0.445,sv*0.42,0.9),(-0.47,sv*0.42,1.0),(-0.445,sv*0.42,1.1)],0.012,samples=4)
        sweep('titanium',[(3.95,2.0),(4.10,2.0),(4.10,2.25),(3.95,2.25)],a-6.5,a+6.5,1.0)     # overhead duct stub to the cove plenum
    item('R8_laundry'); rc,a=2.85,300
    soft_block('reveal',rc,a,0.27,0.52,0,0.08,0.02,nexp=8); soft_block('worktop',rc,a,0.30,0.55,0.08,1.20,0.05,nexp=7)
    for dv in (-0.27,0.27): vdisc('glass',rc,a,-0.302,dv,0.67,0.15,ring=('titanium',0.03))
    soft_block('glass',rc,a,0.004,0.35,1.02,1.12,0.01,nexp=8,du=-0.302)
    item('R9_spares'); rc,a=2.85,330
    soft_block('reveal',rc,a,0.27,0.52,0,0.08,0.02,nexp=8); soft_block('oak',rc,a,0.30,0.55,0.08,2.0,0.05,nexp=7,bulge=0.03)
    for dv in (-0.18,0.18): G.panel_line('reveal',rc,a,-0.31,-0.30,dv,0.12,1.96)
    for dv in (-0.36,0.0,0.36): soft_block('ind',rc,a,0.002,0.006,1.1,1.112,0.001,nexp=2,du=-0.305,dv=dv)
def build():
    G.T.clear(); ctx(); lining(); walls(); shelter(); medical(); life_support(); return G.T
def by_material():
    M={}
    for (it,m),t in G.T.items(): M.setdefault(m,[]).extend(t)
    return M
