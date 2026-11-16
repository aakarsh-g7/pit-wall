"""Exercise the real Streamlit script and both ends of its controls."""

from pathlib import Path
import unittest

from streamlit.testing.v1 import AppTest

APP = Path(__file__).parents[1] / "app.py"


class AppTests(unittest.TestCase):
    def test_default_and_slider_results(self):
        app = AppTest.from_file(str(APP), default_timeout=15).run()
        self.assertEqual(len(app.exception), 0)
        self.assertEqual(len(app.error), 0)
        self.assertEqual(len(app.slider), 2)
        final = app.dataframe[0].value.iloc[-1]
        self.assertAlmostEqual(final["pit_31_total_s"], 974.25)
        self.assertAlmostEqual(final["gap_s"], 1.0770279720279)
        for pace, slowdown, expected_sign in ((94.0, 0.0, 1), (97.0, 0.2, -1)):
            with self.subTest(pace=pace, slowdown=slowdown):
                app.slider(key="pace").set_value(pace)
                app.slider(key="slowdown").set_value(slowdown)
                app.run()
                self.assertEqual(len(app.exception), 0)
                gap = app.dataframe[0].value.iloc[-1]["gap_s"]
                self.assertGreater(gap * expected_sign, 0)


if __name__ == "__main__":
    unittest.main()
