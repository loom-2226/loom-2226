#!/data/data/com.termux/files/usr/bin/bash
set -u

# Governed Pixel qualification runner.
# One command: fetch/pull current qualification branch, run it, copy complete result.

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
CONFIG="$SCRIPT_DIR/active_qualification.txt"

cd "$REPO_ROOT" || exit 90

if [[ ! -f "$CONFIG" ]]; then
  echo "LOOM PIXEL QUALIFICATION: missing $CONFIG" >&2
  exit 91
fi

mapfile -t CFG < "$CONFIG"
QUAL_BRANCH="${CFG[0]:-}"
QUAL_COMMAND="${CFG[1]:-}"

if [[ -z "$QUAL_BRANCH" || -z "$QUAL_COMMAND" ]]; then
  echo "LOOM PIXEL QUALIFICATION: invalid active qualification config" >&2
  exit 92
fi

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
  echo "CONFIG_BRANCH=$QUAL_BRANCH"
  echo "CONFIG_COMMAND=$QUAL_COMMAND"
  echo

  echo "[1/4] FETCH"
  git fetch origin

  CURRENT_BRANCH="$(git branch --show-current)"
  if [[ "$CURRENT_BRANCH" != "$QUAL_BRANCH" ]]; then
    echo "[2/4] SWITCH $CURRENT_BRANCH -> $QUAL_BRANCH"
    if git show-ref --verify --quiet "refs/heads/$QUAL_BRANCH"; then
      git switch "$QUAL_BRANCH"
    else
      git switch --track -c "$QUAL_BRANCH" "origin/$QUAL_BRANCH"
    fi
  else
    echo "[2/4] BRANCH OK $CURRENT_BRANCH"
  fi

  echo "[3/4] FAST-FORWARD"
  git pull --ff-only

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

if command -v termux-clipboard-set >/dev/null 2>&1; then
  termux-clipboard-set < "$TMP"
  echo
  echo "Complete qualification output copied to Android clipboard."
else
  echo
  echo "WARNING: termux-clipboard-set unavailable; output was not copied." >&2
fi

exit "$PIPE_RC"
