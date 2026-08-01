"""Optional plotting adapters."""

from __future__ import annotations

from collections.abc import Iterable
from pathlib import Path

from .models import AssessmentResult


def force_vs_needle_geometry(
    results: Iterable[AssessmentResult], path: str | Path
) -> None:
    """Plot force against actual needle ID, with gauge labels as annotations."""

    try:
        import matplotlib

        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except ImportError as exc:  # pragma: no cover - depends on optional environment
        raise RuntimeError(
            "plotting requires the 'reports' extra: pip install openinjectability[reports]"
        ) from exc

    items = list(results)
    if not items:
        raise ValueError("at least one result is required for plotting")
    ids: list[float] = []
    forces: list[float] = []
    labels: list[str] = []
    for item in items:
        needle_id = item.normalized_input["needle_id_mm"]
        force = item.outputs["fluid_resistance_force_n"]
        if not isinstance(needle_id, (int, float)) or isinstance(needle_id, bool):
            raise TypeError("needle_id_mm must be numeric for plotting")
        if force is None:
            raise ValueError("fluid_resistance_force_n is required for plotting")
        ids.append(float(needle_id))
        forces.append(float(force))
        label = item.normalized_input.get("needle_gauge_label") or item.normalized_input[
            "scenario_id"
        ]
        labels.append(str(label))
    fig, axis = plt.subplots(figsize=(7.2, 4.8), constrained_layout=True)
    axis.scatter(ids, forces, color="#176b87", s=45)
    for x_value, y_value, label in zip(ids, forces, labels, strict=True):
        axis.annotate(str(label), (x_value, y_value), xytext=(5, 5), textcoords="offset points")
    axis.set_xlabel("Traceable needle inner diameter (mm)")
    axis.set_ylabel("Predicted fluid-resistance force (N)")
    axis.set_title(
        "Needle geometry comparison\nNewtonian idealized needle-fluid model"
    )
    axis.grid(True, alpha=0.25)
    fig.savefig(Path(path), dpi=160)
    plt.close(fig)
