# OpenClaw TUI DR Integration (v1)

Goal: Make `openclaw tui --message "/dr ..."` run local Deep-Research router and print DR fingerprint (BugTriageMode-R_ + report/verification paths).

## 1) Patch OpenClaw (one-time, repeatable)
bash scripts/patch_openclaw_tui_dr.sh

Optional:
ROUTER_CLI="/abs/path/to/openclaw_router_cli.py" bash scripts/patch_openclaw_tui_dr.sh

## 2) Smoke (real TUI path)
bash scripts/smoke_openclaw_tui_dr.sh

Expected:
- prints SMOKE_TUI_DR_OK
- RC=0

## 3) Use
DR_RUNS_DIR="$HOME/.openclaw/runs" openclaw tui --message "/dr analyze p007 bugs and innovation"
