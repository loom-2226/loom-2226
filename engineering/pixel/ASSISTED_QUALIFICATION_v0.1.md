# LOOM Pixel Assisted Qualification v0.1

## Two-button model

`LOOM_Qualify.sh`
- existing raw governed qualification;
- no OpenAI API call;
- no local repair;
- full qualification transcript copied to clipboard.

`LOOM_Qualify_AI.sh`
- invokes the same raw governed qualification first;
- if governed qualification passes, no repair is attempted;
- if it fails, creates a detached temporary worktree at the exact failed SHA;
- sends the failed transcript plus editable `engineering/pixel` Python/shell harness files to the OpenAI Responses API;
- permits at most a small configured number of bounded mechanical repair attempts;
- reruns the exact qualification command only inside the temporary worktree;
- emits a compact clipboard report and stores raw logs/decisions/candidate patch under `$HOME/.cache/loom/assisted/`.

## Repair boundary

Version 0.1 may edit only:
- `engineering/pixel/*.py`
- `engineering/pixel/*.sh`

It may not edit:
- tests;
- `engineering/pixel/active_qualification.txt`;
- `src/`;
- `data/`;
- `canon/`;
- schemas;
- expected numerical values;
- Navigator behavior;
- physics/scientific conclusions;
- authority boundaries.

The local agent is for mechanical harness/platform failures only: import/bootstrap paths, Android/Termux path portability, shell quoting, local directories, subprocess/process lifecycle, command invocation, and similarly bounded defects.

## Authority

A raw Pixel PASS is a governed qualification result.

A local repaired PASS is **not** a governed qualification result. It is `LOCAL_REPAIR_CANDIDATE_PASS`: evidence that a candidate patch fixes the mechanical failure in an isolated worktree. The authoritative repository remains unchanged until Sol reviews/reproduces the patch in GitHub and Pixel qualifies the resulting governed head.

The assisted runner has no autonomous commit/push authority.

## API configuration

The repository contains no API key. `configure_openai_key.sh` stores the key only in Termux at `$HOME/.config/loom/openai.env` with mode 600. The default repair model is `gpt-5.6-terra` and may be overridden locally with `LOOM_REPAIR_MODEL`.

Using the AI shortcut sends the failing transcript and editable Pixel harness source context to the OpenAI API. Using the raw shortcut sends nothing to the API.
