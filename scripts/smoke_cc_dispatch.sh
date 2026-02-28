#!/bin/bash
set -euo pipefail

# OpenClaw DR Dispatcher Smoke Test

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CLAWD_DIR="$(dirname "$SCRIPT_DIR")"
SMOKE_RUNS_DIR="$(mktemp -d)"

cleanup() {
    rm -rf "$SMOKE_RUNS_DIR"
}
trap cleanup EXIT

log() { printf '[smoke] %s\n' "$*" >&2; }
fail() { log "FAIL: $*"; exit 1; }

log "SMOKE_RUNS_DIR=$SMOKE_RUNS_DIR"

# Test 1: NOT_HANDLED case (input without /dr or /deapr)
log "=== Test 1: NOT_HANDLED case ==="
set +e
out="$(python3 "$SCRIPT_DIR/cc_dr_dispatch.py" --text "hello world" 2>&1)"
rc=$?
set -e
echo "$out" | head -5 >&2
if [[ "$rc" != 10 ]]; then
    fail "NOT_HANDLED case should return RC=10, got $rc"
fi
if [[ "$out" != *"NOT_HANDLED"* ]]; then
    fail "NOT_HANDLED case should output NOT_HANDLED"
fi
log "Test 1 PASSED: NOT_HANDLED returns RC=10"

# Test 2: Hit /deapr prefix
log "=== Test 2: /deapr prefix dispatch ==="
export DR_RUNS_DIR="$SMOKE_RUNS_DIR"

set +e
out="$(echo "/deapr hvdc market drivers and catalysts" | python3 "$SCRIPT_DIR/cc_dr_dispatch.py" --stdin --runs-dir "$SMOKE_RUNS_DIR" 2>&1)"
rc=$?
set -e

echo "$out" | head -15 >&2
log "Exit code: $rc"

# Check runs created in SMOKE_RUNS_DIR
RUN_COUNT=$(ls -1 "$SMOKE_RUNS_DIR" 2>/dev/null | wc -l | tr -d ' ')
log "Runs in SMOKE_RUNS_DIR: $RUN_COUNT"

if [[ "$RUN_COUNT" -lt 1 ]]; then
    fail "No runs created in SMOKE_RUNS_DIR"
fi

# Check for report and verification
for run_dir in "$SMOKE_RUNS_DIR"/*; do
    if [[ -d "$run_dir" ]]; then
        REPORT="$run_dir/final/report.md"
        VERIFY="$run_dir/final/verification.md"
        if [[ -f "$REPORT" ]]; then
            log "Found report: $REPORT"
        fi
        if [[ -f "$VERIFY" ]]; then
            log "Found verification: $VERIFY"
        fi
    fi
done

if [[ "$RUN_COUNT" -gt 0 ]]; then
    log "Test 2 PASSED: /deapr dispatch creates runs"
else
    fail "Test 2 FAILED"
fi

# Test 3: Topic clarification needed
log "=== Test 3: Clarification needed ==="
set +e
out="$(echo "/deapr hi" | python3 "$SCRIPT_DIR/cc_dr_dispatch.py" --stdin 2>&1)"
rc=$?
set -e
echo "$out" | head -10 >&2

if [[ "$rc" != 2 ]]; then
    fail "Clarification case should return RC=2, got $rc"
fi
if [[ "$out" != *"clarification"* ]]; then
    fail "Clarification case should mention clarification"
fi
log "Test 3 PASSED: Clarification returns RC=2"

log ""

echo "[smoke] === Test 4: bare /deapr should clarify (RC=2) ==="
set +e
echo "/deapr" | python3 scripts/cc_dr_dispatch.py --stdin >/tmp/cc_dispatch_bare.out 2>&1
rc=$?
set -e
if [ "$rc" -ne 2 ]; then
  echo "FAIL: bare /deapr should RC=2, got $rc"
  cat /tmp/cc_dispatch_bare.out || true
  exit 1
fi
echo "[smoke] Test 4 PASSED: bare /deapr returns RC=2"

log "=== ALL SMOKE TESTS PASSED ==="


