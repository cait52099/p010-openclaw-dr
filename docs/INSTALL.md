# OpenClaw DR Installation Guide

## Quick Install (One-Line)

```bash
# From this repo
./install.sh --local

# Or with custom prefix
./install.sh --local --prefix ~/bin
```

## Installation Options

### Local Install (from current directory)

```bash
./install.sh --local
# or
./scripts/install.sh --local
```

This installs:
- Wrapper script to `~/bin/dr`
- Default: auto-outputs full report after completion

### Clone Install (from GitHub)

```bash
./install.sh --clone
```

This clones the repository to `~/.local/share/openclaw-dr` then installs.

### Options

| Option | Description |
|--------|-------------|
| `--local` | Install from current directory (default) |
| `--clone` | Clone from GitHub first |
| `--prefix DIR` | Install directory (default: ~/bin) |
| `--no-full-output` | Don't auto-cat report after completion |

## Post-Installation

### 1. Add to PATH (if needed)

```bash
# Add to PATH if ~/bin is not in it
echo 'export PATH="$HOME/bin:$PATH"' >> ~/.zshrc
source ~/.zshrc
```

### 2. Verify Installation

```bash
dr --help
```

### 3. Run Post-Install Check

```bash
./scripts/post_install_check.sh
```

## Usage

### Basic Usage

```bash
dr "artificial intelligence trends 2024"
```

### With Options

```bash
dr "quantum computing" --depth deep --workers 10
dr --run-id <id>  # Resume a previous run
```

### Exit Codes

| Code | Meaning |
|------|---------|
| 0 | Success - report generated |
| 1 | Error - invalid input or execution failed |
| 2 | Clarification needed - provide a clear topic |
| 3 | Verification failed - check run directory |

## Optional: Enable /dr Shortcut

> **Note**: `/dr` shortcut is **zsh-only**. For bash, use `drs` instead.

### For zsh users

```bash
./scripts/enable_dr_slash.sh --shell zsh
source ~/.zshrc
```

Then use:

```bash
/dr "your topic"
```

### For bash users

```bash
./scripts/enable_dr_slash.sh --shell bash
source ~/.bashrc
```

Then use:

```bash
drs "your topic"
# or just
dr "your topic"
```

To disable:

```bash
./scripts/disable_dr_slash.sh
```

## Uninstall

```bash
./scripts/uninstall.sh           # Remove wrapper only
./scripts/uninstall.sh --purge   # Remove everything
```

## Files

- `scripts/dr` - Main CLI entry point
- `scripts/run_deep_research.py` - Core research engine
- `scripts/install.sh` - Installation script
- `scripts/uninstall.sh` - Uninstallation script
- `scripts/enable_dr_slash.sh` - Enable /dr shortcut
- `scripts/disable_dr_slash.sh` - Disable /dr shortcut
- `scripts/smoke_dr.sh` - Smoke tests
