"""Cache module for Deep Research."""

import json
from datetime import datetime
from pathlib import Path
from typing import Any, Optional


class CacheManager:
    """
    Cache manager for fetched content.

    Provides:
    - Caching of fetched content
    - Resume capability for interrupted runs
    - Second run with same run_id skips fetch
    """

    def __init__(self, cache_dir: str = "./runs/.cache"):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    def _get_cache_path(self, run_id: str) -> Path:
        """Get cache file path for a run."""
        return self.cache_dir / f"{run_id}.json"

    def save_cached(self, run_id: str, data: list[dict]) -> None:
        """
        Save fetched results to cache.

        Args:
            run_id: The run identifier
            data: List of fetched results
        """
        cache_path = self._get_cache_path(run_id)

        cached_data = {
            "run_id": run_id,
            "cached_at": datetime.now().isoformat(),
            "results": data,
        }

        with open(cache_path, "w") as f:
            json.dump(cached_data, f, indent=2)

    def load_cached(self, run_id: str) -> Optional[list[dict]]:
        """
        Load cached results for a run.

        Args:
            run_id: The run identifier

        Returns:
            Cached results if exists, None otherwise
        """
        cache_path = self._get_cache_path(run_id)

        if not cache_path.exists():
            return None

        try:
            with open(cache_path) as f:
                cached_data = json.load(f)

            # Verify it's for the same run
            if cached_data.get("run_id") == run_id:
                return cached_data.get("results", [])

        except (json.JSONDecodeError, IOError):
            pass

        return None

    def has_cache(self, run_id: str) -> bool:
        """Check if cache exists for a run."""
        return self._get_cache_path(run_id).exists()

    def delete_cache(self, run_id: str) -> None:
        """Delete cache for a run."""
        cache_path = self._get_cache_path(run_id)
        if cache_path.exists():
            cache_path.unlink()

    def clear_all(self) -> None:
        """Clear all cached data."""
        for cache_file in self.cache_dir.glob("*.json"):
            cache_file.unlink()

    def get_cache_info(self, run_id: str) -> Optional[dict]:
        """Get cache metadata."""
        cache_path = self._get_cache_path(run_id)

        if not cache_path.exists():
            return None

        try:
            with open(cache_path) as f:
                data = json.load(f)

            return {
                "run_id": data.get("run_id"),
                "cached_at": data.get("cached_at"),
                "result_count": len(data.get("results", [])),
            }

        except (json.JSONDecodeError, IOError):
            return None

    def list_caches(self) -> list[str]:
        """List all cached run IDs."""
        caches = []
        for cache_file in self.cache_dir.glob("*.json"):
            caches.append(cache_file.stem)
        return caches
