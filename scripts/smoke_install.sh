#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PREFIX="$(mktemp -d)"
RUNS="$(mktemp -d)"

echo "ROOT=$ROOT"
echo "PREFIX=$PREFIX"
echo "RUNS=$RUNS"

bash "$ROOT/scripts/install.sh" --local --prefix "$PREFIX" --no-full-output

export PATH="$PREFIX:$PATH"
command -v dr >/dev/null

export DR_RUNS_DIR="$RUNS"

dr "hvdc market drivers and catalysts for near-term trading catalysts and risks"

REPORT="$(ls -1t "$RUNS"/*/final/report.md 2>/dev/null | head -n 1 || true)"
VERIFY="$(ls -1t "$RUNS"/*/final/verification.md 2>/dev/null | head -n 1 || true)"

test -n "$REPORT"
test -f "$REPORT"
test -n "$VERIFY"
test -f "$VERIFY"

echo "REPORT_OK=$REPORT"
echo "VERIFY_OK=$VERIFY"
echo "SMOKE_INSTALL_OK"
