"""Concurrent worker pool for Deep Research."""

import concurrent.futures
import threading
from typing import Any, Callable, Iterable, TypeVar

T = TypeVar("T")
R = TypeVar("R")


class WorkerPool:
    """
    Concurrent workers pool.

    Default workers=5, configurable via --workers flag.
    """

    def __init__(self, max_workers: int = 5):
        self.max_workers = max_workers
        self._lock = threading.Lock()

    def run(self, func: Callable[[T], R], items: list[T]) -> list[R]:
        """
        Run function on items in parallel.

        Args:
            func: Function to apply to each item
            items: List of items to process

        Returns:
            List of results in same order as items
        """
        results = [None] * len(items)

        def process_item(args):
            index, item = args
            result = func(item)
            return index, result

        with concurrent.futures.ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = {
                executor.submit(process_item, (i, item)): i
                for i, item in enumerate(items)
            }

            for future in concurrent.futures.as_completed(futures):
                index, result = future.result()
                results[index] = result

        return results

    def run_with_index(
        self, func: Callable[[int, T], R], items: list[T]
    ) -> list[R]:
        """
        Run function with index on items in parallel.

        Args:
            func: Function that takes (index, item) and returns result
            items: List of items to process

        Returns:
            List of results in same order as items
        """
        results = [None] * len(items)

        def process_item(args):
            index, item = args
            result = func(index, item)
            return index, result

        with concurrent.futures.ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = {
                executor.submit(process_item, (i, item)): i
                for i, item in enumerate(items)
            }

            for future in concurrent.futures.as_completed(futures):
                index, result = future.result()
                results[index] = result

        return results

    def map(self, func: Callable[[T], R], iterable: Iterable[T]) -> Iterable[R]:
        """
        Map function over iterable with parallel execution.

        Note: Results may not be in order.
        """
        with concurrent.futures.ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            return list(executor.map(func, iterable))

    def submit(self, func: Callable[..., R], *args, **kwargs) -> concurrent.futures.Future:
        """
        Submit a single task.

        Returns a Future that can be used to get the result.
        """
        with concurrent.futures.ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            return executor.submit(func, *args, **kwargs)

    def update_workers(self, max_workers: int) -> None:
        """Update the number of workers."""
        with self._lock:
            self.max_workers = max_workers
