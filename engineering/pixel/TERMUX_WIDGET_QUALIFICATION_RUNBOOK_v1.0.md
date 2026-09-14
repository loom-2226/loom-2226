# LOOM Pixel / Termux Widget Qualification Runbook v1.0

## Purpose

This is the canonical operational runbook for the LOOM Pixel qualification workflow on Android/Termux, including the raw governed qualifier, the optional AI-assisted mechanical repair path, home-screen shortcuts, local API-key configuration, clipboard behavior, authority boundaries, and the proven smoke-test procedure.

The design goal is simple:

**GitHub is authority. Pixel qualifies exact governed heads. AI may diagnose and repair only bounded mechanical harness failures in an isolated temporary worktree. AI never gains repository, runtime, Navigator, physics, or campaign authority.**

## Supported mobile runtime

- Device class: Android Pixel.
- Governed runtime: **Termux only**.
- Pydroid is not a governed qualification path.
- The Google Play Termux build is supported.
- Termux:API must be available for clipboard integration.
- The separate legacy Termux:Widget plugin is not required; the Google Play Termux build provides shortcut/widget integration directly.

Repository root used by the Pixel workflow:

```text
/storage/emulated/0/Download/LOOM_GIT
```

## Repository-owned components

The authoritative implementation lives under `engineering/pixel/`:

- `loom_pixel_run.sh` — raw governed qualifier.
- `loom_pixel_run_assisted.sh` — optional assisted wrapper.
- `active_qualification.txt` — branch/command handoff contract.
- `install_qualify_shortcuts.sh` — installs both Termux shortcut scripts.
- `configure_openai_key.sh` — stores the API key locally in Termux.
- `mechanical_repair.py` — bounded OpenAI Responses API repair client.
- `candidate_patch.py` — creates the candidate patch without relying on linked-worktree Git metadata.
- `spatial_review.py` — optional read-only browser review companion when configured.
- `ASSISTED_QUALIFICATION_v0.1.md` — authority-boundary design note; this runbook is the broader operating procedure.

## One-time shortcut installation

From Termux:

```bash
cd /storage/emulated/0/Download/LOOM_GIT
git fetch origin
git switch main
git pull --ff-only
bash engineering/pixel/install_qualify_shortcuts.sh
```

This creates two executable shortcuts under `~/.shortcuts/`:

```text
~/.shortcuts/LOOM_Qualify.sh
~/.shortcuts/LOOM_Qualify_AI.sh
```

Verify with:

```bash
ls -l ~/.shortcuts/LOOM_Qualify*.sh
```

Both files should be executable. These shortcuts may then be exposed through the Termux home-screen widget/shortcut surface.

## Two-button operating model

### `LOOM_Qualify`

Use this for the normal governed qualification path.

Behavior:

1. refuses a dirty authoritative working tree;
2. reads the current `engineering/pixel/active_qualification.txt` bootstrap config;
3. fetches GitHub;
4. verifies/switches to the configured branch;
5. fast-forwards only;
6. rereads config after the pull;
7. follows one branch/config handoff if the refreshed config changes target branch;
8. rereads config again and fails closed if it changes a second time;
9. prints the exact effective branch and SHA;
10. executes the exact configured qualification command;
11. records UTC start/end, exit code, and PASS/FAIL;
12. copies the complete transcript to the Android clipboard;
13. optionally launches a configured read-only Spatial Review companion after PASS.

A raw Pixel PASS is a governed qualification result for the exact reported Git SHA.

### `LOOM_Qualify_AI`

Use this when you want the same governed qualification plus bounded local mechanical triage/repair if and only if the governed run fails.

Behavior:

1. runs the exact same raw governed qualifier first;
2. if raw qualification passes, no API call or repair occurs;
3. if raw qualification fails, verifies that the authoritative repo is still clean;
4. creates a detached temporary worktree at the exact failed SHA;
5. sends the failing transcript plus the allowed Pixel harness source context to the OpenAI Responses API;
6. applies only bounded exact-string replacement edits in the detached worktree;
7. reruns the exact qualification command inside that temporary worktree;
8. allows only a small bounded number of attempts (`LOOM_ASSISTED_MAX_ATTEMPTS`, default 2);
9. if a local retry passes, packages the candidate patch with `candidate_patch.py`;
10. writes logs/decisions/patches under `$HOME/.cache/loom/assisted/`;
11. copies a compact assisted report to the Android clipboard;
12. removes the temporary worktree;
13. never commits or pushes.

A successful assisted repair is **not** a governed PASS. It is reported as:

```text
LOCAL_REPAIR_CANDIDATE_PASS=YES
RESULT=LOCAL_REPAIR_CANDIDATE_PASS
```

That means only: a candidate mechanical patch fixed the failure in an isolated local worktree. The authoritative repository remains unchanged until the patch is reviewed/reproduced through GitHub and a new governed head is qualified on Pixel.

## Active qualification handoff contract

`engineering/pixel/active_qualification.txt` is the repo-owned qualification handoff contract.

Expected structure:

```text
<target branch>
<qualification command>
[optional spatial review command]
```

The raw runner deliberately rereads this file after pulling the bootstrap branch so a just-merged or just-updated branch can hand the Pixel to a new qualification branch in one tap.

Fail-closed rule: after following the first refreshed branch handoff, if a second reread changes branch again, the runner refuses rather than chase an unstable chain.

This is what enables the normal workflow:

```text
Assistant/GitHub prepares governed branch
→ user taps LOOM_Qualify
→ Pixel fetches/switches/qualifies exact head
→ transcript lands on Android clipboard
→ user pastes transcript back into ChatGPT
→ exact head is reviewed/merged only after PASS
```

## OpenAI API key setup for assisted qualification

The repository does not contain an API key.

Run once from Termux:

```bash
cd /storage/emulated/0/Download/LOOM_GIT
bash engineering/pixel/configure_openai_key.sh
```

The prompt is hidden:

```text
Paste OpenAI API key (input hidden):
```

Paste the key there, not into chat.

The script stores:

```text
$HOME/.config/loom/openai.env
```

with mode `600` inside a mode-`700` config directory.

The file exports:

```text
OPENAI_API_KEY=<local secret>
LOOM_REPAIR_MODEL=gpt-5.6-terra
```

The model may be overridden locally with `LOOM_REPAIR_MODEL`.

Security rules:

- never commit the key;
- never place the key in a shortcut script;
- never paste the key into qualification transcripts or chat;
- raw `LOOM_Qualify` sends nothing to the OpenAI API;
- assisted `LOOM_Qualify_AI` sends the failing transcript plus allowed Pixel harness source context only after a governed failure.

## Repair boundary

The v0.1 assisted repair agent may edit only temporary-worktree copies of:

```text
engineering/pixel/*.py
engineering/pixel/*.sh
```

It may not edit:

- tests;
- `engineering/pixel/active_qualification.txt`;
- `src/`;
- `data/`;
- canon;
- schemas;
- expected scientific/numerical values;
- Navigator behavior;
- runtime authority semantics;
- campaign state;
- physics/scientific conclusions.

Examples of allowed mechanical repairs include:

- Android/Termux path portability;
- import/bootstrap paths;
- shell quoting;
- writable local-directory selection;
- subprocess/process lifecycle;
- command invocation;
- similarly bounded Pixel harness defects.

If the agent cannot repair the failure within that boundary, it must escalate.

## Candidate-patch packaging

On Termux/shared storage, linked worktrees can execute the repaired qualification correctly while Git metadata operations inside the worktree are unreliable.

Therefore candidate patches are built by `candidate_patch.py`, which compares the authoritative file copies against the repaired copies using Python `difflib` for only the agent-recorded `applied_paths`.

This avoids treating the temporary linked worktree as Git authority and preserves the no-commit/no-push rule.

## Result semantics

### Raw governed success

```text
LOOM_PIXEL_QUALIFICATION_STATUS=PASS
```

For the AI wrapper, this becomes:

```text
GOVERNED_QUALIFICATION_PASS=YES
LOCAL_REPAIR_ATTEMPTED=NO
RESULT=GOVERNED_QUALIFICATION_PASS
```

### Raw governed failure, assisted repair succeeds locally

```text
GOVERNED_QUALIFICATION_PASS=NO
LOCAL_REPAIR_ATTEMPTED=YES
LOCAL_REPAIR_CANDIDATE_PASS=YES
RESULT=LOCAL_REPAIR_CANDIDATE_PASS
CANDIDATE_PATCH=<path under $HOME/.cache/loom/assisted/...>
```

This is evidence only, not authority.

### Raw governed failure, repair refused or unsuccessful

```text
GOVERNED_QUALIFICATION_PASS=NO
RESULT=ESCALATE
```

The authoritative repo remains unchanged.

## Clipboard workflow

The normal Pixel loop is intentionally low-friction:

```text
GitHub change
→ tap qualification shortcut
→ Pixel runs qualification
→ result copied to Android clipboard
→ switch to ChatGPT
→ paste
```

No manual terminal text selection is required.

For the AI shortcut, the raw qualifier may copy its full transcript first. When the assisted wrapper finishes, it overwrites the clipboard with the compact assisted report.

## Spatial Review companion

When a third line is present in `active_qualification.txt`, the raw runner may launch the read-only Spatial Review companion after a PASS.

Current design:

- local browser only;
- typically `127.0.0.1:8878`;
- Python/state remains authoritative;
- browser is presentation/review only;
- no browser calculation/state/execution authority.

The Spatial Review feature is independent of whether the raw or AI shortcut is used; the qualification command remains authoritative.

## Proven smoke test

The complete assisted workflow was proven on Pixel on 2026-09-14 with a disposable controlled branch containing an intentional mechanical Termux defect:

```text
PermissionError: [Errno 13] Permission denied: '/tmp/loom-assisted-controlled-test.txt'
```

The governed run correctly failed. The assisted wrapper created the detached worktree and the repair model diagnosed the problem as a non-writable `/tmp` path on Termux.

The bounded repair changed the fixture to use a writable Termux-home cache location. The exact qualification command then passed inside the temporary worktree.

Final proven result:

```text
GOVERNED_QUALIFICATION_PASS=NO
LOCAL_REPAIR_ATTEMPTED=YES
LOCAL_REPAIR_ATTEMPTS=1
LOCAL_REPAIR_CANDIDATE_PASS=YES
RESULT=LOCAL_REPAIR_CANDIDATE_PASS
TRIAGE=Fixture writes to non-writable /tmp on Termux.
REASON=Use a writable Termux-home cache directory without changing qualification semantics.
```

The candidate patch was packaged under `$HOME/.cache/loom/assisted/.../candidate.patch`, and the authoritative branch remained deliberately broken/unchanged. This validated the complete authority model end to end.

## Troubleshooting

### Widget appears to run the wrong shortcut

Run the intended shortcut directly in Termux to disambiguate launcher/widget behavior:

```bash
~/.shortcuts/LOOM_Qualify.sh
```

or:

```bash
~/.shortcuts/LOOM_Qualify_AI.sh
```

### AI shortcut shows only a raw PASS

That is expected if the governed qualification passed. The API repair path is not invoked on success.

### AI shortcut shows only a raw FAIL and returns to shell

Run the AI shortcut directly from Termux and inspect output. The assisted wrapper should continue after the raw failure. If it does not, treat that as an assisted-wrapper defect rather than as a successful repair attempt.

### Dirty tree refusal

Do not bypass it. The authoritative Pixel checkout must be clean before governed qualification or assisted repair.

### Branch handoff unexpectedly avoids the intended smoke test

Remember that the raw runner obeys `active_qualification.txt`. For a controlled repair smoke test, the disposable branch must point `active_qualification.txt` to itself so the runner cannot hand off to another passing branch before the intentional failure executes.

### Candidate patch packaging failure

Current main uses metadata-independent `candidate_patch.py`; do not revert to `git -C "$WORKTREE" diff` on Termux shared storage.

## Normal operating rule

Use `LOOM_Qualify` by default.

Use `LOOM_Qualify_AI` when you want automatic bounded triage/repair of likely Pixel harness/platform failures.

In both cases:

- GitHub remains repository authority;
- exact Pixel-qualified heads matter;
- a failed qualifier is a failure until rerun and passed;
- an AI local repair PASS is only a candidate patch;
- final authoritative acceptance still requires GitHub review plus a fresh governed Pixel PASS on the real branch.
