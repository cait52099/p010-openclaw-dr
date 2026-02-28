#!/usr/bin/env python3
"""
Claude Code DR Dispatcher - Hard routing for /dr and /deapr commands.

This dispatcher forces /dr or /deapr to execute as terminal dr commands
instead of being interpreted as repository search/spell correction.

Usage:
    python3 cc_dr_dispatch.py --text "/deapr hvdc market"
    echo "/deapr hvdc market" | python3 cc_dr_dispatch.py --stdin

Exit codes:
    0-3: Pass-through from dr command
    2: Topic unclear, clarification questions printed
    10: NOT_HANDLED (input doesn't start with /dr or /deapr)
"""

import sys
import os
import subprocess
import argparse
from pathlib import Path

# Constants
DR_PREFIXES = ["/dr", "/deapr"]
MAX_CLARIFICATION_QUESTIONS = 3


def find_dr_command():
    """Find dr command in PATH or fallback to repo scripts/dr."""
    # Try PATH first
    result = subprocess.run(
        ["bash", "-c", "command -v dr"],
        capture_output=True,
        text=True
    )
    if result.returncode == 0 and result.stdout.strip():
        return result.stdout.strip()

    # Try ~/.local/bin/dr
    local_bin = Path.home() / ".local/bin/dr"
    if local_bin.exists():
        return str(local_bin)

    # Fallback to repo scripts/dr
    script_dir = Path(__file__).parent.resolve()
    repo_dir = script_dir.parent
    repo_dr = repo_dir / "scripts/dr"
    if repo_dr.exists():
        return str(repo_dr)

    return None


def parse_topic(text):
    """Parse topic from input text starting with /dr or /deapr."""
    text = text.strip()
    for prefix in DR_PREFIXES:
        if text.startswith(prefix):
            topic = text[len(prefix):].strip()
            if not topic:
                print('Topic may need clarification.')
                print('\nClarifying questions:')
                print('  1. What specific aspect of this topic are you most interested in?')
                print('  2. What depth of research do you need? (brief overview / comprehensive analysis)')
                print('  3. Any specific timeframe or region to focus on?')
                import sys
                sys.exit(2)  # bare slash clarify
            return prefix.strip("/ "), topic
    return None, text


def ask_clarification(topic, max_questions=MAX_CLARIFICATION_QUESTIONS):
    """Print clarification questions and return True if topic needs clarification."""
    if not topic or len(topic.split()) < 2:
        print("Topic may need clarification.", file=sys.stderr)
        print("\nClarifying questions:", file=sys.stderr)

        questions = [
            f"1. What specific aspect of '{topic or 'this topic'}' are you most interested in?",
            "2. What depth of research do you need? (brief overview / comprehensive analysis)",
            "3. Any specific timeframe or region to focus on?"
        ]

        for i, q in enumerate(questions[:max_questions], 1):
            print(f"  {q}", file=sys.stderr)

        return True
    return False


def execute_dr(topic, dr_path):
    """Execute dr command with the given topic."""
    # Build environment with PATH including ~/.local/bin
    env = os.environ.copy()
    current_path = env.get("PATH", "")
    local_bin = str(Path.home() / ".local/bin")
    if local_bin not in current_path:
        env["PATH"] = f"{local_bin}:{current_path}"

    # Execute dr command
    result = subprocess.run(
        [dr_path, topic],
        capture_output=False,
        env=env,
        text=True
    )

    return result.returncode


def main():
    parser = argparse.ArgumentParser(
        description="Claude Code DR Dispatcher - Hard routing for /dr commands"
    )
    parser.add_argument(
        "--text",
        help="Input text to process"
    )
    parser.add_argument(
        "--stdin",
        action="store_true",
        help="Read input from stdin"
    )
    parser.add_argument(
        "--runs-dir",
        help="Override runs directory (for testing/isolation)"
    )

    args = parser.parse_args()

    # Get input text
    if args.stdin:
        text = sys.stdin.read()
    elif args.text:
        text = args.text
    else:
        print("NOT_HANDLED", file=sys.stderr)
        print("Error: Either --text or --stdin required", file=sys.stderr)
        sys.exit(10)

    # Parse topic
    prefix, topic = parse_topic(text)

    if prefix is None:
        print("NOT_HANDLED", file=sys.stderr)
        print(f"Input doesn't start with /dr or /deapr", file=sys.stderr)
        sys.exit(10)

    # Find dr command
    dr_path = find_dr_command()
    if dr_path is None:
        print("Error: dr command not found", file=sys.stderr)
        print("Please install OpenClaw DR first:", file=sys.stderr)
        print("  curl -sL https://raw.githubusercontent.com/p010-ai/openclaw-dr/main/install.sh | bash", file=sys.stderr)
        sys.exit(1)

    # Set DR_RUNS_DIR if provided
    if args.runs_dir:
        os.environ["DR_RUNS_DIR"] = args.runs_dir

    # Check if clarification needed
    if ask_clarification(topic):
        sys.exit(2)

    # Execute dr command
    rc = execute_dr(topic, dr_path)
    sys.exit(rc)


if __name__ == "__main__":
    main()
