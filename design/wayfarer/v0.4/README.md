# Wayfarer v0.4 — preserved design record (2026-10-24)

**Classification:** NON-GOVERNING SANDBOX / NON-CANON / NOT ENGINEERING CLOSURE / NOT QUALIFICATION.

**Origin:** Claude design session, 2026-10-24, supplied by kT. Canon was deliberately set aside for the design exercise; physics assumptions were retained. This is a historical design snapshot, **not** a change to current Wayfarer authority.

**Archive:** `wayfarer_v0_4_record_2026-10-24.zip` (unaltered original, 51 ZIP entries including directories; 49 extracted regular files).

**SHA-256:** `f6058e4c25c323509f62b491e0ac43e5f65be9086452f8cd7ffebd618a0a9c22` (verified against supplied archive on quantifactus).

**Source of design details and assumptions:** [`wayfarer_v0_4_record/SPEC.md`](wayfarer_v0_4_record/SPEC.md). **Source of rerun commands and caveats:** [`wayfarer_v0_4_record/MANIFEST.md`](wayfarer_v0_4_record/MANIFEST.md). Original scripts, inputs, outputs, and historical intermediate results are preserved alongside those documents.

## Design snapshot

- **Wayfarer v0.4:** 54.9 m length, 872.8 t dry, 719.2 km/s ECON delta-v; wrap-around grooved tanks, axial round 4.8 m shuttle bore, split fore/aft plant, four accordion radiator strakes at 1,300 K, claimed 6.5 m Metric clearance in FAST and HARD.
- **Shuttle v0.2:** 14.4 × 4.3 m, 34.1 t dry, up to 70.0 t wet, 28.3 t water capacity, 10.5 GW torchlet; six crew; hardened cabin doubles as drive-off rover; proposed Venus surface return using approximately 54 m hydrogen balloon to upper atmosphere followed by torch ascent. Water supplied from Wayfarer inventory.
- **Drones v0.1:** Mars drone 80 kg (395 kg with pod), dense-air drone 60 kg (204 kg with pod); one drone per shuttle trip or independent drop pod delivery.
- **Potential future ledger delta, NOT ADOPTED:** `planetary_launch` 33 -> 35.3 t; Venus kit 12.5 t carried as hold payload.

## Independent reproduction of headline scripts

Run 2026-10-24 on quantifactus using Python 3, extracted archive in a disposable `/tmp` directory; `REPO` pointed to a local clone containing `geometry/wayfarer_geometry_seed.sql`. No source assumptions were tuned to achieve the numbers.

| Command | Observed result | Headline match |
| --- | --- | --- |
| `python3 shuttle_final.py` | wet 70.0 t; dry 34.1 t; water 28.3 t; 14.4 × 4.3 m; torchlet 10.5 GW | Yes |
| `python3 uav_final.py` | Mars drone 80 kg / pod 395 kg; dense-air drone 60 kg / pod 204 kg | Yes |
| `python3 wayfarer_v4.py REPO` | length 54.9 m; dry 872.8 t; ECON delta-v 719.2 km/s; 0.988 g | Yes |

**Scope of reproduction:** script execution and comparison with the requested headline values only. `shuttle_search.py --rebuild` and a complete independent physics/mission audit were not performed. Saved intermediate shuttle results include older v0.1 assumptions, as explained in MANIFEST.md. These runs do not establish structural, thermal, mission, or propulsion feasibility.

## Review flags (not design facts or new requirements)

- Compact 10.5 GW torchlet power density, remass flow, waste heat, and engine mass are load-bearing assumptions needing independent physical closure.
- Shuttle water transfer must reconcile with live Wayfarer remass, protected water, wet mass, and cargo accounting.
- Axial shuttle bore and radiator deployments differ from governing reference geometry; launch/departure clearance and thermal interfaces remain open.
- Venus surface thermal survival, balloon deployment/buoyancy over ascent, and final torch ascent are not demonstrated by headline sizing alone.
- The 6.5 m claimed field clearance is not itself metric environmental certification.
- Canon-era industrial logistics, local landers, autonomous probes, and mission-specific kits may offer simpler mission options than one universal surface vehicle.

See **SPEC.md §7** for the original author's open items. The review flags above are external observations, not retroactive changes to the supplied design.

## Authority and future use

This folder is an **archival design record** under `design/`, not active research authority, a canon amendment, an engineering/current contract, or a runtime specification. Nothing here supersedes `canon/current/**` or `engineering/current/**`. If later considered for adoption, use a separately authorised disposition/CCR or appropriate engineering change. No automatic promotion, and no changes to existing canon, engineering, data, runtime, or media follow from this archive. WALTER provenance/authority boundaries apply.
