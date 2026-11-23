#!/usr/bin/env python3
"""Re-run public B checks and preserve command output; no independent oracle claim."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[2]
BUNDLE = ROOT / "extensions/B"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def package_checks():
    problems = []
    required = ["SKILL.md", "agents/openai.yaml", "references/principles.md",
                "references/flow-contract.md", "references/sources.md",
                "examples/application.md", "checks/check_flow.py", "tests/test_flow_check.py"]
    for relative in required:
        if not (BUNDLE / relative).is_file():
            problems.append("Missing: " + relative)
    skill = (BUNDLE / "SKILL.md").read_text()
    frontmatter = skill.split("---", 2)[1] if skill.startswith("---\n") else ""
    if "name: anything-frontend-ux-flow" not in frontmatter or "description:" not in frontmatter:
        problems.append("Skill frontmatter lacks name/description")
    fields = ["Trigger", "Inputs", "Decision Rules", "Procedure", "Output Contract", "Failure Modes", "Verification", "Sources"]
    principles = (BUNDLE / "references/principles.md").read_text()
    sections = re.split(r"(?m)^## B\d\d — ", principles)[1:]
    if len(sections) != 10:
        problems.append("Expected ten principle sections")
    for index, section in enumerate(sections, 1):
        for field in fields:
            if "**" + field + ":**" not in section:
                problems.append(f"B{index:02d} lacks {field}")
    local_links = 0
    for document in sorted(BUNDLE.rglob("*.md")):
        for target in re.findall(r"\[[^\]]*\]\(([^)]+)\)", document.read_text()):
            if "://" in target or target.startswith("mailto:"):
                continue
            filepart, _, anchor = target.partition("#")
            dest = (document.parent / filepart).resolve() if filepart else document
            local_links += 1
            if not dest.is_relative_to(BUNDLE):
                problems.append(f"Non-portable local link: {document.name} -> {target}")
            elif not dest.is_file():
                problems.append(f"Broken local link: {document.name} -> {target}")
            elif anchor and f'id="{anchor}"' not in dest.read_text():
                # Current B documents use explicit source/principle anchors.
                problems.append(f"Missing explicit anchor: {document.name} -> {target}")
    sources = json.loads((ROOT / "evidence/B/research/sources.json").read_text())
    sources_doc = (BUNDLE / "references/sources.md").read_text()
    if "(references/sources.md)" not in skill:
        problems.append("Missing direct source-index route")
    for source in sources:
        if source["url"] not in sources_doc or f'id="{source["id"].lower()}"' not in sources_doc:
            problems.append("Missing two-hop source entry " + source["id"])
    scope = subprocess.run(["git", "diff", "--name-only", "f5df625dbc577d6a3ca28e13ef09e39b135b4a6f"], cwd=ROOT, capture_output=True, text=True)
    if scope.returncode:
        problems.append("Cannot verify Git scope: " + scope.stderr.strip())
    else:
        for relative in scope.stdout.splitlines():
            if not relative.startswith(("extensions/B/", "evidence/B/")):
                problems.append("Out-of-scope change: " + relative)
    return {"ok": not problems, "problems": problems, "principles": len(sections),
            "local_links": local_links, "source_records": len(sources), "distinct_works": 18,
            "limitations": ["Link checks do not refetch remote sources.", "S17/S19 count as one work.", "Git scope checks tracked changes; final handoff additionally inspects untracked/staged paths."]}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", required=True, help="New directory for immutable run logs (must not already exist)")
    args = parser.parse_args()
    out = Path(args.out).resolve()
    out.mkdir(parents=True, exist_ok=False)
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1")
    commands = [
        ("flow-unit", [sys.executable, "-m", "unittest", "discover", "-s", "extensions/B/tests", "-p", "test_*.py", "-v"]),
        ("booking-contract", [sys.executable, "extensions/B/checks/check_flow.py", "extensions/B/tests/fixtures/booking.json", "--json"]),
        ("report-contract", [sys.executable, "extensions/B/checks/check_flow.py", "extensions/B/tests/fixtures/report.json", "--json"]),
        ("api-selftest", ["node", "--test", "--test-reporter=tap", "evidence/B/experiments/shared/api.test.mjs"]),
        ("comparison", ["node", "evidence/B/experiments/evaluate.mjs", str(out / "comparison")]),
    ]
    report = {"schema": "b-validation-run/v1", "recorded_at": datetime.now(timezone.utc).isoformat(),
              "python": sys.version, "cwd": str(ROOT), "commands": [], "package": package_checks(),
              "formal_gate": "HOLD", "independent_blind": False, "browser": "blocked_not_run"}
    for name, command in commands:
        start = datetime.now(timezone.utc).isoformat()
        completed = subprocess.run(command, cwd=ROOT, env=env, text=True, capture_output=True, timeout=180)
        log = out / (name + ".log")
        log.write_text(completed.stdout + completed.stderr)
        report["commands"].append({"name": name, "command": command, "started_at": start,
                                   "returncode": completed.returncode, "log": log.name, "log_sha256": sha(log)})
    (out / "run.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps({"package": report["package"], "commands": [{"name": r["name"], "returncode": r["returncode"]} for r in report["commands"]], "formal_gate": "HOLD"}, ensure_ascii=False, indent=2))
    return int(not report["package"]["ok"] or any(r["returncode"] for r in report["commands"]))


if __name__ == "__main__":
    raise SystemExit(main())
