# OpenClaw DR Service - Runtime Launchd Integration

This document describes how to install, enable, check, and disable the OpenClaw DR (Deep Research) service using macOS launchd.

## Overview

The DR service provides a background service for handling `/dr` commands via launchd. It invokes `openclaw_dr_service.py` which routes to `openclaw_router`.

## Architecture

### Commands Used

- **enable**: `bootstrap` → `enable` → `kickstart`
- **disable**: `bootout` → `disable`
- **check**: `launchctl print` (preferred) → `grep` fallback

### Why bootstrap/bootout?

The modern `bootstrap`/`bootout` commands (macOS 13+) are preferred over legacy `load`/`unload`:
- Better domain management
- Cleaner separation of service registration and activation
- More explicit error handling

## Installation

### Prerequisites

- macOS (launchd is macOS-specific)
- Python 3.x installed
- OpenClaw repository cloned

### Step 1: Enable Service (User Mode)

```bash
cd /path/to/clawd
./scripts/enable_dr_service.sh
```

This will:
1. Copy the plist to `~/Library/LaunchAgents/`
2. Expand path placeholders (`__CLAWD_DIR__`, `__HOME__`)
3. Try `gui/$UID` domain first, fall back to `user/$UID`
4. Bootstrap → Enable → Kickstart
5. Verify the service is loaded

### Step 1b: Enable Service (System Mode)

For system-wide daemon (requires sudo):

```bash
cd /path/to/clawd
sudo ./scripts/enable_dr_service.sh --system
```

This will:
1. Determine the real user from `SUDO_USER` environment variable
2. Derive the real home directory using `dscl` (or Python fallback)
3. Copy the plist to `/Library/LaunchDaemons/`
4. Expand path placeholders with the **real user's home** (not root's)
5. Set permissions to `644 root:wheel`
6. Bootstrap → Enable → Kickstart in system domain
7. Verify the service is loaded in system domain

### Step 2: Check Status

User mode:
```bash
./scripts/check_dr_service.sh
```

System mode:
```bash
./scripts/check_dr_service.sh --system
```

Expected output when running:
```
=== OpenClaw DR Service Status ===
Status: LOADED
Domain: system
PID: 12345
Plist: /Library/LaunchDaemons/ai.openclaw.dr-service.plist
```

Return codes:
- `0`: Service loaded
- `1`: Service not loaded
- `2`: Error (permission denied, command failed)

### Step 3: Disable Service

User mode:
```bash
./scripts/disable_dr_service.sh
```

System mode:
```bash
sudo ./scripts/disable_dr_service.sh --system
```

This will:
1. Bootout the service from appropriate domain(s)
2. Disable auto-start
3. Remove plist from appropriate location

Return codes:
- `0`: Success (service disabled or not present)
- `1`: Error

## macOS Version Differences

| Command | macOS 12- | macOS 13+ |
|---------|-----------|------------|
| bootstrap | N/A | Preferred |
| bootout | N/A | Preferred |
| load | Supported | Deprecated |
| unload | Supported | Deprecated |

The scripts automatically fall back to available commands based on your macOS version.

## Common Issues

### Permission Denied

If you get permission errors:
```bash
# Check current user
whoami

# Ensure plist is readable
ls -la deploy/openclaw_dr_service.plist
```

### Label Conflict

If another job uses the same label, you'll see an error. Edit `deploy/openclaw_dr_service.plist` and change the `Label` key.

### Service Not Starting

Check logs:
```bash
# View service output
tail -f ~/.openclaw/logs/dr-service.log

# Check launchd stderr
cat ~/.openclaw/logs/dr-service.err.log
```

## CI / Headless Environment

If running in CI or without a GUI:

1. **Verify plist syntax only**:
```bash
plutil -lint deploy/openclaw_dr_service.plist
```

2. **Test service manually**:
```bash
python3 openclaw_dr_service.py "/dr test topic"
```

## Files

- `deploy/openclaw_dr_service.plist` - launchd configuration
- `scripts/enable_dr_service.sh` - Enable script (bootstrap/enable/kickstart)
- `scripts/check_dr_service.sh` - Check status script
- `scripts/disable_dr_service.sh` - Disable script (bootout/disable)
- `openclaw_dr_service.py` - Service entry point
- `openclaw_router.py` - Message router
- `openclaw_dr_handler.py` - DR command handler
