#!/usr/bin/env bash
set -euo pipefail

OPENCLAW_ROOT="/opt/homebrew/lib/node_modules/openclaw"
DIST="$OPENCLAW_ROOT/dist"
ROUTER_CLI="${ROUTER_CLI:-/Users/caihongwei/clawd/scripts/openclaw_router_cli.py}"
MARK="// OPENCLAW_TUI_DR_SHORTCIRCUIT_V1"

if [ ! -d "$DIST" ]; then
  echo "ERROR: openclaw dist not found: $DIST"
  exit 2
fi

if [ ! -f "$ROUTER_CLI" ]; then
  echo "ERROR: router_cli not found: $ROUTER_CLI"
  echo "Hint: set ROUTER_CLI=/path/to/openclaw_router_cli.py"
  exit 2
fi

files=( "$DIST"/tui-cli-*.js )
if [ "${#files[@]}" -eq 0 ]; then
  echo "ERROR: no tui-cli bundle found under $DIST"
  exit 2
fi

ts="$(date +%Y%m%d_%H%M%S)"

for f in "${files[@]}"; do
  echo "Patching: $f"
  cp "$f" "$f.bak_${ts}"

  python3 - <<PY
from pathlib import Path
import re

p = Path("$f")
txt = p.read_text(encoding="utf-8")

if "OPENCLAW_TUI_DR_SHORTCIRCUIT_V1" in txt and "$MARK" not in txt:
    txt = re.sub(r'(^|\\n)\\s*OPENCLAW_TUI_DR_SHORTCIRCUIT_V1(\\s*\\n)', r'\\1$MARK\\2', txt)
    p.write_text(txt, encoding="utf-8")

if "$MARK" in txt:
    print("already patched marker present")
    raise SystemExit(0)

m = re.search(r'\\.action\\(async\\s*\\(opts\\)\\s*=>\\s*\\{', txt)
if not m:
    raise SystemExit("cannot find commander action(async (opts)=>{)")

inject = f'''
$MARK
try {{
  const msg = (opts && typeof opts.message === "string") ? opts.message.trim() : "";
  if (msg.startsWith("/dr") || msg.startsWith("/deapr")) {{
    const os = await import("node:os");
    const fs = await import("node:fs");
    const path = await import("node:path");
    const cp = await import("node:child_process");
    const runsDir = process.env.DR_RUNS_DIR || fs.mkdtempSync(path.join(os.tmpdir(), "openclaw_dr_"));
    const r = cp.spawnSync("python3", ["$ROUTER_CLI", "--runs-dir", runsDir, "--text", msg], {{ encoding: "utf-8" }});
    if (r.stdout) process.stdout.write(r.stdout);
    if (r.stderr) process.stderr.write(r.stderr);
    process.exit(r.status ?? 1);
  }}
}} catch (e) {{
  try {{ process.stderr.write(String(e) + "\\n"); }} catch {{}}
}}
'''
txt2 = txt[:m.end()] + inject + txt[m.end():]
p.write_text(txt2, encoding="utf-8")
print("patched ok")
PY

  grep -q "OPENCLAW_TUI_DR_SHORTCIRCUIT_V1" "$f" || {
    echo "ERROR: marker not found after patch: $f"
    exit 2
  }
done

echo "PATCH_OK"
