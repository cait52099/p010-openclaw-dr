"""Verification module for Deep Research."""

import re
from dataclasses import dataclass
from pathlib import Path
from typing import Optional


@dataclass
class VerificationResult:
    """Result of verification."""
    passed: bool
    total_paragraphs: int
    paragraphs_without_citation: list[int]
    paragraph_without_citation_count: int
    citations_found: int
    verified_claims_count: int
    single_source_claims_count: int
    conflicts_count: int
    issues: list[str]


class Verifier:
    """
    Verification module.

    Key constraint: paragraph_without_citation_count must = 0
    """

    # Citation pattern: (C001), (C002), etc. - must be at END of paragraph (strict \Z)
    # Pattern: matches text ending with (Cddd) or (Cddd, Cddd, ...) - must be at end of paragraph
    CITATION_PATTERN = re.compile(r".*\(C\d{3}(,\s*C\d{3})*\)\s*\Z")

    def __init__(self):
        self.strict = True

    def verify_report(self, report_path: Path) -> VerificationResult:
        """
        Verify a report has proper citations.

        Each paragraph MUST end with a citation (Cxxx...).
        """
        with open(report_path) as f:
            content = f.read()

        return self.verify_text(content)

    def verify_text(self, text: str) -> VerificationResult:
        """
        Verify text has proper paragraph-level citations.

        Each paragraph should end with a citation.
        """
        # Split into paragraphs
        paragraphs = self._split_paragraphs(text)

        issues = []
        paragraphs_without_citation = []
        citations_found = 0

        for i, para in enumerate(paragraphs):
            if not para.strip():
                continue

            # Skip markdown headers (lines starting with # or ##)
            if para.lstrip().startswith("#"):
                continue

            # Check if paragraph ends with citation - use match with \Z for strict end matching
            has_citation = bool(self.CITATION_PATTERN.match(para.rstrip()))

            if has_citation:
                citations_found += 1
            else:
                paragraphs_without_citation.append(i)
                issues.append(f"Paragraph {i+1} missing citation")

        paragraph_without_citation_count = len(paragraphs_without_citation)
        total_paragraphs = len([p for p in paragraphs if p.strip()])

        passed = paragraph_without_citation_count == 0

        # For MVP, these are derived from citation count
        # verified_claims_count: paragraphs with citations
        # single_source_claims_count: citations that appear only once
        # conflicts_count: contradictory claims (mock for MVP)
        verified_claims_count = citations_found
        single_source_claims_count = citations_found  # All citations are single source in MVP
        conflicts_count = 0  # No conflict detection in MVP

        return VerificationResult(
            passed=passed,
            total_paragraphs=total_paragraphs,
            paragraphs_without_citation=paragraphs_without_citation,
            paragraph_without_citation_count=paragraph_without_citation_count,
            citations_found=citations_found,
            verified_claims_count=verified_claims_count,
            single_source_claims_count=single_source_claims_count,
            conflicts_count=conflicts_count,
            issues=issues,
        )

    def _split_paragraphs(self, text: str) -> list[str]:
        """Split text into paragraphs."""
        # Split on double newlines or single newlines with space
        paragraphs = re.split(r"\n\s*\n|\n(?=\S)", text)
        return [p.strip() for p in paragraphs if p.strip()]

    def check_citation_format(self, text: str) -> tuple[int, int]:
        """
        Check citation format in text.

        Returns:
            (valid_format_count, invalid_format_count)
        """
        # Find all potential citations
        potential = re.findall(r"\([^)]+\)", text)

        valid = 0
        invalid = 0

        for cit in potential:
            # Check if it matches our citation format
            if self.CITATION_PATTERN.match(cit):
                valid += 1
            elif cit.startswith("(") and cit.endswith(")"):
                # Looks like a citation but wrong format
                invalid += 1

        return valid, invalid

    def suggest_fix(self, paragraph: str, cid: str) -> str:
        """
        Suggest a fix for a paragraph missing a citation.

        Args:
            paragraph: The paragraph text
            cid: The citation ID to add

        Returns:
            Paragraph with citation appended
        """
        # Add citation at end
        return f"{paragraph.rstrip()} ({cid})"

    def verify_paragraphs_jsonl(self, paragraphs_path: Path) -> tuple[bool, list[str]]:
        """
        Verify paragraphs.jsonl has valid cite_ids for each line.

        Args:
            paragraphs_path: Path to drafts/paragraphs.jsonl

        Returns:
            (passed, errors) - passed=True if all lines have valid cite_ids
        """
        import json

        errors = []
        if not paragraphs_path.exists():
            errors.append(f"paragraphs.jsonl not found: {paragraphs_path}")
            return False, errors

        with open(paragraphs_path) as f:
            lines = f.readlines()

        if not lines:
            errors.append("paragraphs.jsonl is empty")
            return False, errors

        for i, line in enumerate(lines):
            line = line.strip()
            if not line:
                continue
            try:
                data = json.loads(line)
            except json.JSONDecodeError as e:
                errors.append(f"Line {i+1}: invalid JSON: {e}")
                continue

            cite_ids = data.get("cite_ids", [])
            if not cite_ids:
                errors.append(f"Line {i+1}: cite_ids is empty")
                continue

            # Check cite_ids format (Cddd like C001, C002) - strict: C followed by exactly 3 digits
            cite_id_pattern = re.compile(r"C\d{3}\Z")
            for cid in cite_ids:
                if not isinstance(cid, str):
                    errors.append(f"Line {i+1}: cite_id {cid} is not a string")
                elif not cite_id_pattern.fullmatch(cid):
                    errors.append(f"Line {i+1}: cite_id {cid} invalid format (expected C001-C999)")

        passed = len(errors) == 0
        return passed, errors
