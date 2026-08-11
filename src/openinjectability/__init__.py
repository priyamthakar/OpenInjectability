"""Public API for OpenInjectability."""

from ._version import __version__
from .core import assess, assess_many
from .engine import EngineMetadata, OpenInjectabilityEngine, engine_metadata
from .models import (
    AssessmentConfig,
    AssessmentInput,
    AssessmentResult,
    BatchResult,
    InputSchemaError,
    InputValidationError,
    RejectedAssessment,
    ScientificBoundaryError,
    UnitError,
    ValidationRegistryError,
)

__all__ = [
    "AssessmentConfig",
    "AssessmentInput",
    "AssessmentResult",
    "BatchResult",
    "EngineMetadata",
    "InputSchemaError",
    "InputValidationError",
    "OpenInjectabilityEngine",
    "RejectedAssessment",
    "ScientificBoundaryError",
    "UnitError",
    "ValidationRegistryError",
    "__version__",
    "assess",
    "assess_many",
    "engine_metadata",
]
