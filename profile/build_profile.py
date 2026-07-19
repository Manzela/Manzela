#!/usr/bin/env python3
"""Nightly self-maintenance for the profile README (github.com/Manzela).

Renders three charts from Daniel's real GitHub data — no third-party stat
cards — and rewrites the marker sections in README.md, fail-closed: on any
fetch failure the last committed data is kept, the render stamp flips to a
visible "stale" marker, and the process exits nonzero so the workflow-failure
email becomes the alert channel. Nothing is ever fabricated.

Outputs (all inside README.md and profile/ — never anywhere else):
  profile/activity.svg    weekly contribution totals, trailing 12 months
  profile/languages.svg   language composition across public repos, by bytes
  profile/rhythm.svg      own commits by day x hour, author-local time
  profile/data/{contributions,languages,rhythm}.json   committed data caches
  README.md marker sections: stamp   (claims is owned by verify_claims.py)

Modes:
  (default)   full network run — used by .github/workflows/profile-refresh.yml
  --offline   no network: re-render everything from committed data only
  --check     no network, no writes: validate markers, renders, glyph
              coverage and the sanitizer contract — the PR-gate mode

Stdlib only. GraphQL uses the built-in Actions GITHUB_TOKEN and always
queries user(login: OWNER), never viewer — GITHUB_TOKEN is an installation
token and viewer would silently return the wrong identity.
"""

from __future__ import annotations

import json
import math
import os
import re
import sys
import urllib.request
import xml.etree.ElementTree as ET
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PROFILE = ROOT / "profile"
README = ROOT / "README.md"

OWNER = "Manzela"
# The profile repo itself is excluded from the language aggregation: it
# carries the GitHub Pages portfolio (~73KB of hand-written HTML) which would
# skew the chart. The exclusion is declared in the chart footer.
LANG_EXCLUDE_REPOS = {"Manzela"}
LANG_EXCLUDE_LANGS = {"YAML", "Markdown", "Jupyter Notebook"}
RHYTHM_WINDOW_DAYS = 365
USER_AGENT = "Manzela-profile-refresh (github.com/Manzela/Manzela)"

MARKER_SECTIONS = ("stamp", "claims")
SVG_OUTPUTS = ("activity.svg", "languages.svg", "rhythm.svg")

SANITIZER_FORBIDDEN = re.compile(
    r"<script|<style|<center|<iframe|\sstyle\s*=\s*[\"']|\sclass\s*=\s*[\"']",
    re.IGNORECASE,
)

# ---------------------------------------------------------------- utilities


def now_utc() -> datetime:
    return datetime.now(timezone.utc)


def load_json(path: Path, default=None):
    if not path.exists():
        return default
    return json.loads(path.read_text(encoding="utf-8"))


def save_json(path: Path, data) -> None:
    write_if_changed(path, json.dumps(data, ensure_ascii=False) + "\n")


def write_if_changed(path: Path, content: str) -> bool:
    """Byte-compare before writing so no-change nights produce zero commits."""
    if path.exists() and path.read_text(encoding="utf-8") == content:
        return False
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    return True


def graphql(query: str) -> dict | None:
    token = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
    if not token:
        return None
    req = urllib.request.Request(
        "https://api.github.com/graphql",
        data=json.dumps({"query": query}).encode(),
        headers={
            "Authorization": f"bearer {token}",
            "Content-Type": "application/json",
            "User-Agent": USER_AGENT,
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=45) as resp:
            payload = json.loads(resp.read())
    except Exception:
        return None
    return payload.get("data")


def rewrite_section(text: str, name: str, content: str) -> str:
    pattern = re.compile(
        rf"(<!--START_SECTION:{name}-->)(.*?)(<!--END_SECTION:{name}-->)", re.DOTALL
    )
    if not pattern.search(text):
        raise RuntimeError(f"marker pair missing for section '{name}'")
    return pattern.sub(lambda m: m.group(1) + content + m.group(3), text)


# ------------------------------------------------------------------ fetches


def fetch_contributions() -> bool:
    """Daily contribution calendar (public contributions), trailing year."""
    data = graphql(
        'query { user(login: "%s") { contributionsCollection {'
        " contributionCalendar { totalContributions"
        " weeks { contributionDays { date contributionCount } } } } } }" % OWNER
    )
    try:
        cal = data["user"]["contributionsCollection"]["contributionCalendar"]
        days = [
            {"date": d["date"], "count": d["contributionCount"]}
            for w in cal["weeks"]
            for d in w["contributionDays"]
        ]
        if not days:
            return False
    except (KeyError, TypeError):
        return False
    save_json(
        PROFILE / "data" / "contributions.json",
        {
            "as_of": now_utc().strftime("%Y-%m-%d"),
            "source": "github-graphql contributionsCollection (public contributions)",
            "total": cal["totalContributions"],
            "days": days,
        },
    )
    return True


def _public_repo_names(lang_data: dict | None) -> list[str]:
    if lang_data and lang_data.get("repos"):
        return lang_data["repos"]
    return []


def fetch_languages() -> bool:
    """Linguist byte counts aggregated across public, non-fork, owned repos."""
    agg: dict[str, int] = {}
    repos: list[str] = []
    cursor = "null"
    for _ in range(5):  # cursor loop; 100/page covers everything today
        data = graphql(
            'query { user(login: "%s") { repositories(first: 100, privacy: PUBLIC,'
            " isFork: false, ownerAffiliations: [OWNER], after: %s) {"
            " pageInfo { hasNextPage endCursor }"
            " nodes { name languages(first: 10, orderBy: {field: SIZE, direction: DESC})"
            " { edges { size node { name } } } } } } }" % (OWNER, cursor)
        )
        try:
            conn = data["user"]["repositories"]
        except (KeyError, TypeError):
            return False
        for node in conn["nodes"]:
            repos.append(node["name"])
            if node["name"] in LANG_EXCLUDE_REPOS:
                continue
            for edge in node.get("languages", {}).get("edges", []):
                lang = edge["node"]["name"]
                if lang in LANG_EXCLUDE_LANGS:
                    continue
                agg[lang] = agg.get(lang, 0) + edge["size"]
        if not conn["pageInfo"]["hasNextPage"]:
            break
        cursor = json.dumps(conn["pageInfo"]["endCursor"])
    if not agg:
        return False
    langs = sorted(
        ({"lang": k, "bytes": v} for k, v in agg.items()),
        key=lambda x: -x["bytes"],
    )
    save_json(
        PROFILE / "data" / "languages.json",
        {
            "as_of": now_utc().strftime("%Y-%m-%d"),
            "source": "github-graphql linguist bytes, public non-fork owned repos",
            "repos": repos,
            "langs": langs,
        },
    )
    return True


def fetch_rhythm() -> bool:
    """Own commits bucketed day-of-week x hour in author-local time.

    authoredDate is a GitTimestamp (offset-preserving), so the printed wall
    time IS author-local — no timezone conversion, no DST smearing.
    """
    data = graphql('query { user(login: "%s") { id } }' % OWNER)
    try:
        node_id = data["user"]["id"]
    except (KeyError, TypeError):
        return False
    repos = _public_repo_names(load_json(PROFILE / "data" / "languages.json"))
    if not repos:
        return False
    since = (now_utc() - timedelta(days=RHYTHM_WINDOW_DAYS)).strftime("%Y-%m-%dT%H:%M:%SZ")
    grid = [[0] * 24 for _ in range(7)]  # Mon..Sun x 0..23

    def ingest(nodes) -> None:
        for n in nodes:
            # e.g. 2026-07-15T14:23:11+03:00 — parse the wall-clock portion
            dt = datetime.fromisoformat(n["authoredDate"])
            grid[dt.isoweekday() - 1][dt.hour] += 1

    for i in range(0, len(repos), 10):
        chunk = repos[i : i + 10]
        aliases = " ".join(
            f'r{j}: repository(owner: "{OWNER}", name: "{name}") {{'
            f" defaultBranchRef {{ target {{ ... on Commit {{"
            f' history(since: "{since}", author: {{id: "{node_id}"}}, first: 100) {{'
            f" pageInfo {{ hasNextPage endCursor }} nodes {{ authoredDate }} }} }} }} }} }}"
            for j, name in enumerate(chunk)
        )
        data = graphql("query { " + aliases + " }")
        if data is None:
            return False
        for j, name in enumerate(chunk):
            ref = (data.get(f"r{j}") or {}).get("defaultBranchRef")
            if not ref:
                continue
            history = ref["target"]["history"]
            ingest(history["nodes"])
            # per-repo pagination for history beyond the first page
            cursor = history["pageInfo"]["endCursor"]
            more = history["pageInfo"]["hasNextPage"]
            pages = 0
            while more and pages < 9:
                page = graphql(
                    f'query {{ repository(owner: "{OWNER}", name: "{name}") {{'
                    f" defaultBranchRef {{ target {{ ... on Commit {{"
                    f' history(since: "{since}", author: {{id: "{node_id}"}},'
                    f' first: 100, after: "{cursor}") {{'
                    f" pageInfo {{ hasNextPage endCursor }} nodes {{ authoredDate }} }} }} }} }} }} }}"
                )
                try:
                    history = page["repository"]["defaultBranchRef"]["target"]["history"]
                except (KeyError, TypeError):
                    return False
                ingest(history["nodes"])
                cursor = history["pageInfo"]["endCursor"]
                more = history["pageInfo"]["hasNextPage"]
                pages += 1
    if not any(any(row) for row in grid):
        return False
    save_json(
        PROFILE / "data" / "rhythm.json",
        {
            "as_of": now_utc().strftime("%Y-%m-%d"),
            "source": "github-graphql commit history, author-filtered, author-local time",
            "window_days": RHYTHM_WINDOW_DAYS,
            "grid": grid,
        },
    )
    return True


# ------------------------------------------------------------ SVG rendering

LIGHT = {"ink": "#1a1512", "dim": "#6b6257", "acc": "#b8512a", "edge": "#ddd2bd"}
DARK = {"ink": "#ece6da", "dim": "#9a917f", "acc": "#d96730", "edge": "#453f33"}
SANS = "-apple-system,'Segoe UI',Helvetica,Arial,sans-serif"
MONO = "ui-monospace,'SF Mono',Menlo,Consolas,monospace"


def svg_style() -> str:
    return (
        "<style>"
        f".ink{{fill:{LIGHT['ink']}}}.dim{{fill:{LIGHT['dim']}}}"
        f".acc{{fill:{LIGHT['acc']}}}.edge{{stroke:{LIGHT['edge']}}}"
        f".sdim{{stroke:{LIGHT['dim']}}}.sacc{{stroke:{LIGHT['acc']}}}"
        "@media(prefers-color-scheme:dark){"
        f".ink{{fill:{DARK['ink']}}}.dim{{fill:{DARK['dim']}}}"
        f".acc{{fill:{DARK['acc']}}}.edge{{stroke:{DARK['edge']}}}"
        f".sdim{{stroke:{DARK['dim']}}}.sacc{{stroke:{DARK['acc']}}}"
        "}</style>"
    )


def glyph_run(text: str, glyphs: dict, size: float, x: float, baseline: float, cls: str = "ink") -> tuple[str, float]:
    upem = glyphs["unitsPerEm"]
    scale = size / upem
    parts, cursor = [], x
    for ch in text:
        g = glyphs["glyphs"].get(ch)
        if g is None:
            raise RuntimeError(f"glyph missing for character {ch!r}")
        parts.append(
            f'<path class="{cls}" transform="translate({cursor:.1f},{baseline:.1f}) '
            f'scale({scale:.6f},-{scale:.6f})" d="{g["d"]}"/>'
        )
        cursor += g["adv"] * scale
    return "".join(parts), cursor - x


def text_width(text: str, glyphs: dict, size: float) -> float:
    upem = glyphs["unitsPerEm"]
    return sum(glyphs["glyphs"][ch]["adv"] for ch in text) * size / upem


def _glyphs() -> dict:
    return load_json(PROFILE / "glyphs" / "fraunces-glyphs.json")


def header(width: int, title: str) -> str:
    return (
        f'<text x="24" y="25" font-family="{SANS}" font-size="10" '
        f'letter-spacing="2.5" class="dim">{title}</text>'
        f'<line class="edge" x1="24" y1="38" x2="{width - 24}" y2="38" stroke-width="1"/>'
    )


def render_activity_svg(contrib: dict, stale_since: str | None) -> str:
    glyphs = _glyphs()
    width, height = 840, 200
    days = contrib["days"]
    # aggregate into weeks starting Monday
    weekly: dict[str, int] = {}
    for d in days:
        day = date.fromisoformat(d["date"])
        wk = (day - timedelta(days=day.isoweekday() - 1)).isoformat()
        weekly[wk] = weekly.get(wk, 0) + d["count"]
    weeks = sorted(weekly)[-52:]
    values = [weekly[w] for w in weeks]
    total = contrib.get("total", sum(values))

    x0, x1, y0, y1 = 24, 816, 58, 158
    peak = max(values) or 1
    step = (x1 - x0) / max(len(values) - 1, 1)

    def yfor(v: int) -> float:  # sqrt scale keeps burst weeks from flattening the rest
        return y1 - (math.sqrt(v) / math.sqrt(peak)) * (y1 - y0)

    pts = [(x0 + i * step, yfor(v)) for i, v in enumerate(values)]
    line = "M" + " L".join(f"{x:.1f},{y:.1f}" for x, y in pts)
    area = f"M{x0},{y1} L" + " L".join(f"{x:.1f},{y:.1f}" for x, y in pts) + f" L{x1:.1f},{y1} Z"
    zero_dots = "".join(
        f'<circle class="dim" fill-opacity=".35" cx="{x0 + i * step:.1f}" cy="{y1}" r="1.4"/>'
        for i, v in enumerate(values)
        if v == 0
    )
    month_ticks = []
    for i, w in enumerate(weeks):
        d = date.fromisoformat(w)
        if d.day <= 7:  # first week of a month
            month_ticks.append(
                f'<text x="{x0 + i * step:.0f}" y="176" font-family="{SANS}" '
                f'font-size="9" class="dim">{d.strftime("%b").upper()}</text>'
            )
    total_str = f"{total:,}"
    tw = text_width(total_str, glyphs, 40)
    total_run, _ = glyph_run(total_str, glyphs, 40, width - 24 - tw, 30)
    stale = (
        f'<text x="{width / 2:.0f}" y="196" text-anchor="middle" font-family="{MONO}" '
        f'font-size="9" class="acc">⚠ DATA STALE SINCE {stale_since}</text>'
        if stale_since
        else ""
    )
    label = "CONTRIBUTIONS — TRAILING 12 MONTHS · PUBLIC ONLY"
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
        f'viewBox="0 0 {width} {height}" role="img" '
        f'aria-label="{total} public contributions in the trailing twelve months">'
        + svg_style()
        + header(width, label)
        + total_run
        + f'<path class="acc" fill-opacity=".10" d="{area}"/>'
        + f'<path fill="none" class="sacc" stroke-width="1.8" stroke-linejoin="round" d="{line}"/>'
        + f'<line class="edge" x1="{x0}" y1="{y1}" x2="{x1}" y2="{y1}" stroke-width="1"/>'
        + zero_dots
        + "".join(month_ticks)
        + stale
        + "</svg>\n"
    )


def render_languages_svg(langdata: dict, stale_since: str | None) -> str:
    width = 840
    langs = [l for l in langdata["langs"] if l["lang"] not in LANG_EXCLUDE_LANGS]
    top = langs[:5]
    other = sum(l["bytes"] for l in langs[5:])
    rows = [(l["lang"], l["bytes"]) for l in top] + ([("Other", other)] if other else [])
    total = sum(b for _, b in rows) or 1
    height = 58 + len(rows) * 26 + 30
    opacities = [1.0, 0.80, 0.62, 0.46, 0.32, 0.20]
    widest = rows[0][1] or 1
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
        f'viewBox="0 0 {width} {height}" role="img" aria-label="Language composition by bytes: '
        + ", ".join(f"{n} {b * 100 / total:.1f} percent" for n, b in rows)
        + '">',
        svg_style(),
        header(width, "LANGUAGES — PUBLIC REPOSITORIES · BY BYTES OF CODE"),
    ]
    y = 58
    max_bar = 560.0
    for i, (name, b) in enumerate(rows):
        bar = max((b / widest) * max_bar, 3.0)
        pct = f"{b * 100 / total:.1f}%"
        parts.append(
            f'<text x="140" y="{y + 9:.0f}" text-anchor="end" font-family="{SANS}" '
            f'font-size="11.5" class="ink">{name}</text>'
        )
        # square at the baseline end, rounded only at the data end
        r = 4
        parts.append(
            f'<path class="acc" fill-opacity="{opacities[i]}" '
            f'd="M150,{y} h{bar - r:.1f} a{r},{r} 0 0 1 {r},{r} v{10 - 2 * r} '
            f'a{r},{r} 0 0 1 -{r},{r} h-{bar - r:.1f} Z"/>'
        )
        # sans, not Fraunces: the italic flat-top '3' misreads as '5' at this size
        parts.append(
            f'<text x="{150 + bar + 12:.1f}" y="{y + 9:.0f}" font-family="{SANS}" '
            f'font-size="11.5" class="ink">{pct}</text>'
        )
        y += 26
    footer = "LINGUIST BYTES · EXCL. THIS PROFILE REPO (HAND-WRITTEN PORTFOLIO HTML)"
    if stale_since:
        footer = f"⚠ DATA STALE SINCE {stale_since} · " + footer
    parts.append(
        f'<text x="24" y="{height - 10}" font-family="{MONO}" font-size="9" '
        f'class="{"acc" if stale_since else "dim"}">{footer}</text>'
    )
    parts.append("</svg>")
    return "".join(parts) + "\n"


def render_rhythm_svg(rhythm: dict, stale_since: str | None) -> str:
    width, height = 840, 220
    grid = rhythm["grid"]
    values = sorted(v for row in grid for v in row if v > 0)
    def opacity(v: int) -> float:
        if v == 0:
            return 0.06
        idx = min(4, int(5 * values.index(v) / len(values))) if values else 0
        return [0.20, 0.40, 0.62, 0.82, 1.0][idx]
    cell_w, cell_h, pitch_x, pitch_y = 24, 14, 27, 18
    gx, gy = 88, 56
    days = ["MON", "TUE", "WED", "THU", "FRI", "SAT", "SUN"]
    total = sum(sum(row) for row in grid)
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
        f'viewBox="0 0 {width} {height}" role="img" '
        f'aria-label="Work rhythm: {total} commits bucketed by day of week and hour of day in author-local time">',
        svg_style(),
        header(width, "WORK RHYTHM — MY COMMITS BY DAY × HOUR · AUTHOR-LOCAL TIME"),
    ]
    for r, row in enumerate(grid):
        parts.append(
            f'<text x="{gx - 12}" y="{gy + r * pitch_y + cell_h - 3}" text-anchor="end" '
            f'font-family="{SANS}" font-size="9" class="dim">{days[r]}</text>'
        )
        for c, v in enumerate(row):
            parts.append(
                f'<rect class="acc" fill-opacity="{opacity(v):.2f}" x="{gx + c * pitch_x}" '
                f'y="{gy + r * pitch_y}" width="{cell_w}" height="{cell_h}" rx="3"/>'
            )
    for h in (0, 6, 12, 18):
        parts.append(
            f'<text x="{gx + h * pitch_x}" y="{gy + 7 * pitch_y + 12}" '
            f'font-family="{SANS}" font-size="9" class="dim">{h:02d}</text>'
        )
    footer = f"TRAILING {rhythm.get('window_days', 365)} DAYS · AUTHORED COMMITS ONLY · DEFAULT BRANCHES"
    if stale_since:
        footer = f"⚠ DATA STALE SINCE {stale_since} · " + footer
    parts.append(
        f'<text x="{width - 24}" y="{height - 8}" text-anchor="end" font-family="{MONO}" '
        f'font-size="9" class="{"acc" if stale_since else "dim"}">{footer}</text>'
    )
    parts.append("</svg>")
    return "".join(parts) + "\n"


# -------------------------------------------------------------- validation


def validate(readme_text: str) -> list[str]:
    problems = []
    found = set(re.findall(r"<!--START_SECTION:([a-z_]+)-->", readme_text))
    if found != set(MARKER_SECTIONS):
        problems.append(f"marker sections mismatch: found {sorted(found)}, expected {sorted(MARKER_SECTIONS)}")
    for name in MARKER_SECTIONS:
        if f"<!--END_SECTION:{name}-->" not in readme_text:
            problems.append(f"end marker missing: {name}")
    hit = SANITIZER_FORBIDDEN.search(readme_text)
    if hit:
        problems.append(f"sanitizer-stripped markup in README: {hit.group(0)!r}")
    for svg in SVG_OUTPUTS:
        path = PROFILE / svg
        if not path.exists():
            problems.append(f"missing generated asset: profile/{svg}")
            continue
        try:
            ET.fromstring(path.read_text(encoding="utf-8"))
        except ET.ParseError as exc:
            problems.append(f"malformed SVG {svg}: {exc}")
    return problems


def render_all(stale: dict[str, str | None]) -> None:
    contrib = load_json(PROFILE / "data" / "contributions.json")
    langs = load_json(PROFILE / "data" / "languages.json")
    rhythm = load_json(PROFILE / "data" / "rhythm.json")
    write_if_changed(PROFILE / "activity.svg", render_activity_svg(contrib, stale.get("contributions")))
    write_if_changed(PROFILE / "languages.svg", render_languages_svg(langs, stale.get("languages")))
    write_if_changed(PROFILE / "rhythm.svg", render_rhythm_svg(rhythm, stale.get("rhythm")))


# --------------------------------------------------------------------- main


def main() -> int:
    check = "--check" in sys.argv
    offline = check or "--offline" in sys.argv

    if check:
        # Dry-run: prove the committed data renders (glyph coverage included —
        # a missing Fraunces character must fail the PR gate, not the nightly)
        for svg_text in (
            render_activity_svg(load_json(PROFILE / "data" / "contributions.json"), None),
            render_languages_svg(load_json(PROFILE / "data" / "languages.json"), None),
            render_rhythm_svg(load_json(PROFILE / "data" / "rhythm.json"), None),
        ):
            ET.fromstring(svg_text)
        problems = validate(README.read_text(encoding="utf-8"))
        for p in problems:
            print(f"::error::{p}")
        print("check:", "FAILED" if problems else "ok")
        return 2 if problems else 0

    today = now_utc().strftime("%Y-%m-%d")
    failures: list[str] = []
    stale: dict[str, str | None] = {}
    if not offline:
        for name, fetch in (
            ("contributions", fetch_contributions),
            ("languages", fetch_languages),
            ("rhythm", fetch_rhythm),
        ):
            if not fetch():
                cached = load_json(PROFILE / "data" / f"{name}.json") or {}
                stale[name] = cached.get("as_of", today)
                failures.append(f"{name} fetch failed — keeping committed data")

    render_all(stale)

    text = README.read_text(encoding="utf-8")
    stamp = f"⚠ degraded — see chart footers · {today}" if failures else today
    text = rewrite_section(text, "stamp", stamp)

    problems = validate(text)
    if problems:
        for p in problems:
            print(f"::error::{p}")
        return 2  # never commit an invalid README
    write_if_changed(README, text)

    for f in failures:
        print(f"::warning::{f}")
    print("refresh:", "degraded (stale data held)" if failures else "ok")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
