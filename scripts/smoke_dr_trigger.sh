#!/usr/bin/env bash
set -euo pipefail

CLAWD_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SMOKE_RUNS_DIR="$(mktemp -d)"
SMOKE_TMP_DIR="$(mktemp -d)"
EMIT_FILE="$SMOKE_TMP_DIR/dr_cli_smoke.zsh"

cleanup() { rm -rf "$SMOKE_RUNS_DIR" "$SMOKE_TMP_DIR"; }
trap cleanup EXIT

log() { printf '%s\n' "$*" >&2; }
fail() { log "FAIL: $*"; exit 1; }

count_runs() {
  find "$SMOKE_RUNS_DIR" -mindepth 1 -maxdepth 1 -type d 2>/dev/null | wc -l | tr -d ' '
}

assert_eq() {
  local a="$1" b="$2" msg="$3"
  [[ "$a" == "$b" ]] || fail "$msg (expected=$b got=$a)"
}

assert_gt() {
  local a="$1" b="$2" msg="$3"
  [[ "$a" -gt "$b" ]] || fail "$msg (expected > $b got=$a)"
}

# NOTE: Must be callable in current shell; do NOT run in bash -c
invoke_openclaw_router() {
  # Use openclaw_router_cli.py which supports --runs-dir injection
  python3 "$CLAWD_DIR/scripts/openclaw_router_cli.py" \
    --runs-dir "$SMOKE_RUNS_DIR" \
    "$@"
}

run_case() {
  local name="$1"; shift
  log ""
  log "==== CASE: $name ===="

  (
    set -euo pipefail
    # Per-case env isolation
    unset DR_KEYWORD_FORCE_IN_GROUP DR_KEYWORD_DEFAULT DR_KEYWORD_FORCE_IN_DM
    export DR_RUNS_DIR="$SMOKE_RUNS_DIR"
    export SMOKE=1

    # Execute the remaining arguments as a command in THIS subshell
    "$@"
  )
}

run_case_eval() {
  local name="$1"; shift
  local script="$1"; shift || true

  log ""
  log "==== CASE: $name ===="

  (
    set -euo pipefail
    unset DR_KEYWORD_FORCE_IN_GROUP DR_KEYWORD_DEFAULT DR_KEYWORD_FORCE_IN_DM
    export DR_RUNS_DIR="$SMOKE_RUNS_DIR"
    export SMOKE=1
    eval "$script"
  )
}

log "SMOKE_RUNS_DIR=$SMOKE_RUNS_DIR"
log "CLAWD_DIR=$CLAWD_DIR"

# Emit CLI block
run_case "emit dr cli block" bash "$CLAWD_DIR/scripts/enable_dr_cli.sh" --emit "$EMIT_FILE"
[[ -s "$EMIT_FILE" ]] || fail "--emit did not create file: $EMIT_FILE"

# CASE A: keyword suggest-only in group
run_case_eval "keyword suggest-only (group default)" '
  before="$(count_runs)"
  export DR_KEYWORD_DEFAULT="suggest"
  export DR_KEYWORD_FORCE_IN_GROUP="0"
  set +e
  out="$(invoke_openclaw_router --simulate-group --text "please do deep research on hvdc" 2>&1)"
  rc=$?
  set -e
  after="$(count_runs)"
  echo "$out" | head -n 12 >&2
  # Assert runs unchanged
  assert_eq "$after" "$before" "suggest-only must not start pipeline (runs delta)"
  # Assert output contains /dr prompt
  echo "$out" | grep -q "/dr" || fail "suggest output must contain /dr prompt"
'

# CASE B: keyword force in group
run_case_eval "keyword force (group, FORCE_IN_GROUP=1)" '
  before="$(count_runs)"
  export DR_KEYWORD_DEFAULT="suggest"
  export DR_KEYWORD_FORCE_IN_GROUP="1"
  set +e
  out="$(invoke_openclaw_router --simulate-group --text "please do deep research on hvdc" 2>&1)"
  rc=$?
  set -e
  after="$(count_runs)"
  echo "$out" | head -n 12 >&2
  assert_gt "$after" "$before" "force-in-group must start pipeline (runs delta)"
'

# CASE C: drq default runtime-real (suggest)
run_case_eval "drq default suggests (runtime-real)" '
  before="$(count_runs)"
  set +e
  # Use "analysis" keyword to trigger suggestion
  out="$(DR_RUNS_DIR="$SMOKE_RUNS_DIR" DR_CLI_FORCE_REPO=1 zsh -lc "source '\''$EMIT_FILE'\''; drq '\''hvdc market analysis'\''" 2>&1)"
  rc=$?
  set -e
  after="$(count_runs)"
  echo "$out" | head -n 12 >&2
  assert_eq "$rc" "2" "drq default should exit 2 (suggest)"
  assert_eq "$after" "$before" "drq default should not start pipeline (runs delta)"
'

# CASE D: drq --force runtime-real (execute)
run_case_eval "drq --force executes (runtime-real)" '
  before="$(count_runs)"
  set +e
  # Use "analysis" keyword + explicit topic to avoid clarification
  out="$(DR_RUNS_DIR="$SMOKE_RUNS_DIR" DR_CLI_FORCE_REPO=1 zsh -lc "source '\''$EMIT_FILE'\''; drq --force '\''hvdc market analysis'\''" 2>&1)"
  rc=$?
  set -e
  after="$(count_runs)"
  echo "$out" | head -n 12 >&2
  [[ "$rc" != "2" ]] || fail "drq --force must not exit 2"
  assert_gt "$after" "$before" "drq --force must start pipeline (runs delta)"
'

# CASE E: /dr hard trigger (explicit topic to avoid clarify)
run_case_eval "/dr hard trigger starts pipeline" '
  before="$(count_runs)"
  set +e
  out="$(invoke_openclaw_router --text "/dr hvdc market drivers and catalysts" 2>&1)"
  rc=$?
  set -e
  after="$(count_runs)"
  echo "$out" | head -n 12 >&2
  assert_gt "$after" "$before" "/dr hard trigger must start pipeline (runs delta)"
'

log ""
log "ALL PASSED"
