"""State machine for Deep Research 8-stage pipeline."""

import json
import os
import uuid
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Callable, Optional

from .clarify import Clarifier
from .worker import WorkerPool
from .citations import CitationManager
from .verify import Verifier
from .cache import CacheManager


class Stage(Enum):
    """Pipeline stages."""
    INTAKE = "intake"
    PLAN = "plan"
    HARVEST = "harvest"
    FETCH = "fetch"
    EXTRACT = "extract"
    VERIFY = "verify"
    WRITE = "write"
    AUDIT = "audit"
    CACHE = "cache"


class RunState:
    """Represents a research run state."""

    def __init__(self, run_id: str, topic: str, runs_dir: Path):
        self.run_id = run_id
        self.topic = topic
        self.runs_dir = runs_dir
        self.run_dir = runs_dir / run_id
        self.final_dir = self.run_dir / "final"
        self.evidence_dir = self.run_dir / "evidence"
        self.logs_dir = self.run_dir / "logs"

        # State
        self.current_stage: Optional[Stage] = None
        self.workers = 5
        self.depth = "medium"
        self.budget = 10
        self.lang = "en"
        self.plan: dict = {}
        self.harvest_results: list = []
        self.fetch_results: list = []
        self.extract_results: list = []
        self.citations: list = []
        self.clarify_data: dict = {}

        # Create directories
        self.run_dir.mkdir(parents=True, exist_ok=True)
        self.final_dir.mkdir(parents=True, exist_ok=True)
        self.evidence_dir.mkdir(parents=True, exist_ok=True)
        self.logs_dir.mkdir(parents=True, exist_ok=True)

    def to_dict(self) -> dict:
        """Convert to dictionary for serialization."""
        return {
            "run_id": self.run_id,
            "topic": self.topic,
            "current_stage": self.current_stage.value if self.current_stage else None,
            "workers": self.workers,
            "depth": self.depth,
            "budget": self.budget,
            "lang": self.lang,
            "plan": self.plan,
            "clarify_data": self.clarify_data,
        }


class StateMachine:
    """
    8-stage research pipeline:
    intake -> plan -> harvest -> fetch -> extract -> verify -> write -> audit -> cache
    """

    def __init__(
        self,
        runs_dir: str = "./runs",
        workers: int = 5,
        depth: str = "medium",
        budget: int = 10,
        lang: str = "en",
    ):
        self.runs_dir = Path(runs_dir)
        self.runs_dir.mkdir(parents=True, exist_ok=True)

        self.default_workers = workers
        self.default_depth = depth
        self.default_budget = budget
        self.default_lang = lang

        # Components
        self.clarifier = Clarifier()
        self.worker_pool = WorkerPool(max_workers=workers)
        self.citation_manager = CitationManager()
        self.verifier = Verifier()
        self.cache_manager = CacheManager()

        # Stage handlers (pluggable)
        self.stage_handlers: dict[Stage, Callable] = {}

    def _generate_run_id(self, topic: str) -> str:
        """Generate a unique run ID."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_topic = "".join(c for c in topic[:20] if c.isalnum() or c in "_-")
        return f"{safe_topic}_{timestamp}"

    def _log_stage(self, state: RunState, stage: Stage, status: str, details: dict = None):
        """Log stage transition to pipeline.jsonl."""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "run_id": state.run_id,
            "stage": stage.value,
            "status": status,
            "details": details or {},
        }
        log_file = state.logs_dir / "pipeline.jsonl"
        with open(log_file, "a") as f:
            f.write(json.dumps(log_entry) + "\n")

    def _save_plan(self, state: RunState):
        """Save plan to logs/plan.json."""
        plan_file = state.logs_dir / "plan.json"
        with open(plan_file, "w") as f:
            json.dump({
                "workers": state.workers,
                "depth": state.depth,
                "budget": state.budget,
                "lang": state.lang,
                "plan": state.plan,
            }, f, indent=2)

    def _run_stage(self, state: RunState, stage: Stage) -> bool:
        """Execute a single stage."""
        state.current_stage = stage
        self._log_stage(state, stage, "started")

        try:
            if stage == Stage.INTAKE:
                result = self._stage_intake(state)
            elif stage == Stage.PLAN:
                result = self._stage_plan(state)
            elif stage == Stage.HARVEST:
                result = self._stage_harvest(state)
            elif stage == Stage.FETCH:
                result = self._stage_fetch(state)
            elif stage == Stage.EXTRACT:
                result = self._stage_extract(state)
            elif stage == Stage.VERIFY:
                result = self._stage_verify(state)
            elif stage == Stage.WRITE:
                result = self._stage_write(state)
            elif stage == Stage.AUDIT:
                result = self._stage_audit(state)
            elif stage == Stage.CACHE:
                result = self._stage_cache(state)
            else:
                result = True

            self._log_stage(state, stage, "completed", {"success": result})
            return result

        except Exception as e:
            self._log_stage(state, stage, "failed", {"error": str(e)})
            raise

    # Stage implementations (mock for MVP, pluggable interfaces)

    def _stage_intake(self, state: RunState) -> bool:
        """Intake stage: validate and normalize input."""
        # Save clarify.json if exists
        if state.clarify_data:
            clarify_file = state.run_dir / "clarify.json"
            with open(clarify_file, "w") as f:
                json.dump(state.clarify_data, f, indent=2)
        return True

    def _stage_plan(self, state: RunState) -> bool:
        """Plan stage: create research strategy."""
        # Mock plan generation
        state.plan = {
            "queries": [state.topic],
            "sources": ["web", "academic"],
            "estimated_sources": state.budget * 5,
            "depth": state.depth,
        }
        self._save_plan(state)
        return True

    def _stage_harvest(self, state: RunState) -> bool:
        """Harvest stage: discover relevant URLs/sources."""
        # Mock harvest - in production, would call search API
        # Generate exactly budget number of sources
        state.harvest_results = [
            {"url": f"https://example.com/{i}", "title": f"Source {i}", "relevance": 0.9 - i*0.1}
            for i in range(state.budget)
        ]
        return True

    def _stage_fetch(self, state: RunState) -> bool:
        """Fetch stage: retrieve content from sources."""
        # Check cache first
        cached = self.cache_manager.load_cached(state.run_id)
        if cached:
            state.fetch_results = cached
            return True

        # Mock fetch - in production, would fetch actual content
        def fetch_one(item: dict) -> dict:
            return {
                "url": item["url"],
                "title": item["title"],
                "content": f"Mock content for {item['title']}",
                "fetched_at": datetime.now().isoformat(),
            }

        results = self.worker_pool.run(fetch_one, state.harvest_results)
        state.fetch_results = results

        # Cache results
        self.cache_manager.save_cached(state.run_id, results)
        return True

    def _stage_extract(self, state: RunState) -> bool:
        """Extract stage: extract key information."""
        # Mock extraction
        state.extract_results = [
            {
                "url": r["url"],
                "title": r["title"],
                "key_points": [f"Key point from {r['title']}"],
                "quotes": [f"Quote from {r['title']}"],
            }
            for r in state.fetch_results
        ]

        # Build citations
        self.citation_manager.reset()
        for i, result in enumerate(state.extract_results):
            cid = f"C{i+1:03d}"
            self.citation_manager.add_citation(
                cid=cid,
                url=result["url"],
                title=result["title"],
                locator=result.get("url", ""),
            )

        return True

    def _stage_verify(self, state: RunState) -> bool:
        """Verify stage: verify extracted content before writing."""
        # Generate paragraphs from extract results for verification
        paragraphs = []
        for i, result in enumerate(state.extract_results):
            cid = f"C{i+1:03d}"
            key_points = result.get("key_points", [])
            if key_points:
                paragraphs.append({
                    "text": key_points[0],
                    "cite_ids": [cid],
                })

        # Save paragraphs to drafts/paragraphs.jsonl
        drafts_dir = state.run_dir / "drafts"
        drafts_dir.mkdir(parents=True, exist_ok=True)
        paragraphs_file = drafts_dir / "paragraphs.jsonl"

        with open(paragraphs_file, "w") as f:
            for para in paragraphs:
                f.write(json.dumps(para) + "\n")

        # Write evidence/verify.json
        verify_file = state.evidence_dir / "verify.json"
        verify_data = {
            "stage": "verify",
            "status": "completed",
            "paragraphs_count": len(paragraphs),
            "verified": True,
        }
        with open(verify_file, "w") as f:
            json.dump(verify_data, f, indent=2)

        # Store for later use
        state.paragraphs = paragraphs

        return True

    def _stage_write(self, state: RunState) -> bool:
        """Write stage: generate final report using paragraphs from verify stage."""
        # Use paragraphs generated in verify stage
        paragraphs = getattr(state, "paragraphs", [])

        # Generate report with citations from paragraphs
        report_lines = []
        for para in paragraphs:
            cite_str = ", ".join(para["cite_ids"]) if para["cite_ids"] else ""
            if cite_str:
                report_lines.append(f"{para['text']} ({cite_str})")
            else:
                report_lines.append(para["text"])

        report = "# Research Report\n\n" + "\n".join(report_lines)
        report_file = state.final_dir / "report.md"
        with open(report_file, "w") as f:
            f.write(report)

        # Save citations
        citations_file = state.evidence_dir / "citations.json"
        self.citation_manager.save(citations_file)
        state.citations = self.citation_manager.get_all()

        return True

    def _stage_audit(self, state: RunState) -> bool:
        """Audit stage: final verification."""
        # Run verification
        report_file = state.final_dir / "report.md"
        with open(report_file) as f:
            report_content = f.read()

        verification_result = self.verifier.verify_report(report_file)

        # Check paragraphs.jsonl cite_ids
        paragraphs_file = state.run_dir / "drafts" / "paragraphs.jsonl"
        paragraphs_jsonl_passed, paragraphs_errors = self.verifier.verify_paragraphs_jsonl(paragraphs_file)

        # paragraph_end_citation_passed = not paragraphs_without_citation
        paragraph_end_citation_passed = verification_result.paragraph_without_citation_count == 0

        # Issue 1 fix: passed must be AND of all checks
        report_passed = verification_result.passed
        paragraphs_jsonl_cite_ids_passed = paragraphs_jsonl_passed
        passed = report_passed and paragraphs_jsonl_cite_ids_passed and (verification_result.paragraph_without_citation_count == 0)

        # Save verification
        verification_file = state.final_dir / "verification.md"
        with open(verification_file, "w") as f:
            f.write(f"# Verification Report\n\n")
            f.write(f"- paragraph_without_citation_count: {verification_result.paragraph_without_citation_count}\n")
            f.write(f"- total_paragraphs: {verification_result.total_paragraphs}\n")
            f.write(f"- citations_found: {verification_result.citations_found}\n")
            f.write(f"- verified_claims_count: {verification_result.verified_claims_count}\n")
            f.write(f"- single_source_claims_count: {verification_result.single_source_claims_count}\n")
            f.write(f"- conflicts_count: {verification_result.conflicts_count}\n")
            f.write(f"- passed: {passed}\n")

        # Write verify.json with all required fields (Issue 5)
        verify_file = state.evidence_dir / "verify.json"
        verify_data = {
            "stage": "audit",
            "status": "completed",
            "verified_claims_count": verification_result.verified_claims_count,
            "single_source_claims_count": verification_result.single_source_claims_count,
            "conflicts_count": verification_result.conflicts_count,
            "total_paragraphs": verification_result.total_paragraphs,
            "paragraph_without_citation_count": verification_result.paragraph_without_citation_count,
            "paragraph_end_citation_passed": paragraph_end_citation_passed,
            "paragraphs_jsonl_cite_ids_passed": paragraphs_jsonl_passed,
            "citations_found": verification_result.citations_found,
            "passed": passed,  # Issue 1: combined passed from all checks
        }
        with open(verify_file, "w") as f:
            json.dump(verify_data, f, indent=2)

        return passed

    def _stage_cache(self, state: RunState) -> bool:
        """Cache stage: finalize caching."""
        # Already done in fetch stage
        return True

    def run(
        self,
        topic: str,
        run_id: Optional[str] = None,
        workers: Optional[int] = None,
        depth: Optional[str] = None,
        budget: Optional[int] = None,
        lang: Optional[str] = None,
    ) -> RunState:
        """
        Run the research pipeline.

        Returns the final RunState.
        """
        # Generate or use provided run_id
        if not run_id:
            run_id = self._generate_run_id(topic)

        # Check for existing run (resume capability)
        existing_run_dir = self.runs_dir / run_id
        if existing_run_dir.exists():
            # Try to load existing state
            state = self._load_run_state(run_id, topic)
        else:
            state = RunState(run_id, topic, self.runs_dir)

        # Apply overrides
        state.workers = workers or self.default_workers
        state.depth = depth or self.default_depth
        state.budget = budget or self.default_budget
        state.lang = lang or self.default_lang

        # Update worker pool size
        self.worker_pool = WorkerPool(max_workers=state.workers)

        # Run clarification if needed
        if not topic or len(topic) < 20:
            clarification = self.clarifier.clarify(topic)
            if clarification["needs_clarification"]:
                state.clarify_data = clarification

        # Execute pipeline stages: EXTRACT -> VERIFY -> WRITE -> AUDIT
        stages = [
            Stage.INTAKE,
            Stage.PLAN,
            Stage.HARVEST,
            Stage.FETCH,
            Stage.EXTRACT,
            Stage.VERIFY,
            Stage.WRITE,
            Stage.AUDIT,
            Stage.CACHE,
        ]

        for stage in stages:
            if not self._run_stage(state, stage):
                raise RuntimeError(f"Stage {stage.value} failed")

        return state

    def _load_run_state(self, run_id: str, topic: str) -> RunState:
        """Load existing run state for resume."""
        state = RunState(run_id, topic, self.runs_dir)

        # Load plan
        plan_file = state.logs_dir / "plan.json"
        if plan_file.exists():
            with open(plan_file) as f:
                plan_data = json.load(f)
                state.workers = plan_data.get("workers", 5)
                state.depth = plan_data.get("depth", "medium")
                state.budget = plan_data.get("budget", 10)
                state.lang = plan_data.get("lang", "en")

        # Load clarify
        clarify_file = state.run_dir / "clarify.json"
        if clarify_file.exists():
            with open(clarify_file) as f:
                state.clarify_data = json.load(f)

        return state
