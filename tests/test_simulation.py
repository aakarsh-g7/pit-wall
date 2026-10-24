import csv
import io
from pathlib import Path
import unittest

from simulation import compare_strategies, comparison_csv, load_model, simulate_strategy


class SimulationTests(unittest.TestCase):
    def setUp(self):
        self.model = load_model()

    def test_committed_default_result(self):
        final = compare_strategies(95.0, 0.05, self.model)[-1]
        self.assertAlmostEqual(final["pit_31_total_s"], 974.25)
        self.assertAlmostEqual(final["pit_34_total_s"], 975.3270279720279)
        self.assertAlmostEqual(final["gap_s"], 1.0770279720279)

    def test_each_strategy_pays_one_pit_loss(self):
        # Constant 100 s pace makes ten laps plus one 22 s stop easy to check.
        for pit_lap in (31, 34, 40):
            with self.subTest(pit_lap=pit_lap):
                rows = simulate_strategy(pit_lap, 100.0, 0.0, {"intercept": 100.0, "slope": 0.0})
                self.assertEqual([row["lap"] for row in rows], list(range(31, 41)))
                self.assertEqual(rows[-1]["total_s"], 1022.0)
                self.assertEqual(sum(row["lap_time_s"] == 122.0 for row in rows), 1)

    def test_equal_pit_losses_cancel_from_final_gap(self):
        gaps = []
        for loss in (0.0, 22.0, 35.0):
            early = simulate_strategy(31, 95.0, 0.05, self.model, pit_loss=loss)
            late = simulate_strategy(34, 95.0, 0.05, self.model, pit_loss=loss)
            gaps.append(late[-1]["total_s"] - early[-1]["total_s"])
        self.assertAlmostEqual(gaps[0], gaps[1])
        self.assertAlmostEqual(gaps[1], gaps[2])

    def test_slider_changes_can_reverse_the_choice(self):
        self.assertGreater(compare_strategies(94.0, 0.0, self.model)[-1]["gap_s"], 0)
        self.assertLess(compare_strategies(97.0, 0.2, self.model)[-1]["gap_s"], 0)
        low = compare_strategies(95.0, 0.0, self.model)[-1]["gap_s"]
        high = compare_strategies(95.0, 0.2, self.model)[-1]["gap_s"]
        self.assertGreater(low, high)

    def test_saved_csv_matches_shared_calculation(self):
        rows = compare_strategies(95.0, 0.05, self.model)
        saved = Path(__file__).parents[1] / "examples" / "default_strategy.csv"
        self.assertEqual(saved.read_text(encoding="utf-8"), comparison_csv(rows))
        parsed = list(csv.DictReader(io.StringIO(comparison_csv(rows))))
        self.assertEqual(len(parsed), 10)
        self.assertAlmostEqual(float(parsed[-1]["gap_s"]), rows[-1]["gap_s"], places=6)


if __name__ == "__main__":
    unittest.main()
