#!/data/data/com.termux/files/usr/bin/bash
set -u

# Governed Pixel qualification runner.
# One command: fetch, determine whether the current branch is an unmerged
# self-qualifying candidate or a merged/stale branch, switch/pull the governed
# qualification branch, refresh config, run it, copy the complete result, and
# optionally launch a read-only Spatial Review.

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
CONFIG_REL="engineering/pixel/active_qualification.txt"
CONFIG="$SCRIPT_DIR/active_qualification.txt"
LOOM_SPATIAL_REVIEW_URL="http://127.0.0.1:8878/"

cd "$REPO_ROOT" || exit 90

load_config() {
  local phase="${1:-UNSPECIFIED}"
  if [[ ! -f "$CONFIG" ]]; then
    echo "LOOM PIXEL QUALIFICATION: missing $CONFIG during $phase" >&2
    exit 91
  fi

  mapfile -t CFG < "$CONFIG"
  QUAL_BRANCH="${CFG[0]:-}"
  QUAL_COMMAND="${CFG[1]:-}"
  SPATIAL_REVIEW_COMMAND="${CFG[2]:-}"

  if [[ -z "$QUAL_BRANCH" || -z "$QUAL_COMMAND" ]]; then
    echo "LOOM PIXEL QUALIFICATION: invalid active qualification config during $phase" >&2
    exit 92
  fi
}

load_origin_main_config() {
  local phase="${1:-ORIGIN_MAIN_BOOTSTRAP}"
  local remote_config
  if ! remote_config="$(git show "origin/main:engineering/pixel/active_qualification.txt" 2>/dev/null)"; then
    echo "LOOM PIXEL QUALIFICATION: unable to read origin/main:$CONFIG_REL during $phase" >&2
    exit 95
  fi

  mapfile -t CFG <<< "$remote_config"
  QUAL_BRANCH="${CFG[0]:-}"
  QUAL_COMMAND="${CFG[1]:-}"
  SPATIAL_REVIEW_COMMAND="${CFG[2]:-}"

  if [[ -z "$QUAL_BRANCH" || -z "$QUAL_COMMAND" ]]; then
    echo "LOOM PIXEL QUALIFICATION: invalid origin/main active qualification config during $phase" >&2
    exit 96
  fi
}

switch_to_config_branch() {
  local current_branch
  current_branch="$(git branch --show-current)"
  if [[ "$current_branch" != "$QUAL_BRANCH" ]]; then
    echo "SWITCH $current_branch -> $QUAL_BRANCH"
    if git show-ref --verify --quiet "refs/heads/$QUAL_BRANCH"; then
      git switch "$QUAL_BRANCH"
    else
      git switch --track -c "$QUAL_BRANCH" "origin/$QUAL_BRANCH"
    fi
  else
    echo "BRANCH OK $current_branch"
  fi
}

choose_bootstrap_config() {
  local current_branch current_head local_config_branch
  current_branch="$(git branch --show-current)"
  current_head="$(git rev-parse HEAD)"
  local_config_branch=""

  if [[ -f "$CONFIG" ]]; then
    local_config_branch="$(sed -n '1p' "$CONFIG")"
  fi

  CURRENT_BRANCH="$current_branch"
  CURRENT_HEAD="$current_head"
  LOCAL_CONFIG_BRANCH="$local_config_branch"

  # An unmerged candidate branch whose own config points to itself must be able
  # to qualify itself. Once that exact head is merged into origin/main, it is
  # stale for qualification purposes and must follow the authoritative config
  # published by origin/main instead.
  if [[ -n "$CURRENT_BRANCH" && "$CURRENT_BRANCH" != "main" ]]; then
    if [[ "$LOCAL_CONFIG_BRANCH" == "$CURRENT_BRANCH" ]]; then
      if git merge-base --is-ancestor "$CURRENT_HEAD" origin/main; then
        echo "BOOTSTRAP_MODE=CURRENT_BRANCH_MERGED_INTO_ORIGIN_MAIN"
        load_origin_main_config "MERGED_BRANCH_BOOTSTRAP"
        BOOTSTRAP_AUTHORITY="origin/main"
      else
        echo "BOOTSTRAP_MODE=CURRENT_UNMERGED_SELF_QUALIFICATION"
        load_config "CURRENT_UNMERGED_SELF_QUALIFICATION"
        BOOTSTRAP_AUTHORITY="current-unmerged-branch"
      fi
    else
      echo "BOOTSTRAP_MODE=ORIGIN_MAIN_ACTIVE_QUALIFICATION"
      load_origin_main_config "ORIGIN_MAIN_ACTIVE_QUALIFICATION"
      BOOTSTRAP_AUTHORITY="origin/main"
    fi
  else
    echo "BOOTSTRAP_MODE=ORIGIN_MAIN_ACTIVE_QUALIFICATION"
    load_origin_main_config "ORIGIN_MAIN_ACTIVE_QUALIFICATION"
    BOOTSTRAP_AUTHORITY="origin/main"
  fi
}

if [[ -n "$(git status --porcelain)" ]]; then
  echo "LOOM PIXEL QUALIFICATION: REFUSED — working tree is not clean." >&2
  git status --short >&2
  exit 93
fi

TMP="$(mktemp -t loom-pixel-qual.XXXXXX)"
cleanup() { rm -f "$TMP"; }
trap cleanup EXIT

{
  echo "LOOM PIXEL QUALIFICATION"
  echo "========================"
  echo "UTC_START=$(date -u +%Y-%m-%dT%H:%M:%SZ)"
  echo "REPO_ROOT=$REPO_ROOT"
  echo

  echo "[1/4] FETCH + CHOOSE GOVERNED CONFIG"
  git fetch origin
  choose_bootstrap_config
  BOOTSTRAP_BRANCH="$QUAL_BRANCH"
  BOOTSTRAP_COMMAND="$QUAL_COMMAND"
  BOOTSTRAP_SPATIAL_REVIEW_COMMAND="$SPATIAL_REVIEW_COMMAND"
  echo "BOOTSTRAP_AUTHORITY=$BOOTSTRAP_AUTHORITY"
  echo "BOOTSTRAP_CONFIG_BRANCH=$BOOTSTRAP_BRANCH"
  echo "BOOTSTRAP_CONFIG_COMMAND=$BOOTSTRAP_COMMAND"
  if [[ -n "$BOOTSTRAP_SPATIAL_REVIEW_COMMAND" ]]; then
    echo "BOOTSTRAP_SPATIAL_REVIEW_COMMAND=$BOOTSTRAP_SPATIAL_REVIEW_COMMAND"
  fi

  echo "[2/4] SYNC GOVERNED ACTIVE BRANCH"
  switch_to_config_branch

  echo "[3/4] FAST-FORWARD + CONFIG REFRESH"
  git pull --ff-only
  load_config "POST_PULL"

  CURRENT_BRANCH="$(git branch --show-current)"
  if [[ "$QUAL_BRANCH" != "$CURRENT_BRANCH" ]]; then
    echo "CONFIG_HANDOFF=$CURRENT_BRANCH->$QUAL_BRANCH"
    switch_to_config_branch
    git pull --ff-only
    load_config "POST_HANDOFF_PULL"

    CURRENT_BRANCH="$(git branch --show-current)"
    if [[ "$QUAL_BRANCH" != "$CURRENT_BRANCH" ]]; then
      echo "CONFIG_BRANCH_CHAIN_REFUSED=$CURRENT_BRANCH->$QUAL_BRANCH" >&2
      echo "LOOM PIXEL QUALIFICATION: REFUSED — active config requested more than one post-pull branch handoff." >&2
      exit 94
    fi
  fi

  echo "EFFECTIVE_CONFIG_BRANCH=$QUAL_BRANCH"
  echo "EFFECTIVE_CONFIG_COMMAND=$QUAL_COMMAND"
  if [[ -n "$SPATIAL_REVIEW_COMMAND" ]]; then
    echo "EFFECTIVE_SPATIAL_REVIEW_COMMAND=$SPATIAL_REVIEW_COMMAND"
  fi
  echo "BRANCH=$(git branch --show-current)"
  echo "SHA=$(git rev-parse HEAD)"
  echo
  echo "[4/4] RUN"
  echo '$' "$QUAL_COMMAND"
  echo

  set +e
  bash -lc "$QUAL_COMMAND"
  RC=$?
  set -e

  echo
  echo "EXIT_CODE=$RC"
  echo "UTC_END=$(date -u +%Y-%m-%dT%H:%M:%SZ)"
  if [[ $RC -eq 0 ]]; then
    echo "LOOM_PIXEL_QUALIFICATION_STATUS=PASS"
  else
    echo "LOOM_PIXEL_QUALIFICATION_STATUS=FAIL"
  fi
  exit "$RC"
} 2>&1 | tee "$TMP"
PIPE_RC=${PIPESTATUS[0]}

load_config "POST_QUALIFICATION"
if [[ $PIPE_RC -eq 0 && -n "$SPATIAL_REVIEW_COMMAND" ]]; then
  {
    echo
    echo "[SPATIAL REVIEW]"
    echo "READ_ONLY_PRESENTATION=YES"
    echo "LOOM_SPATIAL_REVIEW_URL=$LOOM_SPATIAL_REVIEW_URL"
    REVIEW_LOG_DIR="${TMPDIR:-$HOME/.cache/loom}"
    mkdir -p "$REVIEW_LOG_DIR"
    REVIEW_LOG="$REVIEW_LOG_DIR/loom-spatial-review.log"
    pkill -f "engineering/pixel/spatial_review.py" >/dev/null 2>&1 || true
    nohup bash -lc "$SPATIAL_REVIEW_COMMAND" >"$REVIEW_LOG" 2>&1 &
    REVIEW_PID=$!
    sleep 0.5
    if kill -0 "$REVIEW_PID" >/dev/null 2>&1; then
      echo "SPATIAL_REVIEW_STATUS=LAUNCHED"
      echo "SPATIAL_REVIEW_PID=$REVIEW_PID"
      echo "SPATIAL_REVIEW_LOG=$REVIEW_LOG"
      if command -v termux-open-url >/dev/null 2>&1; then
        termux-open-url "$LOOM_SPATIAL_REVIEW_URL" >/dev/null 2>&1 || true
        echo "SPATIAL_REVIEW_BROWSER=OPEN_REQUESTED"
      else
        echo "SPATIAL_REVIEW_BROWSER=TERMUX_OPEN_URL_UNAVAILABLE"
      fi
    else
      echo "SPATIAL_REVIEW_STATUS=FAILED_TO_STAY_RUNNING"
      echo "SPATIAL_REVIEW_LOG=$REVIEW_LOG"
    fi
  } 2>&1 | tee -a "$TMP"
fi

if command -v termux-clipboard-set >/dev/null 2>&1; then
  termux-clipboard-set < "$TMP"
  echo
  echo "Complete qualification output copied to Android clipboard."
else
  echo
  echo "WARNING: termux-clipboard-set unavailable; output was not copied." >&2
fi

exit "$PIPE_RC"
