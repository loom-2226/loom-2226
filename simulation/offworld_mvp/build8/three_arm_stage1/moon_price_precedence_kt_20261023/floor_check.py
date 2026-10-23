"""Strict mission floor for every campaign-consumed quote; list other below-floor quotes."""
import json,sys
from decimal import Decimal as D
from pathlib import Path
FLOOR=D('0.7')
def check(path):
 data=json.loads(Path(path).read_text());bad=[];used=[];tested=0
 for r in data['matrix']:
  if r['status']!='PRICED_TEST_ONLY':continue
  q=r['quotes'][0];f=q['price_fields'];unit=q.get('unit','USD')
  field=r.get('selected_field') or next(k for k in ('total_usd','lowest_price_usd','model_units','launch_cost_usd') if f.get(k) is not None)
  val=D(f[field]);model=val/D('1000000000') if unit=='USD' else val;tested+=1
  if model<FLOOR:
   item={'body':r['body'],'mission_type':r['mission_type'],'year':r['calendar_year'],'source':q['source'],'field':field,'value_model_units':str(model)}
   bad.append(item)
   if r['mission_type']=='rendezvous' and r['calendar_year']==2026:used.append(item)
 result={'file':str(path),'floor_model_units':str(FLOOR),'priced_rows_checked':tested,'all_below_floor':len(bad),'campaign_used_below_floor':len(used),'result':'FAIL' if used else 'PASS','unused_below_floor_rows':bad}
 print(json.dumps({'result':result['result'],'priced_rows_checked':tested,'all_below_floor':len(bad),'campaign_used_below_floor':len(used),'unused_examples':bad[:5]},sort_keys=True),flush=True)
 if used:raise AssertionError(f'MISSION_PRICE_FLOOR_FAIL: {len(used)} consumed quotes below {FLOOR}: {used}')
 return result
if __name__=='__main__':check(sys.argv[1])
