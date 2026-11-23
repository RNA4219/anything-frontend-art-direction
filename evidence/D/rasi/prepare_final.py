#!/usr/bin/env python3
"""Prepare a new, immutable final evidence version; never rewrite phase one.

Default operation checks inputs only. --freeze must be called only after the
parent has confirmed comparison.json, comparison.md, and validation.md are final.
This script does not call R-ASI or register an experience. Registration remains
an explicit subsequent supported CLI invocation.
"""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
VERSION = "final-v1"
CAMPAIGN = "anything-frontend-D-20261123"
REQUIRED = [
    "evidence/D/evaluation/baseline-review.md",
    "evidence/D/evaluation/baseline-source-checks.json",
    "evidence/D/evaluation/candidate-review.md",
    "evidence/D/evaluation/candidate-logic-log.json",
    "evidence/D/evaluation/candidate-logic-probe.cjs",
    "evidence/D/evaluation/candidate-registration-desktop.json",
    "evidence/D/evaluation/candidate-requests-desktop.json",
    "evidence/D/evaluation/candidate-requests-narrow.json",
    "evidence/D/evaluation/candidate-gate-results.json",
    "evidence/D/evaluation/candidate-manifest.json",
    "evidence/D/evaluation/candidate-manifest-gate.json",
    "evidence/D/evaluation/candidate-skill-manifest.json",
    "evidence/D/evaluation/input-manifest.json",
    "evidence/D/evaluation/execution.json",
    "evidence/D/evaluation/predeclared-rubric.json",
    "evidence/D/evaluation/adjudication.md",
    "evidence/D/evaluation/adjudication.json",
    "evidence/D/evaluation/adjudication-assignment.json",
    "evidence/D/evaluation/replay_reports.py",
    "evidence/D/evaluation/replay-results.json",
    "evidence/D/evaluation/replay-initial-results.json",
    "evidence/D/evaluation/comparison.json",
    "evidence/D/evaluation/comparison.md",
    "evidence/D/validation.md",
    "evidence/D/gate-code-review.md",
    "evidence/D/gate-review/runner-before.py",
    "evidence/D/gate-review/probe_runner.py",
    "evidence/D/gate-review/probe-results.json",
    "evidence/D/gate-review/probe_runner_postfix.py",
    "evidence/D/gate-review/postfix-results.json",
    "extensions/D/checks/run_browser_checks.py",
]


def canonical(data):
    return json.dumps(data, sort_keys=True, ensure_ascii=False, separators=(",", ":"), allow_nan=False).encode("utf-8")


def sha256(raw):
    return hashlib.sha256(raw).hexdigest()


def freeze(path, raw):
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        if path.read_bytes() != raw:
            raise RuntimeError(f"preserve immutable version; choose a new version for changed bytes: {path}")
        return
    with path.open("xb") as output:
        output.write(raw)


def input_paths(extra):
    paths = list(REQUIRED)
    for path in sorted((REPO / "evidence/D/evaluation").glob("candidate-manifest*.json")):
        rel = str(path.relative_to(REPO))
        if rel not in paths:
            paths.append(rel)
    for rel in extra:
        path = (REPO / rel).resolve(strict=True)
        if not path.is_relative_to(REPO) or not path.is_file():
            raise ValueError("extra artifact must be a regular file within the D repository")
        normalized = str(path.relative_to(REPO))
        if normalized not in paths:
            paths.append(normalized)
    return paths


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--freeze", action="store_true")
    parser.add_argument("--include", action="append", default=[])
    args = parser.parse_args()
    paths = input_paths(args.include)
    missing = [rel for rel in paths if not (REPO / rel).is_file()]
    plan = {
        "schema": "D-final-evidence-preparation/v1", "version": VERSION,
        "required_input_count": len(paths), "missing": missing,
        "mode": "freeze" if args.freeze else "check-inputs-only",
        "experience_registered": False,
    }
    print(json.dumps(plan, ensure_ascii=False, indent=2))
    if not args.freeze:
        return 0
    if missing:
        raise RuntimeError("final evidence is incomplete; no manifest/experience may be created")
    artifacts = []
    for rel in paths:
        raw = (REPO / rel).read_bytes()
        snapshot = HERE / "snapshots" / VERSION / rel
        freeze(snapshot, raw)
        artifacts.append({"path": str(snapshot.relative_to(REPO)), "original_repository_path": rel,
                          "sha256": sha256(raw), "size_bytes": len(raw)})
    manifest = {
        "schema": "design-qa-artifacts/v1", "campaign_id": CAMPAIGN, "version": VERSION,
        "phase": "final-external-review-comparison-and-runner-corrections",
        "previous_manifest": "evidence/D/rasi/external-evidence-manifest.json",
        "previous_manifest_sha256": sha256((HERE / "external-evidence-manifest.json").read_bytes()),
        "artifacts": artifacts, "gate_decision": "HOLD", "independent_promotion": False,
        "limitations": [
            "Different review contexts and anonymized adjudication are not OS-protected blind evaluation.",
            "The shared filesystem did not provide a protected oracle or holdout boundary.",
            "One trial per condition, unknown exact model snapshot and sampling, descriptive comparison only.",
            "Browser runner fixes are verified by synthetic controls; actual local fixture browser remains blocked.",
            "Successful artifact or report contracts do not establish general skill effectiveness or product quality.",
        ],
    }
    manifest_path = HERE / f"external-evidence-{VERSION}.json"
    freeze(manifest_path, canonical(manifest))
    print(json.dumps({"frozen_manifest": str(manifest_path.relative_to(REPO)),
                      "sha256": sha256(canonical(manifest)), "artifact_count": len(artifacts),
                      "next_step": "Verify this manifest, then prepare/register a new HOLD experience after parent authorization."}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
