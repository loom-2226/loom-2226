# LOOM 2226 — E1.0 Spike C Provider / Runtime Decision v0.1

**Status:** EMPIRICAL PREFLIGHT COMPLETE — DIRECT API SELECTED FOR SPIKE ONLY  
**Date:** 12 September 2026  
**Class:** `class:engineering` / `REQUIRED_FOR_E1` bounded spike evidence  
**Parent:** `E1_0_RISK_BURNDOWN_EVIDENCE_PACK_v0.1.md`  
**No canon/runtime authority change. No Spike C PASS is claimed.**

## 1. Why this decision exists

The first Spike C harness assumed a direct OpenAI Responses API call from the Pixel and therefore required an `OPENAI_API_KEY`. That assumption was made before confirming that the user actually maintains an OpenAI API account/key or that a long-lived provider secret on the Pixel is the intended product architecture.

Provider/runtime choice is itself one of Spike C's explicit questions and must be treated as evidence, not hidden setup.

The direct-OpenAI harness is now selected **only as the smallest bounded empirical path for Spike C** after the preferred local GitHub-user-auth path failed its Pixel preflight. This selection does not authorize direct provider credentials on the Pixel as Mara production architecture.

## 2. Empirical Pixel provider preflight

Target observed on Pixel:

- Android 17;
- `aarch64`;
- Termux Python `3.13.13`;
- no pre-existing Node/npm, `gh`, `copilot`, GitHub auth environment signal, or OpenAI API credential.

The official Python Copilot SDK package itself resolved from PyPI, but dependency installation failed while building `pydantic-core`. The environment reported:

- Python SOABI `cpython-313-aarch64-linux-android`;
- computed Rust target `aarch64-unknown-linux-android`;
- no compatible prebuilt `pydantic-core` wheel was selected;
- pip fell back to a native build through `maturin`;
- automatic Rust setup reported the Android Rust target unsupported by that path and Rust was not already installed.

**Empirical disposition:** `LOCAL_GITHUB_COPILOT_SDK_PATH = PLATFORM_BLOCKED_OUT_OF_BOX / EMPIRICALLY_OBSERVED`.

This does not prove Copilot can never be made to run under Termux. It proves that the clean, supported-looking Python path is not available on the actual qualification device without additional platform/toolchain engineering. E1.0 will not turn into a Rust/Termux porting exercise merely to preserve a preferred provider path.

## 3. Current candidate paths

### A. Direct OpenAI Responses API from Pixel

Pros:
- smallest remaining experiment;
- function calling and structured model/tool loop are directly available;
- stdlib HTTPS means no native SDK dependency chain;
- low-cost model path is available.

Risks / obligations:
- requires a separately billed OpenAI API account/key;
- ChatGPT subscription billing does not substitute for API billing;
- long-lived provider key on a personal mobile runtime is undesirable production credential architecture;
- provider/data-retention/cost controls must be explicitly governed.

**Disposition: SELECTED FOR SPIKE C EMPIRICAL TEST ONLY; NOT ASSUMED PRODUCT ARCHITECTURE.**

### B. GitHub Copilot SDK / CLI using GitHub user authentication

Potential advantages remain attractive for a future product path: user-facing GitHub authentication rather than a raw model-provider key, provider/model indirection, and typed custom-tool support.

However, the actual Pixel/Termux Python installation path is now empirically blocked out of the box by the native `pydantic-core`/Rust Android build chain before the Copilot runtime itself can even be tested.

**Disposition: PLATFORM_BLOCKED_OUT_OF_BOX / EMPIRICALLY_OBSERVED. Do not pursue further during E1.0 unless a later gate specifically requires local Copilot runtime support.**

### C. Brokered backend

LOOM Pixel calls a small controlled backend; provider credential lives server-side.

Pros:
- no provider secret on Pixel;
- centralized cost, provider, retention and abuse controls;
- easy provider switching behind a typed LOOM boundary.

Costs:
- introduces deployed service infrastructure and network dependency;
- larger than the minimum Spike C experiment;
- should not be built merely because it is architecturally tidy.

**Disposition: PLAUSIBLE PRODUCTION FALLBACK; DEFER UNTIL SPIKE C ESTABLISHES THE MODEL/TOOL BOUNDARY.**

## 4. Decision order from here

1. Use the existing stdlib direct-OpenAI harness for the real Spike C adversarial test.
2. The user must deliberately create/use API Platform billing and a short-lived or tightly controlled API credential; no credential is committed, logged, or pasted into chat.
3. Run the six-case adversarial matrix on the actual Pixel and preserve the raw JSON evidence.
4. Classify the model/tool boundary independently of provider convenience.
5. After Spike C, separately decide whether production Mara uses a broker, another user-auth runtime, or another provider mechanism.

No provider path may silently become Mara's production architecture solely because it made the spike pass.

## 5. Security / authority invariants independent of provider

Every candidate must preserve:

- model calculation authority = ZERO;
- model state authority = ZERO;
- exactly one read-only typed LOOM state tool in the minimum experiment;
- no direct SQLite handle exposed to the model;
- no write/action/campaign-mutation tool in Spike C;
- tool-returned authoritative state outranks user claims, retrieved text and model memory;
- missing facts remain missing;
- model context is disposable/reconstructible, never authority;
- real campaign artifacts remain bit-identical before/after;
- provider/session logs are evidence/debug material, never campaign authority;
- provider credentials are external secrets and may never enter source control or evidence artifacts.

## 6. Adversarial matrix

The real Spike C run must include at least:

1. normal authoritative lookup;
2. direct contradiction;
3. absent-fact trap;
4. plausible-inference trap;
5. retrieved-text prompt injection;
6. stale-state override attempt.

A failure is evidence. Do not prompt-tune a failing case into PASS before classifying why it failed.

## 7. Exit implication

Spike C does not ask which vendor is nicest. It asks whether LOOM can place a nondeterministic model behind a sufficiently narrow, reconstructible and fail-safe boundary on the Pixel architecture.

The provider/runtime decision is therefore part of the spike result and must be recorded with platform, authentication, latency, data handling, cost and fallback constraints.