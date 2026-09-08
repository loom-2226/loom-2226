# LOOM 2226 Computational Shipyard — Model Permutation Experiment v0.1

Status: ENGINEERING_RESEARCH / NON_CANON / NON_PRODUCTION.

This experiment introduces the thinnest model-facing harness around the already-proven Wayfarer Computational Shipyard vertical slice. It does not create a new solver, a new candidate representation, a new physical evaluator, or a new authority path.

## Authority boundary

The deterministic Wayfarer backend remains authoritative for engineering evaluation. Models may propose and critique. They may not claim physical PASS/FAIL authority, flight-dynamics authority, canon mutation, production approval, or closure of OPEN items.

The executable chain is:

existing Wayfarer S1 solver
→ deterministic Designer input packet
→ raw model JSON
→ strict parser / existing DesignProposal validation
→ existing proposal mutation executor
→ existing CandidateDesign
→ unchanged Wayfarer S1 evaluator
→ existing DesignEvidencePackage
→ deterministic Critic input packet
→ raw model JSON
→ strict parser / existing SOL architectural review validation
→ existing critic-evidence adapter
→ CRITIQUE_ONLY DesignCritique.

## Model independence

Designer and Critic are roles, not model names. Every executed run records model identifier, provider, configuration, prompt hash, input-packet hash, raw-response hash, parsed-output hash, candidate/evaluation/evidence hashes, and authority flags.

A model permutation is only counted when a real model response is actually captured and parsed. Test fixtures, hand-written JSON, or model-neutral deterministic fixtures are not counted as model runs.

The current ChatGPT execution environment does not expose a generic external multi-model API to repository code. Therefore v0.1 provides a model-neutral exchange boundary rather than pretending multiple models were executed. Real permutations can be supplied by any external runner capable of returning the exact JSON contract; the backend remains unchanged.

## Fail-closed behavior

Designer responses must contain exactly the admitted DesignProposal fields. Extra keys, unknown targets, unadmitted operations, mismatched candidate/context hashes, malformed JSON, or authority escalation are rejected. There is no silent repair pass.

Critic responses must contain exactly the admitted DesignReviewReport fields and must match the exact candidate, evidence-package hash, and doctrine hash. Unknown criteria, malformed JSON, extra keys, physical/flight/canon/production claims, or authority escalation are rejected. There is no silent repair pass.

## Evidence discipline

The Critic packet explicitly states that numerical evidence is not visual evidence. SOL must request additional evidence when a visual/architectural judgment cannot be supported. The harness does not convert coordinates into aesthetic facts.

## Manufacturing / functional-region continuity

The new manufacturing-capability and FunctionalRegion research layer remains available to future Designer packets, but v0.1 does not expose new mutation operations for it. The existing mutation executor still admits only `SET_INSTANCE_TRANSLATION` and `SET_INSTANCE_ACTIVE`. This is deliberate: ontology growth does not silently become engineering capability.

## First research question

Given the same deterministic Wayfarer baseline, requirements, institutional context, admitted mutation vocabulary, and evidence authority, do different real Designer models propose materially different experiments, and do different real SOL models produce distinguishable but evidence-grounded critiques?

Initial metrics should remain small: schema-validity rate, authority-violation rate, admitted-operation validity, hard-constraint survival, candidate uniqueness, objective-vector delta, evidence-grounding, SOL criterion distribution, and experiment-request actionability.

No model output can alter CANON, production shipclasses, or WAYFARER_FLIGHT_INERTIA qualification status.
