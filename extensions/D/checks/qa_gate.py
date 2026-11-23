#!/usr/bin/env python3
"""Validate Design QA evidence contracts without pretending to evaluate a UI.

Exit 0: valid contract and READY FOR INTEGRATION promotion evidence.
Exit 1: invalid JSON, schema, path, type, or artifact hash.
Exit 2: valid record whose decision is HOLD or REJECT.

The gate checks records and artifact integrity. It cannot authenticate evaluator
identity, establish actual holdout isolation, or infer usability from pixels.
An independent receipt must come from a separately trusted evaluation process.
"""

from __future__ import annotations

import argparse
from datetime import datetime
import hashlib
import json
import math
from pathlib import Path, PurePosixPath
import re
import sys
import unicodedata
from typing import Any


READY = "READY FOR INTEGRATION"
CATEGORIES = {"functional", "information_architecture", "interaction", "visual", "implementation"}
OWNERS = {"A", "B", "C", "D", "art-direction"}
STATUSES = {"confirmed", "hypothesis", "preference", "resolved"}
SEVERITIES = {"blocker", "major", "minor", "note"}
EVIDENCE_KINDS = {"screenshot", "browser_trace", "source", "test_log"}
EXECUTION_KINDS = {"browser_trace", "test_log"}
SCENARIOS = {"normal", "error", "boundary"}
HEX64 = re.compile(r"^[0-9a-f]{64}$")
IMPRESSION = re.compile(r"ai[\s_-]*slop|ダサ(?:い|く|さ)|ださい|ugly|tacky|cringe|センスがない|キモい|気持ち悪い", re.I)
LIMITATION = (
    "Record structure and file integrity are checked. Evaluator identity, receipt authenticity, "
    "protected holdout isolation, and the truth of observations require external audit. "
    "A valid report is not an independently established product-quality PASS."
)


class ContractError(ValueError):
    pass


def _pairs(items: list[tuple[str, Any]]) -> dict:
    result = {}
    for key, value in items:
        if key in result:
            raise ContractError(f"duplicate JSON key: {key}")
        result[key] = value
    return result


def _constant(value: str) -> None:
    raise ContractError(f"non-finite JSON number: {value}")


def file_hash(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def resolve_artifact(root: Path, value: Any) -> Path:
    if not isinstance(value, str) or not value.strip():
        raise ContractError("artifact path must be a nonempty string")
    if "\\" in value or ":" in value or "\x00" in value:
        raise ContractError(f"artifact path has forbidden characters: {value!r}")
    rel = PurePosixPath(value)
    if rel.is_absolute() or ".." in rel.parts or value.startswith("~"):
        raise ContractError(f"artifact path must stay relative to root: {value!r}")
    path = (root / value).resolve(strict=True)
    if not path.is_relative_to(root):
        raise ContractError(f"artifact symlink escapes root: {value!r}")
    if not path.is_file():
        raise ContractError(f"artifact is not a regular file: {value!r}")
    return path


def load_json(path: Path) -> dict:
    try:
        data = json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=_pairs, parse_constant=_constant)
    except (OSError, UnicodeError, json.JSONDecodeError, RecursionError) as exc:
        raise ContractError(f"cannot load JSON {path}: {exc}") from exc
    if not isinstance(data, dict):
        raise ContractError("top-level JSON must be an object")
    return data


class Checks:
    def __init__(self, root: Path):
        self.root = root
        self.errors: list[str] = []

    def require(self, condition: bool, where: str, message: str) -> bool:
        if not condition:
            self.errors.append(f"{where}: {message}")
        return condition

    def obj(self, value: Any, where: str) -> dict:
        return value if self.require(isinstance(value, dict), where, "must be an object") else {}

    def array(self, value: Any, where: str, nonempty: bool = False) -> list:
        if not self.require(isinstance(value, list), where, "must be an array"):
            return []
        self.require(not nonempty or bool(value), where, "must not be empty")
        return value

    def text(self, value: Any, where: str) -> bool:
        return self.require(isinstance(value, str) and bool(value.strip()), where, "must be a nonempty string")

    def choice(self, value: Any, values: set[str], where: str) -> bool:
        return self.require(isinstance(value, str) and value in values, where, f"must be one of {sorted(values)}")

    def integer(self, value: Any, where: str, minimum: int = 0) -> bool:
        return self.require(type(value) is int and value >= minimum, where, f"must be an integer >= {minimum}; bool is invalid")

    def boolean(self, value: Any, where: str) -> bool:
        return self.require(type(value) is bool, where, "must be a boolean")

    def hash(self, value: Any, where: str) -> bool:
        return self.require(isinstance(value, str) and HEX64.fullmatch(value) is not None, where, "must be lowercase SHA-256")

    def texts(self, value: Any, where: str, nonempty: bool = False) -> list:
        values = self.array(value, where, nonempty)
        for i, item in enumerate(values):
            self.text(item, f"{where}[{i}]")
        return values

    def viewport(self, value: Any, where: str) -> dict:
        view = self.obj(value, where)
        for dimension in ("width", "height"):
            self.integer(view.get(dimension), f"{where}.{dimension}", 1)
        return view

    def artifact(self, obj: dict, where: str, size: bool = False) -> Path | None:
        self.text(obj.get("path"), f"{where}.path")
        hash_valid = self.hash(obj.get("sha256"), f"{where}.sha256")
        if size:
            self.integer(obj.get("size_bytes"), f"{where}.size_bytes")
        try:
            path = resolve_artifact(self.root, obj.get("path"))
            if hash_valid:
                self.require(file_hash(path) == obj["sha256"], where, "artifact SHA-256 mismatch")
            if size:
                self.require(path.stat().st_size == obj.get("size_bytes"), where, "artifact size mismatch")
            return path
        except (ContractError, OSError, RuntimeError, ValueError) as exc:
            self.errors.append(f"{where}: {exc}")
            return None


def _unique(value: Any, seen: set, where: str, checks: Checks) -> None:
    if isinstance(value, str):
        checks.require(value not in seen, where, f"duplicate identifier/path: {value}")
        seen.add(value)


def _json_finite(value: Any, where: str, checks: Checks) -> None:
    if isinstance(value, float):
        checks.require(math.isfinite(value), where, "must contain only finite numbers")
    elif isinstance(value, dict):
        for key, child in value.items():
            _json_finite(child, f"{where}.{key}", checks)
    elif isinstance(value, list):
        for i, child in enumerate(value):
            _json_finite(child, f"{where}[{i}]", checks)


def _evidence_refs(value: Any, where: str, known: dict, checks: Checks) -> set[str]:
    ids = checks.texts(value, where)
    seen = set()
    kinds = set()
    for ident in ids:
        if not isinstance(ident, str):
            continue
        _unique(ident, seen, where, checks)
        checks.require(ident in known, where, f"unknown evidence id: {ident}")
        if ident in known:
            kind = known[ident].get("kind")
            if isinstance(kind, str):
                kinds.add(kind)
    return kinds


def _independent_receipt(data: dict, report_path: Path, checks: Checks) -> tuple[bool, str | None, list[str]]:
    independence = checks.obj(data.get("independence"), "independence")
    for key in ("author_id", "evaluator_id"):
        checks.text(independence.get(key), f"independence.{key}")
    for key in ("blind", "protected_holdout"):
        checks.boolean(independence.get(key), f"independence.{key}")
    checks.require("evidence_ref" in independence, "independence", "evidence_ref is required, null when unavailable")
    reference = independence.get("evidence_ref")
    ready = (
        independence.get("author_id") != independence.get("evaluator_id")
        and independence.get("blind") is True
        and independence.get("protected_holdout") is True
    )
    reasons = []
    if not ready:
        reasons.append("independent evaluator, blind setup, and protected holdout are not all established")
    if reference is None:
        reasons.append("independent evaluation receipt is missing")
        return False, None, reasons
    try:
        receipt_path = resolve_artifact(checks.root, reference)
        receipt = load_json(receipt_path)
    except (ContractError, OSError, RuntimeError, ValueError) as exc:
        checks.errors.append(f"independence.evidence_ref: {exc}")
        return False, None, reasons
    checks.require(receipt.get("schema") == "design-qa-independent-evaluation/v1", "independence.receipt", "invalid receipt schema")
    for key in ("report_id",):
        checks.require(receipt.get(key) == data.get(key), f"independence.receipt.{key}", "does not match report")
    for key in ("author_id", "evaluator_id", "blind", "protected_holdout"):
        checks.require(type(receipt.get(key)) is type(independence.get(key)) and receipt.get(key) == independence.get(key), f"independence.receipt.{key}", "does not match independence declaration")
    checks.hash(receipt.get("report_sha256"), "independence.receipt.report_sha256")
    checks.require(receipt.get("report_sha256") == file_hash(report_path), "independence.receipt.report_sha256", "receipt does not cover the exact report bytes")
    decision = receipt.get("decision")
    checks.choice(decision, {READY, "HOLD", "REJECT"}, "independence.receipt.decision")
    when = receipt.get("evaluated_at")
    checks.text(when, "independence.receipt.evaluated_at")
    try:
        instant = datetime.fromisoformat(when.replace("Z", "+00:00"))
        checks.require(instant.tzinfo is not None, "independence.receipt.evaluated_at", "timezone is required")
    except (ValueError, TypeError, AttributeError):
        checks.errors.append("independence.receipt.evaluated_at: invalid ISO-8601 timestamp")
    return ready, decision if isinstance(decision, str) else None, reasons


def inspect_report(data: dict, root: Path, report_path: Path) -> dict:
    c = Checks(root)
    _json_finite(data, "report", c)
    c.require(data.get("schema") == "design-qa-report/v1", "schema", "expected design-qa-report/v1")
    c.text(data.get("report_id"), "report_id")
    reviewed_paths = set()
    reviewed = c.array(data.get("reviewed_artifacts"), "reviewed_artifacts", True)
    for i, value in enumerate(reviewed):
        item = c.obj(value, f"reviewed_artifacts[{i}]")
        c.artifact(item, f"reviewed_artifacts[{i}]")
        _unique(item.get("path"), reviewed_paths, "reviewed_artifacts", c)
    context = c.obj(data.get("context"), "context")
    for key in ("task_id", "evaluation_mode"):
        c.text(context.get(key), f"context.{key}")
    for key in ("requirements_sha256", "content_sha256"):
        c.hash(context.get(key), f"context.{key}")
    env = c.obj(context.get("environment"), "context.environment")
    for key in ("browser", "version", "os", "locale", "timezone", "animation"):
        c.text(env.get(key), f"context.environment.{key}")
    viewport = c.viewport(env.get("viewport"), "context.environment.viewport")
    dpr = env.get("dpr")
    c.require((type(dpr) is int or type(dpr) is float and math.isfinite(dpr)) and dpr > 0, "context.environment.dpr", "must be a positive finite number, not bool")
    for key in ("fonts", "input_modes"):
        c.texts(env.get(key), f"context.environment.{key}", True)
    seed = env.get("data_seed")
    c.require(type(seed) is int or isinstance(seed, str) and bool(seed.strip()), "context.environment.data_seed", "must be an integer or nonempty string, not bool")
    model = c.obj(context.get("model"), "context.model")
    c.text(model.get("id"), "context.model.id")
    sampling = c.obj(model.get("sampling"), "context.model.sampling")
    c.require(bool(sampling), "context.model.sampling", "must state actual sampling settings or explicit unknown values")
    evidence = {}
    for i, value in enumerate(c.array(data.get("evidence"), "evidence", True)):
        where = f"evidence[{i}]"
        item = c.obj(value, where)
        ident = item.get("id")
        c.text(ident, f"{where}.id")
        c.choice(item.get("kind"), EVIDENCE_KINDS, f"{where}.kind")
        c.text(item.get("description"), f"{where}.description")
        c.artifact(item, where)
        if isinstance(ident, str):
            c.require(ident not in evidence, f"{where}.id", "duplicate evidence id")
            evidence[ident] = item
    holds = []
    reject = []
    finding_ids = set()
    findings = c.array(data.get("findings"), "findings")
    for i, value in enumerate(findings):
        where = f"findings[{i}]"
        f = c.obj(value, where)
        c.text(f.get("id"), f"{where}.id")
        _unique(f.get("id"), finding_ids, f"{where}.id", c)
        for field, choices in (("category", CATEGORIES), ("owner", OWNERS), ("status", STATUSES), ("severity", SEVERITIES), ("confidence", {"high", "medium", "low"})):
            c.choice(f.get(field), choices, f"{where}.{field}")
        for field in ("symptom", "expected", "observed", "impact", "repair_direction"):
            c.text(f.get(field), f"{where}.{field}")
        c.texts(f.get("reproduction"), f"{where}.reproduction", True)
        location = c.obj(f.get("location"), f"{where}.location")
        for field in ("artifact", "selector", "state"):
            c.text(location.get(field), f"{where}.location.{field}")
        c.require(isinstance(location.get("artifact"), str) and location.get("artifact") in reviewed_paths, f"{where}.location.artifact", "must identify a reviewed artifact")
        finding_view = c.viewport(location.get("viewport"), f"{where}.location.viewport")
        c.require(finding_view == viewport, f"{where}.location.viewport", "must match this report's frozen viewport; create a separate report for another viewport")
        basis = c.obj(f.get("basis"), f"{where}.basis")
        c.choice(basis.get("kind"), {"requirement", "standard", "heuristic", "intent"}, f"{where}.basis.kind")
        for field in ("reference", "clause"):
            c.text(basis.get(field), f"{where}.basis.{field}")
        kinds = _evidence_refs(f.get("evidence_ids"), f"{where}.evidence_ids", evidence, c)
        status = f.get("status")
        if status in ("confirmed", "resolved"):
            c.require(bool(kinds), f"{where}.evidence_ids", "confirmed/resolved findings require evidence")
            if f.get("category") == "visual":
                c.require("screenshot" in kinds, f"{where}.evidence_ids", "visual confirmation requires a screenshot")
            if f.get("category") == "interaction":
                c.require(bool(kinds & EXECUTION_KINDS), f"{where}.evidence_ids", "interaction confirmation requires browser_trace or test_log; static inference is a hypothesis")
        if status == "confirmed":
            rationale = unicodedata.normalize("NFKC", str(f.get("symptom", "")) + " " + json.dumps(basis, ensure_ascii=False))
            c.require(IMPRESSION.search(rationale) is None, where, "impression words cannot establish a confirmed defect")
            if f.get("severity") in ("blocker", "major"):
                reject.append(f"unresolved {f.get('severity')} finding {f.get('id')}")
            if f.get("confidence") == "low":
                holds.append(f"low-confidence confirmation {f.get('id')} needs review")
        if status == "preference":
            c.require(f.get("severity") == "note", f"{where}.severity", "preference must have note severity")
        if status == "hypothesis":
            holds.append(f"unverified hypothesis {f.get('id')}")
    runs = c.array(data.get("task_runs"), "task_runs")
    run_keys = set()
    covered = set()
    for i, value in enumerate(runs):
        where = f"task_runs[{i}]"
        run = c.obj(value, where)
        c.text(run.get("task_id"), f"{where}.task_id")
        c.require(run.get("task_id") == context.get("task_id"), f"{where}.task_id", "must match context.task_id")
        c.choice(run.get("scenario"), SCENARIOS, f"{where}.scenario")
        c.choice(run.get("status"), {"passed", "failed", "blocked", "not_run"}, f"{where}.status")
        c.choice(run.get("recovery"), {"passed", "failed", "not_applicable", "not_run"}, f"{where}.recovery")
        c.text(run.get("observed"), f"{where}.observed")
        c.require("completion" in run and (run.get("completion") is None or type(run.get("completion")) is bool), f"{where}.completion", "must be boolean or explicit null")
        c.require("steps_count" in run, f"{where}.steps_count", "is required, null if not measured")
        if run.get("steps_count") is not None:
            c.integer(run.get("steps_count"), f"{where}.steps_count")
        key = (run.get("task_id"), run.get("scenario"))
        if all(isinstance(x, str) for x in key):
            c.require(key not in run_keys, where, "duplicate task/scenario; split repeated trials into separate reports")
            run_keys.add(key)
            covered.add(key[1])
        kinds = _evidence_refs(run.get("evidence_ids"), f"{where}.evidence_ids", evidence, c)
        status = run.get("status")
        if status == "passed":
            c.require(run.get("completion") is True, f"{where}.completion", "passed requires observed completion=true")
            c.integer(run.get("steps_count"), f"{where}.steps_count")
            c.require(bool(kinds & EXECUTION_KINDS), f"{where}.evidence_ids", "passed requires observed execution evidence; screenshots/source alone cannot prove completion")
        elif status in ("blocked", "not_run"):
            c.require(run.get("completion") is None, f"{where}.completion", "unexecuted tasks require completion=null")
            c.require(run.get("steps_count") is None, f"{where}.steps_count", "unexecuted tasks require steps_count=null")
        elif status == "failed":
            c.require(run.get("completion") is False, f"{where}.completion", "failed requires completion=false")
            c.require(bool(kinds & EXECUTION_KINDS), f"{where}.evidence_ids", "observed failure requires execution evidence")
        if run.get("recovery") in ("passed", "failed"):
            c.require(bool(kinds & EXECUTION_KINDS), f"{where}.recovery", "recovery claims require execution evidence")
            c.require(status not in ("blocked", "not_run"), f"{where}.recovery", "unexecuted task cannot claim observed recovery")
        if status != "passed":
            holds.append(f"{run.get('scenario')} task status is {status}")
        if run.get("recovery") in ("failed", "not_run"):
            holds.append(f"{run.get('scenario')} recovery is {run.get('recovery')}")
    missing = sorted(SCENARIOS - covered)
    if missing:
        holds.append("missing scenario coverage: " + ", ".join(missing))
    questions = c.texts(data.get("open_questions"), "open_questions")
    if questions:
        holds.append("open questions remain")
    independent, receipt_decision, independent_reasons = _independent_receipt(data, report_path, c)
    if c.errors:
        return {"schema": "design-qa-gate-result/v1", "contract_valid": False, "target_decision": "HOLD", "promotion_decision": "HOLD", "errors": c.errors, "limitations": LIMITATION}
    target = "REJECT" if reject else "HOLD" if holds else READY
    promotion = "HOLD"
    if independent:
        promotion = "REJECT" if target == "REJECT" or receipt_decision == "REJECT" else READY if target == READY and receipt_decision == READY else "HOLD"
    return {
        "schema": "design-qa-gate-result/v1", "report_id": data["report_id"], "contract_valid": True,
        "target_decision": target, "promotion_decision": promotion, "errors": [],
        "target_reasons": reject + holds, "promotion_reasons": independent_reasons,
        "receipt_decision": receipt_decision,
        "counts": {"confirmed": sum(f["status"] == "confirmed" for f in findings), "hypotheses": sum(f["status"] == "hypothesis" for f in findings), "passed_task_runs": sum(r["status"] == "passed" for r in runs), "task_runs": len(runs)},
        "limitations": LIMITATION,
    }


def inspect_manifest(data: dict, root: Path) -> dict:
    c = Checks(root)
    _json_finite(data, "manifest", c)
    c.require(data.get("schema") == "design-qa-artifacts/v1", "schema", "expected design-qa-artifacts/v1")
    seen = set()
    artifacts = c.array(data.get("artifacts"), "artifacts", True)
    for i, value in enumerate(artifacts):
        item = c.obj(value, f"artifacts[{i}]")
        c.artifact(item, f"artifacts[{i}]", size=True)
        _unique(item.get("path"), seen, "artifacts", c)
    return {"schema": "design-qa-manifest-result/v1", "contract_valid": not c.errors,
            "artifact_count": len(artifacts), "integrity_verified": not c.errors,
            "errors": c.errors, "quality_evaluated": False}


def inspect_comparison(base: dict, cand: dict, root: Path, base_path: Path, cand_path: Path) -> dict:
    left = inspect_report(base, root, base_path)
    right = inspect_report(cand, root, cand_path)
    valid = left["contract_valid"] and right["contract_valid"]
    mismatch = []
    if valid:
        if base["context"] != cand["context"]:
            mismatch.append("context differs: requirements/content/model/environment/evaluation mode must match exactly")
        def reviewed(doc: dict) -> list:
            return sorted((item["path"], item["sha256"]) for item in doc["reviewed_artifacts"])
        if reviewed(base) != reviewed(cand):
            mismatch.append("reviewed_artifacts differ: this CLI compares review methods on identical target artifacts")
    result = {
        "schema": "design-qa-comparison-result/v1", "contract_valid": valid,
        "comparison_valid": valid and not mismatch, "descriptive_only": True,
        "target_decision": "HOLD" if not valid or mismatch else right["target_decision"],
        "promotion_decision": "HOLD" if not valid or mismatch else right["promotion_decision"],
        "mismatches": mismatch, "baseline": left, "candidate": right,
        "interpretation": "Finding counts describe report differences; more or fewer findings do not establish improved UI quality or evaluator accuracy.",
        "limitations": LIMITATION,
    }
    if valid and not mismatch:
        result["count_deltas_candidate_minus_baseline"] = {key: right["counts"][key] - left["counts"][key] for key in right["counts"]}
        result["steps_count_deltas"] = {
            scenario: next((r["steps_count"] for r in cand["task_runs"] if r["scenario"] == scenario), None)
            for scenario in sorted(SCENARIOS)
        }
        for scenario, candidate_steps in list(result["steps_count_deltas"].items()):
            baseline_steps = next((r["steps_count"] for r in base["task_runs"] if r["scenario"] == scenario), None)
            result["steps_count_deltas"][scenario] = None if candidate_steps is None or baseline_steps is None else candidate_steps - baseline_steps
    return result


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    for name in ("report", "verify-manifest"):
        command = sub.add_parser(name)
        command.add_argument("input", type=Path)
        command.add_argument("--root", required=True, type=Path)
    compare = sub.add_parser("compare")
    compare.add_argument("baseline", type=Path)
    compare.add_argument("candidate", type=Path)
    compare.add_argument("--root", required=True, type=Path)
    args = parser.parse_args(argv)
    try:
        root = args.root.resolve(strict=True)
        if not root.is_dir():
            raise ContractError("--root must be an existing directory")
        def input_path(path: Path) -> Path:
            # CLI input may be absolute, but every input must remain inside root.
            absolute = path.resolve(strict=True)
            if not absolute.is_relative_to(root) or not absolute.is_file():
                raise ContractError("input JSON must be a regular file inside --root")
            return absolute
        if args.command == "compare":
            left, right = input_path(args.baseline), input_path(args.candidate)
            result = inspect_comparison(load_json(left), load_json(right), root, left, right)
        else:
            path = input_path(args.input)
            data = load_json(path)
            result = inspect_report(data, root, path) if args.command == "report" else inspect_manifest(data, root)
    except (ContractError, OSError, RuntimeError, ValueError, RecursionError) as exc:
        result = {"contract_valid": False, "target_decision": "HOLD", "promotion_decision": "HOLD", "errors": [str(exc)]}
    print(json.dumps(result, ensure_ascii=False, indent=2, allow_nan=False))
    if not result["contract_valid"]:
        return 1
    if args.command == "verify-manifest":
        return 0
    return 0 if result.get("promotion_decision") == READY else 2


if __name__ == "__main__":
    raise SystemExit(main())
