"""Public API for OpenInjectability."""

from .core import assess, assess_many
from .engine import EngineMetadata, OpenInjectabilityEngine, engine_metadata
from .models import (
    AssessmentConfig,
    AssessmentInput,
    AssessmentResult,
    BatchResult,
    InputValidationError,
    RejectedAssessment,
    ScientificBoundaryError,
)

__all__ = [
    "AssessmentConfig",
    "AssessmentInput",
    "AssessmentResult",
    "BatchResult",
    "EngineMetadata",
    "InputValidationError",
    "OpenInjectabilityEngine",
    "RejectedAssessment",
    "ScientificBoundaryError",
    "assess",
    "assess_many",
    "engine_metadata",
]

__version__ = "0.1.0"
