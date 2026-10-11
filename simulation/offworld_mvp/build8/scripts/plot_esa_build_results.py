#!/usr/bin/env python3
"""Record deterministic ESA kernel events and draw a reproducible SVG using stdlib only.

Run from repository root with PYTHONPATH=src:simulation/offworld_mvp/phase3b/kernel:.
  python3 -m simulation.offworld_mvp.build8.scripts.plot_esa_build_results --record
  python3 -m simulation.offworld_mvp.build8.scripts.plot_esa_build_results --plot
All plotted measurements are parsed from event_log; no manually entered data values.
"""
import argparse
import json
from decimal import Decimal as D
from html import escape
from pathlib import Path
from simulation.offworld_mvp.build8.screened_yearly import run_yearly
from simulation.offworld_mvp.build8.esa_build_trial import EXECUTOR_TO_NETWORK_FACTOR

BASE = Path(__file__).resolve().parents[1]
EVENTS = BASE / 'recorded_events' / 'esa_build_step2.json'
FIGURE = BASE / 'recorded_events' / 'esa_build_step2.svg'
CONFIGS = [('A1',False,False,False,None), ('A2',True,False,False,None),
           ('A3',False,True,False,None), ('A4',False,False,True,None),
           ('B1',False,False,False,'Airbus Defence and Space'),
           ('C1',False,False,True,'Airbus Defence and Space')]


def record():
    runs=[]
    for label,tiers,slots,prices,removed in CONFIGS:
        for seed in range(1,6):
            _,_,kernel,_=run_yearly(selection='esa_build_quote_trial', seed=seed,
                tiers=tiers,slots=slots,prices=prices,remove_quote=removed)
            runs.append({'config':label,'tiers':tiers,'slots':slots,'prices':prices,
                         'removed':removed,'seed':seed,
                         'events':[e for e in kernel.event_log if e['kind'].startswith('ESA_BUILD_')]})
    EVENTS.write_text(json.dumps({'source':'kernel.event_log', 'runs':runs},indent=2,sort_keys=True)+'\n')
    print('Recorded',len(runs),'kernel event streams:',EVENTS)


def event(run,kind):
    matches=[e for e in run['events'] if e['kind']==kind]
    if len(matches)!=1: raise ValueError(f'{run["config"]}/{run["seed"]}: expected one {kind}')
    return matches[0]


def plot():
    data=json.loads(EVENTS.read_text());runs=data['runs']
    if len(runs)!=len(CONFIGS)*5: raise ValueError('incomplete event log')
    lookup={(r['config'],r['seed']):r for r in runs}
    for label,tiers,slots,prices,removed in CONFIGS:
        for seed in range(1,6):
            r=lookup[label,seed]
            if (r['tiers'],r['slots'],r['prices'],r['removed'])!=(tiers,slots,prices,removed):
                raise ValueError('switch provenance mismatch')
            quote=event(r,'ESA_BUILD_QUOTES');cash=event(r,'ESA_BUILD_FINANCING')
            readiness=event(r,'ESA_BUILD_READINESS');schedule=event(r,'ESA_BUILD_SCHEDULE')
            delivery=event(r,'ESA_BUILD_DELIVERY')
            if D(quote['winner_quote'])!=D(delivery['paid']): raise ValueError('payment != winning quote')
            if D(cash['committed'])!=D(delivery['paid']): raise ValueError('commitment != payment')
            if D(cash['pre_payment_cash'])!=D(delivery['pre_payment_cash']): raise ValueError('cash evidence mismatch')
            if bool(readiness['ready'])==bool(schedule['readiness_deferred']): raise ValueError('readiness schedule mismatch')
    pieces=[]
    def add(x):pieces.append(x)
    def rect(x,y,w,h,fill,stroke='none',radius=0):
        add(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{radius}" fill="{fill}" stroke="{stroke}"/>')
    def txt(x,y,value,size=15,weight='normal',color='#142944',anchor='start'):
        add(f'<text x="{x}" y="{y}" font-size="{size}" font-weight="{weight}" fill="{color}" text-anchor="{anchor}">{escape(str(value))}</text>')
    def money(v):return f'{D(v):.4f}'
    W,H=1520,1110
    add(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}">')
    rect(0,0,W,H,'#f4f7fb')
    txt(26,42,'ESA BUILD | Recorded-event experiment',30,'bold')
    txt(26,70,'Three quote cases · five readiness seeds · six switch cases · authored, non-canon',16,color='#4a617a')
    rect(20,94,1010,300,'white','#c4d5e6',12)
    rect(1042,94,458,300,'white','#c4d5e6',12)
    txt(40,127,'1  Fictional BUILD quotes and winners',22,'bold')
    cases=[('A1','Both explicit quotes'),('B1','Airbus quote removed / prices off'),('C1','Airbus quote removed / prices on')]
    ceiling=D(event(lookup['A1',1],'ESA_BUILD_FINANCING')['project_ceiling'])
    maxheight=170;bottom=326;scale=maxheight/float(ceiling)
    for i,(label,description) in enumerate(cases):
        quote=event(lookup[label,1],'ESA_BUILD_QUOTES');offers=quote['offered_quotes']
        x=95+i*305
        for j,(name,color) in enumerate((('Thales Alenia Space','#3579ba'),('Airbus Defence and Space','#2a9664'))):
            v=D(offers[name]) if name in offers else None
            bx=x+j*112
            if v is not None:
                height=float(v)*scale
                rect(bx,bottom-height,72,height,color)
                txt(bx+36,bottom-height-9,money(v),15,'bold',anchor='middle')
            else:txt(bx+36,bottom-35,'No quote',13,anchor='middle')
            txt(bx+36,bottom+19,name.split()[0],13,anchor='middle')
        txt(x+92,366,label+' · '+quote['winner'].split()[0]+' wins',15,'bold',anchor='middle')
        txt(x+92,385,description,11,anchor='middle')
    ceiling_y=bottom-float(ceiling)*scale
    add(f'<line x1="74" y1="{ceiling_y}" x2="965" y2="{ceiling_y}" stroke="#b14d42" stroke-dasharray="7,5"/>')
    txt(830,ceiling_y-9,'Ceiling '+money(ceiling),13,color='#b14d42')
    txt(1062,127,'Single named conversion parameter',20,'bold')
    txt(1062,164,'EXECUTOR_TO_NETWORK_FACTOR',16,'bold')
    txt(1062,191,str(EXECUTOR_TO_NETWORK_FACTOR),20,'bold')
    txt(1062,225,'NASA authored LAND buys one default lander.',14)
    # Read the fallback executor-unit default and actual recorded quote; never type plot numbers.
    defaults=json.loads((BASE/'capacity_authored_defaults.json').read_text())
    land=D(defaults['price_units_if_no_authored_quote']['LAND'])
    build=D(defaults['price_units_if_no_authored_quote']['BUILD'])
    txt(1062,260,f'LAND: {land} / factor = {money(land/EXECUTOR_TO_NETWORK_FACTOR)}',15)
    txt(1062,288,f'BUILD: {build} / factor = {money(build/EXECUTOR_TO_NETWORK_FACTOR)}',15)
    fallback=event(lookup['C1',1],'ESA_BUILD_QUOTES')
    if D(fallback['winner_quote']) != build/EXECUTOR_TO_NETWORK_FACTOR:raise ValueError('fallback conversion mismatch')
    txt(1062,324,'Division, never addition; authored price-scale only.',13,color='#4a617a')
    rect(20,407,1480,306,'white','#c4d5e6',12)
    txt(40,439,'2  Five-seed BUILD timeline (baseline A1)',22,'bold')
    for year in range(2026,2031):
        x=630+(year-2026)*154
        add(f'<line x1="{x}" y1="476" x2="{x}" y2="688" stroke="#d9e3ed"/>')
        txt(x+4,469,year,14)
    for seed in range(1,6):
        r=lookup['A1',seed];draw=event(r,'ESA_BUILD_READINESS');schedule=event(r,'ESA_BUILD_SCHEDULE')
        y=510+(seed-1)*42
        txt(55,y,f'Seed {seed}',15,'bold')
        txt(158,y,f'draw {D(draw["draw"]):.6f}',15)
        txt(323,y,'Ready' if draw['ready'] else 'Deferred',15,color='#21784b' if draw['ready'] else '#c35a24')
        start=int(schedule['start']);finish=int(schedule['finish'])
        rect(630+(start-2026)*154,y-17,(finish-start)*154,27,'#3579ba' if draw['ready'] else '#ed8b46',radius=3)
        txt(630+(start-2026)*154+8,y+2,f'BUILD {start}–{finish}',14,color='white')
    rect(20,726,1480,300,'white','#c4d5e6',12)
    txt(40,760,'3  Switch configurations (all five seeds per row)',22,'bold')
    headers=[('Config',45),('Tiers',135),('Slots',205),('Prices',275),('Removed quote',345),('Winner',695),('Quote',930),('Opening',1040),('Committed',1150),('Pre-payment',1280),('Headroom',1420)]
    for name,x in headers:txt(x,792,name,13,'bold')
    for i,(label,tiers,slots,prices,removed) in enumerate(CONFIGS):
        r=lookup[label,1];q=event(r,'ESA_BUILD_QUOTES');c=event(r,'ESA_BUILD_FINANCING')
        # All five seeds must agree on price and cash for a row.
        for seed in range(2,6):
            r2=lookup[label,seed]
            if event(r2,'ESA_BUILD_QUOTES')['offered_quotes']!=q['offered_quotes'] or event(r2,'ESA_BUILD_FINANCING')['committed']!=c['committed']:
                raise ValueError('seed changed deterministic quote/cash')
        y=821+i*29
        if i%2==0:rect(36,y-19,1447,27,'#eef4fa')
        values=[label,'On' if tiers else 'Off','On' if slots else 'Off','On' if prices else 'Off',
                removed or 'None',q['winner'].split()[0],money(q['winner_quote']),
                money(c['opening_cash']),money(c['committed']),money(c['pre_payment_cash']),
                money(D(c['pre_payment_cash'])-D(q['winner_quote']))]
        for (name,x),v in zip(headers,values):txt(x,y,v,13)
    txt(42,1039,'Source: committed kernel event_log streams; readiness p authored and uncalibrated.',14,color='#4a617a')
    txt(42,1066,'Slots: no contention test. Tiers: descriptive. Cash headroom zero by construction; helper bypasses original yearly execution.',13,color='#4a617a')
    txt(42,1091,'Figure reproducible from the committed JSON; frozen replay tests are verified separately, not inferred from this plot.',13,color='#4a617a')
    add('</svg>')
    FIGURE.write_text('\n'.join(pieces)+'\n')
    print('Plotted',FIGURE)


def main():
    parser=argparse.ArgumentParser();group=parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--record',action='store_true');group.add_argument('--plot',action='store_true')
    args=parser.parse_args()
    if args.record:record()
    else:plot()

if __name__=='__main__':main()
