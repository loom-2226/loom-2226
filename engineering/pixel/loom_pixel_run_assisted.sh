#!/data/data/com.termux/files/usr/bin/bash
set -u

# LOOM ASSISTED QUALIFICATION
# Runs the normal governed Pixel qualifier first. Only after a failure does it
# create a detached temporary worktree and attempt bounded mechanical repairs.
# A locally repaired run is evidence for a candidate patch, never a governed PASS.

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
RAW_RUNNER="$SCRIPT_DIR/loom_pixel_run.sh"
CONFIG="$SCRIPT_DIR/active_qualification.txt"
REPAIR_AGENT="$SCRIPT_DIR/mechanical_repair.py"
PATCH_BUILDER="$SCRIPT_DIR/candidate_patch.py"
MAX_ATTEMPTS="${LOOM_ASSISTED_MAX_ATTEMPTS:-2}"
STATE_ROOT="$HOME/.cache/loom/assisted"
ENV_FILE="$HOME/.config/loom/openai.env"

if [[ -f "$ENV_FILE" ]]; then
  # shellcheck disable=SC1090
  source "$ENV_FILE"
fi

mkdir -p "$STATE_ROOT"
RAW_TMP="$(mktemp -t loom-assisted-raw.XXXXXX)"
WORKTREE=""

cleanup() {
  rm -f "$RAW_TMP"
  if [[ -n "$WORKTREE" && -d "$WORKTREE" ]]; then
    git -C "$REPO_ROOT" worktree remove --force "$WORKTREE" >/dev/null 2>&1 || true
  fi
}
trap cleanup EXIT

set +e
bash "$RAW_RUNNER" 2>&1 | tee "$RAW_TMP"
RAW_RC=${PIPESTATUS[0]}
set -e

HEAD_SHA="$(git -C "$REPO_ROOT" rev-parse HEAD 2>/dev/null || echo UNKNOWN)"
BRANCH="$(git -C "$REPO_ROOT" branch --show-current 2>/dev/null || echo UNKNOWN)"
STAMP="$(date -u +%Y%m%dT%H%M%SZ)"
RUN_DIR="$STATE_ROOT/${STAMP}-${HEAD_SHA:0:8}"
mkdir -p "$RUN_DIR"
cp "$RAW_TMP" "$RUN_DIR/governed-transcript.txt"
REPORT="$RUN_DIR/report.txt"
QUALIFICATION_SUMMARY="$(grep -E '^QUALIFICATION_(AXIS|DISPOSITION|MISSING_REQUIRED_EVIDENCE)=' "$RAW_TMP" | tail -n 3 || true)"

copy_report() {
  if command -v termux-clipboard-set >/dev/null 2>&1; then
    termux-clipboard-set < "$REPORT"
  fi
  cat "$REPORT"
}

append_qualification_summary() {
  if [[ -n "$QUALIFICATION_SUMMARY" ]]; then
    printf '%s\n' "$QUALIFICATION_SUMMARY" >> "$REPORT"
  fi
}

if [[ $RAW_RC -eq 0 ]]; then
  cat > "$REPORT" <<EOF
LOOM ASSISTED QUALIFICATION REPORT
=================================
GOVERNED_QUALIFICATION_PASS=YES
LOCAL_REPAIR_ATTEMPTED=NO
BRANCH=$BRANCH
SHA=$HEAD_SHA
RAW_LOG=$RUN_DIR/governed-transcript.txt
RESULT=GOVERNED_QUALIFICATION_PASS
EOF
  append_qualification_summary
  copy_report
  exit 0
fi

if [[ -z "${OPENAI_API_KEY:-}" ]]; then
  cat > "$REPORT" <<EOF
LOOM ASSISTED QUALIFICATION REPORT
=================================
GOVERNED_QUALIFICATION_PASS=NO
LOCAL_REPAIR_ATTEMPTED=NO
BRANCH=$BRANCH
SHA=$HEAD_SHA
RAW_LOG=$RUN_DIR/governed-transcript.txt
RESULT=ESCALATE
REASON=OPENAI_API_KEY is not configured in $ENV_FILE or the environment.
EOF
  append_qualification_summary
  copy_report
  exit "$RAW_RC"
fi

if [[ ! -f "$CONFIG" ]]; then
  cat > "$REPORT" <<EOF
LOOM ASSISTED QUALIFICATION REPORT
=================================
GOVERNED_QUALIFICATION_PASS=NO
LOCAL_REPAIR_ATTEMPTED=NO
BRANCH=$BRANCH
SHA=$HEAD_SHA
RESULT=ESCALATE
REASON=active qualification config is missing after governed failure.
EOF
  append_qualification_summary
  copy_report
  exit "$RAW_RC"
fi

mapfile -t CFG < "$CONFIG"
QUAL_COMMAND="${CFG[1]:-}"
if [[ -z "$QUAL_COMMAND" ]]; then
  cat > "$REPORT" <<EOF
LOOM ASSISTED QUALIFICATION REPORT
=================================
GOVERNED_QUALIFICATION_PASS=NO
LOCAL_REPAIR_ATTEMPTED=NO
BRANCH=$BRANCH
SHA=$HEAD_SHA
RESULT=ESCALATE
REASON=active qualification command is empty after governed failure.
EOF
  append_qualification_summary
  copy_report
  exit "$RAW_RC"
fi

if [[ -n "$(git -C "$REPO_ROOT" status --porcelain)" ]]; then
  cat > "$REPORT" <<EOF
LOOM ASSISTED QUALIFICATION REPORT
=================================
GOVERNED_QUALIFICATION_PASS=NO
LOCAL_REPAIR_ATTEMPTED=NO
BRANCH=$BRANCH
SHA=$HEAD_SHA
RESULT=ESCALATE
REASON=authoritative working tree is dirty; assisted repair refused.
EOF
  append_qualification_summary
  copy_report
  exit "$RAW_RC"
fi

WORK_BASE="${TMPDIR:-$HOME/.cache/loom}"
mkdir -p "$WORK_BASE"
WORKTREE="$WORK_BASE/loom-assisted-worktree-${STAMP}-$$"
(cd "$REPO_ROOT" && git worktree add --detach "$WORKTREE" "$HEAD_SHA") >/dev/null

CURRENT_TRANSCRIPT="$RUN_DIR/governed-transcript.txt"
ATTEMPT=0
LAST_SUMMARY=""
LAST_REASON=""
LOCAL_PASS=0

while [[ $ATTEMPT -lt $MAX_ATTEMPTS ]]; do
  ATTEMPT=$((ATTEMPT + 1))
  DECISION="$RUN_DIR/decision-$ATTEMPT.json"
  set +e
  python "$REPAIR_AGENT" \
    --root "$WORKTREE" \
    --transcript "$CURRENT_TRANSCRIPT" \
    --attempt "$ATTEMPT" \
    --output "$DECISION" >/dev/null
  AGENT_RC=$?
  set -e

  if [[ -f "$DECISION" ]]; then
    LAST_SUMMARY="$(python -c 'import json,sys; print(json.load(open(sys.argv[1])).get("summary", ""))' "$DECISION" 2>/dev/null || true)"
    LAST_REASON="$(python -c 'import json,sys; print(json.load(open(sys.argv[1])).get("reason", ""))' "$DECISION" 2>/dev/null || true)"
  fi

  if [[ $AGENT_RC -ne 0 ]]; then
    break
  fi

  ATTEMPT_LOG="$RUN_DIR/retry-$ATTEMPT.txt"
  set +e
  (cd "$WORKTREE" && bash -lc "$QUAL_COMMAND") >"$ATTEMPT_LOG" 2>&1
  RETRY_RC=$?
  set -e
  CURRENT_TRANSCRIPT="$ATTEMPT_LOG"

  if [[ $RETRY_RC -eq 0 ]]; then
    set +e
    python "$PATCH_BUILDER" \
      --authoritative-root "$REPO_ROOT" \
      --repaired-root "$WORKTREE" \
      --decision "$DECISION" \
      --output "$RUN_DIR/candidate.patch"
    PATCH_RC=$?
    set -e
    if [[ $PATCH_RC -ne 0 ]]; then
      LAST_SUMMARY="Local repair passed qualification, but candidate patch packaging failed."
      LAST_REASON="metadata-independent candidate patch builder returned exit $PATCH_RC"
      break
    fi
    LOCAL_PASS=1
    break
  fi
done

if [[ $LOCAL_PASS -eq 1 ]]; then
  cat > "$REPORT" <<EOF
LOOM ASSISTED QUALIFICATION REPORT
=================================
GOVERNED_QUALIFICATION_PASS=NO
LOCAL_REPAIR_ATTEMPTED=YES
LOCAL_REPAIR_ATTEMPTS=$ATTEMPT
LOCAL_REPAIR_CANDIDATE_PASS=YES
BRANCH=$BRANCH
SHA=$HEAD_SHA
RESULT=LOCAL_REPAIR_CANDIDATE_PASS
TRIAGE=$LAST_SUMMARY
REASON=$LAST_REASON
CANDIDATE_PATCH=$RUN_DIR/candidate.patch
RAW_LOG=$RUN_DIR/governed-transcript.txt
NOTE=Temporary worktree only. Authoritative repo unchanged. Sol/GitHub review and a new governed Pixel qualification are still required.
EOF
else
  cat > "$REPORT" <<EOF
LOOM ASSISTED QUALIFICATION REPORT
=================================
GOVERNED_QUALIFICATION_PASS=NO
LOCAL_REPAIR_ATTEMPTED=YES
LOCAL_REPAIR_ATTEMPTS=$ATTEMPT
LOCAL_REPAIR_CANDIDATE_PASS=NO
BRANCH=$BRANCH
SHA=$HEAD_SHA
RESULT=ESCALATE
TRIAGE=$LAST_SUMMARY
REASON=$LAST_REASON
RAW_LOG=$RUN_DIR/governed-transcript.txt
LAST_RETRY_LOG=$CURRENT_TRANSCRIPT
NOTE=No authoritative files were changed.
EOF
fi

append_qualification_summary
copy_report
exit "$RAW_RC"
