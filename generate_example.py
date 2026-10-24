"""Save the default simulation output without downloading race data."""

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

from simulation import compare_strategies, comparison_csv, load_model


def main():
    rows = compare_strategies(95.0, 0.05, load_model())
    folder = Path(__file__).parent / "examples"
    folder.mkdir(exist_ok=True)
    (folder / "default_strategy.csv").write_text(comparison_csv(rows), encoding="utf-8")

    plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 11})
    figure, axes = plt.subplots(figsize=(9, 4.8), layout="constrained")
    laps = [30] + [row["lap"] for row in rows]
    gap = [0.0] + [row["gap_s"] for row in rows]
    axes.plot(laps, gap, color="#0071e3", linewidth=2, marker="o", markersize=4)
    axes.axhline(0, color="#68686d", linewidth=1)
    axes.set(xlabel="Lap", ylabel="Lap 34 total minus lap 31 total (s)", xticks=laps)
    axes.set_title("Pit Wall | Bahrain 2024 · Max Verstappen", loc="left", fontsize=15, pad=34)
    axes.text(0, 1.04, "Simulation: 95.00 s starting pace · 0.05 s/lap slowdown · 22 s pit loss",
              transform=axes.transAxes, fontsize=10, color="#68686d")
    axes.annotate("Lap 31 stop", xy=(31, gap[1]), xytext=(31.6, -18),
                  arrowprops={"arrowstyle": "-", "color": "#68686d"}, color="#68686d")
    axes.annotate("Lap 34 stop", xy=(34, gap[4]), xytext=(34.8, -7),
                  arrowprops={"arrowstyle": "-", "color": "#68686d"}, color="#68686d")
    axes.annotate(f"Lap 31 finishes {gap[-1]:.2f} s ahead", xy=(40, gap[-1]),
                  xytext=(36, 4), fontsize=11, color="#0071e3")
    axes.set_ylim(min(gap) - 3, 7)
    axes.grid(axis="y", alpha=0.15)
    axes.spines[["top", "right"]].set_visible(False)
    figure.savefig(folder / "default_strategy.png", dpi=160)
    plt.close(figure)

    final = rows[-1]
    print(f"Lap 31 stop: {final['pit_31_total_s']:.6f} s")
    print(f"Lap 34 stop: {final['pit_34_total_s']:.6f} s")
    print(f"Gap: {final['gap_s']:.6f} s (positive favors lap 31)")
    print("Saved examples/default_strategy.csv and examples/default_strategy.png")


if __name__ == "__main__":
    main()
