"""Read-only reconciliation between canonical campaign authority and shadow SQL.

The legacy HistoryLedger remains the sole parser/verifier for canonical history.
This module consumes its already-verified records and compares only the
FLIGHT_ARRIVED transitions mirrored by CampaignShadowLedger.
"""
from __future__ import annotations
from pathlib import Path
from typing import Any
import json, sqlite3
from .shadow_ledger import CampaignShadowLedger, SHADOW_LEDGER_CONTRACT
RECONCILIATION_CONTRACT="LOOM_CAMPAIGN_SHADOW_RECONCILIATION_V1"
class CampaignShadowReconciliationError(RuntimeError):pass
def _state(root:Path,core:Any)->dict[str,Any]:
    path=root/str(getattr(core,"STATE_FILE","LOOM_STATE_V1.json"))
    try:value=json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:raise CampaignShadowReconciliationError(f"cannot read canonical campaign state: {path}") from exc
    if not isinstance(value,dict):raise CampaignShadowReconciliationError("canonical campaign state must be a JSON object")
    validate=getattr(core,"_validate_state",None)
    if not callable(validate):raise CampaignShadowReconciliationError("canonical state validator unavailable")
    validate(value); return value
def reconcile_campaign_shadow(campaign_root:Path|str,core:Any)->dict[str,Any]:
    """Compare verified canonical flight-arrival history to shadow SQL without writes."""
    root=Path(campaign_root).expanduser().resolve(); state=_state(root,core); ledger_type=getattr(core,"HistoryLedger",None)
    if ledger_type is None:raise CampaignShadowReconciliationError("canonical HistoryLedger unavailable")
    history=ledger_type(root,state); verified=history.verify(); arrivals=[r for r in history.records if r.get("record_type")=="FLIGHT_ARRIVED"]
    shadow=CampaignShadowLedger(root); base={"contract":RECONCILIATION_CONTRACT,"shadow_contract":SHADOW_LEDGER_CONTRACT,"canonical_history_records":int(verified["records"]),"canonical_arrival_records":len(arrivals),"canonical_last_sha256":verified.get("last_sha256"),"canonical_state_revision":state.get("revision"),"shadow_path":str(shadow.path)}
    if not shadow.path.is_file():return {**base,"status":"MISSING_DB","match":False,"shadow_rows":0,"missing_in_sql":[str(r.get("flight_id") or "") for r in arrivals],"extra_in_sql":[],"mismatches":[],"revision_gaps":[],"shadow_latest_revision":None,"state_revision_aligned":False}
    try:
        uri=f"file:{shadow.path.as_posix()}?mode=ro"
        with sqlite3.connect(uri,uri=True) as conn:rows=conn.execute("SELECT flight_id,revision_before,revision_after,state_before_id,state_after_id,history_record_number,history_record_sha256,canonical_commit_json FROM campaign_flight_commits ORDER BY revision_after,flight_id").fetchall()
    except sqlite3.Error as exc:raise CampaignShadowReconciliationError(f"cannot read shadow SQL: {exc}") from exc
    sql={str(r[0]):r for r in rows}; canonical={str(r.get("flight_id") or ""):r for r in arrivals}; missing=sorted(set(canonical)-set(sql)); extra=sorted(set(sql)-set(canonical)); mismatches=[]
    for fid in sorted(set(canonical)&set(sql)):
        h=canonical[fid]; s=sql[fid]; after=h.get("state_after_snapshot") or {}
        if not isinstance(after,dict):after={}
        last=after.get("last_flight") or {}
        if not isinstance(last,dict):last={}
        expected={"history_record_number":int(h.get("record_number",-1)),"history_record_sha256":str(h.get("record_sha256") or ""),"state_before_id":last.get("departure_state_id"),"state_after_id":after.get("state_id")}; actual={"history_record_number":int(s[5]),"history_record_sha256":str(s[6]),"state_before_id":s[3],"state_after_id":s[4]}
        if after.get("revision") is not None:expected.update(revision_before=int(after["revision"])-1,revision_after=int(after["revision"])); actual.update(revision_before=int(s[1]),revision_after=int(s[2]))
        try:commit=json.loads(s[7])
        except Exception:commit={}
        if expected!=actual or str(commit.get("flight_id") or "")!=fid:mismatches.append({"flight_id":fid,"canonical":expected,"shadow":actual})
    revisions=sorted(int(r[2]) for r in rows); gaps=[[left,right] for left,right in zip(revisions,revisions[1:]) if right!=left+1]; latest_sql=max(revisions) if revisions else None; current_revision=state.get("revision"); state_aligned=(latest_sql is None and not arrivals) or (latest_sql is not None and current_revision is not None and int(latest_sql)==int(current_revision)); match=not missing and not extra and not mismatches and not gaps and state_aligned
    return {**base,"status":"MATCH" if match else "MISMATCH","match":match,"shadow_rows":len(rows),"missing_in_sql":missing,"extra_in_sql":extra,"mismatches":mismatches,"revision_gaps":gaps,"shadow_latest_revision":latest_sql,"state_revision_aligned":state_aligned}
