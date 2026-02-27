"""Deep Research MVP v2 - Autonomous research pipeline with verification."""

from .state_machine import StateMachine, RunState, Stage
from .clarify import Clarifier
from .worker import WorkerPool
from .citations import CitationManager
from .verify import Verifier
from .cache import CacheManager

__all__ = [
    "StateMachine",
    "RunState",
    "Stage",
    "Clarifier",
    "WorkerPool",
    "CitationManager",
    "Verifier",
    "CacheManager",
]

__version__ = "2.0.0"
