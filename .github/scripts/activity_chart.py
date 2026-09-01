import json
import os
import urllib.request
from datetime import date, datetime, timedelta, timezone
from html import escape
from pathlib import Path


def render_chart(week_counts, generated_on):
    chart_width = 1200
    baseline = 174
    chart_height = 96
    left = 72
    available_width = 940
    gap = 16
    count = max(len(week_counts), 1)
    bar_width = (available_width - gap * (count - 1)) / count
    maximum = max(week_counts, default=0) or 1

    bars = []
    nodes = []
    points = []
    for index, contributions in enumerate(week_counts):
        height = contributions / maximum * chart_height
        x = left + index * (bar_width + gap)
        y = baseline - height
        center = x + bar_width / 2
        bars.append(
            f'<rect class="bar" x="{x:.1f}" y="{y:.1f}" '
            f'width="{bar_width:.1f}" height="{height:.1f}" rx="2" />'
        )
        points.append(f"{center:.1f},{y:.1f}")
        nodes.append(
            f'<circle class="signal-node" cx="{center:.1f}" cy="{y:.1f}" r="3.5" />'
        )

    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{chart_width}" height="220" viewBox="0 0 {chart_width} 220" role="img" aria-labelledby="title description">
  <title id="title">Recent public contribution build signal</title>
  <desc id="description">A twelve-week telemetry chart of public GitHub contributions, last synchronized {escape(generated_on.isoformat())}.</desc>
  <defs>
    <linearGradient id="signalFill" x1="0" x2="0" y1="0" y2="1">
      <stop offset="0" stop-color="#ff5c5c" />
      <stop offset="1" stop-color="#9e2020" />
    </linearGradient>
  </defs>
  <rect width="1200" height="220" rx="8" fill="#0d1117" stroke="#30363d" />
  <g stroke="#30363d" stroke-width="1">
    <path d="M72 110H1012" opacity="0.38" />
    <path d="M72 142H1012" opacity="0.58" />
    <path d="M72 174H1128" />
  </g>
  <text x="72" y="42" fill="#f0f6fc" font-family="ui-monospace, SFMono-Regular, Menlo, Consolas, monospace" font-size="17" font-weight="700">BUILD SIGNAL / TELEMETRY</text>
  <text x="72" y="66" fill="#8b949e" font-family="ui-monospace, SFMono-Regular, Menlo, Consolas, monospace" font-size="11">12 WEEK ACTIVITY  //  PUBLIC CONTRIBUTIONS</text>
  <text x="72" y="198" fill="#6e7681" font-family="ui-monospace, SFMono-Regular, Menlo, Consolas, monospace" font-size="10">LAST SYNC UTC: {escape(generated_on.isoformat())}</text>
  <g fill="url(#signalFill)" opacity="0.88">{''.join(bars)}</g>
  <polyline class="signal-line" points="{' '.join(points)}" fill="none" stroke="#ff7070" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" />
  <g fill="#ff8585" stroke="#0d1117" stroke-width="2">{''.join(nodes)}</g>
  <g class="circuit-signature" fill="none" stroke="#ff4d4d" stroke-opacity="0.4" stroke-width="1.2" stroke-linecap="square">
    <path d="M1062 62H1100V82H1128" />
    <path d="M1062 104H1090V84H1128" />
    <path d="M1108 54V116" />
    <path d="M1078 85H1138" />
    <circle cx="1108" cy="54" r="2" fill="#ff4d4d" />
    <circle cx="1138" cy="85" r="2" fill="#ff4d4d" />
    <circle cx="1108" cy="116" r="2" fill="#ff4d4d" />
  </g>
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
