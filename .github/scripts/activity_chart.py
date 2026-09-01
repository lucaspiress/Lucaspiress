import json
import os
import urllib.request
from datetime import date, datetime, timedelta, timezone
from html import escape
from pathlib import Path


def render_chart(week_counts, generated_on):
    chart_width = 1200
    baseline = 168
    chart_height = 96
    left = 56
    available_width = 1088
    gap = 14
    count = max(len(week_counts), 1)
    bar_width = (available_width - gap * (count - 1)) / count
    maximum = max(week_counts, default=0) or 1

    bars = []
    for index, contributions in enumerate(week_counts):
        height = contributions / maximum * chart_height
        x = left + index * (bar_width + gap)
        y = baseline - height
        bars.append(
            f'<rect class="bar" x="{x:.1f}" y="{y:.1f}" '
            f'width="{bar_width:.1f}" height="{height:.1f}" rx="3" />'
        )

    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{chart_width}" height="220" viewBox="0 0 {chart_width} 220" role="img" aria-labelledby="title description">
  <title id="title">Recent public contribution activity</title>
  <desc id="description">A minimal weekly bar chart of public GitHub contributions, updated {escape(generated_on.isoformat())}.</desc>
  <rect width="1200" height="220" rx="8" fill="#0d1117" stroke="#30363d" />
  <path d="M56 168H1144" stroke="#30363d" stroke-width="1" />
  <text x="56" y="48" fill="#e6edf3" font-family="ui-monospace, SFMono-Regular, Menlo, Consolas, monospace" font-size="18" font-weight="700">ACTIVITY / PUBLIC CONTRIBUTIONS</text>
  <text x="56" y="76" fill="#8b949e" font-family="ui-monospace, SFMono-Regular, Menlo, Consolas, monospace" font-size="12">last {len(week_counts)} weeks · updated {escape(generated_on.isoformat())}</text>
  <g fill="#58a6ff">{''.join(bars)}</g>
</svg>'''


def fetch_week_counts(today):
    token = os.environ["GH_TOKEN"]
    start = today - timedelta(days=83)
    query = """
    query($login: String!, $from: DateTime!, $to: DateTime!) {
      user(login: $login) {
        contributionsCollection(from: $from, to: $to) {
          contributionCalendar {
            weeks {
              contributionDays { date contributionCount }
            }
          }
        }
      }
    }
    """
    payload = json.dumps(
        {
            "query": query,
            "variables": {
                "login": "lucaspiress",
                "from": f"{start.isoformat()}T00:00:00Z",
                "to": f"{today.isoformat()}T23:59:59Z",
            },
        }
    ).encode("utf-8")
    request = urllib.request.Request(
        "https://api.github.com/graphql",
        data=payload,
        headers={
            "Accept": "application/vnd.github+json",
            "Authorization": f"Bearer {token}",
            "User-Agent": "lucaspiress-profile",
        },
        method="POST",
    )
    with urllib.request.urlopen(request, timeout=30) as response:
        result = json.load(response)

    if result.get("errors"):
        raise RuntimeError(result["errors"])

    weeks = result["data"]["user"]["contributionsCollection"]["contributionCalendar"]["weeks"]
    counts = []
    for week in weeks:
        days = [
            day
            for day in week["contributionDays"]
            if start <= date.fromisoformat(day["date"]) <= today
        ]
        if days:
            counts.append(sum(day["contributionCount"] for day in days))
    return counts[-12:]


def main():
    today = datetime.now(timezone.utc).date()
    chart = render_chart(fetch_week_counts(today), today)
    output = Path(__file__).resolve().parents[2] / "assets" / "activity-chart.svg"
    output.write_text(chart, encoding="utf-8")


if __name__ == "__main__":
    main()
