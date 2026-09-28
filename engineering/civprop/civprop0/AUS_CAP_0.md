# AUS-CAP-0: Australian lunar service access

**Qualified proposition.** At the 2026 boundary, Fleet Space Technologies, an
Australian firm, has a documented agreement with Firefly Aerospace for delivery
and lunar surface operation of its SPIDER payload on Blue Ghost Mission 2.
Firefly [announced the agreement on 8 November 2023](https://fireflyspace.com/news/firefly-announces-agreement-with-fleet-space-to-deliver-payload-to-the-moon/).
Its [19 March 2026 presentation](https://investors.fireflyspace.com/static-files/4a40daaa-c23c-4253-9c67-ca6964087c35)
reports SPIDER delivered to Firefly for integration. The Australian Space Agency
also [described the planned SPIDER mission](https://www.space.gov.au/news-and-media/on-the-horizon-for-space-in-2026).
These are evidence of **Fleet's provider agreement and integration progress**, not
evidence that SPIDER had landed or that Australia owns lunar transport.

The generic resolver returns **USABLE** for Fleet's *documented access agreement to
this service class*, with the named SPIDER/Firefly scope. A request for a different
mission returns **CONDITIONAL**: no matching slot/date, polar landing coverage,
payload accommodation, operations support, or mission price is evidenced.
`AUS` in CIVPROP-0 is a **country actor**. Fleet's contract is not a right held by
that actor, so its access result is **UNKNOWN**. The evidence-backed CIVPROP-0
entrypoint therefore yields transport **UNKNOWN** and a rational **WAIT**, with
no spending or observation. The original scenario run and frozen replay artifacts
remain available as the reference causal experiment.

Firefly's [current Mission 2 page](https://fireflyspace.com/missions/blue-ghost-mission-2/)
lists an upcoming far-side mission no earlier than 2027 and roughly 44 days of
transit. It further rules out treating that **named** route as CIVPROP-0's
September 2026 departure and five-day synthetic polar-site arrival. The page's
revision date is unavailable, so that updated schedule is a **review finding**, not
an input backdated into the 2026 actor assessment. Alternative routes remain
UNKNOWN. No launch economics, trajectory, provider capacity or Earth/Solar database
state is changed.

**Next seam:** obtain a dated access right or procurement path for the actual
CIVPROP-0 country actor (or explicitly choose Fleet as a different simulated
actor), then qualify a dated site/payload service envelope. Until then an
empirical access path cannot clear that exact mission.
