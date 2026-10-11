# ESA BUILD-only experiment: idle actor inventory

Scope: the **20-sponsor network trial roster and its 16 selected executors**, not all 91 research-cast actors. The standalone ESA helper instantiates only ESA as purchaser and the selected winning BUILD supplier. These are **scenario participation reasons**, not evidence that any real organization is inactive.

## Sponsors (19 idle, ESA active)

| Actor | Reason idle in this run |
|---|---|
| NASA | LAND project; excluded by ESA-only selection |
| CNSA | LAND project; excluded by ESA-only selection |
| Roscosmos | LAUNCH project; outside BUILD-only selection |
| ISRO | BUILD project; excluded by ESA-only selection |
| JAXA | LAND project; excluded by ESA-only selection |
| CNES | BUILD project; excluded by ESA-only selection |
| DLR | BUILD project; excluded by ESA-only selection |
| CSA | RUN project; outside BUILD-only selection |
| KASA | LAUNCH project; outside BUILD-only selection |
| Australian Space Agency | BUILD project; excluded by ESA-only selection |
| UAE Space Agency | BUILD project; excluded by ESA-only selection |
| SpaceX | LAUNCH sponsor project; outside BUILD-only selection |
| Blue Origin | LAUNCH sponsor project; outside BUILD-only selection |
| Axiom | RUN project; outside BUILD-only selection |
| ispace | LAND project; excluded by ESA-only selection |
| Interlune | BUILD project; excluded by ESA-only selection |
| Isar Aerospace | LAUNCH project; outside BUILD-only selection |
| Starlab | RUN project; outside BUILD-only selection |
| LandSpace | LAUNCH project; outside BUILD-only selection |

## Selected executor roster (15 idle per run, one active)

| Actor | Reason idle in this run |
|---|---|
| Thales Alenia Space | Competing BUILD quote; loses to Airbus with both explicit quotes, **wins** when Airbus explicit quote removed and fallback prices off |
| Airbus Defence and Space | **Active winner** with both quotes or with price fallback on; idle when its explicit quote is removed and fallback prices are off |
| Astrobotic | Not offered a quote for the ESA BUILD service |
| Blue Origin | Not offered a quote for the ESA BUILD service |
| CASC | Not offered a quote for the ESA BUILD service |
| HAL / L&T | Not offered a quote for the ESA BUILD service |
| Hanwha Aerospace | Not offered a quote for the ESA BUILD service |
| Isar Aerospace | LAUNCH-only in selected network roster; no ESA BUILD quote |
| MDA Space | Not offered a quote for the ESA BUILD service |
| Mitsubishi Heavy Industries | Not offered a quote for the ESA BUILD service |
| Northrop Grumman | Not offered a quote for the ESA BUILD service |
| OHB | Not offered a quote for the ESA BUILD service |
| RKK Energia | Not offered a quote for the ESA BUILD service |
| SpaceX | Not offered a quote for the ESA BUILD service |
| Toyota | Not offered a quote for the ESA BUILD service |
| ispace | No ESA BUILD quote; selected network role is LAND/RUN |

Other master-cast actors are **not instantiated**, rather than assessed as idle. The German country capital pool and the authored financier are accounting participants, not competing sponsors or executors. No inference about multi-project contention is possible.

## Price-removal control and model limits

Removing Airbus's **explicit** quote does not remove its BUILD eligibility. With `prices=False`, it has no offer, so Thales's fictional 0.0270 wins. With `prices=True`, the existing BUILD executor fallback 1.70 is converted to network units using the selected NASA LAND anchor `200/3`, giving Airbus a fictional 0.0255 quote and the award. When the original explicit Airbus 0.0240 quote exists, it takes precedence in both modes. Slots are accepted as a switch but **not tested for behavioral effects**; no competing workload exists.

This is a standalone `run_esa_build()` helper **dispatched from** `run_yearly()` when selected. It bypasses `run_yearly()`'s original screened financing, policy and BUILD-then-LAND scheduling path. ESA cash headroom is **zero by construction**: the helper authorizes exactly the selected quote, commits exactly that amount and disburses it before payment. The original network trial's ESA cash is not carried into this helper and must not be added to it.
