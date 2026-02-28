#!/usr/bin/env bash
set -euo pipefail

OUT="$(mktemp)"
TMP_RUNS="$(mktemp -d)"
export DR_RUNS_DIR="$TMP_RUNS"

set +e
/opt/homebrew/bin/openclaw tui --session main --timeout-ms 20000 --message "/dr analyze bugs and innovation" >"$OUT" 2>&1
rc=$?
set -e

if ! grep -q "BugTriageMode-R_" "$OUT"; then
  echo "FAIL: no BugTriageMode-R_ in openclaw tui output"
  echo "RC=$rc"
  tail -n 120 "$OUT" || true
  exit 1
fi

echo "SMOKE_TUI_DR_OK"
echo "RC=$rc"
