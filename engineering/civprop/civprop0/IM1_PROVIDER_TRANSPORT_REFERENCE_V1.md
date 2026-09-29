# IM-1 provider reference and Roo-ver rerun

**Class:** engineering. **Reference:** Intuitive Machines IM-1 / Odysseus,
NASA CLPS TO2-IM, completed February 2024. This reuses Blue Ghost 1's
reported-event timing, observed-versus-prospective segment structure and
qualified `loom_solar` state checks. The [pinned result](runs/im1_provider_reference_roover_rerun_v1.json)
includes a separate, unchanged Roo-ver assessment.

| Segment | What Intuitive Machines demonstrated on IM-1 | Limit for Roo-ver / IM-5 |
|---|---|---|
| Launch | Nova-C launched on SpaceX Falcon 9 and separated from its second stage. | Launch service was provided by SpaceX; IM-5 launch vehicle, date and acceptance remain unknown. |
| Transfer | Odysseus reached lunar orbit after a reported seven-day journey. | No IM-5 trajectory, transfer duration, delta-v or propulsion margin follows. |
| Lunar delivery | Nova-C soft-landed with six NASA instruments near **Malapert A** in the South Pole region. | IM-5 plans the larger **Nova-D** and targets **Mons Malapert**; its flight mass, site and landing outcome remain unqualified. |
| Site/operations | NASA acquired surface data from the six instruments. | Odysseus leaned after landing, constraining communications and some objectives; instruments ceased operations after seven reported days. This does not establish Roo-ver deployment or 14-day operation. |

The first three IM-1 segments are `OBSERVED_COMPLETE`; site/operations is
`OBSERVED_LIMITED`. All prospective feasibility fields remain `NOT_ASSESSED`.
NASA reported IM-1 launch at **01:05 EST on 15 February 2024**, separation at
approximately **01:53 EST**, lunar orbit insertion on **21 February**, and
landing at **17:24 CST on 22 February**. Launch-to-landing elapsed time from
the reported minutes is **185.317 hours (7.722 days)**; launch-to-separation
is approximately **0.8 hours**. Lunar orbit insertion and surface-end times
are date-only in the admitted sources, so exact phase and surface durations
are not calculated.

Read-only Solar authority resolved Earth/Moon states at the reported launch
and landing epochs. Their simultaneous separations were **373,168 km** and
**404,093 km**. Those are body geometry context, not Odysseus' path or speed.
The reported roughly **100 kg of IM-1 payload** is carried mass, not a
Nova-C capacity certification or a Nova-D allowance.

**Roo-ver rerun:** overall `UNKNOWN`; launch `UNKNOWN`, transfer `UNKNOWN`,
named planned lunar-delivery service scope `FEASIBLE`, site/operations
`UNKNOWN`. The IM-1 reference is not passed to the Roo-ver assessor. Its
precedent changes none of the missing IM-5 window, vehicle, transfer,
flight-mass, exact-site or operations evidence.

Primary sources: [NASA launch](https://www.nasa.gov/news-release/nasa-artemis-science-first-intuitive-machines-flight-head-to-moon/),
[NASA separation](https://www.nasa.gov/blogs/artemis/2024/02/15/intuitive-machines-moon-lander-successfully-deploys/),
[NASA landing](https://www.nasa.gov/news-release/nasa-tech-contributes-to-soft-moon-landing-agency-science-underway/),
[NASA surface results](https://www.nasa.gov/missions/artemis/clps/nasa-collects-first-surface-science-in-decades-via-commercial-moon-mission/),
and [Intuitive Machines completion](https://investors.intuitivemachines.com/news-releases/news-release-details/intuitive-machines-historic-im-1-mission-success-american).
The one-mission [fixture](im1_reference.json) records assertion scope and
source provenance. Revalidate this reference if a source event or Solar/DE440
authority changes; Roo-ver requires its own IM-5 evidence.
