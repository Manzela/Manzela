#!/usr/bin/env python3
"""Nightly self-maintenance for the profile README (github.com/Manzela).

Regenerates every dynamic surface of README.md from live sources, fail-closed:
on any fetch failure the last committed value is kept, the audit stamp flips to
a visible "stale" marker, and the process exits nonzero so the workflow-failure
email becomes the alert channel. Nothing is ever fabricated or silently
re-stamped.

Outputs (all inside README.md and profile/ — never anywhere else):
  profile/kpi.svg                  hero: KPI numerals in outlined Fraunces italic
  profile/status/{tng,atelier,agdag,agos}.svg   3-state production status dots
  profile/data/status.json         probe state machine (consecutive failures)
  profile/data/gcp-credentials.json  shields.io endpoint payload (credential count)
  README.md marker sections:       stamp, tng_metric, agdag_metric, releases,
                                   writing, certs

Modes:
  (default)   full network run — used by .github/workflows/profile-refresh.yml
  --offline   no network: re-render everything from committed data only
  --check     no network, no writes: validate templates, markers, SVGs and the
              sanitizer contract — used by the PR preview gate

Stdlib only. No PAT: GITHUB_TOKEN (the built-in Actions token) is optional and
only used for the GraphQL releases query.
"""

from __future__ import annotations

import json
import os
import re
import ssl
import sys
import urllib.error
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PROFILE = ROOT / "profile"
README = ROOT / "README.md"

OWNER = "Manzela"
MEDIUM_FEED = "https://medium.com/feed/@manzela"
GCP_PROFILE_URL = (
    "https://partner.skills.google/public_profiles/"
    "69fa3af8-3032-4a04-a818-f7277009c3a9"
)
# Future source of truth: a machine-readable export published by the
# pipeline-observatory site. 404s harmlessly until it ships; the committed
# profile/data/metrics.json seed is used instead.
REMOTE_METRICS_URL = "https://manzela.github.io/pipeline-observatory/data/metrics.json"

# Probe targets for the production-status dots (README section 02).
SYSTEMS = {
    "tng": "https://tngshopper.com",
    "atelier": "https://atelier.autonomous-agent.dev",
    "agdag": "https://manzela.github.io/pipeline-observatory/",
    "agos": "https://pypi.org/pypi/ag-os/json",
}
# Consecutive hard-404 probes before a dot is demoted to "archived".
ARCHIVE_AFTER_404S = 7

USER_AGENT = "Manzela-profile-refresh (github.com/Manzela/Manzela)"

# Markup that must never appear in README.md — GitHub's sanitizer strips these
# silently, which would degrade the page without anyone noticing.
SANITIZER_FORBIDDEN = re.compile(
    r"<script|<style|<center|<iframe|\sstyle\s*=\s*[\"']|\sclass\s*=\s*[\"']",
    re.IGNORECASE,
)
MARKER_SECTIONS = (
    "stamp",
    "kpi_text",
    "tng_metric",
    "agdag_metric",
    "releases",
    "writing",
    "certs",
    "claims",
)

# ---------------------------------------------------------------- utilities


def now_utc() -> datetime:
    return datetime.now(timezone.utc)


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def save_json(path: Path, data) -> None:
    write_if_changed(path, json.dumps(data, indent=2, ensure_ascii=False) + "\n")


def write_if_changed(path: Path, content: str) -> bool:
    """Byte-compare before writing so no-change nights produce zero commits."""
    if path.exists() and path.read_text(encoding="utf-8") == content:
        return False
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    return True


def http_get(url: str, timeout: int = 20, retries: int = 2, headers: dict | None = None):
    """GET with retries. Returns (status_code, body_bytes) or (None, None)."""
    hdrs = {"User-Agent": USER_AGENT}
    if headers:
        hdrs.update(headers)
    last_status = None
    for _ in range(retries + 1):
        req = urllib.request.Request(url, headers=hdrs)
        try:
            with urllib.request.urlopen(
                req, timeout=timeout, context=ssl.create_default_context()
            ) as resp:
                return resp.status, resp.read()
        except urllib.error.HTTPError as exc:
            last_status = exc.code
        except Exception:
            last_status = None
    return last_status, None


def rewrite_section(text: str, name: str, content: str) -> str:
    """Replace the body between <!--START_SECTION:name--> ... <!--END_SECTION:name-->."""
    pattern = re.compile(
        rf"(<!--START_SECTION:{name}-->)(.*?)(<!--END_SECTION:{name}-->)", re.DOTALL
    )
    if not pattern.search(text):
        raise RuntimeError(f"marker pair missing for section '{name}'")
    return pattern.sub(lambda m: m.group(1) + content + m.group(3), text)


# ------------------------------------------------------------------ fetches


def fetch_metrics(offline: bool) -> tuple[dict, bool]:
    """Metrics contract: prefer the observatory export, else the committed seed.

    Returns (metrics, fresh). fresh=False only means the remote export was
    unreachable AND had previously been the source — a seed-sourced file is
    considered fresh by definition (it is the current source of truth).
    """
    seed = load_json(PROFILE / "data" / "metrics.json")
    if offline:
        return seed, True
    status, body = http_get(REMOTE_METRICS_URL)
    if status == 200 and body:
        try:
            remote = json.loads(body)
            if isinstance(remote.get("kpis"), list) and len(remote["kpis"]) >= 4:
                remote["source"] = REMOTE_METRICS_URL
                remote["as_of"] = now_utc().strftime("%Y-%m-%d")
                save_json(PROFILE / "data" / "metrics.json", remote)
                return remote, True
        except (ValueError, KeyError):
            pass  # malformed remote → fall through to committed seed
    if seed.get("source") == "seed":
        return seed, True  # remote endpoint hasn't shipped yet; seed is canonical
    return seed, False  # remote WAS the source and is now unreachable → stale


def probe_systems(offline: bool) -> dict:
    """3-state probe machine: operational / unverified / archived.

    Failures render a neutral hollow dot, never red (Cloud Run cold starts
    cause false alarms). Persistent hard 404s demote to archived so a retired
    endpoint never shows a live dot.
    """
    state_path = PROFILE / "data" / "status.json"
    state = load_json(state_path) if state_path.exists() else {}
    today = now_utc().strftime("%Y-%m-%d")
    for sys_id, url in SYSTEMS.items():
        entry = state.setdefault(
            sys_id, {"state": "unverified", "consecutive_404s": 0, "last_ok": None}
        )
        entry["url"] = url
        entry["last_checked"] = today
        if offline:
            continue
        status, _ = http_get(url, timeout=25, retries=2)
        if status is not None and 200 <= status < 400:
            entry.update(state="operational", consecutive_404s=0, last_ok=today)
        elif status in (404, 410):
            entry["consecutive_404s"] += 1
            if entry["consecutive_404s"] >= ARCHIVE_AFTER_404S:
                entry["state"] = "archived"
            elif entry["state"] == "operational":
                entry["state"] = "unverified"
        else:
            # Timeouts / 5xx / transient: demote operational → unverified only.
            entry["consecutive_404s"] = 0
            if entry["state"] == "operational":
                entry["state"] = "unverified"
    save_json(state_path, state)
    return state


def fetch_releases() -> list[str] | None:
    """Latest releases across all public repos via one GraphQL call."""
    token = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
    if not token:
        return None
    query = """
    query { user(login: "%s") {
      repositories(first: 50, privacy: PUBLIC, isFork: false,
                   orderBy: {field: PUSHED_AT, direction: DESC}) {
        nodes { name url
          releases(first: 1, orderBy: {field: CREATED_AT, direction: DESC}) {
            nodes { name tagName createdAt url isDraft } } } } } }
    """ % OWNER
    status, body = _graphql_post(query, token)
    if status != 200 or not body:
        return None
    try:
        nodes = json.loads(body)["data"]["user"]["repositories"]["nodes"]
    except (ValueError, KeyError, TypeError):
        return None
    releases = []
    for repo in nodes:
        for rel in repo.get("releases", {}).get("nodes", []):
            if rel.get("isDraft"):
                continue
            title = rel.get("name") or rel.get("tagName") or "release"
            month = (rel.get("createdAt") or "")[:7]
            releases.append((rel.get("createdAt") or "", f"- [{repo['name']} — {title}]({rel['url']}) · {month}"))
    releases.sort(reverse=True)
    return [line for _, line in releases[:5]] or None


def _graphql_post(query: str, token: str):
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
        with urllib.request.urlopen(req, timeout=30) as resp:
            return resp.status, resp.read()
    except Exception:
        return None, None


def fetch_writing() -> list[str] | None:
    """Latest essays from the Medium RSS feed."""
    status, body = http_get(MEDIUM_FEED)
    if status != 200 or not body:
        return None
    try:
        root = ET.fromstring(body)
    except ET.ParseError:
        return None
    lines = []
    for item in root.iter("item"):
        title = (item.findtext("title") or "").strip()
        link = (item.findtext("link") or "").split("?")[0].strip()
        pub = (item.findtext("pubDate") or "").strip()
        try:
            month = datetime.strptime(pub[:16], "%a, %d %b %Y").strftime("%b %Y")
        except ValueError:
            month = ""
        if title and link:
            lines.append(f"- [{title}]({link})" + (f" · {month}" if month else ""))
        if len(lines) >= 4:
            break
    return lines or None


def fetch_gcp_credential_count() -> bool:
    """Refresh the shields.io endpoint payload from the public skills profile.

    HTML-fragile by nature: on any doubt the last-known payload is kept
    (the badge freezes conservatively and still links to the ground truth).
    """
    payload_path = PROFILE / "data" / "gcp-credentials.json"
    status, body = http_get(GCP_PROFILE_URL, timeout=25)
    if status != 200 or not body:
        return False
    text = body.decode("utf-8", errors="ignore")
    counts = [int(m) for m in re.findall(r"(\d{1,3})\s+(?:skill\s+badges?|credentials?|badges?)", text, re.I)]
    if not counts:
        return False
    payload = load_json(payload_path)
    payload["message"] = f"{max(counts)} credentials"
    save_json(payload_path, payload)
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
        f".sdim{{stroke:{LIGHT['dim']}}}"
        "@media(prefers-color-scheme:dark){"
        f".ink{{fill:{DARK['ink']}}}.dim{{fill:{DARK['dim']}}}"
        f".acc{{fill:{DARK['acc']}}}.edge{{stroke:{DARK['edge']}}}"
        f".sdim{{stroke:{DARK['dim']}}}"
        "}</style>"
    )


def glyph_run(text: str, glyphs: dict, size: float, x: float, baseline: float, cls: str = "ink") -> tuple[str, float]:
    """Compose a string from pre-outlined glyph paths. Returns (svg, width)."""
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


def render_kpi_svg(metrics: dict, stamp: str, stale_since: str | None) -> str:
    glyphs = load_json(PROFILE / "glyphs" / "fraunces-glyphs.json")
    kpis = metrics["kpis"][:4]
    width, height = 840, 190
    col_w = width / len(kpis)
    # Uniform numeral size across columns, capped, fitted to the widest value.
    size = min(
        58.0,
        min((col_w - 26) / (text_width(k["value"], glyphs, 1.0) or 1) for k in kpis),
    )
    body = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
        f'viewBox="0 0 {width} {height}" role="img" aria-label="Production KPIs">',
        svg_style(),
        # header: pulsing LIVE dot + rubric, right-aligned brand
        '<circle class="acc" cx="28" cy="21" r="4">'
        '<animate attributeName="opacity" values="1;.25;1" dur="2.4s" repeatCount="indefinite"/>'
        "</circle>",
        f'<text x="40" y="25" font-family="{SANS}" font-size="10" letter-spacing="2.5" class="dim">'
        "IN PRODUCTION — AUTONOMOUS CONTENT OPERATIONS</text>",
        f'<text x="{width - 24}" y="25" text-anchor="end" font-family="{SANS}" '
        'font-size="10" letter-spacing="2.5" class="acc">TNG SHOPPER</text>',
        f'<line class="edge" x1="24" y1="38" x2="{width - 24}" y2="38" stroke-width="1"/>',
    ]
    baseline, label_y, sublabel_y = 106.0, 134.0, 150.0
    for i, kpi in enumerate(kpis):
        center = col_w * i + col_w / 2
        w = text_width(kpi["value"], glyphs, size)
        run, _ = glyph_run(kpi["value"], glyphs, size, center - w / 2, baseline)
        body.append(run)
        body.append(
            f'<text x="{center:.0f}" y="{label_y:.0f}" text-anchor="middle" '
            f'font-family="{SANS}" font-size="11.5" class="dim">{kpi["label"]}</text>'
        )
        if kpi.get("sublabel"):
            body.append(
                f'<text x="{center:.0f}" y="{sublabel_y:.0f}" text-anchor="middle" '
                f'font-family="{SANS}" font-size="11.5" class="dim">{kpi["sublabel"]}</text>'
            )
        if i:
            body.append(
                f'<line class="edge" x1="{col_w * i:.0f}" y1="56" x2="{col_w * i:.0f}" '
                'y2="146" stroke-width="1"/>'
            )
    footer = f"LAST SYNC {stamp} · RE-RENDERED NIGHTLY · FIGURES HELD STALE, NEVER INVENTED, ON FETCH FAILURE"
    if stale_since:
        body.append(
            f'<text x="{width / 2:.0f}" y="176" text-anchor="middle" font-family="{MONO}" '
            f'font-size="9.5" class="acc">⚠ METRICS STALE SINCE {stale_since} · {footer}</text>'
        )
    else:
        body.append(
            f'<text x="{width / 2:.0f}" y="176" text-anchor="middle" font-family="{MONO}" '
            f'font-size="9.5" class="dim">{footer}</text>'
        )
    body.append("</svg>")
    return "".join(body) + "\n"


def render_dot_svg(state: str) -> str:
    head = (
        '<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" '
        f'viewBox="0 0 20 20" role="img" aria-label="{state}">{svg_style()}'
    )
    if state == "operational":
        core = (
            '<circle class="acc" cx="10" cy="10" r="5">'
            '<animate attributeName="opacity" values="1;.35;1" dur="2.4s" repeatCount="indefinite"/>'
            "</circle>"
        )
    elif state == "archived":
        core = '<circle class="dim" cx="10" cy="10" r="5"/>'
    else:  # unverified
        core = '<circle fill="none" class="sdim" cx="10" cy="10" r="4.5" stroke-width="1.6"/>'
    return head + core + "</svg>\n"


# -------------------------------------------------------------- validation


def validate(readme_text: str) -> list[str]:
    problems = []
    for name in MARKER_SECTIONS:
        if f"<!--START_SECTION:{name}-->" not in readme_text or f"<!--END_SECTION:{name}-->" not in readme_text:
            problems.append(f"marker pair missing: {name}")
    hit = SANITIZER_FORBIDDEN.search(readme_text)
    if hit:
        problems.append(f"sanitizer-stripped markup in README: {hit.group(0)!r}")
    for svg in [PROFILE / "kpi.svg", *sorted((PROFILE / "status").glob("*.svg"))]:
        if not svg.exists():
            problems.append(f"missing generated asset: {svg.relative_to(ROOT)}")
            continue
        try:
            ET.fromstring(svg.read_text(encoding="utf-8"))
        except ET.ParseError as exc:
            problems.append(f"malformed SVG {svg.name}: {exc}")
    return problems


# --------------------------------------------------------------------- main


def main() -> int:
    check = "--check" in sys.argv
    offline = check or "--offline" in sys.argv
    failures: list[str] = []

    if check:
        # Dry-run: validate committed state + that templates render from seeds.
        metrics = load_json(PROFILE / "data" / "metrics.json")
        render_kpi_svg(metrics, "0000-00-00 00:00 UTC", None)  # raises on template break
        for state in ("operational", "unverified", "archived"):
            ET.fromstring(render_dot_svg(state))
        problems = validate(README.read_text(encoding="utf-8"))
        for p in problems:
            print(f"::error::{p}")
        print("check:", "FAILED" if problems else "ok")
        return 2 if problems else 0

    stamp = now_utc().strftime("%Y-%m-%d %H:%M UTC")
    today = now_utc().strftime("%Y-%m-%d")

    metrics, metrics_fresh = fetch_metrics(offline)
    if not metrics_fresh:
        failures.append("metrics export unreachable — keeping last committed figures")
    stale_since = None if metrics_fresh else metrics.get("as_of", today)

    status = probe_systems(offline)

    releases = writing = None
    if not offline:
        releases = fetch_releases()
        if releases is None:
            failures.append("releases (GitHub GraphQL) fetch failed — keeping last list")
        writing = fetch_writing()
        if writing is None:
            failures.append("writing (Medium RSS) fetch failed — keeping last list")
        if not fetch_gcp_credential_count():
            # Known-fragile, best-effort scrape (the page is JS-rendered more
            # often than not). The badge freezes at its conservative last-known
            # value and links to the ground-truth profile, so this warns
            # without failing the nightly run.
            print("::warning::gcp credential count scrape failed — keeping last-known badge")

    # ---- render assets
    write_if_changed(PROFILE / "kpi.svg", render_kpi_svg(metrics, stamp, stale_since))
    for sys_id in SYSTEMS:
        write_if_changed(
            PROFILE / "status" / f"{sys_id}.svg",
            render_dot_svg(status[sys_id]["state"]),
        )

    # ---- rewrite README marker sections
    certs = load_json(PROFILE / "data" / "certs.json")
    cert_bits = []
    for c in certs["certs"]:
        when = f" ({datetime.strptime(c['issued'], '%Y-%m').strftime('%b %Y')})" if c.get("issued") else " (active)"
        cert_bits.append(f"{c['issuer']} **{c['name']}**{when}")
    certs_line = (
        " · ".join(cert_bits)
        + " · **32** Google Cloud credentials"
        + "".join(f" · {r}" for r in certs.get("recognition", []))
    )

    kpi_text = " · ".join(
        f"**{k['value']}** {k['label']}" + (f" {k['sublabel']}" if k.get("sublabel") else "")
        for k in metrics["kpis"][:4]
    )

    text = README.read_text(encoding="utf-8")
    stamp_note = f"⚠ stale since {stale_since}" if stale_since else today
    text = rewrite_section(text, "stamp", stamp_note)
    text = rewrite_section(text, "kpi_text", kpi_text)
    text = rewrite_section(text, "tng_metric", metrics.get("tng_metric", ""))
    text = rewrite_section(text, "agdag_metric", metrics.get("agdag_metric", ""))
    text = rewrite_section(text, "certs", "\n" + certs_line + "\n")
    if releases:
        text = rewrite_section(text, "releases", "\n" + "\n".join(releases) + "\n")
    if writing:
        text = rewrite_section(text, "writing", "\n" + "\n".join(writing) + "\n")

    problems = validate(text)
    if problems:
        for p in problems:
            print(f"::error::{p}")
        return 2  # never commit an invalid README

    write_if_changed(README, text)

    for f in failures:
        print(f"::warning::{f}")
    print("refresh:", "degraded (stale values held)" if failures else "ok")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
