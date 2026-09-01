import unittest
from datetime import date
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parents[1] / ".github" / "scripts"))
from activity_chart import render_chart


class ActivityChartTests(unittest.TestCase):
    def test_renders_a_telemetry_signal_with_one_bar_and_node_per_week(self):
        chart = render_chart([0, 4, 8], date(2026, 9, 1))

        self.assertEqual(chart.count('class="bar"'), 3)
        self.assertEqual(chart.count('class="signal-node"'), 3)
        self.assertIn('BUILD SIGNAL / TELEMETRY', chart)
        self.assertIn('12 WEEK ACTIVITY', chart)
        self.assertIn('LAST SYNC UTC: 2026-09-01', chart)
        self.assertIn('class="signal-line"', chart)
        self.assertIn('class="circuit-signature"', chart)
        self.assertIn('Recent public contribution build signal', chart)
        self.assertIn('height="96.0"', chart)


if __name__ == "__main__":
    unittest.main()
