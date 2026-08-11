"""Optional, grayscale-safe plotting adapters for assessment results."""

from __future__ import annotations

import re
from collections.abc import Iterable
from pathlib import Path
from typing import Any

from .models import AssessmentResult


def _pyplot() -> Any:
    try:
        import matplotlib

        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except ImportError as exc:  # pragma: no cover - depends on optional environment
        raise RuntimeError(
            "plotting requires the 'reports' extra: pip install openinjectability[reports]"
        ) from exc
    return plt


def _items(results: Iterable[AssessmentResult]) -> list[AssessmentResult]:
    materialized = list(results)
    if not materialized:
        raise ValueError("at least one result is required for plotting")
    return materialized


def _save(fig: Any, path: str | Path, *, title: str, description: str) -> None:
    destination = Path(path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(
        destination,
        dpi=160,
        metadata={"Title": title, "Description": description},
    )


def force_vs_needle_geometry(results: Iterable[AssessmentResult], path: str | Path) -> None:
    """Plot force against actual needle ID, with gauge labels as annotations."""

    plt = _pyplot()
    items = _items(results)
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
        label = (
            item.normalized_input.get("needle_gauge_label") or item.normalized_input["scenario_id"]
        )
        labels.append(str(label))
    fig, axis = plt.subplots(figsize=(7.2, 4.8), constrained_layout=True)
    axis.scatter(ids, forces, color="0.2", marker="o", s=45)
    for x_value, y_value, label in zip(ids, forces, labels, strict=True):
        axis.annotate(label, (x_value, y_value), xytext=(5, 5), textcoords="offset points")
    axis.set_xlabel("Traceable needle inner diameter (mm)")
    axis.set_ylabel("Predicted fluid-resistance force (N)")
    axis.set_title("Needle geometry comparison\nNewtonian idealized needle-fluid model")
    axis.grid(True, alpha=0.25)
    _save(
        fig,
        path,
        title="Predicted fluid-resistance force versus needle geometry",
        description=(
            f"Model {items[0].model_id}; scenarios "
            + ", ".join(str(item.normalized_input["scenario_id"]) for item in items)
        ),
    )
    plt.close(fig)


def pressure_vs_flow_rate(results: Iterable[AssessmentResult], path: str | Path) -> None:
    """Plot modeled needle pressure drop against calculated flow rate."""

    plt = _pyplot()
    items = _items(results)
    flow_ml_s = [float(item.outputs["flow_rate_m3_s"] or 0.0) * 1_000_000.0 for item in items]
    pressure_mpa = [
        float(item.outputs["needle_pressure_drop_pa"] or 0.0) / 1_000_000.0 for item in items
    ]
    labels = [str(item.normalized_input["scenario_id"]) for item in items]
    fig, axis = plt.subplots(figsize=(7.2, 4.8), constrained_layout=True)
    axis.plot(flow_ml_s, pressure_mpa, color="0.2", marker="s", linestyle="none")
    for x_value, y_value, label in zip(flow_ml_s, pressure_mpa, labels, strict=True):
        axis.annotate(label, (x_value, y_value), xytext=(5, 5), textcoords="offset points")
    axis.set_xlabel("Calculated flow rate (mL/s)")
    axis.set_ylabel("Predicted needle pressure drop (MPa)")
    axis.set_title("Pressure versus flow rate\nNewtonian idealized needle-fluid model")
    axis.grid(True, alpha=0.25)
    _save(
        fig,
        path,
        title="Predicted needle pressure drop versus flow rate",
        description=f"Model {items[0].model_id}; measured inputs and calculated outputs labeled",
    )
    plt.close(fig)


def sensitivity_tornado(result: AssessmentResult, path: str | Path) -> None:
    """Plot deterministic one-at-a-time force changes for one scenario."""

    plt = _pyplot()
    if not result.sensitivity:
        raise ValueError("sensitivity results are required for plotting")
    labels = [f"{item.input_name} ({item.relative_change:+.0%})" for item in result.sensitivity]
    changes = [item.force_relative_change * 100.0 for item in result.sensitivity]
    positions = list(range(len(labels)))
    fig, axis = plt.subplots(figsize=(8.2, max(4.8, len(labels) * 0.32)), constrained_layout=True)
    bars = axis.barh(positions, changes, color="0.7", edgecolor="0.1")
    for bar, change in zip(bars, changes, strict=True):
        if change < 0:
            bar.set_hatch("//")
    axis.set_yticks(positions, labels=labels)
    axis.set_xlabel("Relative change in predicted fluid-resistance force (%)")
    axis.set_title(
        f"Deterministic sensitivity - {result.normalized_input['scenario_id']}\n"
        "Newtonian idealized needle-fluid model"
    )
    axis.axvline(0.0, color="0.1", linewidth=0.8)
    axis.grid(True, axis="x", alpha=0.25)
    _save(
        fig,
        path,
        title=f"Deterministic sensitivity for {result.normalized_input['scenario_id']}",
        description=f"Model {result.model_id}; hatched bars indicate negative changes",
    )
    plt.close(fig)


def scenario_comparison(results: Iterable[AssessmentResult], path: str | Path) -> None:
    """Compare scenario forces and distinguish warning-bearing results by marker."""

    plt = _pyplot()
    items = _items(results)
    labels = [str(item.normalized_input["scenario_id"]) for item in items]
    forces = [float(item.outputs["fluid_resistance_force_n"] or 0.0) for item in items]
    fig, axis = plt.subplots(figsize=(8.0, 4.8), constrained_layout=True)
    for index, (item, force) in enumerate(zip(items, forces, strict=True)):
        marker = "^" if item.warnings else "o"
        face = "none" if item.warnings else "0.35"
        axis.scatter(
            index,
            force,
            marker=marker,
            facecolors=face,
            edgecolors="0.1",
            s=70,
        )
    axis.set_xticks(range(len(labels)), labels=labels, rotation=25, ha="right")
    axis.set_ylabel("Predicted fluid-resistance force (N)")
    axis.set_xlabel("Scenario (declared inputs)")
    axis.set_title("Scenario comparison\nNewtonian idealized needle-fluid model")
    axis.grid(True, axis="y", alpha=0.25)
    axis.text(
        0.01,
        0.98,
        "Triangle/hollow = result has warnings; circle/filled = no warnings",
        transform=axis.transAxes,
        va="top",
        fontsize=8,
    )
    _save(
        fig,
        path,
        title="Scenario comparison with warning markers",
        description=f"Model {items[0].model_id}; warning state distinguished by shape and fill",
    )
    plt.close(fig)


def write_required_plots(
    results: Iterable[AssessmentResult], directory: str | Path
) -> tuple[Path, ...]:
    """Generate the complete specification plot set as portable PNG files."""

    items = _items(results)
    output = Path(directory)
    output.mkdir(parents=True, exist_ok=True)
    paths: list[Path] = []
    geometry = output / "force-vs-needle-geometry.png"
    force_vs_needle_geometry(items, geometry)
    paths.append(geometry)
    pressure = output / "pressure-vs-flow-rate.png"
    pressure_vs_flow_rate(items, pressure)
    paths.append(pressure)
    comparison = output / "scenario-comparison.png"
    scenario_comparison(items, comparison)
    paths.append(comparison)
    for result in items:
        scenario = re.sub(
            r"[^A-Za-z0-9_.-]+", "-", str(result.normalized_input["scenario_id"])
        ).strip("-")
        sensitivity = output / f"sensitivity-{scenario or 'scenario'}.png"
        sensitivity_tornado(result, sensitivity)
        paths.append(sensitivity)
    return tuple(paths)
