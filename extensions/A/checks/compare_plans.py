#!/usr/bin/env python3
"""Reproduce structural checks for frozen paired plans; no model or UX scoring.

Exit 0 means the report was written, not that the designs passed promotion.
Use the per-arm status and issues. This script never rewrites input plans.
"""
import argparse
from collections import Counter, deque
import hashlib
import json
from pathlib import Path

from validate_plan import validate


def read_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


def shortest_declared_path(plan, route, role):
    screens = {s["id"]: s for s in plan.get("screens", [])}
    start, target = route["start_screen"], route["target_screen"]
    if start not in screens or role not in screens[start].get("roles", []):
        return None
    pending, seen = deque([(start, 0)]), {start}
    while pending:
        current, distance = pending.popleft()
        if current == target:
            return distance
        for edge in plan.get("navigation", []):
            dest = edge.get("to")
            if (edge.get("from") == current and role in edge.get("roles", [])
                    and dest in screens and role in screens[dest].get("roles", [])
                    and dest not in seen):
                seen.add(dest)
                pending.append((dest, distance + 1))
    return None


def inspect(brief, path):
    plan = read_json(path)
    result = validate(brief, plan)
    goals = {g["id"]: g for g in brief["goals"]}
    return {
        "input": str(path),
        "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
        "validation": result,
        "error_count": sum(i["severity"] == "error" for i in result["issues"]),
        "hold_count": sum(i["severity"] == "hold" for i in result["issues"]),
        "issues_by_category": dict(Counter(i["category"] for i in result["issues"])),
        "dispositions": dict(Counter(f["disposition"] for f in plan["features"])),
        "feature_decisions": {f["id"]: {"disposition": f["disposition"], "target": f["target"]} for f in plan["features"]},
        "declared_navigation_distance": {
            r["goal_id"]: shortest_declared_path(plan, r, goals[r["goal_id"]]["role"])
            for r in plan.get("goal_routes", []) if r["goal_id"] in goals
        },
        "limitations": [
            "Distances count declared navigation edges, not complete user actions or measured task completion.",
            "Fewer screens, links, holds, or features is not defined as better.",
            "A report cannot establish semantic correctness, user benefit, independent evaluation, or promotion."
        ]
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--briefs-dir", type=Path, required=True)
    parser.add_argument("--baseline-dir", type=Path, required=True)
    parser.add_argument("--candidate-dir", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    cases = []
    for brief_path in sorted(args.briefs_dir.glob("*.json")):
        brief = read_json(brief_path)
        case = {"case_id": brief["case_id"], "brief_sha256": hashlib.sha256(brief_path.read_bytes()).hexdigest()}
        for arm, folder in [("baseline", args.baseline_dir), ("candidate", args.candidate_dir)]:
            case[arm] = inspect(brief, folder / (brief_path.stem + ".plan.json"))
        case["candidate_minus_baseline_error_count"] = case["candidate"]["error_count"] - case["baseline"]["error_count"]
        case["feature_decisions_identical"] = case["candidate"]["feature_decisions"] == case["baseline"]["feature_decisions"]
        cases.append(case)
    if not cases:
        parser.error("No brief JSON files were found")
    report = {"schema": "A-paired-structural-report/v1", "cases": cases, "promotion": "NOT_ASSESSED_BY_THIS_SCRIPT"}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(str(args.output))


if __name__ == "__main__":
    main()
