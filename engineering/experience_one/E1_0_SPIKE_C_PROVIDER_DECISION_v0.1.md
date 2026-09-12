# LOOM 2226 — E1.0 Spike C Provider / Runtime Decision v0.1

**Status:** ACTIVE PREFLIGHT — PROVIDER/RUNTIME NOT YET SELECTED  
**Date:** 12 September 2026  
**Class:** `class:engineering` / `REQUIRED_FOR_E1` bounded spike evidence  
**Parent:** `E1_0_RISK_BURNDOWN_EVIDENCE_PACK_v0.1.md`  
**No canon/runtime authority change. No Spike C PASS is claimed.**

## 1. Why this decision exists

The first Spike C harness assumed a direct OpenAI Responses API call from the Pixel and therefore required an `OPENAI_API_KEY`. That assumption was made before confirming that the user actually maintains an OpenAI API account/key or that a long-lived provider secret on the Pixel is the intended product architecture.

That was premature. Provider/runtime choice is itself one of Spike C's explicit questions and must be treated as evidence, not hidden setup.

The existing direct-OpenAI harness remains a valid **candidate experiment path**, not the selected production architecture.

## 2. Current candidate paths

### A. Direct OpenAI Responses API from Pixel

Pros:
- smallest experiment;
- function calling and structured model/tool loop are directly available;
- stdlib HTTPS means minimal local dependencies;
- low-cost models are available.

Risks / obligations:
- requires a separately billed OpenAI API account/key;
- ChatGPT subscription credentials do not substitute for an API key;
- long-lived provider key on a personal mobile runtime is undesirable production credential architecture;
- provider/data-retention/cost controls must be explicitly governed.

Disposition: **VALID SPIKE FALLBACK; NOT ASSUMED PRODUCT ARCHITECTURE.**

### B. GitHub Copilot SDK / CLI using GitHub user authentication

Current official GitHub documentation states that the Copilot SDK can use a signed-in GitHub user, GitHub OAuth, or supported user tokens, and can bill model usage through the user's Copilot entitlement without exposing a model-provider API key to the application.

Important correction: the retired **GitHub Models inference API is not a viable path**. GitHub Models was retired on 30 July 2026. The candidate here is the newer Copilot SDK/CLI runtime, not GitHub Models.

Potential advantages for LOOM:
- user-facing GitHub authentication rather than a raw model-provider key;
- model/provider indirection and lower provider lock-in at the LOOM boundary;
- Python SDK support and explicit custom-tool registration;
- OAuth/device-flow patterns are closer to a product credential boundary.

Open risk:
- Pixel uses Termux/Android ARM64, not a conventional glibc Linux host;
- GitHub documents Copilot CLI support for Linux/macOS/Windows and publishes Linux ARM64 runtime paths, but Android/Termux support is not documented;
- therefore Pixel viability must be **empirically tested**, not inferred from `arm64` alone.

Disposition: **PREFERRED PREFLIGHT CANDIDATE IF PIXEL RUNTIME WORKS.**

### C. Brokered backend

LOOM Pixel calls a small controlled backend; provider credential lives server-side. This is a standard production shape if no safe user-authenticated local runtime exists.

Pros:
- no provider secret on Pixel;
- centralized cost, provider, retention and abuse controls;
- easy provider switching behind a typed LOOM boundary.

Costs:
- introduces deployed service infrastructure and network dependency;
- larger than the minimum Spike C experiment;
- should not be built merely because it is architecturally tidy.

Disposition: **PRODUCTION FALLBACK; DO NOT BUILD UNTIL LOCAL USER-AUTH PATH IS TESTED.**

## 3. Decision order

1. Empirically preflight GitHub Copilot CLI/SDK viability on the actual Pixel/Termux runtime.
2. If viable and an appropriate Copilot entitlement is available, use it for the real Spike C adversarial test.
3. If runtime or entitlement blocks it, record the blocker and use direct OpenAI API only if the user deliberately chooses to create/use an API account for the experiment.
4. If neither local path is acceptable, classify the product need as requiring a brokered backend and size that seam before E1.1.

No provider path may silently become Mara's production architecture solely because it made the spike pass.

## 4. Security / authority invariants independent of provider

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
- provider/session logs are evidence/debug material, never campaign authority.

## 5. Adversarial matrix

The real Spike C run must include at least:

1. normal authoritative lookup;
2. direct contradiction;
3. absent-fact trap;
4. plausible-inference trap;
5. retrieved-text prompt injection;
6. stale-state override attempt.

A failure is evidence. Do not prompt-tune a failing case into PASS before classifying why it failed.

## 6. Exit implication

Spike C does not ask which vendor is nicest. It asks whether LOOM can place a nondeterministic model behind a sufficiently narrow, reconstructible and fail-safe boundary on the Pixel architecture.

The provider/runtime decision is therefore part of the spike result and must be recorded with platform, authentication, latency, data handling, cost and fallback constraints.