# LOOM 2226 — E1.0 Spike C Pixel Copilot Runtime Finding v0.1

**Status:** EMPIRICALLY OBSERVED PLATFORM BLOCKER — LOCAL COPILOT PATH NOT YET VIABLE  
**Date:** 12 September 2026  
**Class:** `class:engineering` / `REQUIRED_FOR_E1` bounded spike evidence  
**Parent:** `E1_0_SPIKE_C_PROVIDER_DECISION_v0.1.md`  
**No canon/runtime authority change. No Spike C PASS is claimed.**

## 1. Pixel/runtime context

Direct device preflight established:

- Android 17 / aarch64 / Termux;
- Python 3.13.13;
- no pre-existing `copilot`, `gh`, `node`, or `npm` executable;
- no GitHub/OpenAI credential environment variables present.

This was classified `PIXEL_RUNTIME_PREREQUISITE_GAP`, not an authentication failure.

## 2. Official Python Copilot SDK install experiment

Command attempted on the Pixel:

`python -m pip install --upgrade github-copilot-sdk`

Observed dependency path:

- `github-copilot-sdk 1.0.13` resolved successfully;
- `pydantic 2.13.5` required `pydantic-core 2.46.5`;
- no compatible prebuilt `pydantic-core` wheel was selected for `cpython-313-aarch64-linux-android`;
- pip fell back to a source build;
- the build pulled `maturin 1.15.0`;
- maturin reported `Python reports SOABI: cpython-313-aarch64-linux-android`;
- computed Rust target was `aarch64-unknown-linux-android`;
- rustup reported that target as unsupported for its automatic installation path;
- Rust was not available locally;
- metadata generation failed before the Copilot SDK could install.

Therefore the official Python SDK path did **not** reach Copilot runtime download, authentication, or model invocation. The blocker is earlier in the dependency/toolchain path.

## 3. Interpretation

This is evidence that the preferred local GitHub-user-authenticated path is **not cleanly installable on the current Pixel/Termux environment out of the box**.

It is not evidence that Copilot itself is intrinsically incompatible with Android. A custom Rust/toolchain build path may exist. However, forcing Termux-specific native dependency compilation merely to make the spike proceed would materially change the implementation-size question and risks turning Spike C into platform-porting work.

Under the E1.0 rule, setup friction is evidence, not something to hide.

Current disposition:

`LOCAL_GITHUB_COPILOT_SDK_PATH = PLATFORM_BLOCKED_OUT_OF_BOX / EMPIRICALLY_OBSERVED`

Do not classify as permanent impossibility. Do not invest in Rust/Android porting before comparing the two remaining bounded options:

1. direct provider API for the spike with an explicit disposable credential decision; or
2. a tiny broker seam with provider credential off-device.

## 4. WALTER implications

- Do not confuse `arm64` with a supported Android runtime.
- Do not convert Spike C into a Termux package-engineering project without a gate that requires it.
- Do not place long-lived provider credentials on the Pixel merely to avoid acknowledging the platform seam.
- Keep the model/tool authority boundary provider-independent.

## 5. Next decision

The next Spike C step is an explicit provider/runtime choice, not another blind install attempt.

A direct API run remains the smallest way to test the actual nondeterministic-model boundary. A broker remains the likely production-shaped fallback if device-held provider credentials are rejected. Either can satisfy the spike if the authority, provenance, adversarial, and campaign-immutability requirements remain intact.
