# M2 — Dorrington & Olsen → LOOM CIVPROP input assessment

Status: **M2 INPUT-BOUNDARY ASSESSMENT COMPLETE**

Source: Scott Dorrington & John Olsen, “Parametric economic modelling of asteroid mining architectures,” *Acta Astronautica* 241 (2026) 19–47, DOI 10.1016/j.actaastro.2025.11.006. Full 29-page paper reviewed. This note uses the paper as the model authority and cites its own references where they materially define an input.

## BLUF

Dorrington–Olsen is useful to LOOM, but it is **not an asteroid-value database model**. It is a compact mission-architecture/economic kernel. Given transport, spacecraft/mining technology, costs/prices, and a resource-return assumption, it computes extraction/return/propellant masses and economic figures of merit including profit, NPV, expected NPV, MPBR and BEMR.

That distinction matters. We should **not** contort Solar Facts into storing D&O technology or economics. Solar Facts needs to provide the empirical object state from which a later CIVPROP layer can decide what is physically there and how certain we are. Navigator provides accessibility. Technology/economics provide the rest.

The current bulk SQLite baseline is therefore **not yet sufficient for resource-specific CIVPROP**, but the missing bridge is much narrower than “finish all physical data”: target-specific material/resource evidence, especially presence/abundance/scope/uncertainty, plus mining-relevant surface state when available.

## What the paper actually consumes

The paper separates parameters into system (Table 3, p. 24), mission (Table 4, p. 25), masses (Table 5, p. 27), and specific costs (Table 6, p. 28). Its central mass/economic chain is Eqs. 9–24 (pp. 26–29) and architecture-specific forms in Appendix A (pp. 40–45).

### Object facts that belong in, or can be derived from, Solar Facts

| Empirical lane | Why D&O/CIVPROP needs it | Current V10 state |
|---|---|---|
| Stable target identity | Join facts, dynamics and simulation state | present for 110 authority bodies |
| Mass | Whole-asteroid return sets extraction mass equal to asteroid/boulder mass (Eq. 10 discussion, p. 27); also bounds inventory | **10** candidate assertions: sparse |
| Size/shape | Paper says whole-body return mass can be controlled by selecting expected size and density (p. 31); supports mass/inventory inference | **143** candidate size/shape assertions across several property types: partial |
| Bulk density | Converts size/shape into mass/inventory where defensible | **49** candidate assertions: partial |
| Taxonomy | Paper uses taxonomic knowledge as a proxy for resource-presence probability | **35** candidate SMASSII/Tholen assertions: partial |
| Resource presence + abundance | Needed to turn “asteroid exists” into resource inventory and a defensible success/availability state | **0 in the bulk baseline property set**: principal gap |
| Rotation/orientation | Not required by D&O core equations, but relevant to actual extraction/site operations | rotation **52** candidate assertions; WGCCRE orientation broad but not universal |
| Surface/geotechnical state | Needed by a credible extraction/mining-rate model, but D&O treats mining rate parametrically | not represented in the bulk baseline property set |

The three-body promoted Solar Facts corpus already proves that material_evidence can represent resource evidence without laundering it into an economic score. That is the pattern to scale, not a new “asteroid value” column.

### Inputs that do **not** belong in Solar Facts

**Transport:** ΔV_EA, ΔV_AE, TOF_EA, TOF_AE, and opportunity/wait cadence belong to Navigator/transport. D&O explicitly notes that realistic delta-V and flight time can come from numerical trajectory designs; its Shoemaker–Helin approximation is a survey simplification (pp. 24–26, citing Shoemaker–Helin [13] and Dorrington’s thesis [52]). LOOM already has a better authority boundary: use Navigator rather than copy trajectory values into factual object properties.

**Technology:** dry mass, mining-equipment mass, Isp, thrust, tank capacity, power, mining rate and operational durations are technology/architecture state. D&O Table 3 makes these explicit. Mining rate is deliberately external to this paper; the authors point to their earlier mining-requirements model [51].

**Economics:** production, launch, propellant and operations costs; sale price; discount rate; and campaign choices belong downstream. Table 6 and Eqs. 13–19 make that separation explicit.

## The important resource-model caveat

D&O does **not** infer ore grade or resource abundance from asteroid observations. For the expectation-value example it estimates probability of finding a desired water resource from population/taxonomic priors: about 10% C-type among NEAs, then 25% of those assumed rich in water (>6 wt% H2O), giving 2.5% for an unclassified asteroid and 25% for a known C-type (p. 36). The paper cites Stuart & Binzel [64], Jarosewich meteorite analyses [65], and Elvis & Esty [66].

For LOOM that is a useful **fallback uncertainty model**, not a license to convert C-type into 25% water or 6 wt% H2O in Solar Facts. Taxonomy is evidence. Resource abundance is another proposition. CIVPROP can consume a probability distribution when abundance is unknown.

This is precisely where the 2226 simulation becomes interesting: exploration can convert UNKNOWN/PARTIAL resource state into measured state over time. That works whether propagation is deterministic, agent-based, or some future hybrid contraption humans invent to make the scheduler cry.

## What SQLite needs before CIVPROP

We do **not** need another broad WGCCRE-like enrichment campaign. We need a minimal empirical contract:

1. **Identity and physical inventory:** mass where directly known; otherwise size/shape + density with derivation lineage.
2. **Material evidence:** resource/material identity, presence/absence/upper limit, abundance or abundance range where actually supported, spatial scope (global/regional/site), evidence class, uncertainty/confidence, source and observation epoch.
3. **Resource uncertainty:** preserve UNKNOWN and competing interpretations. Taxonomy may inform a downstream prior but must not become fabricated abundance.
4. **Mining-relevant physical evidence:** rotation/orientation and surface/geotechnical properties only where a downstream extraction model actually consumes them.
5. **No duplicated transport:** Navigator supplies ΔV, flight time and cadence.
6. **No embedded economics:** prices, costs, technology performance, extraction efficiency and investment decisions remain CIVPROP/technology/economic state.

This is independent of whether CIVPROP later uses deterministic rules or agents. Both need the same world-state interface: **what exists, where, how much we know about it, and with what uncertainty.**

## Current readiness conclusion

The current V10 bulk baseline is good enough for **physical screening** and for joining targets to Navigator. It is not good enough to assign defensible resource-specific economic potential across the catalog because the bulk candidate schema contains no resource-presence/abundance lane.

That is now the next factual-data problem. It is contract-driven, not archival completionism.

**M2 decision:** adopt Dorrington–Olsen as the economic/mission architecture kernel and use it to define the boundary, but do not treat it as the resource-potential model. Extend Solar Facts only enough to expose empirical resource inventory/evidence and uncertainty. Then CIVPROP combines that with Navigator + technology + economics.

## Source references used from Dorrington & Olsen

- [13] Shoemaker–Helin transfer approximation, used by the paper for rapid asteroid accessibility estimates.
- [51] Dorrington & Olsen (2017), *Mining requirements for asteroid ore extraction*, cited by the paper for a separate mining-rate model.
- [52] Dorrington (2019), PhD thesis, cited for trajectory/logistics details and transfer approximations.
- [53] Minor Planet Center MPCORB, source of the paper’s large asteroid orbital survey.
- [64] Stuart & Binzel (2004), debiased NEO population/taxonomy estimate.
- [65] Jarosewich (1990), meteorite chemical analyses used in the water-rich prior chain.
- [66] Elvis & Esty (2014), probabilistic assay-probe framing for finding ore-bearing asteroids.

These citations support the paper’s parameterization. They are not silently promoted to LOOM empirical authority; any use as Solar Facts sources requires normal provenance/qualification.
