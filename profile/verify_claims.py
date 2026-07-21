#!/usr/bin/env python3
"""Weekly claims ledger for the profile README (github.com/Manzela).

Re-derives every load-bearing figure on the profile from a fresh shallow clone
of its source repo, then rewrites the "Auditor's notes" table between the
<!--START_SECTION:claims--> markers and persists profile/data/claims.json.

Fail-closed contract, per claim: a claim that cannot be re-derived keeps its
last verified value and is rendered with a visible "⚠ stale since <date>"
marker — never re-stamped fresh, never invented. If any claim failed, the
process exits nonzero (after writing everything that succeeded) so the
workflow-failure email fires.

Derivation specs live in profile/data/sources.json. Stdlib + git only.
"""

from __future__ import annotations

import json
import re
import subprocess
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PROFILE = ROOT / "profile"
README = ROOT / "README.md"


def today() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d")


def load_json(path: Path, default=None):
    if not path.exists():
        return default
    return json.loads(path.read_text(encoding="utf-8"))


def clone(owner: str, repo: str, dest: Path) -> Path | None:
    target = dest / repo
    result = subprocess.run(
        ["git", "clone", "--quiet", "--depth", "1",
         f"https://github.com/{owner}/{repo}.git", str(target)],
        capture_output=True, timeout=300,
    )
    return target if result.returncode == 0 else None


# ------------------------------------------------------------- derivations
# Each returns (value, derived_by) or raises.

TEST_RE = re.compile(r"^\s*(async\s+)?def test_", re.MULTILINE)


def derive_file_lines(repo_dir: Path, claim: dict):
    path = repo_dir / claim["path"]
    n = len(path.read_text(encoding="utf-8", errors="ignore").splitlines())
    if n == 0:
        raise RuntimeError(f"{claim['path']} is empty or missing")
    return f"{n:,}", f"`wc -l` on `{Path(claim['path']).name}`, fresh clone"


def derive_test_count(repo_dir: Path):
    total, files = 0, 0
    for py in repo_dir.rglob("*.py"):
        if ".git" in py.parts:
            continue
        hits = len(TEST_RE.findall(py.read_text(encoding="utf-8", errors="ignore")))
        if hits:
            total += hits
            files += 1
    if total == 0:
        raise RuntimeError("no test functions found")
    return f"{total:,} in {files} files", "`grep -rcE '^\\s*(async )?def test_' --include='*.py'` on fresh clone"


def derive_orav_thresholds(repo_dir: Path):
    config = (repo_dir / "agent_dag" / "config.py").read_text(encoding="utf-8")
    values = {}
    for dim in ("originality", "relevance", "accuracy", "value"):
        m = re.search(rf"^\s*{dim}:\s*float\s*=\s*Field\(default=([0-9.]+)", config, re.MULTILINE)
        if not m:
            raise RuntimeError(f"threshold for {dim} not found")
        values[dim] = m.group(1)
    joined = " / ".join(values[d] for d in ("originality", "relevance", "accuracy", "value"))
    return joined, "constants in `agent_dag/config.py`, fresh clone"


def derive_rule_count(repo_dir: Path):
    rules = sorted((repo_dir / "templates" / "rules").glob("*.md"))
    if not rules:
        raise RuntimeError("no rule files found")
    return str(len(rules)), "count of `templates/rules/*.md` on fresh clone"


def derive_runbook_sections(repo_dir: Path):
    runbook = (repo_dir / "docs" / "FORENSIC_RUNBOOK.md").read_text(encoding="utf-8")
    count = len(re.findall(r"^### \d+\.\d+ ", runbook, re.MULTILINE))
    if count == 0:
        raise RuntimeError("no numbered failure-mode sections found")
    return str(count), "numbered `###` sections in `docs/FORENSIC_RUNBOOK.md`, fresh clone"


DERIVATIONS = {
    "test_count": derive_test_count,
    "orav_thresholds": derive_orav_thresholds,
    "rule_count": derive_rule_count,
    "runbook_sections": derive_runbook_sections,
    "file_lines": derive_file_lines,
}


# --------------------------------------------------------------------- main


def main() -> int:
    spec = load_json(PROFILE / "data" / "sources.json")
    previous = {c["id"]: c for c in load_json(PROFILE / "data" / "claims.json", {"claims": []})["claims"]}
    owner = spec["owner"]

    clones: dict[str, Path | None] = {}
    rows, failed = [], []
    with tempfile.TemporaryDirectory() as tmp:
        tmpdir = Path(tmp)
        for claim in spec["claims"]:
            repo = claim["repo"]
            if repo not in clones:
                clones[repo] = clone(owner, repo, tmpdir)
            repo_dir = clones[repo]
            entry = {
                "id": claim["id"],
                "label": claim["label"],
                "repo": f"{owner}/{repo}",
            }
            try:
                if repo_dir is None:
                    raise RuntimeError(f"clone of {repo} failed")
                fn = DERIVATIONS[claim["kind"]]
                value, derived_by = fn(repo_dir, claim) if claim["kind"] == "file_lines" else fn(repo_dir)
                entry.update(value=value, derived_by=derived_by, verified_at=today(), stale=False)
            except Exception as exc:
                prev = previous.get(claim["id"])
                if prev:
                    entry.update(
                        value=prev["value"],
                        derived_by=prev["derived_by"],
                        verified_at=prev["verified_at"],
                        stale=True,
                    )
                else:
                    entry.update(value="—", derived_by="(never derived)", verified_at="—", stale=True)
                failed.append(f"{claim['id']}: {exc}")
            rows.append(entry)

    payload = json.dumps({"claims": rows}, indent=2, ensure_ascii=False) + "\n"
    (PROFILE / "data" / "claims.json").write_text(payload, encoding="utf-8")

    lines = ["", "| Claim | Value | Derived by | Verified |", "|---|---:|---|---|"]
    esc = lambda s: str(s).replace("|", "\\|")  # a raw pipe would break the table
    for r in rows:
        repo_link = f"[{r['repo'].split('/')[1]}](https://github.com/{r['repo']})"
        verified = f"⚠ stale since {r['verified_at']}" if r["stale"] else r["verified_at"]
        lines.append(
            f"| {esc(r['label'])} ({repo_link}) | {esc(r['value'])} | {esc(r['derived_by'])} | {verified} |"
        )
    table = "\n".join(lines) + "\n"

    text = README.read_text(encoding="utf-8")
    pattern = re.compile(r"(<!--START_SECTION:claims-->)(.*?)(<!--END_SECTION:claims-->)", re.DOTALL)
    if not pattern.search(text):
        print("::error::claims marker pair missing in README.md")
        return 2
    new_text = pattern.sub(lambda m: m.group(1) + table + m.group(3), text)
    if new_text != text:
        README.write_text(new_text, encoding="utf-8")

    for f in failed:
        print(f"::warning::claim held stale — {f}")
    print("claims:", f"{len(rows) - len(failed)}/{len(rows)} re-derived")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
