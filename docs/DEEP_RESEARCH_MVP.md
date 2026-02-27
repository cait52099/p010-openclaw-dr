# Deep Research MVP v2

Autonomous research pipeline with verification and caching.

## Overview

Deep Research is a multi-stage research pipeline that:
1. Takes a research topic
2. Plans the research strategy
3. Harvests relevant sources
4. Fetches content (with caching)
5. Extracts key information
6. Verifies citations
7. Writes the final report
8. Audits the output

## Architecture

```
intake -> plan -> harvest -> fetch -> extract -> verify -> write -> audit -> cache
```

### Modules

| Module | Description |
|--------|-------------|
| `state_machine.py` | 8-stage pipeline orchestration |
| `clarify.py` | Clarification gate for vague topics |
| `worker.py` | Concurrent worker pool (default: 5 workers) |
| `citations.py` | Paragraph-level citation manager |
| `verify.py` | Citation verification |
| `cache.py` | Content caching and resume |

## Usage

### CLI (Unix)

```bash
# Basic usage
./scripts/dr "artificial intelligence trends 2024"

# With options
./scripts/dr "quantum computing applications" --depth deep --workers 10

# Resume a run
./scripts/dr --run-id <run_id> "new topic"
```

### CLI (Windows)

```powershell
# Basic usage
.\scripts\dr.ps1 "artificial intelligence trends 2024"

# With options
.\scripts\dr.ps1 -Topic "quantum computing" -Depth deep -Workers 10
```

### Python API

```python
from deep_research import StateMachine

sm = StateMachine(
    runs_dir="./runs",
    workers=5,
    depth="medium",
    budget=10,
    lang="en",
)

state = sm.run(
    topic="artificial intelligence trends 2024",
    run_id="optional_run_id",
)
```

## Clarification Gate

The system checks if a topic needs clarification:
- Topic < 20 characters triggers clarification
- Ambiguous terms (it, this, that, etc.) trigger clarification
- Short abbreviations (ai, ml, dl, etc.) trigger clarification

When clarification is needed, up to 3 questions are asked.

## Citations

- Format: `(Cxxx...)` where xxx is a 3-digit number
- Stored in: `evidence/citations.json`
- Each paragraph MUST end with a citation
- Verification ensures `paragraph_without_citation_count = 0`

## Output Structure

```
runs/<run_id>/
├── final/
│   ├── report.md           # Research report with citations
│   └── verification.md     # Verification results
├── evidence/
│   └── citations.json       # Citation data
├── logs/
│   ├── pipeline.jsonl       # Stage transitions
│   └── plan.json           # Research plan
└── clarify.json            # Clarification Q&A (if any)
```

## Configuration

| Option | Default | Description |
|--------|---------|-------------|
| `--workers` | 5 | Number of concurrent workers |
| `--depth` | medium | Research depth (brief/medium/deep) |
| `--budget` | 10 | Budget for sources |
| `--lang` | en | Output language |
| `--runs-dir` | ./runs | Runs directory |

## Caching

- Second run with same `run_id` skips fetch stage
- Cache stored in `runs/.cache/<run_id>.json`
- Resume capability for interrupted runs

## Verification

Every paragraph must end with a citation. The verifier checks:
- Total paragraphs
- Paragraphs without citations
- Citations found in text
- Pass/fail status

## Mock Implementation

The MVP uses mock implementations for:
- Harvest (generates sample URLs)
- Fetch (returns mock content)
- Extract (generates mock key points)

These can be replaced with real implementations by extending the `StateMachine` class and overriding the stage methods.
