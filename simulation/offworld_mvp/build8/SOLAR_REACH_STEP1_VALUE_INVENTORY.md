# SOLAR REACH Step 1: Complete Route 1 experiment-value inventory

**PROPOSAL ONLY, NOT AN EXECUTED SCENARIO.** GitHub main 19377b854c529e74afc61202d9eb2e780c5b4884.
This inventory resolves existing Python constants, runtime defaults and inherited financier settings without simulating a campaign. The single authored scenario owns proposed values, external source digests and two options; no current Route 1 code consumes it.

Scenario SHA-256: `2551c693b73156f4d81ba3b3d0cbc566be9ec411728cf8e434502c1f95534f81`. Values are also fully serialized in `solar_reach_scenario.json`.

## Every identified effective experiment input

Paths are relative to the repository root. A few derived values have the defining assignment line rather than individual key lines. Category/source coverage details are pinned, not copied in full from Earth v4.

| File:line | Value / parameter | Effective value in existing Route 1 |
|---|---|---|
| `simulation/offworld_mvp/build8/country_capital_input.py:9` | `source horizon boundary` | `{"qualified_end":2031,"stage_end":2060,"successor_end":2226}` |
| `simulation/offworld_mvp/build8/four_usa_financier.py:12` | `SEED` | `"BUILD8_USA_FINANCIER_TEST_0"` |
| `simulation/offworld_mvp/build8/four_usa_financier.py:14` | `UNDERWRITING:underwriting.DEVELOPMENT_CAPEX` | `".125"` |
| `simulation/offworld_mvp/build8/four_usa_financier.py:14` | `UNDERWRITING:underwriting.EXPLORATION_CAPEX` | `".125"` |
| `simulation/offworld_mvp/build8/four_usa_financier.py:14` | `UNDERWRITING:underwriting.LEAD_TIME` | `"1"` |
| `simulation/offworld_mvp/build8/four_usa_financier.py:14` | `UNDERWRITING:underwriting.OPERATING_COST` | `".5"` |
| `simulation/offworld_mvp/build8/four_usa_financier.py:14` | `UNDERWRITING:underwriting.PRICE` | `"1"` |
| `simulation/offworld_mvp/build8/opening.py:16` | `Build8 Earth opening defaults` | `{"end_year":2035,"world_seed":"BUILD8-80-COUNTRY-10-YEAR"}` |
| `simulation/offworld_mvp/build8/route1_all_body_campaign_pr3b.py:22` | `AUTHORING:BENNU` | `["BENNU-A1-RESOURCE","BENNU-A2-CONCEPT"]` |
| `simulation/offworld_mvp/build8/route1_all_body_campaign_pr3b.py:23` | `AUTHORING:CERES` | `["CERES-A1-SURFACE","CERES-A2-ASSESS"]` |
| `simulation/offworld_mvp/build8/route1_all_body_campaign_pr3b.py:24` | `AUTHORING:MARS` | `["MARS-A1-REMOTE","MARS-A2-SURFACE"]` |
| `simulation/offworld_mvp/build8/route1_all_body_campaign_pr3b.py:25` | `AUTHORING:MOON` | `["MOON-A1-SURFACE","MOON-A2-ASSESS"]` |
| `simulation/offworld_mvp/build8/route1_all_body_campaign_pr3b.py:28` | `PR3B_SETTINGS:A1_REOPEN_ON` | `["INSUFFICIENT","NO_RESULT"]` |
| `simulation/offworld_mvp/build8/route1_all_body_campaign_pr3b.py:29` | `PR3B_SETTINGS:A1_REOPEN_AT` | `"NEXT_YEARLY_DECISION_AFTER_REVIEW"` |
| `simulation/offworld_mvp/build8/route1_all_body_campaign_pr3b.py:30` | `PR3B_SETTINGS:A1_RETRY_LIMIT` | `null` |
| `simulation/offworld_mvp/build8/route1_all_body_campaign_pr3b.py:31` | `PR3B_SETTINGS:A1_RETRY_DRAW_KEY` | `"A1_REVIEW_SEED\|BODY\|A1\|ATTEMPT (first attempt unchanged)"` |
| `simulation/offworld_mvp/build8/route1_all_body_campaign_pr3b.py:32` | `PR3B_SETTINGS:MAX_ACTIVE_CLAIMANTS_PER_BODY` | `1` |
| `simulation/offworld_mvp/build8/route1_all_body_campaign_pr3b.py:33` | `PR3B_SETTINGS:SPONSOR_ALLOCATION_ORDER` | `"REPEATED_CAST_ID_ROUNDS"` |
| `simulation/offworld_mvp/build8/route1_all_body_campaign_pr3b.py:34` | `PR3B_SETTINGS:A1_RESULT_SOURCE` | `"BUILD6C_AUTHORED_OR_SHA256_TEST_ONLY"` |
| `simulation/offworld_mvp/build8/route1_all_body_campaign_pr3b.py:35` | `PR3B_SETTINGS:CHECKPOINT_BODY_COUNT` | `45` |
| `simulation/offworld_mvp/build8/route1_all_body_campaign_pr3b.py:36` | `PR3B_SETTINGS:BODY_COUNT` | `90` |
| `simulation/offworld_mvp/build8/route1_all_body_campaign_pr3b.py:37` | `PR3B_SETTINGS:ACCESS_UNKNOWN_TREATMENT` | `"ABSTRACT_STUDY_ONLY_NO_TRAJECTORY"` |
| `simulation/offworld_mvp/build8/route1_all_body_campaign_pr3b.py:38` | `PR3B_SETTINGS:MAX_NEW_STAGES_PER_SPONSOR_YEAR` | `null` |
| `simulation/offworld_mvp/build8/route1_all_body_campaign_pr3b.py:40` | `ALL_BODIES` | `["AMUN","APOPHIS","ARIEL","ARROKOTH","ASTEROID_6178","ATLAS3I","BENNU","BORISOV","BORRELLY","BRAILLE","CALLISTO","CERES","CHARON","CHIRON","COMET_67P","COMET_HALLEY","DACTYL","DAVIDA","DEIMOS","DIDYMOS","DINKINESH","DIONE","DONALDJOHANSON","ENCELADUS","ERIS","EROS","EUROPA","EURYBATES","GANYMEDE","GASPRA","GONGGONG","HARTLEY2","HAUMEA","HYDRA","HYGIEA","HYPERION","IAPETUS","IDA","INTERAMNIA","IO",… [full value in scenario]` |
| `simulation/offworld_mvp/build8/route1_all_body_campaign_pr3b.py:40` | `body catalog admission filter` | `["SOLID","SOLID_WITH_ATMOSPHERE"]` |
| `simulation/offworld_mvp/build8/route1_all_body_campaign_pr3b.py:44` | `REFERENCE_STATUS:AMUN` | `"DERIVABLE"` |
| `simulation/offworld_mvp/build8/route1_all_body_campaign_pr3b.py:44` | `REFERENCE_STATUS:APOPHIS` | `"DERIVABLE"` |
| `simulation/offworld_mvp/build8/route1_all_body_campaign_pr3b.py:44` | `REFERENCE_STATUS:ARIEL` | `"DERIVABLE"` |
| `simulation/offworld_mvp/build8/route1_all_body_campaign_pr3b.py:44` | `REFERENCE_STATUS:ARROKOTH` | `"DERIVABLE"` |
| `simulation/offworld_mvp/build8/route1_all_body_campaign_pr3b.py:44` | `REFERENCE_STATUS:ASTEROID_6178` | `"DERIVABLE"` |
| `simulation/offworld_mvp/build8/route1_all_body_campaign_pr3b.py:44` | `REFERENCE_STATUS:ATLAS3I` | `"DERIVABLE"` |
| `simulation/offworld_mvp/build8/route1_all_body_campaign_pr3b.py:44` | `REFERENCE_STATUS:BENNU` | `"DERIVABLE"` |
| `simulation/offworld_mvp/build8/route1_all_body_campaign_pr3b.py:44` | `REFERENCE_STATUS:BORISOV` | `"DERIVABLE"` |
| `simulation/offworld_mvp/build8/route1_all_body_campaign_pr3b.py:44` | `REFERENCE_STATUS:BORRELLY` | `"DERIVABLE"` |
| `simulation/offworld_mvp/build8/route1_all_body_campaign_pr3b.py:44` | `REFERENCE_STATUS:BRAILLE` | `"DERIVABLE"` |
| `simulation/offworld_mvp/build8/route1_all_body_campaign_pr3b.py:44` | `REFERENCE_STATUS:CALLISTO` | `"DERIVABLE"` |
| `simulation/offworld_mvp/build8/route1_all_body_campaign_pr3b.py:44` | `REFERENCE_STATUS:CERES` | `"DERIVABLE"` |
| `simulation/offworld_mvp/build8/route1_all_body_campaign_pr3b.py:44` | `REFERENCE_STATUS:CHARON` | `"DERIVABLE"` |
| `simulation/offworld_mvp/build8/route1_all_body_campaign_pr3b.py:44` | `REFERENCE_STATUS:CHIRON` | `"DERIVABLE"` |
| `simulation/offworld_mvp/build8/route1_all_body_campaign_pr3b.py:44` | `REFERENCE_STATUS:COMET_67P` | `"DERIVABLE"` |
| `simulation/offworld_mvp/build8/route1_all_body_campaign_pr3b.py:44` | `REFERENCE_STATUS:COMET_HALLEY` | `"DERIVABLE"` |
| `simulation/offworld_mvp/build8/route1_all_body_campaign_pr3b.py:44` | `REFERENCE_STATUS:DACTYL` | `"UNKNOWN"` |
| `simulation/offworld_mvp/build8/route1_all_body_campaign_pr3b.py:44` | `REFERENCE_STATUS:DAVIDA` | `"DERIVABLE"` |
| `simulation/offworld_mvp/build8/route1_all_body_campaign_pr3b.py:44` | `REFERENCE_STATUS:DEIMOS` | `"DERIVABLE"` |
| `simulation/offworld_mvp/build8/route1_all_body_campaign_pr3b.py:44` | `REFERENCE_STATUS:DIDYMOS` | `"DERIVABLE"` |
| `simulation/offworld_mvp/build8/route1_all_body_campaign_pr3b.py:44` | `REFERENCE_STATUS:DINKINESH` | `"DERIVABLE"` |
| `simulation/offworld_mvp/build8/route1_all_body_campaign_pr3b.py:44` | `REFERENCE_STATUS:DIONE` | `"DERIVABLE"` |
| `simulation/offworld_mvp/build8/route1_all_body_campaign_pr3b.py:44` | `REFERENCE_STATUS:DONALDJOHANSON` | `"DERIVABLE"` |
| `simulation/offworld_mvp/build8/route1_all_body_campaign_pr3b.py:44` | `REFERENCE_STATUS:ENCELADUS` | `"DERIVABLE"` |
| `simulation/offworld_mvp/build8/route1_all_body_campaign_pr3b.py:44` | `REFERENCE_STATUS:ERIS` | `"DERIVABLE"` |
| `simulation/offworld_mvp/build8/route1_all_body_campaign_pr3b.py:44` | `REFERENCE_STATUS:EROS` | `"DERIVABLE"` |
| `simulation/offworld_mvp/build8/route1_all_body_campaign_pr3b.py:44` | `REFERENCE_STATUS:EUROPA` | `"DERIVABLE"` |
| `simulation/offworld_mvp/build8/route1_all_body_campaign_pr3b.py:44` | `REFERENCE_STATUS:EURYBATES` | `"DERIVABLE"` |
| `simulation/offworld_mvp/build8/route1_all_body_campaign_pr3b.py:44` | `REFERENCE_STATUS:GANYMEDE` | `"DERIVABLE"` |
| `simulation/offworld_mvp/build8/route1_all_body_campaign_pr3b.py:44` | `REFERENCE_STATUS:GASPRA` | `"DERIVABLE"` |
| `simulation/offworld_mvp/build8/route1_all_body_campaign_pr3b.py:44` | `REFERENCE_STATUS:GONGGONG` | `"DERIVABLE"` |
| `simulation/offworld_mvp/build8/route1_all_body_campaign_pr3b.py:44` | `REFERENCE_STATUS:HARTLEY2` | `"DERIVABLE"` |
| `simulation/offworld_mvp/build8/route1_all_body_campaign_pr3b.py:44` | `REFERENCE_STATUS:HAUMEA` | `"DERIVABLE"` |
| `simulation/offworld_mvp/build8/route1_all_body_campaign_pr3b.py:44` | `REFERENCE_STATUS:HYDRA` | `"UNKNOWN"` |
| `simulation/offworld_mvp/build8/route1_all_body_campaign_pr3b.py:44` | `REFERENCE_STATUS:HYGIEA` | `"DERIVABLE"` |
| `simulation/offworld_mvp/build8/route1_all_body_campaign_pr3b.py:44` | `REFERENCE_STATUS:HYPERION` | `"DERIVABLE"` |
| `simulation/offworld_mvp/build8/route1_all_body_campaign_pr3b.py:44` | `REFERENCE_STATUS:IAPETUS` | `"DERIVABLE"` |
| `simulation/offworld_mvp/build8/route1_all_body_campaign_pr3b.py:44` | `REFERENCE_STATUS:IDA` | `"DERIVABLE"` |
| `simulation/offworld_mvp/build8/route1_all_body_campaign_pr3b.py:44` | `REFERENCE_STATUS:INTERAMNIA` | `"DERIVABLE"` |
| `simulation/offworld_mvp/build8/route1_all_body_campaign_pr3b.py:44` | `REFERENCE_STATUS:IO` | `"DERIVABLE"` |
| `simulation/offworld_mvp/build8/route1_all_body_campaign_pr3b.py:44` | `REFERENCE_STATUS:ITOKAWA` | `"DERIVABLE"` |
| `simulation/offworld_mvp/build8/route1_all_body_campaign_pr3b.py:44` | `REFERENCE_STATUS:IXION` | `"DERIVABLE"` |
| `simulation/offworld_mvp/build8/route1_all_body_campaign_pr3b.py:44` | `REFERENCE_STATUS:JUNO` | `"DERIVABLE"` |
| `simulation/offworld_mvp/build8/route1_all_body_campaign_pr3b.py:44` | `REFERENCE_STATUS:KERBEROS` | `"UNKNOWN"` |
| `simulation/offworld_mvp/build8/route1_all_body_campaign_pr3b.py:44` | `REFERENCE_STATUS:KLEOPATRA` | `"DERIVABLE"` |
| `simulation/offworld_mvp/build8/route1_all_body_campaign_pr3b.py:44` | `REFERENCE_STATUS:LEUCUS` | `"DERIVABLE"` |
| `simulation/offworld_mvp/build8/route1_all_body_campaign_pr3b.py:44` | `REFERENCE_STATUS:LUTETIA` | `"DERIVABLE"` |
| `simulation/offworld_mvp/build8/route1_all_body_campaign_pr3b.py:44` | `REFERENCE_STATUS:MAKEMAKE` | `"DERIVABLE"` |
| `simulation/offworld_mvp/build8/route1_all_body_campaign_pr3b.py:44` | `REFERENCE_STATUS:MARS` | `"DERIVABLE"` |
| `simulation/offworld_mvp/build8/route1_all_body_campaign_pr3b.py:44` | `REFERENCE_STATUS:MATHILDE` | `"DERIVABLE"` |
| `simulation/offworld_mvp/build8/route1_all_body_campaign_pr3b.py:44` | `REFERENCE_STATUS:MERCURY` | `"DERIVABLE"` |
| `simulation/offworld_mvp/build8/route1_all_body_campaign_pr3b.py:44` | `REFERENCE_STATUS:MIMAS` | `"DERIVABLE"` |
| `simulation/offworld_mvp/build8/route1_all_body_campaign_pr3b.py:44` | `REFERENCE_STATUS:MIRANDA` | `"DERIVABLE"` |
| `simulation/offworld_mvp/build8/route1_all_body_campaign_pr3b.py:44` | `REFERENCE_STATUS:MOON` | `"DERIVABLE"` |
| `simulation/offworld_mvp/build8/route1_all_body_campaign_pr3b.py:44` | `REFERENCE_STATUS:MS4` | `"DERIVABLE"` |
| `simulation/offworld_mvp/build8/route1_all_body_campaign_pr3b.py:44` | `REFERENCE_STATUS:NEREID` | `"DERIVABLE"` |
| `simulation/offworld_mvp/build8/route1_all_body_campaign_pr3b.py:44` | `REFERENCE_STATUS:NIX` | `"UNKNOWN"` |
| `simulation/offworld_mvp/build8/route1_all_body_campaign_pr3b.py:44` | `REFERENCE_STATUS:OBERON` | `"DERIVABLE"` |
| `simulation/offworld_mvp/build8/route1_all_body_campaign_pr3b.py:44` | `REFERENCE_STATUS:ORCUS` | `"DERIVABLE"` |
| `simulation/offworld_mvp/build8/route1_all_body_campaign_pr3b.py:44` | `REFERENCE_STATUS:ORUS` | `"DERIVABLE"` |
| `simulation/offworld_mvp/build8/route1_all_body_campaign_pr3b.py:44` | `REFERENCE_STATUS:OUMUAMUA` | `"DERIVABLE"` |
| `simulation/offworld_mvp/build8/route1_all_body_campaign_pr3b.py:44` | `REFERENCE_STATUS:PALLAS` | `"DERIVABLE"` |
| `simulation/offworld_mvp/build8/route1_all_body_campaign_pr3b.py:44` | `REFERENCE_STATUS:PATROCLUS` | `"DERIVABLE"` |
| `simulation/offworld_mvp/build8/route1_all_body_campaign_pr3b.py:44` | `REFERENCE_STATUS:PHOBOS` | `"DERIVABLE"` |
| `simulation/offworld_mvp/build8/route1_all_body_campaign_pr3b.py:44` | `REFERENCE_STATUS:PHOEBE` | `"DERIVABLE"` |
| `simulation/offworld_mvp/build8/route1_all_body_campaign_pr3b.py:44` | `REFERENCE_STATUS:PLUTO` | `"DERIVABLE"` |
| `simulation/offworld_mvp/build8/route1_all_body_campaign_pr3b.py:44` | `REFERENCE_STATUS:POLYMELE` | `"DERIVABLE"` |
| `simulation/offworld_mvp/build8/route1_all_body_campaign_pr3b.py:44` | `REFERENCE_STATUS:PROTEUS` | `"UNKNOWN"` |
| `simulation/offworld_mvp/build8/route1_all_body_campaign_pr3b.py:44` | `REFERENCE_STATUS:PSYCHE` | `"DERIVABLE"` |
| `simulation/offworld_mvp/build8/route1_all_body_campaign_pr3b.py:44` | `REFERENCE_STATUS:QUAOAR` | `"DERIVABLE"` |
| `simulation/offworld_mvp/build8/route1_all_body_campaign_pr3b.py:44` | `REFERENCE_STATUS:RHEA` | `"DERIVABLE"` |
| `simulation/offworld_mvp/build8/route1_all_body_campaign_pr3b.py:44` | `REFERENCE_STATUS:RYUGU` | `"DERIVABLE"` |
| `simulation/offworld_mvp/build8/route1_all_body_campaign_pr3b.py:44` | `REFERENCE_STATUS:SALACIA` | `"DERIVABLE"` |
| `simulation/offworld_mvp/build8/route1_all_body_campaign_pr3b.py:44` | `REFERENCE_STATUS:SEDNA` | `"DERIVABLE"` |
| `simulation/offworld_mvp/build8/route1_all_body_campaign_pr3b.py:44` | `REFERENCE_STATUS:SELAM` | `"UNKNOWN"` |
| `simulation/offworld_mvp/build8/route1_all_body_campaign_pr3b.py:44` | `REFERENCE_STATUS:STEINS` | `"DERIVABLE"` |
| `simulation/offworld_mvp/build8/route1_all_body_campaign_pr3b.py:44` | `REFERENCE_STATUS:STYX` | `"UNKNOWN"` |
| `simulation/offworld_mvp/build8/route1_all_body_campaign_pr3b.py:44` | `REFERENCE_STATUS:SWIFTTUTTLE` | `"DERIVABLE"` |
| `simulation/offworld_mvp/build8/route1_all_body_campaign_pr3b.py:44` | `REFERENCE_STATUS:TEMPEL1` | `"DERIVABLE"` |
| `simulation/offworld_mvp/build8/route1_all_body_campaign_pr3b.py:44` | `REFERENCE_STATUS:TETHYS` | `"DERIVABLE"` |
| `simulation/offworld_mvp/build8/route1_all_body_campaign_pr3b.py:44` | `REFERENCE_STATUS:THEMIS` | `"DERIVABLE"` |
| `simulation/offworld_mvp/build8/route1_all_body_campaign_pr3b.py:44` | `REFERENCE_STATUS:TITAN` | `"DERIVABLE"` |
| `simulation/offworld_mvp/build8/route1_all_body_campaign_pr3b.py:44` | `REFERENCE_STATUS:TITANIA` | `"DERIVABLE"` |
| `simulation/offworld_mvp/build8/route1_all_body_campaign_pr3b.py:44` | `REFERENCE_STATUS:TOUTATIS` | `"DERIVABLE"` |
| `simulation/offworld_mvp/build8/route1_all_body_campaign_pr3b.py:44` | `REFERENCE_STATUS:TRITON` | `"DERIVABLE"` |
| `simulation/offworld_mvp/build8/route1_all_body_campaign_pr3b.py:44` | `REFERENCE_STATUS:UMBRIEL` | `"DERIVABLE"` |
| `simulation/offworld_mvp/build8/route1_all_body_campaign_pr3b.py:44` | `REFERENCE_STATUS:VARUNA` | `"DERIVABLE"` |
| `simulation/offworld_mvp/build8/route1_all_body_campaign_pr3b.py:44` | `REFERENCE_STATUS:VENUS` | `"DERIVABLE"` |
| `simulation/offworld_mvp/build8/route1_all_body_campaign_pr3b.py:44` | `REFERENCE_STATUS:VESTA` | `"DERIVABLE"` |
| `simulation/offworld_mvp/build8/route1_all_body_campaign_pr3b.py:44` | `REFERENCE_STATUS:WILD2` | `"DERIVABLE"` |
| `simulation/offworld_mvp/build8/route1_all_body_campaign_pr3b.py:49` | `reference accessibility totals` | `{"DERIVABLE":83,"UNKNOWN":7}` |
| `simulation/offworld_mvp/build8/route1_all_body_campaign_pr3b.py:181` | `repeated A1 result decision` | `"SHA256(seed\|body\|A1\|attempt) < fraction"` |
| `simulation/offworld_mvp/build8/route1_all_body_campaign_pr3b.py:314` | `all-body runner defaults` | `{"body_count":90,"ceilings_enabled":true,"end_year":2226,"failures":[],"participating_sponsors":null}` |
| `simulation/offworld_mvp/build8/route1_all_body_campaign_pr3b.py:318` | `report first year` | `"2026"` |
| `simulation/offworld_mvp/build8/route1_body_campaign.py:21` | `BODIES` | `["EUROPA","PHOBOS"]` |
| `simulation/offworld_mvp/build8/route1_body_campaign.py:22` | `HISTORICAL_BODIES` | `["BENNU","CERES","MARS","MOON"]` |
| `simulation/offworld_mvp/build8/route1_body_campaign.py:25` | `ORDER` | `["Australian Space Agency","Axiom","Blue Origin","CNES","CNSA","CSA","DLR","ESA","Interlune","Isar Aerospace","ispace","ISRO","JAXA","KASA","LandSpace","NASA","Roscosmos","SpaceX","Starlab","UAE Space Agency"]` |
| `simulation/offworld_mvp/build8/route1_body_campaign.py:30` | `SETTINGS:CAMPAIGN_START_YEAR` | `2036` |
| `simulation/offworld_mvp/build8/route1_body_campaign.py:31` | `SETTINGS:CAMPAIGN_END_YEAR` | `2226` |
| `simulation/offworld_mvp/build8/route1_body_campaign.py:32` | `SETTINGS:MAX_NEW_STAGES_PER_SPONSOR_YEAR` | `1` |
| `simulation/offworld_mvp/build8/route1_body_campaign.py:33` | `SETTINGS:MAX_CLAIMANTS_PER_BODY_CAMPAIGN` | `1` |
| `simulation/offworld_mvp/build8/route1_body_campaign.py:34` | `SETTINGS:MAX_AUTHORED_STAGE` | `"A2"` |
| `simulation/offworld_mvp/build8/route1_body_campaign.py:35` | `SETTINGS:SPONSOR_CLAIM_ORDER` | `["Australian Space Agency","Axiom","Blue Origin","CNES","CNSA","CSA","DLR","ESA","Interlune","Isar Aerospace","ispace","ISRO","JAXA","KASA","LandSpace","NASA","Roscosmos","SpaceX","Starlab","UAE Space Agency"]` |
| `simulation/offworld_mvp/build8/route1_body_campaign.py:36` | `SETTINGS:BODY_SELECTION_ORDER` | `["EUROPA","PHOBOS"]` |
| `simulation/offworld_mvp/build8/route1_body_campaign.py:37` | `SETTINGS:A1_POSITIVE_REVIEW_FRACTION` | `"0.50"` |
| `simulation/offworld_mvp/build8/route1_body_campaign.py:38` | `SETTINGS:A1_REVIEW_SEED` | `"ROUTE1_BODY_PR3A_V1"` |
| `simulation/offworld_mvp/build8/route1_body_campaign.py:39` | `SETTINGS:STUDY_DURATION_YEARS` | `1` |
| `simulation/offworld_mvp/build8/route1_body_campaign.py:40` | `SETTINGS:A1_SERVICE_CATEGORY` | `"RUN"` |
| `simulation/offworld_mvp/build8/route1_body_campaign.py:41` | `SETTINGS:A1_SERVICE_PRICE` | `".015"` |
| `simulation/offworld_mvp/build8/route1_body_campaign.py:42` | `SETTINGS:A2_SERVICE_CATEGORY` | `"BUILD"` |
| `simulation/offworld_mvp/build8/route1_body_campaign.py:43` | `SETTINGS:A2_SERVICE_PRICE` | `".015"` |
| `simulation/offworld_mvp/build8/route1_body_campaign.py:44` | `SETTINGS:COUNTRY_ALLOCATION_SHARE` | `"0.25"` |
| `simulation/offworld_mvp/build8/route1_body_campaign.py:45` | `SETTINGS:FINANCIER_RESOURCE_BELIEF` | `"0.5"` |
| `simulation/offworld_mvp/build8/route1_body_campaign.py:46` | `SETTINGS:FINANCIER_RESOURCE_PRIOR` | `"0.5"` |
| `simulation/offworld_mvp/build8/route1_body_campaign.py:47` | `SETTINGS:FINANCIER_UNDERWRITING_FACTS` | `{"underwriting.DEVELOPMENT_CAPEX":".125","underwriting.EXPLORATION_CAPEX":".125","underwriting.LEAD_TIME":"1","underwriting.OPERATING_COST":".5","underwriting.PRICE":"1"}` |
| `simulation/offworld_mvp/build8/route1_body_campaign.py:48` | `SETTINGS:A1_DISCLOSED_EVIDENCE_SOURCE` | `"AUTHORED:UNIFORM_NEUTRAL_ROUTE1_2026"` |
| `simulation/offworld_mvp/build8/route1_body_campaign.py:49` | `SETTINGS:SPONSOR_REQUEST_CEILINGS` | `{"Australian Space Agency":".050","Axiom":".100","Blue Origin":".200","CNES":".100","CNSA":".300","CSA":".100","DLR":".100","ESA":".200","ISRO":".120","Interlune":".025","Isar Aerospace":".100","JAXA":".180","KASA":".100","LandSpace":".100","NASA":".350","Roscosmos":".100","SpaceX":".200","Starlab":".100","UAE Space Agency":".025","ispace":".100"}` |
| `simulation/offworld_mvp/build8/route1_body_campaign.py:50` | `SETTINGS:LIFETIME_SPENDING_CAP` | `null` |
| `simulation/offworld_mvp/build8/route1_body_campaign.py:51` | `SETTINGS:CARRY_CAP` | `null` |
| `simulation/offworld_mvp/build8/route1_body_campaign.py:52` | `SETTINGS:GLOBAL_PROJECT_CAP` | `null` |
| `simulation/offworld_mvp/build8/route1_body_campaign.py:53` | `SETTINGS:EXECUTOR_CAPACITY_CAP` | `null` |
| `simulation/offworld_mvp/build8/route1_body_campaign.py:55` | `BLOCK_ORDER` | `["MAX_NEW_STAGES_PER_SPONSOR_YEAR","MAX_CLAIMANTS_PER_BODY_CAMPAIGN","A1_REVIEW_NOT_READY","A1_REVIEW_INSUFFICIENT","COMPARABLE_EXECUTOR_QUOTE","EXECUTOR_CAPABILITY","SPONSOR_REQUEST_CEILINGS","ACTUAL_SPONSOR_CASH","FINANCIER_CONCENTRATION","FINANCIER_INFORMATION","FINANCIER_RETURN","FINANCIER_OTHER"]` |
| `simulation/offworld_mvp/build8/route1_body_campaign.py:69` | `A1 seeded uniform SHA256 modulus` | `"2**256"` |
| `simulation/offworld_mvp/build8/route1_body_campaign.py:74` | `blocker decade window` | `10` |
| `simulation/offworld_mvp/build8/route1_body_campaign.py:249` | `project sponsor ownership fraction` | `"1"` |
| `simulation/offworld_mvp/build8/route1_cast_payments.py:16` | `EXTRA_CEILINGS:CSA` | `".100"` |
| `simulation/offworld_mvp/build8/route1_cast_payments.py:16` | `EXTRA_CEILINGS:KASA` | `".100"` |
| `simulation/offworld_mvp/build8/route1_cast_payments.py:16` | `EXTRA_CEILINGS:Roscosmos` | `".100"` |
| `simulation/offworld_mvp/build8/route1_cast_payments.py:17` | `EXTRA_CEILINGS:Axiom` | `".100"` |
| `simulation/offworld_mvp/build8/route1_cast_payments.py:17` | `EXTRA_CEILINGS:Blue Origin` | `".200"` |
| `simulation/offworld_mvp/build8/route1_cast_payments.py:17` | `EXTRA_CEILINGS:SpaceX` | `".200"` |
| `simulation/offworld_mvp/build8/route1_cast_payments.py:18` | `EXTRA_CEILINGS:Isar Aerospace` | `".100"` |
| `simulation/offworld_mvp/build8/route1_cast_payments.py:18` | `EXTRA_CEILINGS:LandSpace` | `".100"` |
| `simulation/offworld_mvp/build8/route1_cast_payments.py:18` | `EXTRA_CEILINGS:Starlab` | `".100"` |
| `simulation/offworld_mvp/build8/route1_cast_payments.py:26` | `SERVICES:BUILD` | `["ONE_AUTHORED_BUILD_WORK_PACKAGE",".015"]` |
| `simulation/offworld_mvp/build8/route1_cast_payments.py:27` | `SERVICES:LAND` | `["ONE_AUTHORED_LANDING_WORK_PACKAGE",".020"]` |
| `simulation/offworld_mvp/build8/route1_cast_payments.py:28` | `SERVICES:LAUNCH` | `["ONE_AUTHORED_LAUNCH_SERVICE_UNIT",".020"]` |
| `simulation/offworld_mvp/build8/route1_cast_payments.py:29` | `SERVICES:RUN` | `["ONE_AUTHORED_OPERATIONS_SERVICE_UNIT",".015"]` |
| `simulation/offworld_mvp/build8/route1_cast_payments.py:34` | `PREFERRED:CNSA` | `"CASC"` |
| `simulation/offworld_mvp/build8/route1_cast_payments.py:34` | `PREFERRED:NASA` | `"Astrobotic"` |
| `simulation/offworld_mvp/build8/route1_cast_payments.py:34` | `PREFERRED:Roscosmos` | `"RKK Energia"` |
| `simulation/offworld_mvp/build8/route1_cast_payments.py:35` | `PREFERRED:ISRO` | `"HAL / L&T"` |
| `simulation/offworld_mvp/build8/route1_cast_payments.py:35` | `PREFERRED:JAXA` | `"Mitsubishi Heavy Industries"` |
| `simulation/offworld_mvp/build8/route1_cast_payments.py:36` | `PREFERRED:CNES` | `"Airbus Defence and Space"` |
| `simulation/offworld_mvp/build8/route1_cast_payments.py:36` | `PREFERRED:ESA` | `"Thales Alenia Space"` |
| `simulation/offworld_mvp/build8/route1_cast_payments.py:37` | `PREFERRED:CSA` | `"MDA Space"` |
| `simulation/offworld_mvp/build8/route1_cast_payments.py:37` | `PREFERRED:DLR` | `"OHB"` |
| `simulation/offworld_mvp/build8/route1_cast_payments.py:37` | `PREFERRED:KASA` | `"Hanwha Aerospace"` |
| `simulation/offworld_mvp/build8/route1_cast_payments.py:38` | `PREFERRED:Australian Space Agency` | `"Toyota"` |
| `simulation/offworld_mvp/build8/route1_cast_payments.py:39` | `PREFERRED:UAE Space Agency` | `"Thales Alenia Space"` |
| `simulation/offworld_mvp/build8/route1_cast_payments.py:40` | `PREFERRED:Blue Origin` | `"Blue Origin"` |
| `simulation/offworld_mvp/build8/route1_cast_payments.py:40` | `PREFERRED:SpaceX` | `"SpaceX"` |
| `simulation/offworld_mvp/build8/route1_cast_payments.py:41` | `PREFERRED:Axiom` | `"Thales Alenia Space"` |
| `simulation/offworld_mvp/build8/route1_cast_payments.py:41` | `PREFERRED:ispace` | `"ispace"` |
| `simulation/offworld_mvp/build8/route1_cast_payments.py:42` | `PREFERRED:Interlune` | `"Northrop Grumman"` |
| `simulation/offworld_mvp/build8/route1_cast_payments.py:42` | `PREFERRED:Isar Aerospace` | `"Isar Aerospace"` |
| `simulation/offworld_mvp/build8/route1_cast_payments.py:43` | `PREFERRED:LandSpace` | `"CASC"` |
| `simulation/offworld_mvp/build8/route1_cast_payments.py:43` | `PREFERRED:Starlab` | `"MDA Space"` |
| `simulation/offworld_mvp/build8/route1_cast_payments.py:156` | `cast payment defaults` | `{"end_year":2035,"scenario":"B","share":"0.25"}` |
| `simulation/offworld_mvp/build8/route1_gate1.py:18` | `CEILINGS:CNSA` | `".300"` |
| `simulation/offworld_mvp/build8/route1_gate1.py:18` | `CEILINGS:ISRO` | `".120"` |
| `simulation/offworld_mvp/build8/route1_gate1.py:18` | `CEILINGS:JAXA` | `".180"` |
| `simulation/offworld_mvp/build8/route1_gate1.py:18` | `CEILINGS:NASA` | `".350"` |
| `simulation/offworld_mvp/build8/route1_gate1.py:19` | `CEILINGS:CNES` | `".100"` |
| `simulation/offworld_mvp/build8/route1_gate1.py:19` | `CEILINGS:DLR` | `".100"` |
| `simulation/offworld_mvp/build8/route1_gate1.py:19` | `CEILINGS:ESA` | `".200"` |
| `simulation/offworld_mvp/build8/route1_gate1.py:20` | `CEILINGS:Australian Space Agency` | `".050"` |
| `simulation/offworld_mvp/build8/route1_gate1.py:20` | `CEILINGS:UAE Space Agency` | `".025"` |
| `simulation/offworld_mvp/build8/route1_gate1.py:21` | `CEILINGS:Interlune` | `".025"` |
| `simulation/offworld_mvp/build8/route1_gate1.py:21` | `CEILINGS:ispace` | `".100"` |
| `simulation/offworld_mvp/build8/route1_gate1.py:23` | `DEFAULT_PRICE:BUILD` | `"0.085"` |
| `simulation/offworld_mvp/build8/route1_gate1.py:23` | `DEFAULT_PRICE:LAND` | `"0.150"` |
| `simulation/offworld_mvp/build8/route1_gate1.py:25` | `EVIDENCE` | `[["underwriting.PRICE","1"],["underwriting.EXPLORATION_CAPEX",".125"],["underwriting.DEVELOPMENT_CAPEX",".125"],["underwriting.OPERATING_COST",".5"],["underwriting.LEAD_TIME","1"]]` |
| `simulation/offworld_mvp/build8/route1_gate1.py:26` | `EVIDENCE_TAG` | `"AUTHORED:UNIFORM_NEUTRAL_ROUTE1_2026"` |
| `simulation/offworld_mvp/build8/route1_gate1.py:27` | `PREFERRED:CNSA` | `"CASC"` |
| `simulation/offworld_mvp/build8/route1_gate1.py:27` | `PREFERRED:ISRO` | `"HAL / L&T"` |
| `simulation/offworld_mvp/build8/route1_gate1.py:27` | `PREFERRED:NASA` | `"Astrobotic"` |
| `simulation/offworld_mvp/build8/route1_gate1.py:28` | `PREFERRED:ESA` | `"Thales Alenia Space"` |
| `simulation/offworld_mvp/build8/route1_gate1.py:28` | `PREFERRED:JAXA` | `"Mitsubishi Heavy Industries"` |
| `simulation/offworld_mvp/build8/route1_gate1.py:29` | `PREFERRED:CNES` | `"Airbus Defence and Space"` |
| `simulation/offworld_mvp/build8/route1_gate1.py:29` | `PREFERRED:DLR` | `"OHB"` |
| `simulation/offworld_mvp/build8/route1_gate1.py:30` | `PREFERRED:Australian Space Agency` | `"Toyota"` |
| `simulation/offworld_mvp/build8/route1_gate1.py:30` | `PREFERRED:UAE Space Agency` | `"Thales Alenia Space"` |
| `simulation/offworld_mvp/build8/route1_gate1.py:31` | `PREFERRED:Interlune` | `"Northrop Grumman"` |
| `simulation/offworld_mvp/build8/route1_gate1.py:31` | `PREFERRED:ispace` | `"ispace"` |
| `simulation/offworld_mvp/build8/route1_gate1.py:64` | `run_gate1 defaults` | `{"earth_end_year":2035,"run_setting":"pilot","scenario":"A","share":"0.10"}` |
| `simulation/offworld_mvp/build8/route1_gate1.py:76` | `allowed country allocation shares` | `["0.10","0.25"]` |
| `simulation/offworld_mvp/build8/route1_gate1.py:79` | `Route1 opening seed` | `"BUILD8_ROUTE1_GATE1"` |
| `simulation/offworld_mvp/build8/route1_gate1.py:93` | `missing country sponsor preference weight` | `"1"` |
| `simulation/offworld_mvp/build8/route1_gate1.py:103` | `commercial_opportunity` | `"1"` |
| `simulation/offworld_mvp/build8/route1_gate1.py:143` | `project owner share` | `"1"` |
| `simulation/offworld_mvp/build8/route1_gate1.py:145` | `2026 sponsor type` | `"PRIVATE_SPONSOR for all 20"` |
| `simulation/offworld_mvp/build8/route1_gate1.py:146` | `2026 sponsor prior` | `"0.5"` |
| `simulation/offworld_mvp/build8/route1_gate1.py:148` | `2026 disclosure scenario` | `"B: one authored neutral observation per sponsor"` |
| `simulation/offworld_mvp/build8/route1_gate1.py:170` | `financier belief and prior` | `"0.5"` |
| `simulation/offworld_mvp/build8/route1_gate2.py:15` | `run_gate2 defaults` | `{"carry_cap":null,"end_year":2029,"scenario":"B","share":"0.10"}` |
| `simulation/offworld_mvp/build8/route1_gate2.py:33` | `end year bounds` | `"2029..2035 or opt-in cast 2029..2226"` |
| `simulation/offworld_mvp/build8/route1_gate2.py:35` | `all-body campaign horizon` | `"2226 only, carry cap=None"` |
| `simulation/offworld_mvp/build8/route1_gate2.py:36` | `permitted carry caps` | `[null,0,1,2]` |
| `simulation/offworld_mvp/build8/route1_gate2.py:102` | `annual origin years` | `"2026..end_year"` |
| `simulation/offworld_mvp/build8/route1_gate2.py:113` | `commercial_opportunity` | `"1"` |
| `simulation/offworld_mvp/build8/route1_gate2.py:193` | `NASA legacy exceptional study price` | `"0.300"` |
| `simulation/offworld_mvp/build8/route1_gate2.py:207` | `financier beliefs and priors` | `"0.5"` |
| `simulation/offworld_mvp/build8/sponsor_executor_network_trial.py:13` | `PUBLIC_PARTICIPATION:CNSA` | `["CHN"]` |
| `simulation/offworld_mvp/build8/sponsor_executor_network_trial.py:13` | `PUBLIC_PARTICIPATION:NASA` | `["USA"]` |
| `simulation/offworld_mvp/build8/sponsor_executor_network_trial.py:13` | `PUBLIC_PARTICIPATION:Roscosmos` | `["RUS"]` |
| `simulation/offworld_mvp/build8/sponsor_executor_network_trial.py:14` | `PUBLIC_PARTICIPATION:ISRO` | `["IND"]` |
| `simulation/offworld_mvp/build8/sponsor_executor_network_trial.py:14` | `PUBLIC_PARTICIPATION:JAXA` | `["JPN"]` |
| `simulation/offworld_mvp/build8/sponsor_executor_network_trial.py:15` | `PUBLIC_PARTICIPATION:ESA` | `["DEU","FRA","ITA","GBR","ESP","NLD","BEL","SWE","CHE","AUT","NOR","POL"]` |
| `simulation/offworld_mvp/build8/sponsor_executor_network_trial.py:16` | `PUBLIC_PARTICIPATION:CNES` | `["FRA"]` |
| `simulation/offworld_mvp/build8/sponsor_executor_network_trial.py:16` | `PUBLIC_PARTICIPATION:CSA` | `["CAN"]` |
| `simulation/offworld_mvp/build8/sponsor_executor_network_trial.py:16` | `PUBLIC_PARTICIPATION:DLR` | `["DEU"]` |
| `simulation/offworld_mvp/build8/sponsor_executor_network_trial.py:17` | `PUBLIC_PARTICIPATION:Australian Space Agency` | `["AUS"]` |
| `simulation/offworld_mvp/build8/sponsor_executor_network_trial.py:17` | `PUBLIC_PARTICIPATION:KASA` | `["KOR"]` |
| `simulation/offworld_mvp/build8/sponsor_executor_network_trial.py:17` | `PUBLIC_PARTICIPATION:UAE Space Agency` | `["ARE"]` |
| `simulation/offworld_mvp/build8/sponsor_executor_network_trial.py:20` | `PRIVATE_PARTICIPATION:Blue Origin` | `["USA"]` |
| `simulation/offworld_mvp/build8/sponsor_executor_network_trial.py:20` | `PRIVATE_PARTICIPATION:SpaceX` | `["USA"]` |
| `simulation/offworld_mvp/build8/sponsor_executor_network_trial.py:21` | `PRIVATE_PARTICIPATION:Axiom` | `["USA","SAU","QAT","KOR","HUN","JPN"]` |
| `simulation/offworld_mvp/build8/sponsor_executor_network_trial.py:21` | `PRIVATE_PARTICIPATION:ispace` | `["JPN"]` |
| `simulation/offworld_mvp/build8/sponsor_executor_network_trial.py:22` | `PRIVATE_PARTICIPATION:Interlune` | `["USA"]` |
| `simulation/offworld_mvp/build8/sponsor_executor_network_trial.py:22` | `PRIVATE_PARTICIPATION:Isar Aerospace` | `["DEU","GBR","USA"]` |
| `simulation/offworld_mvp/build8/sponsor_executor_network_trial.py:23` | `PRIVATE_PARTICIPATION:LandSpace` | `["CHN"]` |
| `simulation/offworld_mvp/build8/sponsor_executor_network_trial.py:23` | `PRIVATE_PARTICIPATION:Starlab` | `["USA","DEU","FRA","JPN","CAN"]` |
| `simulation/offworld_mvp/build8/sponsor_executor_network_trial.py:29` | `PREFERENCES:USA` | `{"Axiom":1,"Blue Origin":2,"Interlune":1,"Isar Aerospace":1,"NASA":5,"SpaceX":3,"Starlab":1}` |
| `simulation/offworld_mvp/build8/sponsor_executor_network_trial.py:30` | `PREFERENCES:CHN` | `{"CNSA":5,"LandSpace":2}` |
| `simulation/offworld_mvp/build8/sponsor_executor_network_trial.py:30` | `PREFERENCES:JPN` | `{"Axiom":1,"JAXA":5,"Starlab":1,"ispace":2}` |
| `simulation/offworld_mvp/build8/sponsor_executor_network_trial.py:31` | `PREFERENCES:DEU` | `{"DLR":3,"ESA":3,"Isar Aerospace":2,"Starlab":1}` |
| `simulation/offworld_mvp/build8/sponsor_executor_network_trial.py:32` | `PREFERENCES:CAN` | `{"CSA":5,"Starlab":2}` |
| `simulation/offworld_mvp/build8/sponsor_executor_network_trial.py:32` | `PREFERENCES:FRA` | `{"CNES":4,"ESA":3,"Starlab":1}` |
| `simulation/offworld_mvp/build8/sponsor_executor_network_trial.py:33` | `PREFERENCES:GBR` | `{"ESA":3,"Isar Aerospace":2}` |
| `simulation/offworld_mvp/build8/sponsor_executor_network_trial.py:33` | `PREFERENCES:KOR` | `{"Axiom":1,"KASA":5}` |
| `simulation/offworld_mvp/build8/sponsor_executor_network_trial.py:38` | `EXECUTOR_SELECTION` | `["Astrobotic","CASC","RKK Energia","HAL / L&T","Mitsubishi Heavy Industries","Thales Alenia Space","Airbus Defence and Space","OHB","MDA Space","Hanwha Aerospace","Toyota","SpaceX","Blue Origin","ispace","Northrop Grumman","Isar Aerospace"]` |
| `simulation/offworld_mvp/build8/sponsor_executor_network_trial.py:45` | `AUTHOR_CAPABILITIES:Astrobotic` | `["LAND","BUILD"]` |
| `simulation/offworld_mvp/build8/sponsor_executor_network_trial.py:45` | `AUTHOR_CAPABILITIES:CASC` | `["BUILD","LAUNCH","LAND"]` |
| `simulation/offworld_mvp/build8/sponsor_executor_network_trial.py:46` | `AUTHOR_CAPABILITIES:HAL / L&T` | `["BUILD","LAUNCH"]` |
| `simulation/offworld_mvp/build8/sponsor_executor_network_trial.py:46` | `AUTHOR_CAPABILITIES:RKK Energia` | `["BUILD","LAUNCH"]` |
| `simulation/offworld_mvp/build8/sponsor_executor_network_trial.py:47` | `AUTHOR_CAPABILITIES:Mitsubishi Heavy Industries` | `["BUILD","LAUNCH"]` |
| `simulation/offworld_mvp/build8/sponsor_executor_network_trial.py:48` | `AUTHOR_CAPABILITIES:Airbus Defence and Space` | `["BUILD","RUN"]` |
| `simulation/offworld_mvp/build8/sponsor_executor_network_trial.py:48` | `AUTHOR_CAPABILITIES:Thales Alenia Space` | `["BUILD","RUN"]` |
| `simulation/offworld_mvp/build8/sponsor_executor_network_trial.py:49` | `AUTHOR_CAPABILITIES:MDA Space` | `["BUILD","RUN"]` |
| `simulation/offworld_mvp/build8/sponsor_executor_network_trial.py:49` | `AUTHOR_CAPABILITIES:OHB` | `["BUILD"]` |
| `simulation/offworld_mvp/build8/sponsor_executor_network_trial.py:50` | `AUTHOR_CAPABILITIES:Hanwha Aerospace` | `["BUILD","LAUNCH"]` |
| `simulation/offworld_mvp/build8/sponsor_executor_network_trial.py:50` | `AUTHOR_CAPABILITIES:Toyota` | `["BUILD","RUN"]` |
| `simulation/offworld_mvp/build8/sponsor_executor_network_trial.py:51` | `AUTHOR_CAPABILITIES:Blue Origin` | `["BUILD","LAUNCH","LAND"]` |
| `simulation/offworld_mvp/build8/sponsor_executor_network_trial.py:51` | `AUTHOR_CAPABILITIES:SpaceX` | `["BUILD","LAUNCH","RUN"]` |
| `simulation/offworld_mvp/build8/sponsor_executor_network_trial.py:52` | `AUTHOR_CAPABILITIES:Northrop Grumman` | `["BUILD","RUN"]` |
| `simulation/offworld_mvp/build8/sponsor_executor_network_trial.py:52` | `AUTHOR_CAPABILITIES:ispace` | `["LAND","RUN"]` |
| `simulation/offworld_mvp/build8/sponsor_executor_network_trial.py:53` | `AUTHOR_CAPABILITIES:Isar Aerospace` | `["LAUNCH"]` |
| `simulation/offworld_mvp/build8/sponsor_executor_network_trial.py:67` | `PROJECTS:CNSA` | `["STRATEGIC","LAND","0.045"]` |
| `simulation/offworld_mvp/build8/sponsor_executor_network_trial.py:67` | `PROJECTS:NASA` | `["STRATEGIC","LAND","0.045"]` |
| `simulation/offworld_mvp/build8/sponsor_executor_network_trial.py:68` | `PROJECTS:Roscosmos` | `["STRATEGIC","LAUNCH","0.030"]` |
| `simulation/offworld_mvp/build8/sponsor_executor_network_trial.py:69` | `PROJECTS:ISRO` | `["SCIENTIFIC","BUILD","0.015"]` |
| `simulation/offworld_mvp/build8/sponsor_executor_network_trial.py:70` | `PROJECTS:JAXA` | `["SCIENTIFIC","LAND","0.030"]` |
| `simulation/offworld_mvp/build8/sponsor_executor_network_trial.py:71` | `PROJECTS:ESA` | `["SCIENTIFIC","BUILD","0.030"]` |
| `simulation/offworld_mvp/build8/sponsor_executor_network_trial.py:72` | `PROJECTS:CNES` | `["SCIENTIFIC","BUILD","0.015"]` |
| `simulation/offworld_mvp/build8/sponsor_executor_network_trial.py:73` | `PROJECTS:DLR` | `["SCIENTIFIC","BUILD","0.015"]` |
| `simulation/offworld_mvp/build8/sponsor_executor_network_trial.py:74` | `PROJECTS:CSA` | `["SCIENTIFIC","RUN","0.015"]` |
| `simulation/offworld_mvp/build8/sponsor_executor_network_trial.py:75` | `PROJECTS:KASA` | `["STRATEGIC","LAUNCH","0.030"]` |
| `simulation/offworld_mvp/build8/sponsor_executor_network_trial.py:76` | `PROJECTS:Australian Space Agency` | `["SCIENTIFIC","BUILD","0.015"]` |
| `simulation/offworld_mvp/build8/sponsor_executor_network_trial.py:77` | `PROJECTS:UAE Space Agency` | `["STRATEGIC","BUILD","0.045"]` |
| `simulation/offworld_mvp/build8/sponsor_executor_network_trial.py:78` | `PROJECTS:SpaceX` | `["COMMERCIAL","LAUNCH","0.090"]` |
| `simulation/offworld_mvp/build8/sponsor_executor_network_trial.py:79` | `PROJECTS:Blue Origin` | `["COMMERCIAL","LAUNCH","0.090"]` |
| `simulation/offworld_mvp/build8/sponsor_executor_network_trial.py:80` | `PROJECTS:Axiom` | `["COMMERCIAL","RUN","0.045"]` |
| `simulation/offworld_mvp/build8/sponsor_executor_network_trial.py:81` | `PROJECTS:ispace` | `["COMMERCIAL","LAND","0.045"]` |
| `simulation/offworld_mvp/build8/sponsor_executor_network_trial.py:82` | `PROJECTS:Interlune` | `["COMMERCIAL","BUILD","0.090"]` |
| `simulation/offworld_mvp/build8/sponsor_executor_network_trial.py:83` | `PROJECTS:Isar Aerospace` | `["COMMERCIAL","LAUNCH","0.045"]` |
| `simulation/offworld_mvp/build8/sponsor_executor_network_trial.py:84` | `PROJECTS:Starlab` | `["COMMERCIAL","RUN","0.090"]` |
| `simulation/offworld_mvp/build8/sponsor_executor_network_trial.py:85` | `PROJECTS:LandSpace` | `["COMMERCIAL","LAUNCH","0.045"]` |
| `simulation/offworld_mvp/phase3b/kernel/offworld_kernel/policies/manifest.py:145` | `test_only_manifest.identity` | `{"policy_id":"FINANCIER_SCREENING_V1","status":"TEST_ONLY","version":"0.1"}` |
| `simulation/offworld_mvp/phase3b/kernel/offworld_kernel/policies/manifest.py:156` | `test_only_manifest.parameters:hurdle_rate` | `{"authorization_ref":"TEST_ONLY:BUILD5_TEST001_SYNTHETIC_FIXTURE:NOT_POLICY_BASELINE","status":"TEST_ONLY","unit":"DIMENSIONLESS_ANNUAL_RATE","value":"0.20"}` |
| `simulation/offworld_mvp/phase3b/kernel/offworld_kernel/policies/manifest.py:157` | `test_only_manifest.parameters:horizon_years` | `{"authorization_ref":"TEST_ONLY:BUILD5_TEST001_SYNTHETIC_FIXTURE:NOT_POLICY_BASELINE","status":"TEST_ONLY","unit":"YEARS","value":"10"}` |
| `simulation/offworld_mvp/phase3b/kernel/offworld_kernel/policies/manifest.py:158` | `test_only_manifest.parameters:agent_detection_rate` | `{"authorization_ref":"TEST_ONLY:BUILD5_TEST001_SYNTHETIC_FIXTURE:NOT_POLICY_BASELINE","status":"TEST_ONLY","unit":"PROBABILITY","value":"0.80"}` |
| `simulation/offworld_mvp/phase3b/kernel/offworld_kernel/policies/manifest.py:159` | `test_only_manifest.parameters:agent_false_positive_rate` | `{"authorization_ref":"TEST_ONLY:BUILD5_TEST001_SYNTHETIC_FIXTURE:NOT_POLICY_BASELINE","status":"TEST_ONLY","unit":"PROBABILITY","value":"0.20"}` |
| `simulation/offworld_mvp/phase3b/kernel/offworld_kernel/policies/manifest.py:160` | `test_only_manifest.parameters:normalized_throughput` | `{"authorization_ref":"TEST_ONLY:BUILD5_TEST001_SYNTHETIC_FIXTURE:NOT_POLICY_BASELINE","status":"TEST_ONLY","unit":"MODEL_RESOURCE_UNIT_PER_YEAR","value":"10"}` |
| `simulation/offworld_mvp/phase3b/kernel/offworld_kernel/policies/manifest.py:161` | `test_only_manifest.parameters:max_concentration_fraction` | `{"authorization_ref":"TEST_ONLY:BUILD5_TEST001_SYNTHETIC_FIXTURE:NOT_POLICY_BASELINE","status":"TEST_ONLY","unit":"DIMENSIONLESS_SHARE","value":"0.80"}` |

## External/reference data that are not invented experiment literals

- The Earth v4 80-country data through 2226 are separate pinned files. Qualified owns 2026–2031, stage owns 2032–2060, successor owns 2061–2226. Source bytes and SHA-256 are in the scenario.
- The eligible 90 bodies and the seven unknown accessibility statuses are derived from pinned Build 6E applicability metadata and Build 7 accessibility reference, not generated WORLD hidden truth.
- Four authored A1/A2 standings come from the pinned Build 6C scenario. Other result outcomes use the named deterministic TEST_ONLY SHA-256 draw. These are not physical missions.
- The financier policy is the unchanged TEST_ONLY `FINANCIER_SCREENING_V1`; its six effective parameter values are included above.

## Important values outside scenario ownership today

Route 1 currently consumes module-level `SETTINGS`, `PR3B_SETTINGS`, `CEILINGS`, `SERVICES`, sponsor participation/weights, and hardcoded runner literals. Merely listing these values in a JSON file does NOT bind execution to them. Changing JSON alone would change a proposed file hash but not existing Route 1 decisions.

## Identified seam blocker: no G1-derived Route 1 construction

- `genesis_g1.py:39-46` rejects multiple actors/nodes; `:101-105` and `:188-205` build exactly one SPN Agent/account and a source-backed USA 2026 opening.
- `opening.py:16-22` instead calls the historical Build 7 `_build_kernel`, and `:22-102` expands 80-country assertions/accounts before recomputing an experimental manifest. It never calls G1.
- `route1_gate1.py:79` invokes that separate opening; `:97-113` creates sponsor budgets and country transfers; `:140-146` creates 20 individual Sponsor Agents and projects during 2026 financing, *after* the Route 1 opening. `route1_gate2.py:41` relies on this path.
- G1 uses the historical USA 2026–2045 Earth reference for population and a one-actor opening; Route 1 uses external Earth v4 80-country 2026–2226 investment data. Admitting and reconciling those source contracts cannot be achieved by forwarding `run_all_body_campaign` keyword arguments.
- Existing Route 1 passes `ceilings_enabled`, `participating_sponsors`, `failures`, `body_count` to its campaign, but does not accept a preconstructed G1 kernel nor a complete authored configuration object.
- Result: a two-setting direct Route 1 run would be an interesting existing isolated economic comparison, but would NOT answer this G1 seam objective. Both runs are intentionally stopped, no invented ledger totals.

## Narrowest imaginable connection (not authorized)

One Build 8-only *pre-hash* multi-actor Genesis constructor would have to derive country/source assertions, actor capabilities, nodes, initial accounts, project identities and relevant policy inputs from the authored scenario, then supply its kernel to a re-used Route 1 yearly funding conductor. Current Route 1 has no such injection seam and constructs its own opening, accounts and 2026 projects. Building an entire new campaign conductor is explicitly forbidden by this step. Do not use monkeypatches, post-seal manifest patches or a second ledger.

## Two authored comparison settings (not executed)

- **A_ALL_20**: all existing 20 requesters; ceilings enabled; 90 eligible bodies.
- **B_NASA_ONLY**: one existing requester, NASA; ceilings enabled; same 90 eligible bodies. Other funded 2026 sponsors remain in the historical Route 1 opening as coded; removing requesters is not the same as deleting actors or national funding.
- The scenario hash is `2551c693b73156f4d81ba3b3d0cbc566be9ec411728cf8e434502c1f95534f81`; any future executable identity must include this hash plus all source pins and effective value table. These settings have no reported funded-body or cash results because the stated stop condition was encountered.

## After 2042: previously measured, not rerun here

The historical all-90-body PR3B report states the **last new A1/A2 stage was funded in 2042**. From 2043 to 2226, the body/year and account records advance but no further new stage is purchased; the program does not create new projects, transport, settlements or inhabitants. Do not attribute those historical totals to A_ALL_20/B_NASA_ONLY.

## Result / stop

**BLOCKED: G1_ONE_ACTOR_OPENING_NOT_ROUTE1_MULTI_ACTOR_OPENING.** No frozen edit or campaign framework authorized. Proposal only; no simulations run, no historical tests edited, no WORLD, database, payment or observation executed.
