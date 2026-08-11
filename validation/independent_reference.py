"""Standalone cross-implementation of the v0.1 equations.

This module deliberately imports no OpenInjectability code. It exists only as an
independent arithmetic cross-check for the locked reference fixture.
"""

from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any


def calculate(inputs: dict[str, Any]) -> dict[str, float]:
    mu = float(inputs["viscosity_value"]) / 1000.0
    length = float(inputs["needle_length_mm"]) * 1e-3
    needle_id = float(inputs["needle_id_mm"]) * 1e-3
    barrel_id = float(inputs["barrel_id_mm"]) * 1e-3
    volume = float(inputs["volume_ml"]) * 1e-6
    time_s = float(inputs["injection_time_s"])
    density = float(inputs["density_kg_m3"])
    flow = volume / time_s
    pressure = 128.0 * mu * length * flow / (math.pi * needle_id**4)
    area = math.pi * barrel_id**2 / 4.0
    velocity = 4.0 * flow / (math.pi * needle_id**2)
    return {
        "flow_rate_m3_s": flow,
        "needle_pressure_drop_pa": pressure,
        "fluid_resistance_force_n": pressure * area,
        "wall_shear_rate_s_1": 32.0 * flow / (math.pi * needle_id**3),
        "reynolds_number": density * velocity * needle_id / mu,
    }


if __name__ == "__main__":
    fixture_path = Path(__file__).parents[1] / "tests/reference_data/reference_case.json"
    fixture = json.loads(fixture_path.read_text(encoding="utf-8"))
    print(json.dumps(calculate(fixture["inputs"]), indent=2, sort_keys=True))
