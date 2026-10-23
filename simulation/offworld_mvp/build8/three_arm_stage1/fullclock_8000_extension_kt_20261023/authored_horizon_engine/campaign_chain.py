"""Detached sequential campaigns after each required 2026 quote population is complete."""
import os,sys,time,subprocess,csv,json
from pathlib import Path
P=Path(__file__).resolve().parent;O=P.parent;world=list(csv.DictReader((O.parent/'RENDEZVOUS_WORLD_AUTHORITY_TEST_ONLY.csv').open()));moons=[r for r in world if r['parent'] and r['body'] not in ('DACTYL','SELAM')]
for limit in (1400,3000,5000,8000):
 report=P/f'fullclock_{limit}_days_report.json'
 if report.exists():print('ALREADY_COMPLETE',limit,flush=True);continue
 while True:
  if limit==1400:ready=report.exists()
  elif limit==8000:ready=all((P/'price_rows_8000'/(f"{r['body']}_2026_8000.json")).exists() for r in world)
  else:ready=all((O/'parent_corrected_price_rows'/(f"{r['body']}_2026_{limit}.json")).exists() for r in moons)
  if ready:break
  if limit==1400:print('WAIT_CAMPAIGN_1400',flush=True)
  elif limit==8000:print('WAIT_8000_2026_ROWS',sum((P/'price_rows_8000'/(f"{r['body']}_2026_8000.json")).exists() for r in world),'OF',len(world),flush=True)
  else:print('WAIT_MOON_CORRECTION',limit,sum((O/'parent_corrected_price_rows'/(f"{r['body']}_2026_{limit}.json")).exists() for r in moons),'OF',len(moons),flush=True)
  time.sleep(120)
 if report.exists():continue
 print('CAMPAIGN_START',limit,flush=True)
 x=subprocess.run([sys.executable,str(P/'make_campaign_inputs.py')],capture_output=True,text=True)
 if x.returncode:print('INPUT_FAIL',x.stderr[-800:],flush=True);break
 env=os.environ.copy();env['PR427_ONLY_LIMIT']=str(limit)
 x=subprocess.run([sys.executable,str(P/'run_four_campaigns.py')],capture_output=True,text=True,env=env)
 (P/f'campaign_{limit}_detached.log').write_text(x.stdout+'\n'+x.stderr)
 print('CAMPAIGN_END',limit,x.returncode,(x.stdout or x.stderr)[-350:],flush=True)
 if x.returncode:break
subprocess.run([sys.executable,str(P/'funnel.py')],capture_output=True,text=True)
