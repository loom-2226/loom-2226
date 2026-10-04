# Phase 2 Post-Closure Erratum 001 — Primitive Authority Roots

**Status:** ADOPTED ERRATUM / PRE-CONTRACT / SINGLE-AUTHORITY  
**Owner:** @kT  
**Scope:** Narrow correction of Phase 2 normative language  
**Amends:** `04_PHASE2_CLAIM_AUTHORITY_MODEL_NORMATIVE.md` interpretation only  
**Does not reopen Phase 2**

## 1. Reason

Phase 0 D0.18 explicitly rejected a closed ontology of "exactly two roots" and retained an extensible authority-root model. It required Phase 1 to investigate candidate root classes including physical law, mathematical relationships, standards, institutional/legal authority, entity identity and internally verified computation, while prohibiting implementation from inventing roots merely to fit a claim.

Phase 2 §12 subsequently stated that Phase 2 "adjudicates two primitive roots": EVIDENTIARY ROOT and AUTHORIZATION ROOT. Phase 2 also stated that it did not amend Phase 0.

Those statements cannot both govern a closed root ontology. This erratum restores Phase 0 precedence.

## 2. Corrected interpretation

Phase 2 establishes **EVIDENTIARY ROOT** and **AUTHORIZATION ROOT** as the two primitive root classes positively adjudicated by Phase 2.

It does **not** establish that these are the only primitive root classes LOOM may ever recognize.

Therefore:

1. the root ontology remains extensible under D0.18;
2. no additional primitive root is recognized merely because a model, implementation or claim needs one;
3. proposed additional root classes require explicit governance treatment before use;
4. storage, Git state, automation, AI origin, repeated use and computational convenience remain non-roots by themselves;
5. deterministic computation remains derivative unless a later governed act explicitly establishes a distinct root class and its conditions;
6. Phase 3 must represent root identity extensibly rather than encode a two-value closed enum;
7. Phase 3 may use EVIDENTIARY_ROOT and AUTHORIZATION_ROOT now, while allowing future governed root classes without schema breakage.

## 3. Textual precedence

Where Phase 2 uses phrases such as:

- "two primitive roots";
- "at least one primitive root";
- "AUTHORIZATION-root";
- "evidentiary root";

they shall be read consistently with this erratum.

"Two primitive roots" means **the two primitive roots adjudicated in Phase 2**, not **the exhaustive set of all primitive roots permitted by LOOM**.

No other Phase 2 semantics are changed.

## 4. No retroactive invention

This erratum does not recognize physical law, mathematics, standards, institutional/legal authority, entity identity, internally verified computation, or any other candidate as a primitive root.

Those remain candidates for later governance analysis where needed.

## 5. Phase transition consequence

The Phase 3 blocker concerning the D0.18 / Phase 2 root contradiction is resolved for design purposes.

Phase 3 shall use an extensible root representation and shall not hard-code exactly two root types.

This erratum does not release Authority Contract v1 or grant v1 qualification to any holding.
