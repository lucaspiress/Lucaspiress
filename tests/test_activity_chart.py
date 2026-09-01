import unittest
from datetime import date
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parents[1] / ".github" / "scripts"))
from activity_chart import render_chart


class ActivityChartTests(unittest.TestCase):
    def test_renders_a_compact_mobile_readable_activity_signal(self):
        chart = render_chart([0, 4, 8], date(2026, 9, 1))

        self.assertEqual(chart.count('class="bar"'), 3)
        self.assertEqual(chart.count('class="signal-node"'), 3)
        self.assertIn('width="720" height="184" viewBox="0 0 720 184"', chart)
        self.assertIn('>ACTIVITY<', chart)
        self.assertIn('>12 WEEKS<', chart)
        self.assertIn('>12 WEEKS AGO<', chart)
        self.assertIn('>NOW<', chart)
        self.assertIn('class="signal-line"', chart)
        self.assertIn('class="circuit-signature"', chart)
        self.assertIn('Recent public contribution build signal', chart)
        self.assertIn('font-size="20"', chart)
        self.assertNotIn('LAST SYNC UTC:', chart)


if __name__ == "__main__":
    unittest.main()
