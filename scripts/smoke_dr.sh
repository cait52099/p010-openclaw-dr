#!/bin/bash
# Smoke test for Deep Research MVP
# 4-case gate + 1 regression

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
RUNS_DIR="$SCRIPT_DIR/../runs"
DR_SCRIPT="$SCRIPT_DIR/run_deep_research.py"

echo "=== Deep Research MVP Smoke Tests (4-case gate + 1 regression) ==="
echo ""

# Cleanup function
cleanup_runs() {
    rm -rf "$RUNS_DIR"/test_no_topic_* "$RUNS_DIR"/test_unclear_* "$RUNS_DIR"/test_normal_* 2>/dev/null || true
}

# Clean up before tests
cleanup_runs

#######################################
# Case 2: no-topic non-interactive -> exit(2)
#######################################
echo "Case 2: no-topic non-interactive (expect exit 2)..."
set +e
python3 "$DR_SCRIPT" --non-interactive --runs-dir="$RUNS_DIR" 2>&1
EXIT_CODE=$?
set -e
if [ "$EXIT_CODE" -ne 2 ]; then
    echo "FAIL: Expected exit code 2, got $EXIT_CODE"
    exit 1
fi
echo "Case 2: PASSED (exit 2)"
echo ""

#######################################
# Case 1: no-topic interactive success
# (Real stdin: provide answer via echo)
#######################################
echo "Case 1: no-topic interactive success..."

RUN_ID="test_no_topic_$(date +%s)"
RUN_DIR="$RUNS_DIR/$RUN_ID"
mkdir -p "$RUN_DIR"

# Run with no topic, provide answer via stdin
echo "climate change impact on agriculture" | python3 "$DR_SCRIPT" --run-id="$RUN_ID" --runs-dir="$RUNS_DIR" 2>&1 | tail -3

# Verify outputs exist
if [ ! -f "$RUN_DIR/final/report.md" ]; then
    echo "FAIL: report.md not found"
    exit 1
fi

if [ ! -f "$RUN_DIR/final/verification.md" ]; then
    echo "FAIL: verification.md not found"
    exit 1
fi

# Check paragraph_without_citation_count = 0
COUNT=$(grep "paragraph_without_citation_count" "$RUN_DIR/final/verification.md" | grep -o '[0-9]*')
if [ "$COUNT" != "0" ]; then
    echo "FAIL: paragraph_without_citation_count = $COUNT (expected 0)"
    exit 1
fi

echo "Case 1: PASSED"
echo ""

#######################################
# Case 3: unclear-topic failure exit(1)
# (Short topic "ai" without answering clarification)
#######################################
echo "Case 3: unclear-topic failure exit(1)..."

RUN_ID="test_unclear_$(date +%s)"

# Run with short topic "ai" (will need clarification)
# In interactive mode without providing answers, should exit(1)
set +e
echo "" | python3 "$DR_SCRIPT" "ai" --run-id="$RUN_ID" --runs-dir="$RUNS_DIR" 2>&1
EXIT_CODE=$?
set -e

# Verify exit code is 1
if [ "$EXIT_CODE" -ne 1 ]; then
    echo "FAIL: Expected exit code 1, got $EXIT_CODE"
    exit 1
fi

# Check if clarify.json was created with failure_reason
if [ -f "$RUNS_DIR/$RUN_ID/clarify.json" ]; then
    FAILURE_REASON=$(python3 -c "import json; print(json.load(open('$RUNS_DIR/$RUN_ID/clarify.json')).get('failure_reason', ''))")
    if [ -n "$FAILURE_REASON" ]; then
        echo "Case 3: PASSED (clarify.json with failure_reason: $FAILURE_REASON)"
    else
        echo "FAIL: clarify.json missing failure_reason"
        exit 1
    fi
else
    echo "FAIL: clarify.json not created"
    exit 1
fi
echo ""

#######################################
# Case 4: normal-topic success
#######################################
echo "Case 4: normal-topic success..."
RUN_ID="test_normal_$(date +%s)"
python3 "$DR_SCRIPT" "climate change impact" --run-id="$RUN_ID" --runs-dir="$RUNS_DIR" 2>&1 | tail -3

# Verify outputs
if [ ! -f "$RUNS_DIR/$RUN_ID/final/report.md" ]; then
    echo "FAIL: report.md not found"
    exit 1
fi

if [ ! -f "$RUNS_DIR/$RUN_ID/final/verification.md" ]; then
    echo "FAIL: verification.md not found"
    exit 1
fi

# Check paragraph_without_citation_count = 0
COUNT=$(grep "paragraph_without_citation_count" "$RUNS_DIR/$RUN_ID/final/verification.md" | grep -o '[0-9]*')
if [ "$COUNT" != "0" ]; then
    echo "FAIL: paragraph_without_citation_count = $COUNT (expected 0)"
    exit 1
fi

# Verify workers = 5
WORKERS=$(python3 -c "import json; print(json.load(open('$RUNS_DIR/$RUN_ID/logs/plan.json'))['workers'])")
if [ "$WORKERS" != "5" ]; then
    echo "FAIL: workers = $WORKERS (expected 5)"
    exit 1
fi

# Verify citations format
if ! grep -q "(C0" "$RUNS_DIR/$RUN_ID/final/report.md"; then
    echo "FAIL: No citations found in report"
    exit 1
fi

# Verify citations.json exists
if [ ! -f "$RUNS_DIR/$RUN_ID/evidence/citations.json" ]; then
    echo "FAIL: citations.json not found"
    exit 1
fi

# Verify pipeline.jsonl exists
if [ ! -f "$RUNS_DIR/$RUN_ID/logs/pipeline.jsonl" ]; then
    echo "FAIL: pipeline.jsonl not found"
    exit 1
fi

echo "Case 4: PASSED"
echo ""

#######################################
# Regression: verify.json exists
#######################################
echo "Regression: verify.json exists..."

if [ ! -f "$RUNS_DIR/$RUN_ID/evidence/verify.json" ]; then
    echo "FAIL: evidence/verify.json not found"
    exit 1
fi

# Verify verify.json has correct structure
VERIFY_STATUS=$(python3 -c "import json; print(json.load(open('$RUNS_DIR/$RUN_ID/evidence/verify.json'))['status'])")
if [ "$VERIFY_STATUS" != "completed" ]; then
    echo "FAIL: verify.json status = $VERIFY_STATUS (expected completed)"
    exit 1
fi

# Verify verify.json has all required keys (Issue 4)
python3 -c "
import json
v = json.load(open('$RUNS_DIR/$RUN_ID/evidence/verify.json'))
required_keys = ['status', 'passed', 'paragraph_without_citation_count', 'paragraphs_jsonl_cite_ids_passed', 'paragraph_end_citation_passed']
missing = [k for k in required_keys if k not in v]
if missing:
    print(f'FAIL: verify.json missing keys: {missing}')
    exit(1)
# Also verify passed is True for this passing case
if not v.get('passed'):
    print('FAIL: verify.json passed should be True')
    exit(1)
print('verify.json keys validation: PASSED')
"

echo "Regression: PASSED"
echo ""

#######################################
# Case 5: failing verify-only test (cite_ids=[] -> exit 3)
#######################################
echo "Case 5: failing verify-only test (cite_ids=[] -> exit 3)..."

# First create proper run structure
RUN_ID_FAIL="test_verify_only"
python3 "$DR_SCRIPT" "quantum computing applications" --run-id="$RUN_ID_FAIL" --runs-dir="$RUNS_DIR" --budget=2 2>&1 | tail -1

# Modify paragraphs.jsonl to have empty cite_ids (should fail)
echo '{"text": "Test paragraph", "cite_ids": []}' > "$RUNS_DIR/$RUN_ID_FAIL/drafts/paragraphs.jsonl"

# Run verify-only - should exit(3) because cite_ids is empty
set +e
python3 "$DR_SCRIPT" --verify-only --run-id="$RUN_ID_FAIL" --runs-dir="$RUNS_DIR" 2>&1
EXIT_CODE=$?
set -e

if [ "$EXIT_CODE" -ne 3 ]; then
    echo "FAIL: Expected exit code 3 for failing verify, got $EXIT_CODE"
    exit 1
fi
echo "Case 5: PASSED (exit 3)"
echo ""

echo "=== All Smoke Tests PASSED (5-case gate + 1 regression) ==="
