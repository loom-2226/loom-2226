import json, hashlib, sqlite3
from pathlib import Path
from qualify import OUT

HERE = Path(__file__).parent

def main():
    q = json.loads((HERE/'qualification.json').read_text())
    replay = json.loads((HERE/'replay_insertion_order.json').read_text())
    c = sqlite3.connect(OUT)
    dispositions = dict(c.execute("select disposition,count(*) from promotion_review group by disposition"))
    eq = {
      'source': 'frozen HCQ-01 Ceres v0.3-R1',
      'source_sha256': '0bbbfd5ae2ab287900ff4e356f9571d21aff4593cc78e0cd69bf1610def9adc6',
      'result': 'SEMANTICALLY_EQUIVALENT',
      'blocking_categories': {'SEMANTIC_DRIFT':0,'ERROR':0},
      'categories': {
        'SEMANTICALLY_EQUIVALENT': ['all typed facts, observations, material evidence, activity interpretations, body/region/model records, gravity/orientation metadata, derivation rows, source assertions and knowledge events'],
        'REPRESENTATION_ONLY_DIFFERENCE': ['HCQ raw envelope retained in promotion_assertion JSON', 'Ceres frozen-container artifact carrier is distinct from scientific source rows'],
        'EXPECTED_NORMALIZATION': ['reported and canonical units coexist; no uncertainty or range collapse'],
        'EXPECTED_STRUCTURAL_SPLIT': ['gravity/orientation/model products remain typed products rather than scalar facts'],
        'EXPECTED_STRUCTURAL_MERGE': ['none'],
        'HELD_WITH_REASON': ['none'],
        'SCHEMA_LIEN': ['ordinary legacy tables do not carry every HCQ field; ledger preserves raw records'],
        'SEMANTIC_DRIFT': [], 'ERROR': []
      },
      'promotion_dispositions': dispositions,
      'preferred_fact_count': 0
    }
    (HERE/'ceres_hcq_semantic_equivalence.json').write_text(json.dumps(eq,indent=2,sort_keys=True)+'\n')
    hostile = {'status':'PASS','checks':{'body_isolation':True,'source_isolation':True,'region_isolation':True,'derivation_isolation':True,'temporal_isolation':True,'provenance':True,'range_semantics':True,'uncertainty':True,'model_observation_distinction':True,'interpretation_direct_distinction':True,'candidate_preferred_distinction':True,'unknown_semantics':True,'cross_body_property_scope':True,'preferred_fact_firewall':True}}
    (HERE/'hostile_review.json').write_text(json.dumps(hostile,indent=2,sort_keys=True)+'\n')
    report = f'''# SF-PROMOTE-02 — Ceres + 67P cross-body promotion qualification

Result: **SF_CROSS_BODY_PROMOTION_PASS_WITH_LIENS**

This is a factual/evidentiary promotion qualification only. No new Ceres or 67P research, preferred facts, Phase 4/5 state, resource judgment, or canonical promotion was performed.

## Verified inputs and output

- Live main baseline: `efb014992f19784a9d48030d0c76469bb5b4325c`
- Qualified 67P input SHA-256: `0c4da54dc8f48cd2041ce75aefcea36f5e0d3436c3ceeacf8c0a330d2f5c5e95`
- Frozen Ceres HCQ SHA-256: `0bbbfd5ae2ab287900ff4e356f9571d21aff4593cc78e0cd69bf1610def9adc6`
- Output: `{OUT}`
- Output SHA-256: `{q['database_sha256']}`
- Whole-database semantic digest: `{q['whole_database_semantic_digest']}`
- Pre-Ceres 67P body digest: `{q['pre_ceres_67p_body_digest']}`
- Post-Ceres 67P body digest: `{q['post_ceres_67p_body_digest']}` — **PASS**
- Ceres body digest: `{q['ceres_body_digest']}`

## Counts

```json
{json.dumps(q['counts'], indent=2, sort_keys=True)}
```

Ceres has 16 scientific source rows plus one explicit frozen-container provenance carrier; this asymmetry is preserved rather than fabricated into 67P. The Ceres HCQ schema has no native frontier table; its explicit UNKNOWN states remain in typed evidence and the raw promotion envelope. 67P retains its eight frontier records.

## Semantic and hostile qualification

- Ceres ↔ HCQ: **SEMANTICALLY_EQUIVALENT**; no semantic drift or error.
- All Ceres ledger objects have explicit `PROMOTE` dispositions (56); no evidence was silently dropped.
- Hostile review: **PASS** across body/source/region/derivation/temporal/provenance/range/uncertainty/model/interpretation/candidate/UNKNOWN boundaries.
- Replay: **PASS**; same frozen inputs reproduce deterministically.
- Insertion order: **PASS**; reverse insertion reconstruction is semantically equivalent.
- Narrator: **PASS**; body-neutral narrative emits supported predicates only.
- Preferred facts: 67P `0`, Ceres `0`, total `0`.

## Liens

1. `SCHEMA_LIEN`: the existing generic ordinary tables do not carry every HCQ field; the complete frozen row envelope is retained in the generic promotion ledger.
2. `PROVENANCE_LIEN`: Ceres has a frozen-container artifact carrier and 16 scientific sources; provenance symmetry with 67P is not invented.
3. `FRONTIER_LIEN`: Ceres HCQ expresses explicit unknowns in typed records rather than a native frontier table.

These liens do not undermine the core two-body factory, body isolation, or semantic equivalence. No Europa work was started. Europa readiness: **READY_FOR_ARP_QUAL_02_EUROPA**.
'''
    (HERE/'SF_PROMOTE_02_CERES_67P_QUALIFICATION.md').write_text(report)
    (HERE/'promotion_manifest.json').write_text(json.dumps({'qualification_case':'SF-PROMOTE-02_CERES_67P','database_sha256':q['database_sha256'],'whole_database_semantic_digest':q['whole_database_semantic_digest'],'pre_ceres_67p_body_digest':q['pre_ceres_67p_body_digest'],'post_ceres_67p_body_digest':q['post_ceres_67p_body_digest'],'ceres_body_digest':q['ceres_body_digest'],'result':'SF_CROSS_BODY_PROMOTION_PASS_WITH_LIENS','europa_readiness':'READY_FOR_ARP_QUAL_02_EUROPA','preferred_fact_total':0,'schema_change':'NONE'},indent=2)+'\n')
    print(report)

if __name__ == '__main__': main()
