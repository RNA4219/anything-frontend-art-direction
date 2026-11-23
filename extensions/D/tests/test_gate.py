"""Synthetic mutation tests for evidence integrity and fail-closed decisions.

All browser outcomes and independent receipts here are explicit unit-test
fixtures. Their success does not constitute a blind skill evaluation.
"""

from __future__ import annotations

import base64
import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


GATE_PATH = Path(__file__).resolve().parents[1] / "checks" / "qa_gate.py"
spec = importlib.util.spec_from_file_location("design_qa_gate", GATE_PATH)
gate = importlib.util.module_from_spec(spec)
spec.loader.exec_module(gate)


class GateMutations(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix="design-qa-gate-")
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name).resolve()
        (self.root / "fixture.html").write_text("<!doctype html><button id='submit'>Submit</button>\n")
        (self.root / "requirements.txt").write_text("Synthetic contract test: submit the fixture task.\n")
        (self.root / "trace.json").write_text(json.dumps({"synthetic_test_fixture": True, "events": ["submit", "success"]}))
        # A real one-pixel PNG used only to exercise file integrity checks.
        (self.root / "screen.png").write_bytes(base64.b64decode("iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAusB9Y9Zl1sAAAAASUVORK5CYII="))
        self.report = self.make_report()

    def sha(self, name):
        return hashlib.sha256((self.root / name).read_bytes()).hexdigest()

    def make_report(self):
        viewport = {"width": 1280, "height": 800}
        return {
            "schema": "design-qa-report/v1",
            "report_id": "synthetic-unit-fixture",
            "reviewed_artifacts": [
                {"path": "fixture.html", "sha256": self.sha("fixture.html")},
                {"path": "requirements.txt", "sha256": self.sha("requirements.txt")},
            ],
            "context": {
                "task_id": "synthetic-submit",
                "requirements_sha256": self.sha("requirements.txt"),
                "content_sha256": self.sha("fixture.html"),
                "environment": {
                    "browser": "synthetic-browser", "version": "unit-test-v1", "os": "synthetic-os",
                    "viewport": viewport, "dpr": 1, "locale": "ja-JP", "timezone": "Asia/Tokyo",
                    "fonts": ["fixture-font"], "animation": "disabled", "data_seed": 7,
                    "input_modes": ["keyboard", "pointer"],
                },
                "model": {"id": "synthetic-unit-test", "sampling": {"temperature": 0, "seed": 7}},
                "evaluation_mode": "synthetic-unit-test-only",
            },
            "evidence": [
                {"id": "trace", "path": "trace.json", "sha256": self.sha("trace.json"), "kind": "browser_trace", "description": "Synthetic event log for contract mutation tests."},
                {"id": "screen", "path": "screen.png", "sha256": self.sha("screen.png"), "kind": "screenshot", "description": "One-pixel synthetic image, never a real UI evaluation."},
                {"id": "source", "path": "fixture.html", "sha256": self.sha("fixture.html"), "kind": "source", "description": "Minimal synthetic source fixture."},
            ],
            "findings": [],
            "task_runs": [
                {"task_id": "synthetic-submit", "scenario": scenario, "status": "passed", "completion": True,
                 "steps_count": 1, "recovery": "passed" if scenario == "error" else "not_applicable",
                 "evidence_ids": ["trace"], "observed": "Synthetic fixture observation for schema testing only."}
                for scenario in ["normal", "error", "boundary"]
            ],
            "open_questions": [],
            "independence": {"author_id": "unit-author", "evaluator_id": "unit-author", "blind": False,
                             "protected_holdout": False, "evidence_ref": None},
        }

    def finding(self, **overrides):
        f = {
            "id": "synthetic-finding", "category": "visual", "owner": "art-direction", "status": "confirmed",
            "severity": "minor", "location": {"artifact": "fixture.html", "selector": "#submit", "state": "ready",
                                               "viewport": {"width": 1280, "height": 800}},
            "symptom": "Synthetic button bounding box crosses the container edge.",
            "expected": "The synthetic action remains within its defined container.",
            "observed": "Synthetic image evidence is referenced for this integrity test.",
            "impact": "Synthetic case tests an overflow observation record.",
            "repair_direction": "Inspect the bounding box and preserve the existing visual intent.",
            "reproduction": ["Open the fixture.", "Inspect the synthetic submit button."],
            "basis": {"kind": "requirement", "reference": "requirements.txt", "clause": "Synthetic fixture task."},
            "confidence": "high", "evidence_ids": ["screen"],
        }
        f.update(overrides)
        return f

    def write_report(self, data=None, name="report.json"):
        path = self.root / name
        path.write_text(json.dumps(self.report if data is None else data, ensure_ascii=False, indent=2) + "\n")
        return path

    def inspect(self, data=None):
        data = self.report if data is None else data
        return gate.inspect_report(data, self.root, self.write_report(data))

    def invalid(self, data=None, text=None):
        result = self.inspect(data)
        self.assertFalse(result["contract_valid"], result)
        self.assertEqual(result["promotion_decision"], "HOLD")
        if text:
            self.assertTrue(any(text in error for error in result["errors"]), result["errors"])
        return result

    def cli(self, command, *paths):
        process = subprocess.run([sys.executable, str(GATE_PATH), command, *map(str, paths), "--root", str(self.root)],
                                 text=True, capture_output=True, timeout=10)
        self.assertFalse(process.stderr, process.stderr)
        return process.returncode, json.loads(process.stdout)

    def add_receipt(self, decision=gate.READY):
        self.report["independence"] = {"author_id": "unit-author", "evaluator_id": "unit-independent-fixture",
                                       "blind": True, "protected_holdout": True, "evidence_ref": "independent.json"}
        path = self.write_report()
        receipt = {"schema": "design-qa-independent-evaluation/v1", "report_id": self.report["report_id"],
                   "report_sha256": gate.file_hash(path), **{k: v for k, v in self.report["independence"].items() if k != "evidence_ref"},
                   "decision": decision, "evaluated_at": "2026-11-23T00:00:00Z",
                   "synthetic_test_fixture": True}
        (self.root / "independent.json").write_text(json.dumps(receipt))
        return path, receipt

    def test_complete_self_review_still_holds_promotion(self):
        result = self.inspect()
        self.assertTrue(result["contract_valid"])
        self.assertEqual(result["target_decision"], gate.READY)
        self.assertEqual(result["promotion_decision"], "HOLD")
        code, _ = self.cli("report", self.root / "report.json")
        self.assertEqual(code, 2)

    def test_missing_boundary_is_valid_hold(self):
        self.report["task_runs"].pop()
        result = self.inspect()
        self.assertTrue(result["contract_valid"])
        self.assertEqual(result["target_decision"], "HOLD")
        self.assertTrue(any("boundary" in reason for reason in result["target_reasons"]))

    def test_not_run_is_honest_hold(self):
        self.report["task_runs"][0].update(status="not_run", completion=None, steps_count=None, recovery="not_run", evidence_ids=[])
        result = self.inspect()
        self.assertTrue(result["contract_valid"])
        self.assertEqual(result["target_decision"], "HOLD")

    def test_unresolved_major_rejects_target(self):
        self.report["findings"] = [self.finding(severity="major")]
        result = self.inspect()
        self.assertTrue(result["contract_valid"])
        self.assertEqual(result["target_decision"], "REJECT")
        self.assertEqual(result["promotion_decision"], "HOLD")

    def test_resolved_major_does_not_reject(self):
        self.report["findings"] = [self.finding(severity="major", status="resolved")]
        result = self.inspect()
        self.assertTrue(result["contract_valid"])
        self.assertEqual(result["target_decision"], gate.READY)

    def test_resolved_without_evidence_is_invalid(self):
        self.report["findings"] = [self.finding(status="resolved", evidence_ids=[])]
        self.invalid(text="require evidence")

    def test_visual_confirmation_requires_screenshot(self):
        self.report["findings"] = [self.finding(evidence_ids=["source"])]
        self.invalid(text="requires a screenshot")

    def test_interaction_confirmation_requires_execution(self):
        self.report["findings"] = [self.finding(category="interaction", owner="B", evidence_ids=["screen"])]
        self.invalid(text="requires browser_trace")

    def test_static_hypothesis_is_valid_but_hold(self):
        self.report["findings"] = [self.finding(category="interaction", owner="B", status="hypothesis", evidence_ids=["source"])]
        result = self.inspect()
        self.assertTrue(result["contract_valid"])
        self.assertEqual(result["target_decision"], "HOLD")

    def test_preference_is_note_and_does_not_reject(self):
        self.report["findings"] = [self.finding(status="preference", severity="note", symptom="個人的にはダサいと感じる", evidence_ids=[])]
        result = self.inspect()
        self.assertTrue(result["contract_valid"])
        self.assertEqual(result["target_decision"], gate.READY)

    def test_preference_cannot_be_major(self):
        self.report["findings"] = [self.finding(status="preference", severity="major")]
        self.invalid(text="note severity")

    def test_impression_words_in_symptom_are_not_defects(self):
        for phrase in ("AI Slop", "AI-slop", "ＡＩ　Ｓｌｏｐ", "ダサい", "ugly"):
            with self.subTest(phrase=phrase):
                self.report["findings"] = [self.finding(symptom=phrase)]
                self.invalid(text="impression words")

    def test_impression_words_in_basis_are_not_defects(self):
        f = self.finding()
        f["basis"]["clause"] = "AI slopだから"
        self.report["findings"] = [f]
        self.invalid(text="impression words")

    def test_missing_category_is_invalid(self):
        f = self.finding(); del f["category"]
        self.report["findings"] = [f]
        self.invalid(text="category")

    def test_duplicate_finding_ids_are_invalid(self):
        self.report["findings"] = [self.finding(), self.finding()]
        self.invalid(text="duplicate identifier")

    def test_duplicate_evidence_ids_are_invalid(self):
        self.report["evidence"].append(copy.deepcopy(self.report["evidence"][0]))
        self.invalid(text="duplicate evidence id")

    def test_unknown_evidence_reference_is_invalid(self):
        self.report["task_runs"][0]["evidence_ids"] = ["missing"]
        self.invalid(text="unknown evidence id")

    def test_empty_evidence_is_invalid(self):
        self.report["evidence"] = []
        self.invalid(text="must not be empty")

    def test_passed_with_false_completion_is_invalid(self):
        self.report["task_runs"][0]["completion"] = False
        self.invalid(text="completion=true")

    def test_passed_without_execution_evidence_is_invalid(self):
        self.report["task_runs"][0]["evidence_ids"] = ["screen", "source"]
        self.invalid(text="cannot prove completion")

    def test_bool_is_not_step_count(self):
        self.report["task_runs"][0]["steps_count"] = True
        self.invalid(text="bool is invalid")

    def test_float_is_not_step_count(self):
        self.report["task_runs"][0]["steps_count"] = 1.5
        self.invalid(text="must be an integer")

    def test_negative_steps_are_invalid(self):
        self.report["task_runs"][0]["steps_count"] = -1
        self.invalid(text="must be an integer")

    def test_bool_is_not_dpr(self):
        self.report["context"]["environment"]["dpr"] = True
        self.invalid(text="not bool")

    def test_bool_is_not_viewport_size(self):
        self.report["context"]["environment"]["viewport"]["width"] = True
        self.invalid(text="bool is invalid")

    def test_null_required_text_is_invalid(self):
        self.report["context"]["environment"]["browser"] = None
        self.invalid(text="nonempty string")

    def test_wrong_boolean_type_is_invalid(self):
        self.report["independence"]["blind"] = "false"
        self.invalid(text="must be a boolean")

    def test_tampered_evidence_hash_is_invalid(self):
        (self.root / "trace.json").write_text("tampered after observation")
        self.invalid(text="SHA-256 mismatch")

    def test_tampered_reviewed_artifact_is_invalid(self):
        (self.root / "fixture.html").write_text("changed target")
        self.invalid(text="SHA-256 mismatch")

    def test_parent_path_traversal_is_invalid(self):
        self.report["evidence"][0]["path"] = "../outside.json"
        self.invalid(text="stay relative")

    def test_absolute_artifact_path_is_invalid(self):
        self.report["evidence"][0]["path"] = str(self.root / "trace.json")
        self.invalid(text="stay relative")

    def test_windows_path_is_invalid(self):
        self.report["evidence"][0]["path"] = "C:\\secret.json"
        self.invalid(text="forbidden characters")

    def test_symlink_escape_is_invalid(self):
        with tempfile.TemporaryDirectory(prefix="design-qa-outside-") as outside:
            target = Path(outside) / "outside.json"
            target.write_text("outside")
            try:
                (self.root / "escape.json").symlink_to(target)
            except OSError as exc:
                self.skipTest(f"host lacks symlink support: {exc}")
            self.report["evidence"][0]["path"] = "escape.json"
            self.report["evidence"][0]["sha256"] = gate.file_hash(target)
            self.invalid(text="symlink escapes")

    def test_finding_viewport_must_match_observation_context(self):
        f = self.finding(); f["location"]["viewport"]["width"] = 320
        self.report["findings"] = [f]
        self.invalid(text="frozen viewport")

    def test_finding_location_must_be_reviewed(self):
        f = self.finding(); f["location"]["artifact"] = "unknown.html"
        self.report["findings"] = [f]
        self.invalid(text="reviewed artifact")

    def test_not_run_cannot_claim_recovery(self):
        self.report["task_runs"][0].update(status="not_run", completion=None, steps_count=None, recovery="passed")
        self.invalid(text="cannot claim observed recovery")

    def test_duplicate_task_scenario_is_invalid(self):
        self.report["task_runs"].append(copy.deepcopy(self.report["task_runs"][0]))
        self.invalid(text="duplicate task/scenario")

    def test_unanswered_question_holds(self):
        self.report["open_questions"] = ["Is the retry safe under a real timeout?"]
        result = self.inspect()
        self.assertTrue(result["contract_valid"])
        self.assertEqual(result["target_decision"], "HOLD")

    def compare(self, candidate):
        left = self.write_report(self.report, "baseline.json")
        right = self.write_report(candidate, "candidate.json")
        return gate.inspect_comparison(self.report, candidate, self.root, left, right)

    def test_comparison_context_mismatch_holds(self):
        candidate = copy.deepcopy(self.report)
        candidate["context"]["environment"]["data_seed"] = 8
        result = self.compare(candidate)
        self.assertTrue(result["contract_valid"])
        self.assertFalse(result["comparison_valid"])
        self.assertEqual(result["target_decision"], "HOLD")
        self.assertNotIn("count_deltas_candidate_minus_baseline", result)

    def test_comparison_model_mismatch_holds(self):
        candidate = copy.deepcopy(self.report)
        candidate["context"]["model"]["id"] = "another-model"
        result = self.compare(candidate)
        self.assertFalse(result["comparison_valid"])

    def test_comparison_artifact_order_does_not_matter(self):
        candidate = copy.deepcopy(self.report)
        candidate["reviewed_artifacts"].reverse()
        result = self.compare(candidate)
        self.assertTrue(result["comparison_valid"])
        self.assertTrue(result["descriptive_only"])

    def test_comparison_different_target_artifacts_holds(self):
        candidate = copy.deepcopy(self.report)
        (self.root / "another.html").write_text("another target")
        candidate["reviewed_artifacts"][0] = {"path": "another.html", "sha256": self.sha("another.html")}
        result = self.compare(candidate)
        self.assertTrue(result["contract_valid"])
        self.assertFalse(result["comparison_valid"])

    def test_count_delta_never_claims_quality_improvement(self):
        candidate = copy.deepcopy(self.report)
        candidate["findings"] = [self.finding()]
        result = self.compare(candidate)
        self.assertTrue(result["comparison_valid"])
        self.assertEqual(result["count_deltas_candidate_minus_baseline"]["confirmed"], 1)
        self.assertTrue(result["descriptive_only"])
        self.assertNotIn("quality_improved", result)
        self.assertEqual(result["promotion_decision"], "HOLD")

    def test_duplicate_json_keys_fail_cli(self):
        path = self.root / "duplicate.json"
        path.write_text('{"schema":"design-qa-report/v1","schema":"other"}')
        code, result = self.cli("report", path)
        self.assertEqual(code, 1)
        self.assertFalse(result["contract_valid"])
        self.assertIn("duplicate JSON key", result["errors"][0])

    def test_nan_json_fails_cli(self):
        self.report["context"]["environment"]["dpr"] = float("nan")
        code, result = self.cli("report", self.write_report())
        self.assertEqual(code, 1)
        self.assertIn("non-finite", result["errors"][0])

    def test_infinite_exponent_fails_cli(self):
        path = self.write_report()
        path.write_text(path.read_text().replace('"dpr": 1', '"dpr": 1e999'))
        code, result = self.cli("report", path)
        self.assertEqual(code, 1)
        self.assertFalse(result["contract_valid"])

    def test_synthetic_independent_receipt_exercises_ready_branch(self):
        path, _ = self.add_receipt()
        code, result = self.cli("report", path)
        self.assertEqual(code, 0)
        self.assertEqual(result["promotion_decision"], gate.READY)
        self.assertIn("external audit", result["limitations"])

    def test_receipt_must_cover_exact_report_bytes(self):
        path, _ = self.add_receipt()
        path.write_text(path.read_text() + " \n")
        code, result = self.cli("report", path)
        self.assertEqual(code, 1)
        self.assertTrue(any("exact report bytes" in e for e in result["errors"]))

    def test_receipt_with_wrong_evaluator_is_invalid(self):
        path, receipt = self.add_receipt()
        receipt["evaluator_id"] = "mismatched-evaluator"
        (self.root / "independent.json").write_text(json.dumps(receipt))
        code, result = self.cli("report", path)
        self.assertEqual(code, 1)
        self.assertFalse(result["contract_valid"])

    def test_blind_flags_without_receipt_hold(self):
        self.report["independence"].update(evaluator_id="different-id", blind=True, protected_holdout=True)
        result = self.inspect()
        self.assertTrue(result["contract_valid"])
        self.assertEqual(result["promotion_decision"], "HOLD")

    def test_self_named_receipt_cannot_promote(self):
        path, receipt = self.add_receipt()
        self.report["independence"]["evaluator_id"] = "unit-author"
        self.write_report()
        receipt["evaluator_id"] = "unit-author"
        receipt["report_sha256"] = gate.file_hash(path)
        (self.root / "independent.json").write_text(json.dumps(receipt))
        code, result = self.cli("report", path)
        self.assertEqual(code, 2)
        self.assertEqual(result["promotion_decision"], "HOLD")

    def test_independent_reject_cannot_promote(self):
        path, _ = self.add_receipt(decision="REJECT")
        code, result = self.cli("report", path)
        self.assertEqual(code, 2)
        self.assertEqual(result["promotion_decision"], "REJECT")

    def test_manifest_integrity_is_not_quality(self):
        manifest = {"schema": "design-qa-artifacts/v1", "artifacts": [
            {"path": "fixture.html", "sha256": self.sha("fixture.html"), "size_bytes": (self.root / "fixture.html").stat().st_size}
        ]}
        path = self.root / "manifest.json"; path.write_text(json.dumps(manifest))
        code, result = self.cli("verify-manifest", path)
        self.assertEqual(code, 0)
        self.assertTrue(result["integrity_verified"])
        self.assertFalse(result["quality_evaluated"])

    def test_manifest_wrong_size_fails(self):
        manifest = {"schema": "design-qa-artifacts/v1", "artifacts": [
            {"path": "fixture.html", "sha256": self.sha("fixture.html"), "size_bytes": 0}
        ]}
        result = gate.inspect_manifest(manifest, self.root)
        self.assertFalse(result["contract_valid"])

    def test_manifest_bool_size_fails(self):
        manifest = {"schema": "design-qa-artifacts/v1", "artifacts": [
            {"path": "fixture.html", "sha256": self.sha("fixture.html"), "size_bytes": True}
        ]}
        result = gate.inspect_manifest(manifest, self.root)
        self.assertFalse(result["contract_valid"])

    def test_manifest_duplicate_path_fails(self):
        item = {"path": "fixture.html", "sha256": self.sha("fixture.html"), "size_bytes": (self.root / "fixture.html").stat().st_size}
        result = gate.inspect_manifest({"schema": "design-qa-artifacts/v1", "artifacts": [item, item]}, self.root)
        self.assertFalse(result["contract_valid"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
