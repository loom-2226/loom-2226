#!/data/data/com.termux/files/usr/bin/bash
set -u

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
CONFIG_REL="engineering/pixel/active_qualification.txt"
CONFIG="$SCRIPT_DIR/active_qualification.txt"
QUALIFICATION_POINTER_REF="origin/qualification/active"
QUALIFICATION_LOG_DIR="${LOOM_QUALIFICATION_LOG_DIR:-$(dirname "$REPO_ROOT")/LOOM_Qualification_Logs}"
QUALIFICATION_LOCK_DIR="${TMPDIR:-$HOME/.cache/loom}/qualification.lock"
QUALIFICATION_LOCK_OWNER_BASHPID="$BASHPID"

cd "$REPO_ROOT" || exit 90
mkdir -p "$(dirname "$QUALIFICATION_LOCK_DIR")"
if ! mkdir "$QUALIFICATION_LOCK_DIR" 2>/dev/null; then
  LOCK_PID="$(cat "$QUALIFICATION_LOCK_DIR/pid" 2>/dev/null || true)"
  if [[ -n "$LOCK_PID" ]] && kill -0 "$LOCK_PID" 2>/dev/null; then echo "LOOM PIXEL QUALIFICATION: QUALIFICATION_ALREADY_RUNNING (PID=$LOCK_PID)" >&2; exit 97; fi
  rm -rf "$QUALIFICATION_LOCK_DIR"; mkdir "$QUALIFICATION_LOCK_DIR" 2>/dev/null || exit 98
fi
printf '%s\n' "$QUALIFICATION_LOCK_OWNER_BASHPID" > "$QUALIFICATION_LOCK_DIR/pid"
TMP="$(mktemp -t loom-pixel-qual.XXXXXX)"; CLIPBOARD_RECEIPT="$(mktemp -t loom-pixel-receipt.XXXXXX)"
cleanup(){ rm -f "$TMP" "$CLIPBOARD_RECEIPT"; [[ "$BASHPID" != "$QUALIFICATION_LOCK_OWNER_BASHPID" ]] || rm -rf "$QUALIFICATION_LOCK_DIR"; }
trap cleanup EXIT

_parse_remote_config(){ local remote_config="$1" ref="$2" phase="$3"; mapfile -t CFG <<< "$remote_config"; QUAL_BRANCH="${CFG[0]:-}"; QUAL_COMMAND="${CFG[1]:-}"; [[ -n "$QUAL_BRANCH" && -n "$QUAL_COMMAND" ]] || { echo "LOOM PIXEL QUALIFICATION: invalid config from $ref during $phase" >&2; exit 96; }; }
load_qualification_pointer_config(){ local phase="${1:-REMOTE_QUALIFICATION_POINTER}" remote_config; remote_config="$(git show "$QUALIFICATION_POINTER_REF:$CONFIG_REL" 2>/dev/null)" || { echo "LOOM PIXEL QUALIFICATION: unable to read $QUALIFICATION_POINTER_REF:$CONFIG_REL during $phase" >&2; exit 95; }; _parse_remote_config "$remote_config" "$QUALIFICATION_POINTER_REF" "$phase"; }
switch_to_config_branch(){ local current_branch="$(git branch --show-current)"; if [[ "$current_branch" != "$QUAL_BRANCH" ]]; then echo "SWITCH $current_branch -> $QUAL_BRANCH"; if git show-ref --verify --quiet "refs/heads/$QUAL_BRANCH"; then git switch "$QUAL_BRANCH"; else git switch --track -c "$QUAL_BRANCH" "origin/$QUAL_BRANCH"; fi; else echo "BRANCH OK $current_branch"; fi; }

if [[ -n "$(git status --porcelain)" ]]; then echo "LOOM PIXEL QUALIFICATION: REFUSED — working tree is not clean." >&2; git status --short >&2; exit 93; fi
{
 echo "LOOM PIXEL QUALIFICATION"; echo "========================"; echo "UTC_START=$(date -u +%Y-%m-%dT%H:%M:%SZ)"; echo "REPO_ROOT=$REPO_ROOT"; echo
 echo "[1/4] FETCH + LOAD GOVERNED POINTER"; git fetch origin; load_qualification_pointer_config "REMOTE_QUALIFICATION_POINTER"; echo "BOOTSTRAP_AUTHORITY=$QUALIFICATION_POINTER_REF"; echo "BOOTSTRAP_CONFIG_BRANCH=$QUAL_BRANCH"; echo "BOOTSTRAP_CONFIG_COMMAND=$QUAL_COMMAND"
 echo "[2/4] SYNC GOVERNED ACTIVE BRANCH"; switch_to_config_branch
 echo "[3/4] FAST-FORWARD + RELOAD GOVERNED POINTER"; git pull --ff-only; git fetch origin qualification/active; load_qualification_pointer_config "POST_PULL_GOVERNED_POINTER"; CURRENT_BRANCH="$(git branch --show-current)"; [[ "$QUAL_BRANCH" == "$CURRENT_BRANCH" ]] || { echo "GOVERNED_POINTER_HANDOFF_REFUSED=$CURRENT_BRANCH->$QUAL_BRANCH" >&2; exit 94; }
 echo "EFFECTIVE_CONFIG_BRANCH=$QUAL_BRANCH"; echo "EFFECTIVE_CONFIG_COMMAND=$QUAL_COMMAND"; echo "BRANCH=$CURRENT_BRANCH"; echo "SHA=$(git rev-parse HEAD)"; echo; echo "[4/4] RUN"; echo '$' "$QUAL_COMMAND"; echo
 set +e; export PYTHONPATH="$REPO_ROOT${PYTHONPATH:+:$PYTHONPATH}"; bash -lc "$QUAL_COMMAND"; RC=$?; set -e
 echo; echo "EXIT_CODE=$RC"; echo "UTC_END=$(date -u +%Y-%m-%dT%H:%M:%SZ)"; if [[ $RC -eq 0 ]]; then echo "LOOM_PIXEL_QUALIFICATION_STATUS=PASS"; else echo "LOOM_PIXEL_QUALIFICATION_STATUS=FAIL"; fi; exit "$RC"
} 2>&1 | tee "$TMP"
PIPE_RC=${PIPESTATUS[0]}
load_qualification_pointer_config "POST_QUALIFICATION"
mkdir -p "$QUALIFICATION_LOG_DIR"; STAMP="$(date -u +%Y%m%dT%H%M%SZ)"; LOG="$QUALIFICATION_LOG_DIR/qualification-$STAMP.log"; LATEST="$QUALIFICATION_LOG_DIR/latest.log"; cp "$TMP" "$LOG"; cp "$TMP" "$LATEST"
TRANSCRIPT_SHA256="$(sha256sum "$LOG" | awk '{print $1}')"; FINAL_BRANCH="$(grep '^BRANCH=' "$TMP" | tail -1 | cut -d= -f2-)"; FINAL_SHA="$(grep '^SHA=' "$TMP" | tail -1 | cut -d= -f2-)"; FINAL_STATUS="$(grep '^LOOM_PIXEL_QUALIFICATION_STATUS=' "$TMP" | tail -1 | cut -d= -f2-)"; [[ $PIPE_RC -eq 0 && "$FINAL_STATUS" == PASS ]] && TESTS=PASS || TESTS=FAIL
{ echo "LOOM PIXEL QUALIFICATION RECEIPT"; echo "BRANCH=$FINAL_BRANCH"; echo "SHA=$FINAL_SHA"; echo "TESTS=$TESTS"; echo "EXIT_CODE=$PIPE_RC"; echo "LOOM_PIXEL_QUALIFICATION_STATUS=${FINAL_STATUS:-FAIL}"; echo "TRANSCRIPT_SHA256=$TRANSCRIPT_SHA256"; } > "$CLIPBOARD_RECEIPT"
echo; echo "QUALIFICATION_LOG_SAVED=$LOG"; echo "QUALIFICATION_LOG_LATEST=$LATEST"; echo "TRANSCRIPT_SHA256=$TRANSCRIPT_SHA256"
if command -v termux-clipboard-set >/dev/null 2>&1; then termux-clipboard-set < "$CLIPBOARD_RECEIPT"; echo "Compact qualification receipt copied to Android clipboard; full transcript retained locally."; else cat "$CLIPBOARD_RECEIPT"; fi
exit "$PIPE_RC"
