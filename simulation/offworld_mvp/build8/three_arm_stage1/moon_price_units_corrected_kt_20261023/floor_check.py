import json,sys
from decimal import Decimal as D
from pathlib import Path
FLOOR=D("0.7")
def check(path):
 data=json.loads(Path(path).read_text());bad=[];tested=0
 for r in data["matrix"]:
  if r["status"]!="PRICED_TEST_ONLY":continue
  q=r["quotes"][0];f=q["price_fields"];unit=q.get("unit")
  if unit is None:unit="model_units" if "model_units" in f and "lowest_price_usd" not in f and "total_usd" not in f and "launch_cost_usd" not in f else "USD"
  val=next((f[k] for k in ("lowest_price_usd","total_usd","model_units","launch_cost_usd") if f.get(k) is not None),None)
  if val is None:raise AssertionError(f"PRICED_WITHOUT_PRICE: {r['body']} {r['mission_type']} {r['calendar_year']}")
  model=D(val)/D("1000000000") if unit=="USD" else D(val)
  tested+=1
  if model<FLOOR:bad.append(dict(body=r['body'],year=r['calendar_year'],mission_type=r['mission_type'],model_units=str(model),source=q['source']))
 print(json.dumps(dict(file=str(path),tested=tested,floor_model_units=str(FLOOR),violations=len(bad),examples=bad[:25],result="FAIL" if bad else "PASS"),sort_keys=True))
 if bad:raise AssertionError(f"MISSION_PRICE_FLOOR_FAIL: {len(bad)} priced rows below {FLOOR} model units")
if __name__=="__main__":check(sys.argv[1])
