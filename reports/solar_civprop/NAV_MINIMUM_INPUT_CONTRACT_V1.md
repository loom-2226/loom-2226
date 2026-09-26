# NAV Minimum Input Contract V1 — M1 Result

Assessment epoch: 2226-08-22T00:00:00Z

## Result

- Bodies assessed: **110**
- NAV-0 identity supported: **108**
- NAV-1 flight supported at assessment epoch from currently qualified Phase-4 ephemeris manifests: **92**
- NAV-1 gaps requiring reconciliation/remediation: **18**

## Consumer-derived NAV-1 minimum

- LOOM_BODY_IDENTITY
- ACTIVE_NAIF_ID
- QUALIFIED_POSITION_VELOCITY_EPHEMERIS_AT_EPOCH
- REFERENCE_FRAME_AND_UNITS
- VALIDITY_INTERVAL
- SOURCE_PROVENANCE

The current direct NAV-V1-A solver consumes synchronized authoritative position/velocity state rows and ship/propulsion configuration. It does not consume body GM, mass, radius, rotation, orientation, or shape for direct interbody arrival solving. Those belong to higher local/surface capability or future gravity-assist/close-operations consumers, not the minimum direct-flight contract.

## Current gaps

- DACTYL — NAV0=MISSING; active NAIF=[]; qualified ephemeris at epoch=0
- EARTH — NAV0=SUPPORTED; active NAIF=['399']; qualified ephemeris at epoch=0
- EARTH_MOON_BARYCENTER — NAV0=SUPPORTED; active NAIF=['3']; qualified ephemeris at epoch=0
- HYDRA — NAV0=SUPPORTED; active NAIF=['903']; qualified ephemeris at epoch=0
- KERBEROS — NAV0=SUPPORTED; active NAIF=['904']; qualified ephemeris at epoch=0
- MARS — NAV0=SUPPORTED; active NAIF=['499']; qualified ephemeris at epoch=0
- MERCURY — NAV0=SUPPORTED; active NAIF=['199']; qualified ephemeris at epoch=0
- MERCURY_SYSTEM_BARYCENTER — NAV0=SUPPORTED; active NAIF=['1']; qualified ephemeris at epoch=0
- MOON — NAV0=SUPPORTED; active NAIF=['301']; qualified ephemeris at epoch=0
- NEPTUNE — NAV0=SUPPORTED; active NAIF=['899']; qualified ephemeris at epoch=0
- NIX — NAV0=SUPPORTED; active NAIF=['902']; qualified ephemeris at epoch=0
- PROTEUS — NAV0=SUPPORTED; active NAIF=['808']; qualified ephemeris at epoch=0
- SELAM — NAV0=MISSING; active NAIF=[]; qualified ephemeris at epoch=0
- STYX — NAV0=SUPPORTED; active NAIF=['905']; qualified ephemeris at epoch=0
- SUN — NAV0=SUPPORTED; active NAIF=['10']; qualified ephemeris at epoch=0
- URANUS — NAV0=SUPPORTED; active NAIF=['799']; qualified ephemeris at epoch=0
- VENUS — NAV0=SUPPORTED; active NAIF=['299']; qualified ephemeris at epoch=0
- VENUS_SYSTEM_BARYCENTER — NAV0=SUPPORTED; active NAIF=['2']; qualified ephemeris at epoch=0

## Interpretation

This is a readiness measurement, not a promotion. A MISSING result may mean an existing authority is not yet represented in the currently qualified Phase-4 manifest set; it does not automatically authorize new external research. Reconcile existing JPL/NAIF/Horizons authority first.

## M1 disposition

**M1 CONTRACT DERIVED; NAV-1 REMEDIATION REQUIRED BEFORE NAV BASELINE CLOSURE.**

Next action: reconcile the NAV-1 gap list against existing Phase-4/JPL authority and distinguish mapping/manifest gaps from genuine source gaps. Do not acquire new physical-property corpora as part of that reconciliation.

## Architectural finding from the actual Navigator

The current production Navigator does not discover arbitrary route nodes from the 110-body Solar authority. Its locked workflow still carries an explicit route-object catalog and acquires JPL Horizons vectors for those supported nodes. Separately, Phase-4 has a broader governed ephemeris authority.

Therefore M1 does not equate "present in the 110-body Solar catalog" with "currently selectable as a production Navigator destination." Generalizing route-node discovery is an implementation task downstream of this contract, not a reason to invent additional physical facts.

The direct NAV-V1-A mathematics establishes an unexpectedly small minimum: authoritative synchronized position and velocity states plus identity/provenance. GM, radius, mass and rotational/shape properties are not inputs to the current direct transfer root solve. They become requirements only when a consumer such as gravity assist, close operations, landing, surface-relative navigation, or another future solver actually uses them.
