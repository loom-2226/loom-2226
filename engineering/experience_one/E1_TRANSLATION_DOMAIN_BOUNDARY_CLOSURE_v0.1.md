# Experience One — Translation-Domain Boundary Closure v0.1

**Class:** ENGINEERING QUALIFICATION SUPPORT  
**Scope:** SUPPORTS_E1 only  
**Status:** CANDIDATE / NON-CANON / NON-RUNTIME-POLICY

## Purpose

Close the epistemic question immediately upstream of E1 translation-domain membership:

> Does current governing LOOM engineering contain enough information to derive the spatial boundary of the committed Wayfarer translation domain?

The answer at this revision is **NO**. The governing repository contains boundary calibration anchors and a distributed-node architecture, but no qualified constitutive map from committed vessel/node/actuator state to a spatial translation-domain boundary.

This is a closure result, not a failure of the setting. Crew-rated Loom remains governing in-world fact. The result limits what the engineering model may calculate without inventing an unqualified law.

## 1. Evidence already present

The current authority chain supplies:

- committed Wayfarer configuration identity;
- committed component/material geometry envelope;
- 208 distributed boundary/metric nodes, with a deterministic design-baseline placement that is explicitly non-canon;
- 100 active Mc-299m tiles / 10 kg active inventory;
- shared plant/bank/thermal architecture;
- Loom normal controlled-boundary calibration of approximately 1,900 m²;
- extended mature-route envelope calibration of approximately 2,430 m²;
- normal effective-patch calibration approximately 971;
- normal boundary-authority calibration approximately 670;
- configuration-lock and domain-membership rules;
- environmental Metric node-control equations;
- explicit permission for anisotropic and time-varying certification volumes.

None of those individually or jointly defines a spatial boundary solution.

## 2. Rejected substitutions

The following are not translation-domain boundary solutions:

- Hill radius;
- Laplace sphere of influence;
- surface-radius multiple;
- current collapse radius;
- universal Metric ramp-displacement multiple;
- hull dimensions or material AABB;
- the Phase-3 approximately 1,900 m² geometry regression surrogate;
- node count alone;
- design-baseline node placement alone;
- the canonical 1,900 m² or 2,430 m² area calibration treated as a sphere, cylinder, ellipsoid, or other silently chosen shape.

Area is not geometry. A scalar boundary calibration cannot uniquely determine an anisotropic, configuration-bound spatial domain.

## 3. Missing constitutive seam

The minimum missing engineering object is a calibrated **translation-domain boundary-solution operator**:

[
\boxed{
\mathcal B_D:
(X_{cfg},X_{node},X_{tile},X_{mass},X_{hw},X_{env},X_{form};\Theta_D)
\rightarrow
(\Sigma_D,\mathcal U_D,\Pi_D)
}
]

where:

- (X_{cfg}) is committed configuration and attachment/deployable state;
- (X_{node}) is node placement/topology/health/phase/control state;
- (X_{tile}) is Mc-299m tile/actuator state;
- (X_{mass}) is the live mass-state model;
- (X_{hw}) is relevant plant/hardware condition;
- (X_{env}) is the qualified local environment;
- (X_{form}) is formation/control state;
- (Theta_D) is a versioned empirical calibration set;
- (Sigma_D) is the solved spatial boundary in an explicit vessel frame;
- (mathcal U_D) is uncertainty/confidence over that boundary;
- (Pi_D) is provenance/calibration identity.

This operator is an **effective engineering constitutive seam**. It does not require a microscopic ontology, Tick/Tock dynamics, a cell complex, or a fundamental Weave metric.

## 4. Minimum output contract

A candidate boundary solution must expose at least:

- schema/version;
- configuration identity and configuration-state hash;
- epoch and vessel frame;
- boundary representation and units;
- node/topology calibration identity;
- actuator/Mc calibration identity;
- environmental input identity;
- boundary area and any other calibrated summary observables;
- containment result for every committed material component;
- uncertainty/confidence;
- provenance;
- calibration applicability;
- disposition: `SOLVED_CERTIFIABLE`, `INDETERMINATE_NOT_CERTIFIABLE`, or `HARD_FAIL`;
- explicit missing evidence / failure reason.

A solved boundary may be anisotropic and time varying.

## 5. Calibration obligations

The operator may not be instantiated from one scalar anchor. A qualified calibration package must establish enough information to constrain spatial shape and configuration response.

At minimum it must identify:

1. one or more measured/certified boundary geometries, not area alone;
2. the corresponding committed configuration and node topology;
3. node/actuator state used to produce each calibration;
4. how configuration, node loss/damage and formation state perturb the boundary;
5. uncertainty and repeatability;
6. applicability limits;
7. whether the approximately 1,900 m² normal and approximately 2,430 m² extended values are surface-area observables, another boundary measure, or merely operational calibration labels.

Until item 7 is qualified, those values must not be used as geometric surface areas by the boundary solver.

## 6. E1 present disposition

For the current E1 Ceres → Neptune committed configuration:

[
\boxed{
\text{TRANSLATION DOMAIN BOUNDARY}
=
\text{INDETERMINATE\_NOT\_CERTIFIABLE}
}
]

because the required (mathcal B_D) calibration package is absent.

Consequently:

[
\text{boundary unresolved}
\Rightarrow
\text{domain membership unresolved}
\Rightarrow
\text{lattice coherence cannot close through membership}
\Rightarrow
\text{Compound GA remains indeterminate}.
]

This does not retroactively invalidate the earned operational E1 handoff and does not bind runtime policy.

## 7. Architectural placement

The boundary operator belongs in the effective engineering layer:

[
\text{Canon}
\rightarrow
\text{effective calibrated engineering}
\rightarrow
\mathcal B_D
\rightarrow
\text{domain membership}
\rightarrow
\text{lattice coherence / GA}
\rightarrow
\text{Navigator}
\rightarrow
\text{runtime commit}.
]

A future Tick/Tock/cell-complex/other foundational model may implement or explain (mathcal B_D), but Navigator and E1 qualification must depend on the observable contract rather than that ontology.

## 8. Anti-smuggling rules

This closure does not:

- create a boundary shape;
- promote the design-baseline 208-node placement to canon;
- reinterpret 1,900 m² as literal hull or field surface area;
- define a universal domain radius;
- create new Mc-299m physics;
- promote Relational Foundations research;
- make Tick/Tock authoritative;
- alter Metric cards;
- alter Loom constants;
- move the Neptune endpoint;
- mutate campaign/runtime state.

## 9. Next bounded engineering step

Construct a **candidate calibration package specification** for (mathcal B_D) using the existing canonical Loom boundary observables as calibration constraints while leaving spatial geometry UNKNOWN until sufficient shape/configuration evidence is deliberately authored or recovered.

The first candidate implementation should be a fail-closed interface and calibration validator, not a numerical field solver.

Only after a calibration package passes may a boundary solver be introduced and tested against the committed E1 component envelope.

## 10. Exit criterion

This seam closes when E1 can produce, from a versioned qualified calibration package and the exact committed configuration:

1. a deterministic (Sigma_D);
2. uncertainty/provenance;
3. component containment/domain-membership results;
4. deterministic replay;
5. invalidation on configuration change;
6. no dependence on HUD/browser/LLM calculation.

Until then the correct machine result is `INDETERMINATE_NOT_CERTIFIABLE`.
