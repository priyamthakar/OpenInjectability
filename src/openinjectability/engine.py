"""Side-effect-free programmatic engine for Newtonian assessments.

This module is deliberately limited to typed in-memory inputs and results.  File
parsing, plotting, reporting, and the CLI remain adapter layers outside this
engine so a backend caller cannot accidentally broaden the scientific model.
"""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import asdict, dataclass

from .core import EXCLUSIONS, assess
from .models import (
    AssessmentConfig,
    AssessmentInput,
    AssessmentResult,
    BatchResult,
    InputValidationError,
    OpenInjectabilityError,
    RejectedAssessment,
)

PACKAGE_VERSION = "0.1.0"
SCHEMA_VERSION = "1.0"
MODEL_ID = "newtonian_hagen_poiseuille_v1"
VALIDATION_STATUS = "internal_validation; experimental_validation_pending"


@dataclass(frozen=True)
class EngineMetadata:
    """Versioned capabilities and strict scientific boundary of the engine."""

    engine_name: str = "OpenInjectabilityEngine"
    engine_version: str = PACKAGE_VERSION
    result_schema_version: str = SCHEMA_VERSION
    supported_model_ids: tuple[str, ...] = (MODEL_ID,)
    supported_rheology_classes: tuple[str, ...] = ("newtonian",)
    batch_rejections_are_explicit: bool = True
    filesystem_side_effects: bool = False
    validation_status: str = VALIDATION_STATUS
    exclusions: tuple[str, ...] = EXCLUSIONS

    def to_dict(self) -> dict[str, object]:
        """Return JSON-compatible metadata for service or audit adapters."""

        return asdict(self)


class OpenInjectabilityEngine:
    """Execute the validated v0.1 Newtonian model entirely in memory.

    The engine intentionally computes only predicted fluid-resistance force.
    It never reads files, writes artifacts, renders reports, or estimates total
    device force.  Unsupported rheology and invalid provenance remain typed,
    fail-closed errors from the underlying validated core.
    """

    def __init__(self, config: AssessmentConfig | None = None) -> None:
        if config is not None and not isinstance(config, AssessmentConfig):
            raise InputValidationError("config must be an AssessmentConfig or None")
        self._config = config or AssessmentConfig()
        if self._config.model_id != MODEL_ID:
            raise InputValidationError(
                f"OpenInjectabilityEngine supports only model_id {MODEL_ID!r}"
            )
        self._metadata = EngineMetadata(
            supported_model_ids=(self._config.model_id,),
        )

    @property
    def config(self) -> AssessmentConfig:
        """The immutable effective configuration used by this engine."""

        return self._config

    @property
    def metadata(self) -> EngineMetadata:
        """The immutable, versioned engine capability contract."""

        return self._metadata

    def assess(self, case: AssessmentInput) -> AssessmentResult:
        """Assess one case or raise a typed, fail-closed domain error."""

        if not isinstance(case, AssessmentInput):
            raise InputValidationError("case must be an AssessmentInput")
        return assess(case, config=self._config)

    def assess_batch(self, cases: Iterable[AssessmentInput]) -> BatchResult:
        """Assess cases in input order, retaining every domain rejection.

        Invalid or scientifically unsupported cases become explicit rejected-row
        records. Duplicate scenario identifiers are hard errors recorded without
        dropping later rows. Unexpected programming errors deliberately propagate
        rather than being represented as a scientific rejection.
        """

        results: list[AssessmentResult] = []
        rejected: list[RejectedAssessment] = []
        seen_ids: set[str] = set()
        for row_number, case in enumerate(cases, start=1):
            scenario_id = case.scenario_id if isinstance(case, AssessmentInput) else None
            if isinstance(case, AssessmentInput) and scenario_id is not None:
                if scenario_id in seen_ids:
                    rejected.append(
                        RejectedAssessment(
                            row_number=row_number,
                            scenario_id=scenario_id,
                            error_type="InputValidationError",
                            message=f"duplicate scenario_id: {scenario_id!r}",
                        )
                    )
                    continue
                seen_ids.add(scenario_id)
            try:
                results.append(self.assess(case))
            except OpenInjectabilityError as exc:
                rejected.append(
                    RejectedAssessment(
                        row_number=row_number,
                        scenario_id=scenario_id,
                        error_type=type(exc).__name__,
                        message=str(exc),
                    )
                )
        return BatchResult(results=tuple(results), rejected=tuple(rejected))


def engine_metadata() -> EngineMetadata:
    """Return default-engine capabilities without triggering any calculation."""

    return OpenInjectabilityEngine().metadata
