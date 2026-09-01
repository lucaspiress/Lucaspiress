import unittest
from datetime import date
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parents[1] / ".github" / "scripts"))
from activity_chart import render_chart


class ActivityChartTests(unittest.TestCase):
    def test_renders_one_bar_per_week_and_marks_the_generation_date(self):
        chart = render_chart([0, 4, 8], date(2026, 9, 1))

        self.assertEqual(chart.count('class="bar"'), 3)
        self.assertIn('updated 2026-09-01', chart)
        self.assertIn('Recent public contribution activity', chart)
        self.assertIn('height="96.0"', chart)


if __name__ == "__main__":
    unittest.main()
