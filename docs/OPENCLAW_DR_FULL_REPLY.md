# OpenClaw DR Full Reply

## Overview

This document describes the `/dr` command implementation in OpenClaw for Deep Research with full reply functionality.

## Command Syntax

```
/dr <topic>
```

Examples:
- `/dr artificial intelligence trends 2026`
- `/dr quantum computing applications`
- `/dr climate change mitigation strategies`

## Exit Code Handling

| Code | Meaning | Response |
|------|---------|----------|
| 0 | Success | Send report.md in chunks (3500 chars) |
| 1 | Error | Show error message with fallback |
| 2 | Clarification needed | Show questions, save state, wait for answer |
| 3 | Verification failed | Show verification.md + suggestions |

## Exit 0: Success - Report Full Reply

When research completes successfully (exit code 0):

1. Read `runs/<run_id>/final/report.md`
2. Split into chunks of 3500 characters
3. Send each chunk as a separate message
4. At the end, include:
   ```
   Run ID: <run_id>
   Report: <REPO_ROOT>/runs/<run_id>/final/report.md
   ```

## Exit 2: Clarification Needed

When topic is unclear (exit code 2):

1. Parse questions from stdout
2. Display questions to user
3. Save state to `.openclaw/dr_state.json`:
   ```json
   {
     "run_id": "...",
     "status": "clarification",
     "questions": ["Question 1?", "Question 2?"]
   }
   ```
4. Wait for user's answer
5. On answer, continue the research with clarified topic

## Exit 3: Verification Failed

When verification fails (exit code 3):

1. Read `runs/<run_id>/final/verification.md`
2. Read `runs/<run_id>/evidence/verify.json`
3. Send full verification content
4. Include retry suggestions:
   ```
   To retry: /dr <original_topic> --budget <higher>
   Full verification: <REPO_ROOT>/runs/<run_id>/evidence/verify.json
   ```

## Fallback: Send Failed

If sending fails (e.g., file too large):

1. Generate a summary of the content
2. Send the summary + file path:
   ```
   [Summary of content]

   Full report: <REPO_ROOT>/runs/<run_id>/final/report.md
   ```

## State Management

State is persisted to: `<REPO_ROOT>/.openclaw/dr_state.json`

## Run Directory Structure

```
runs/<run_id>/
├── clarify.json          # Clarification questions/answers
├── drafts/
│   └── paragraphs.jsonl # Draft paragraphs with cite_ids
├── final/
│   ├── report.md        # Final research report
│   └── verification.md  # Verification results
├── evidence/
│   ├── verify.json      # Detailed verification data
│   └── citations.json   # Source citations
└── logs/
    ├── plan.json        # Research plan
    └── pipeline.jsonl   # Pipeline execution log
```

## Smoke Tests

Test the three paths:

1. **Exit 2 path**: `/dr` (no topic) → clarification → answer → success
2. **Exit 0 path**: `/dr "AI trends"` → success → report chunks
3. **Exit 3 path**: Corrupt paragraphs.jsonl → verify fails → exit 3 → verification shown

See `scripts/smoke_openclaw_router_dr.py` for OpenClaw router-level smoke tests (6 tests including router entry, clarification flow, send retry, degraded mode with sanitized paths, and continuation).
