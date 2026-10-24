"""Download the case-study data, evaluate the pace trend, and save evidence."""

import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
from statistics import linear_regression

import matplotlib.pyplot as plt
import pandas as pd
import requests

from simulation import PIT_LOSS, compare_strategies

PROJECT = Path(__file__).parent
API = "https://api.openf1.org/v1"


def fetch_records(endpoint, params):
    response = requests.get(f"{API}/{endpoint}", params=params, timeout=30)
    response.raise_for_status()
    records = response.json()
    if not records:
        raise ValueError(f"OpenF1 returned no {endpoint} records for {params}.")
    return records


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--no-show", action="store_true", help="Save the chart without opening a window.")
    args = parser.parse_args()
    if args.no_show:
        plt.switch_backend("Agg")

    session_query = {"year": 2024, "country_name": "Bahrain", "session_name": "Race"}
    try:
        session = fetch_records("sessions", session_query)[0]
        query = {"session_key": session["session_key"], "driver_number": 1}
        laps = pd.DataFrame(fetch_records("laps", query))
        stints = pd.DataFrame(fetch_records("stints", query))
    except (requests.RequestException, ValueError) as error:
        raise SystemExit(f"Could not download race data: {error}") from error

    laps = laps[["driver_number", "lap_number", "lap_duration", "is_pit_out_lap"]]
    laps = laps.sort_values("lap_number")
    stints = stints[["stint_number", "lap_start", "lap_end", "compound", "tyre_age_at_start"]]
    stints = stints.sort_values("stint_number")

    clean_laps = laps.dropna(subset=["lap_duration"]).copy()
    clean_laps = clean_laps[
        (clean_laps["lap_number"] > 1)
        & (clean_laps["is_pit_out_lap"] == False)
    ]
    # Exclude pit-in laps, but keep the final race lap.
    clean_laps = clean_laps[~clean_laps["lap_number"].isin(stints["lap_end"].iloc[:-1])]

    summary_rows = []
    for _, stint in stints.iterrows():
        stint_laps = clean_laps[
            clean_laps["lap_number"].between(stint["lap_start"], stint["lap_end"])
        ]
        summary_rows.append({
            "Stint": int(stint["stint_number"]),
            "Tire": stint["compound"],
            "Laps analyzed": len(stint_laps),
            "Median time (s)": stint_laps["lap_duration"].median(),
            "Standard deviation (s)": stint_laps["lap_duration"].std(),
        })
    summary = pd.DataFrame(summary_rows)

    # Use source stint boundaries rather than hardcoded lap numbers.
    hard_stints = stints[stints["compound"] == "HARD"]
    if hard_stints.empty:
        raise SystemExit("No hard-tire stint was returned.")
    hard_stint = hard_stints.iloc[0]
    hard_laps = clean_laps[
        clean_laps["lap_number"].between(hard_stint["lap_start"], hard_stint["lap_end"])
    ].sort_values("lap_number")
    if len(hard_laps) <= 12:
        raise SystemExit("Need 12 training laps and at least one test lap in the hard-tire stint.")

    # Chronological split: fit on the first 12 clean laps; test on later laps.
    train, test = hard_laps.iloc[:12], hard_laps.iloc[12:]
    fit = linear_regression(train["lap_number"].tolist(), train["lap_duration"].tolist())
    model = {"slope": float(fit.slope), "intercept": float(fit.intercept)}
    results = test[["lap_number", "lap_duration"]].copy()
    results["prediction"] = fit.intercept + fit.slope * results["lap_number"]
    results["baseline"] = train["lap_duration"].median()
    model_mae = float((results["lap_duration"] - results["prediction"]).abs().mean())
    baseline_mae = float((results["lap_duration"] - results["baseline"]).abs().mean())

    output = PROJECT / "outputs"
    output.mkdir(exist_ok=True)
    laps.to_csv(output / "laps.csv", index=False)
    stints.to_csv(output / "stints.csv", index=False)
    clean_laps.to_csv(output / "clean_laps.csv", index=False)
    summary.to_csv(output / "stint_summary.csv", index=False)
    results.to_csv(output / "predictions.csv", index=False)
    metadata = {
        "source": API,
        "session_query": session_query,
        "data_query": query,
        "retrieved_at_utc": datetime.now(timezone.utc).isoformat(),
        "train_laps": train["lap_number"].astype(int).tolist(),
        "test_laps": test["lap_number"].astype(int).tolist(),
        "model": model,
        "model_mae_s": model_mae,
        "median_baseline_mae_s": baseline_mae,
        "simulation_assumptions": {
            "starting_pace_s": 95.0, "slowdown_s_per_lap": 0.05, "pit_loss_s": PIT_LOSS,
        },
    }
    (output / "analysis_summary.json").write_text(json.dumps(metadata, indent=2) + "\n", encoding="utf-8")
    (PROJECT / "model_parameters.json").write_text(json.dumps(model, indent=2) + "\n", encoding="utf-8")

    print("Race ID:", session["session_key"])
    print("\nTire stints:\n", stints.to_string(index=False))
    print("\nStint comparison:\n", summary.round(3).to_string(index=False))
    print("\nPrediction results:\n", results.round(3).to_string(index=False))
    print(f"\nTrend model MAE: {model_mae:.3f} seconds")
    print(f"Median baseline MAE: {baseline_mae:.3f} seconds")
    comparison = compare_strategies(95.0, 0.05, model)[-1]
    print("\nStrategy simulation — laps 31–40:")
    print(f"Pit on lap 31: {comparison['pit_31_total_s']:.3f} seconds")
    print(f"Pit on lap 34: {comparison['pit_34_total_s']:.3f} seconds")
    print(f"Gap: {comparison['gap_s']:.3f} seconds (positive favors lap 31)")

    colors = {"SOFT": "#c64242", "MEDIUM": "#ab8500", "HARD": "#68686d"}
    figure, axes = plt.subplots(figsize=(10, 5), layout="constrained")
    for _, stint in stints.iterrows():
        stint_laps = clean_laps[
            clean_laps["lap_number"].between(stint["lap_start"], stint["lap_end"])
        ]
        axes.plot(
            stint_laps["lap_number"], stint_laps["lap_duration"],
            color=colors.get(stint["compound"], "#0071e3"), marker="o", markersize=3,
            label=f"Stint {stint['stint_number']}: {stint['compound']}",
        )
    axes.set(title="Verstappen's Race Pace by Tire Stint — Bahrain 2024",
             xlabel="Lap number", ylabel="Lap time (s)")
    axes.legend()
    axes.grid(alpha=0.2)
    figure.savefig(output / "race_pace.png", dpi=160)
    print("\nSaved model_parameters.json and analysis evidence in outputs/.")
    if not args.no_show:
        plt.show()
    plt.close(figure)


if __name__ == "__main__":
    main()
