#!/usr/bin/env python3
"""Deep Research CLI runner - only clarification entry point."""

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path

# Add parent to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from deep_research import StateMachine, Clarifier


def parse_args():
    parser = argparse.ArgumentParser(description="Deep Research CLI")
    parser.add_argument("topic", nargs="?", help="Research topic")
    parser.add_argument("--run-id", help="Run ID for resume")
    parser.add_argument("--depth", default="medium", choices=["brief", "medium", "deep"])
    parser.add_argument("--budget", type=int, default=10, help="Budget for sources")
    parser.add_argument("--lang", default="en", help="Language")
    parser.add_argument("--workers", type=int, default=5, help="Number of workers")
    parser.add_argument("--runs-dir", default="./runs", help="Runs directory")
    parser.add_argument(
        "--non-interactive",
        action="store_true",
        help="Exit with code 2 if clarification needed",
    )
    parser.add_argument(
        "--verify-only",
        action="store_true",
        help="Only run verification on existing run, exit 0 if passed, 3 if not",
    )
    return parser.parse_args()


def generate_run_id(topic: str = "") -> str:
    """Generate a unique run ID."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    if topic:
        safe_topic = "".join(c for c in topic[:20] if c.isalnum() or c in "_-")
        return f"{safe_topic}_{timestamp}"
    return f"no_topic_{timestamp}"


def handle_no_topic(args) -> None:
    """Handle case when no topic is provided."""
    # Generate run_id
    run_id = args.run_id if args.run_id else generate_run_id("")
    runs_dir = Path(args.runs_dir)
    run_dir = runs_dir / run_id

    # Create directory
    run_dir.mkdir(parents=True, exist_ok=True)

    # Generate questions for empty topic
    clarifier = Clarifier()
    questions = clarifier.generate_questions("")

    # Write clarify.json with status=pending
    clarify_data = {
        "status": "pending",
        "questions": questions,
        "answers": [],
        "failure_reason": None,
    }

    clarify_file = run_dir / "clarify.json"
    with open(clarify_file, "w") as f:
        json.dump(clarify_data, f, indent=2)

    if args.non_interactive:
        # Non-interactive: print questions and exit(2)
        print("Deep Research - Clarification Required")
        print("=" * 40)
        print("No topic provided.")
        print()
        print("Please clarify by answering:")
        for i, q in enumerate(questions, 1):
            print(f"  {i}. {q}")
        print()
        sys.exit(2)

    # Interactive: ask questions
    print("Deep Research - Clarification Mode")
    print("=" * 40)
    print("No topic provided. Please answer the following questions:")
    print()

    answers = []
    for q in questions:
        try:
            answer = input(f"{q}\n> ")
            if answer.strip():
                answers.append(answer.strip())
        except EOFError:
            break

    # Update clarify.json with answers
    if answers:
        clarify_data["status"] = "clarified"
        clarify_data["answers"] = answers
        with open(clarify_file, "w") as f:
            json.dump(clarify_data, f, indent=2)

        # Update topic
        args.topic = " ".join(answers)
        print(f"\nClarified topic: {args.topic}")
    else:
        # No answers provided - clarification failure
        clarify_data["status"] = "failed"
        clarify_data["failure_reason"] = "No clarification provided"
        with open(clarify_file, "w") as f:
            json.dump(clarify_data, f, indent=2)
        print("\nNo clarification provided. Exiting.")
        sys.exit(1)


def main():
    args = parse_args()

    # Handle --verify-only mode FIRST (before any topic or clarification handling)
    if hasattr(args, 'verify_only') and args.verify_only:
        if not args.run_id:
            print("Error: --verify-only requires --run-id")
            sys.exit(1)

        runs_dir = Path(args.runs_dir)
        run_dir = runs_dir / args.run_id
        report_file = run_dir / "final" / "report.md"
        paragraphs_file = run_dir / "drafts" / "paragraphs.jsonl"

        if not report_file.exists():
            print(f"Error: report.md not found at {report_file}")
            sys.exit(1)

        # Run verification
        sys.path.insert(0, str(Path(__file__).parent.parent))
        from deep_research.verify import Verifier

        verifier = Verifier()

        # Verify report.md citations
        report_result = verifier.verify_report(report_file)
        report_passed = report_result.passed
        paragraph_without_citation_count = report_result.paragraph_without_citation_count
        paragraph_end_citation_passed = report_result.passed

        # Verify paragraphs.jsonl
        paragraphs_jsonl_passed = True
        if paragraphs_file.exists():
            paragraphs_jsonl_passed, _ = verifier.verify_paragraphs_jsonl(paragraphs_file)
        else:
            paragraphs_jsonl_passed = False

        # Combined passed
        passed = report_passed and paragraphs_jsonl_passed and (paragraph_without_citation_count == 0)

        print(f"Verification result for {args.run_id}: {'PASSED' if passed else 'FAILED'}")
        print(f"  - paragraph_without_citation_count: {paragraph_without_citation_count}")
        print(f"  - paragraphs_jsonl_cite_ids_passed: {paragraphs_jsonl_passed}")
        print(f"  - paragraph_end_citation_passed: {paragraph_end_citation_passed}")

        if passed:
            sys.exit(0)
        else:
            sys.exit(3)

    # No topic: handle via clarification flow (skip if verify-only mode)
    if not args.topic and not args.verify_only:
        handle_no_topic(args)
        # After handle_no_topic, if we get here, topic was clarified
        # continue with the clarified topic

    # Initialize clarifier
    clarifier = Clarifier()

    # Generate run_id for clarification file path
    if args.run_id:
        run_id = args.run_id
    else:
        # Generate same ID as state machine would
        safe_topic = "".join(c for c in args.topic[:20] if c.isalnum() or c in "_-")
        run_id = f"{safe_topic}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

    runs_dir = Path(args.runs_dir)
    run_dir = runs_dir / run_id

    # Check if clarification needed
    if clarifier.needs_clarification(args.topic):
        questions = clarifier.generate_questions(args.topic)

        if args.non_interactive:
            # Non-interactive mode: print questions and exit with code 2
            print("Deep Research - Clarification Required")
            print("=" * 40)
            print(f"Topic: {args.topic}")
            print()
            print("Please clarify your topic by answering:")
            for i, q in enumerate(questions, 1):
                print(f"  {i}. {q}")
            print()
            sys.exit(2)

        # Interactive mode: ask for clarification
        print(f"Topic: {args.topic}")
        print("This topic may need clarification.")
        print("\nQuestions to clarify:")
        for i, q in enumerate(questions, 1):
            print(f"  {i}. {q}")

        answers = []
        for q in questions:
            try:
                answer = input(f"\n{q}\n> ")
                if answer.strip():
                    answers.append(answer.strip())
            except EOFError:
                break

        # Save clarification to runs/<run_id>/clarify.json
        clarify_data = {
            "status": "clarified" if answers else "failed",
            "original_topic": args.topic,
            "questions": questions,
            "answers": answers,
            "failure_reason": None if answers else "No clarification provided",
        }

        run_dir.mkdir(parents=True, exist_ok=True)
        clarify_file = run_dir / "clarify.json"
        with open(clarify_file, "w") as f:
            json.dump(clarify_data, f, indent=2)

        if answers:
            args.topic = " ".join(answers)
            print(f"\nClarified topic: {args.topic}")
        else:
            # No answers provided, exit
            print("\nNo clarification provided. Exiting.")
            sys.exit(1)

    # Initialize state machine
    sm = StateMachine(
        runs_dir=args.runs_dir,
        workers=args.workers,
        depth=args.depth,
        budget=args.budget,
        lang=args.lang,
    )

    # Run research
    print(f"\nStarting research: {args.topic}")
    print(f"Workers: {args.workers}, Depth: {args.depth}, Budget: {args.budget}")

    try:
        state = sm.run(
            topic=args.topic,
            run_id=args.run_id,
            workers=args.workers,
            depth=args.depth,
            budget=args.budget,
            lang=args.lang,
        )

        print(f"\nResearch complete!")
        print(f"Run ID: {state.run_id}")
        print(f"Report: {state.final_dir / 'report.md'}")
        print(f"Verification: {state.final_dir / 'verification.md'}")

        # Check verification result - exit(3) if failed
        verify_file = state.evidence_dir / "verify.json"
        if verify_file.exists():
            with open(verify_file) as f:
                verify_data = json.load(f)
            if not verify_data.get("passed", False):
                print(f"\nVerification FAILED. Exiting with code 3.")
                sys.exit(3)

    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
