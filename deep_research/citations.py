"""Citation manager for Deep Research."""

import hashlib
import json
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Optional


@dataclass
class Citation:
    """Represents a single citation."""
    cid: str  # e.g., "C001", "C002"
    url: str
    title: str
    locator: str
    fetched_at: str = field(default_factory=lambda: datetime.now().isoformat())
    quote_hash: Optional[str] = None
    local_path: Optional[str] = None

    def to_dict(self) -> dict:
        return {
            "cid": self.cid,
            "url": self.url,
            "title": self.title,
            "locator": self.locator,
            "fetched_at": self.fetched_at,
            "quote_hash": self.quote_hash,
            "local_path": self.local_path,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Citation":
        return cls(**data)


class CitationManager:
    """
    Manages paragraph-level citations.

    Format: (Cxxx...) where xxx is a 3-digit number.
    Citations stored in citations.json.
    """

    def __init__(self):
        self._citations: list[Citation] = []
        self._cid_counter = 0
        self._citation_map: dict[str, Citation] = {}

    def reset(self) -> None:
        """Reset the citation manager."""
        self._citations = []
        self._cid_counter = 0
        self._citation_map = {}

    def add_citation(
        self,
        cid: str,
        url: str,
        title: str,
        locator: str = "",
        quote: Optional[str] = None,
    ) -> Citation:
        """
        Add a new citation.

        Args:
            cid: Citation ID (e.g., "C001")
            url: Source URL
            title: Source title
            locator: Page/section locator
            quote: Optional quote for hash

        Returns:
            Created Citation object
        """
        # Generate quote hash if quote provided
        quote_hash = None
        if quote:
            quote_hash = hashlib.md5(quote.encode()).hexdigest()[:16]

        citation = Citation(
            cid=cid,
            url=url,
            title=title,
            locator=locator,
            quote_hash=quote_hash,
        )

        self._citations.append(citation)
        self._citation_map[cid] = citation

        # Update counter
        try:
            num = int(cid[1:])
            if num > self._cid_counter:
                self._cid_counter = num
        except ValueError:
            pass

        return citation

    def get_citation(self, cid: str) -> Optional[Citation]:
        """Get citation by ID."""
        return self._citation_map.get(cid)

    def get_all(self) -> list[Citation]:
        """Get all citations."""
        return self._citations.copy()

    def get_all_dicts(self) -> list[dict]:
        """Get all citations as dictionaries."""
        return [c.to_dict() for c in self._citations]

    def generate_next_cid(self) -> str:
        """Generate the next citation ID."""
        self._cid_counter += 1
        return f"C{self._cid_counter:03d}"

    def format_citation(self, cid: str) -> str:
        """Format citation for inline use."""
        return f"({cid})"

    def save(self, path: Path) -> None:
        """Save citations to JSON file."""
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w") as f:
            json.dump(self.get_all_dicts(), f, indent=2)

    def load(self, path: Path) -> None:
        """Load citations from JSON file."""
        with open(path) as f:
            data = json.load(f)
            self.reset()
            for item in data:
                citation = Citation.from_dict(item)
                self._citations.append(citation)
                self._citation_map[citation.cid] = citation

    def find_citations_in_text(self, text: str) -> list[str]:
        """Find all citation references in text."""
        import re
        # Match (C001), (C002), etc.
        pattern = r"\((C\d+)\)"
        return re.findall(pattern, text)

    def validate_citations(self, text: str) -> tuple[int, int]:
        """
        Validate citations in text.

        Returns:
            (valid_count, invalid_count)
        """
        found = self.find_citations_in_text(text)
        valid = sum(1 for cid in found if cid in self._citation_map)
        return valid, len(found) - valid
