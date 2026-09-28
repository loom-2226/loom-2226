# Roo-ver CT-4 / IM-5 service envelope (2026 evidence)

**Assessment:** the named Australian Roo-ver mission is **CONDITIONAL** within
the published NASA CLPS CT-4 / Intuitive Machines IM-5 service path. `AUS`
access is **USABLE for Roo-ver**, as qualified in AUS-ACCESS-1. This establishes
a manifested robotic mission and a planned delivery service; exact transport
feasibility remains **UNKNOWN**. A different payload, actor or 2026 landing is
**OUT_OF_SCOPE for this named path**. That result says nothing about other routes.

| Dimension | Admitted 2026 envelope | Limit |
|---|---|---|
| Date | IM-5 initial launch target **mid-2030**; NASA targets South Pole delivery in **2030** | No booked launch day/window or arrival epoch |
| Payload | Roo-ver with NASA MNP manifested; rover **about 20 kg** | Approximate design figure, not provider capacity or final accepted flight mass |
| Mission mass | NASA lists rovers and instruments collectively at **about 75 kg** | Aggregate manifested suite, not spare capacity |
| Destination | Lunar South Pole region; provider targets **Mons Malapert** | No final landing coordinates or qualification of an arbitrary polar site/PSR |
| Delivery | NASA buys CLPS service; Intuitive Machines plans Nova-D lander, landing and stated network/data support | Launch vehicle, interface details and service guarantees unqualified |
| Surface operations | ELO2 builds and remotely operates Roo-ver for the Agency; planned operation **about 14 days** | Rover-specific deployment, power/data terms and duration guarantee unqualified |
| Transport metrics | No mission-specific delta-v, transfer duration or trajectory in admitted sources | Preserved **UNKNOWN**; no proxy from other Intuitive Machines flights |

Primary sources: [NASA's March 2026 award](https://www.nasa.gov/missions/artemis/clps/nasa-selects-intuitive-machines-to-deliver-artemis-science-tech-to-moon/)
for the manifest, provider, region, aggregate mass and responsibilities;
[Intuitive Machines' March 2026 award release](https://intuitivemachines.gcs-web.com/news-releases/news-release-details/intuitive-machines-expands-lunar-surface-operations-1804-million)
for Nova-D, IM-5, Mons Malapert and network plans; the company's [May 2026
SEC filing](https://www.sec.gov/Archives/edgar/data/1844452/000162828026035236/lunr-20260331.htm)
for the initial mid-2030 launch target; an [Australian Space Agency
presentation hosted by NASA](https://www.nasa.gov/wp-content/uploads/2026/03/ip-asa.pdf)
for approximate rover mass and expected surface duration; and the [Australian
Government mission announcement](https://www.minister.industry.gov.au/t-ayres/media/mission-confirmed-aussie-moon-rover-ready-roll)
for ELO2 operation. The presentation itself is undated; its host path indicates
March 2026. Its quantitative figures are retained as **planned estimates**.

The executable check is `python3 -m engineering.civprop.civprop0.roover_service`.
It consumes the existing `AUS` actor-access result, matches only the named
mission, and reports the supported scope and remaining liens. It does not alter
CIVPROP-0's synthetic 2026 prospecting mission or its transport adapter.
