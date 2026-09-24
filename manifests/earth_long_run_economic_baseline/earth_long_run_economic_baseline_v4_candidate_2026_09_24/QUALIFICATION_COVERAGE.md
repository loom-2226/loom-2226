# Economy-universe, evidence and network coverage

The deterministic target set is the 237 unique ISO3 `Country/Area` rows in UN WPP 2024 Medium for 2026. This includes separately modeled economies and territories; it does not impose a sovereignty-only filter. HKG and TWN remain separate. WDI aggregate rows are excluded: the recovered WDI envelope has 281 codes, of which 44 are aggregates absent from the WPP Country/Area set. WPP's `Country/Area` label does not resolve sovereign status, territory status or special administrative legal status per row, so those political categories are **unresolved evidence fields**, not guessed classifications. No WPP Country/Area is excluded from identity or demography.

| Layer | Qualified/model-ready economies | Added 157 with no joint model-ready state | Evidence detail |
|---|---:|---:|---|
| Identity/geography | 237 | 0 | WPP Country/Area ISO3; source designation does not certify sovereignty |
| Population and working-age demography | 237 | 0 | WPP Medium Jan-1 and 15–64 percentages |
| Labor | 80 | 157 | 145 added areas have an ILOSTAT employment envelope, but full compatible LF/WAP/employment model state is not jointly qualified |
| Macroeconomic envelope | 189 source-bridged | 48 without GDP bridge | 109 added areas have WDI constant-2015-USD level plus IMF WEO real-growth bridge |
| Productivity/TFP and factor shares | 80 | 157 | 105 added areas appear in raw recent PWT; 34 have all seven audited raw fields somewhere in 2019–2023; no new calibration has been qualified |
| Investment/capital | 80 | 157 | WDI GFCF share may be present, but compatible productive capital and four-asset state are not jointly qualified |
| Ten-sector and four-asset decomposition | 80 | 157 | OECD 2024 source reducer has 80 modeled economies plus `ROW` aggregate; `ROW` is not an added economy |
| Bilateral trade/IO topology | 80 | 157 | The 80 modeled nodes have inherited OECD topology; no added area receives an invented edge or regional clone |

On WPP's consistent 2026 Jan-1 basis, the 80 contain **6,764,256,339** people of the **8,266,245,291** world total, or **81.8298526%**. The other 157 contain **1,501,988,952** people. The 189 areas with a source GDP bridge contain **8,113,247,470** people, but that does not make them economic-model ready.

On the existing WDI+WEO 2026 bridge's available-source GDP basis, the 80 contribute **97.972106 trillion** of **101.920497 trillion** constant-2015-USD-scale source values, or **96.1260%**. This denominator covers only 189 areas and cannot be called world GDP. The 157 added areas with no model-ready topology have the residual **3.87399% of that available-source GDP denominator** where GDP is present; the 48 missing GDP cases have unknown economic weight. Population-weighted trade-topology classes are 81.83% inherited OECD model topology and 18.17% unavailable. The **economic weight of unavailable topology is not fully known**.

No added-economy fallback method was installed. Thus the **added-economy** fallback count and its population/economic weights are zero by construction; unavailable evidence remains `UNAVAILABLE`, not `FALLBACK` or numeric zero. This does not erase inherited v3 fallback provenance among the original 80. `COUNTRY_EVIDENCE.json` provides per-area fields, source/method IDs and reasons. `COVERAGE_REPORT.json` gives exact machine-readable counts and denominators. `SOURCE_PROVENANCE.json` pins the original source snapshots and macro envelope. Full economic propagation is held pending a separately qualified source/method for sector allocation, assets/factor shares and network topology.
