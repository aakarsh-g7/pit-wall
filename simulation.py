"""Shared ten-lap calculation for the app, analysis, and saved example."""

import csv
import io
import json
import math
from pathlib import Path

FIRST_LAP = 31
LAST_LAP = 40
PIT_LOSS = 22.0
MODEL_PATH = Path(__file__).parent / "model_parameters.json"


def load_model(path=MODEL_PATH):
    with Path(path).open(encoding="utf-8") as file:
        parameters = json.load(file)
    for key in ("slope", "intercept"):
        value = parameters[key]
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            raise ValueError(f"Model {key} must be a number.")
        if not math.isfinite(value):
            raise ValueError(f"Model {key} must be finite.")
    return parameters


def simulate_strategy(pit_lap, starting_pace, slowdown, model, pit_loss=PIT_LOSS):
    """Return lap times and running totals; change tires before pit_lap."""
    if pit_lap not in range(FIRST_LAP, LAST_LAP + 1):
        raise ValueError("The pit lap must be between 31 and 40.")
    total_time = 0.0
    rows = []
    for lap in range(FIRST_LAP, LAST_LAP + 1):
        if lap < pit_lap:
            lap_time = model["intercept"] + model["slope"] * lap
        else:
            lap_time = starting_pace + slowdown * (lap - pit_lap)
        if lap == pit_lap:
            lap_time += pit_loss
        total_time += lap_time
        rows.append({"lap": lap, "lap_time_s": lap_time, "total_s": total_time})
    return rows


def compare_strategies(starting_pace, slowdown, model):
    """Positive gap means stopping on lap 31 is ahead."""
    early = simulate_strategy(31, starting_pace, slowdown, model)
    late = simulate_strategy(34, starting_pace, slowdown, model)
    return [
        {
            "lap": now["lap"],
            "pit_31_lap_s": now["lap_time_s"],
            "pit_34_lap_s": later["lap_time_s"],
            "pit_31_total_s": now["total_s"],
            "pit_34_total_s": later["total_s"],
            "gap_s": later["total_s"] - now["total_s"],
        }
        for now, later in zip(early, late)
    ]


def comparison_csv(rows):
    """Use the same six-decimal CSV format in the app and example export."""
    output = io.StringIO(newline="")
    writer = csv.DictWriter(output, fieldnames=list(rows[0]), lineterminator="\n")
    writer.writeheader()
    for row in rows:
        writer.writerow({
            key: value if key == "lap" else f"{value:.6f}"
            for key, value in row.items()
        })
    return output.getvalue()
