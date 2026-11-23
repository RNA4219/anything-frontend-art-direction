"""Contract tests for normal, error and boundary flows; no network or third-party dependencies."""

import copy
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


HERE = Path(__file__).resolve().parent
CHECKER = HERE.parent / "checks" / "check_flow.py"
spec = importlib.util.spec_from_file_location("check_flow", CHECKER)
check_flow = importlib.util.module_from_spec(spec)
spec.loader.exec_module(check_flow)


def fixture(name="booking"):
    return json.loads((HERE / "fixtures" / (name + ".json")).read_text(encoding="utf-8"))


def by_id(items, identifier):
    return next(item for item in items if item["id"] == identifier)


def codes(document):
    return {item["code"] for item in check_flow.validate(document)}


def local_transition(identifier, source, target):
    return {
        "id": identifier, "from": source, "to": target, "event": identifier,
        "actor": "user", "guard": "always", "effect": "local",
        "feedback": "現在の状態と次の操作を示す。", "preserves": [],
    }


class FlowContractTests(unittest.TestCase):
    def test_normal_booking_fixture(self):
        self.assertEqual(check_flow.validate(fixture()), [])

    def test_normal_report_fixture(self):
        self.assertEqual(check_flow.validate(fixture("report")), [])

    def test_non_object_roots_do_not_crash(self):
        for value in [None, [], "text", 42, True, 1.5]:
            with self.subTest(value=value):
                self.assertIn("TYPE", codes(value))

    def test_missing_required_root_field(self):
        doc = fixture()
        del doc["success_predicate"]
        self.assertIn("FIELD_REQUIRED", codes(doc))

    def test_unknown_field_is_not_silently_ignored(self):
        for scope in ["root", "states", "operations", "transitions", "scenarios"]:
            with self.subTest(scope=scope):
                doc = fixture()
                target = doc if scope == "root" else doc[scope][0]
                target["typo_feedback"] = "Never silently drop this field."
                self.assertIn("UNKNOWN_FIELD", codes(doc))

    def test_unknown_schema_is_rejected(self):
        doc = fixture()
        doc["schema"] = "ux-flow/v2"
        self.assertIn("SCHEMA_UNSUPPORTED", codes(doc))

    def test_empty_root_is_rejected(self):
        self.assertIn("FIELD_REQUIRED", codes({}))

    def test_required_text_is_not_whitespace(self):
        doc = fixture()
        doc["goal"] = " \n\t "
        self.assertIn("STRING_EMPTY", codes(doc))

    def test_object_arrays_reject_wrong_container_types(self):
        for name in ["operations", "states", "transitions", "scenarios"]:
            for value in [None, {}, "[]", True, 1]:
                with self.subTest(name=name, value=value):
                    doc = fixture()
                    doc[name] = value
                    self.assertIn("TYPE", codes(doc))

    def test_object_arrays_reject_non_objects(self):
        for name in ["operations", "states", "transitions", "scenarios"]:
            with self.subTest(name=name):
                doc = fixture()
                doc[name].append("invalid-object")
                self.assertIn("TYPE", codes(doc))

    def test_missing_per_object_fields(self):
        for name in ["operations", "states", "transitions", "scenarios"]:
            with self.subTest(name=name):
                doc = fixture()
                doc[name].append({})
                self.assertIn("FIELD_REQUIRED", codes(doc))

    def test_enum_wrong_types_do_not_crash(self):
        for name, field in [("states", "kind"), ("operations", "retry"), ("transitions", "effect"), ("transitions", "actor"), ("scenarios", "category")]:
            for value in [None, {}, [], 1, True]:
                with self.subTest(name=name, field=field, value=value):
                    doc = fixture()
                    doc[name][0][field] = value
                    self.assertIn("TYPE", codes(doc))

    def test_unsupported_enum_value(self):
        doc = fixture()
        doc["states"][0]["kind"] = "screen"
        self.assertIn("ENUM", codes(doc))

    def test_outcome_lookup_requires_real_boolean(self):
        for value in [0, 1, "true", "false", None, [], {}]:
            with self.subTest(value=value):
                doc = fixture()
                doc["operations"][0]["outcome_lookup"] = value
                self.assertIn("TYPE", codes(doc))

    def test_duplicate_ids_in_each_namespace(self):
        for name in ["operations", "states", "transitions", "scenarios"]:
            with self.subTest(name=name):
                doc = fixture()
                doc[name].append(copy.deepcopy(doc[name][0]))
                self.assertIn("DUPLICATE_ID", codes(doc))

    def test_missing_transition_references(self):
        for field in ["from", "to", "operation"]:
            with self.subTest(field=field):
                doc = fixture()
                by_id(doc["transitions"], "submit")[field] = "missing"
                self.assertIn("BAD_REFERENCE", codes(doc))

    def test_missing_entry_reference(self):
        doc = fixture()
        doc["entry_state"] = "missing"
        self.assertIn("BAD_REFERENCE", codes(doc))

    def test_wait_operation_reference(self):
        doc = fixture()
        by_id(doc["states"], "sending")["operation"] = "missing"
        self.assertIn("BAD_REFERENCE", codes(doc))

    def test_unreachable_state(self):
        doc = fixture()
        doc["states"].append({"id": "orphan", "kind": "exit", "description": "到達しない出口。", "reason": "仕様の不足。"})
        self.assertIn("UNREACHABLE_STATE", codes(doc))

    def test_nonterminal_dead_end(self):
        doc = fixture()
        doc["states"].append({"id": "trap", "kind": "task", "description": "操作がない。"})
        doc["transitions"].append(local_transition("to_trap", "edit", "trap"))
        self.assertIn("DEAD_END", codes(doc))
        self.assertIn("NO_TERMINAL_PATH", codes(doc))

    def test_closed_cycle_is_detected_with_other_success_path_present(self):
        doc = fixture()
        for identifier in ["trap_a", "trap_b"]:
            doc["states"].append({"id": identifier, "kind": "task", "description": "閉じた循環。"})
        doc["transitions"].extend([
            local_transition("enter_trap", "edit", "trap_a"),
            local_transition("trap_ab", "trap_a", "trap_b"),
            local_transition("trap_ba", "trap_b", "trap_a"),
        ])
        self.assertIn("CLOSED_CYCLE", codes(doc))
        self.assertIn("NO_TERMINAL_PATH", codes(doc))

    def test_closed_self_loop(self):
        doc = fixture()
        doc["states"].append({"id": "trap", "kind": "task", "description": "自分に戻るだけ。"})
        doc["transitions"].extend([local_transition("enter_trap", "edit", "trap"), local_transition("loop", "trap", "trap")])
        self.assertIn("CLOSED_CYCLE", codes(doc))

    def test_valid_edit_review_cycle_has_escape(self):
        doc = fixture()
        doc["scenarios"].append({
            "id": "review-and-edit", "category": "boundary",
            "path": ["review_input", "edit_again", "review_input", "submit", "accepted"],
            "expected_state": "confirmed", "assertions": ["編集内容を再確認する。"],
        })
        self.assertEqual(check_flow.validate(doc), [])

    def test_all_exit_flow_cannot_claim_completion(self):
        doc = fixture()
        completed = by_id(doc["states"], "confirmed")
        completed["kind"] = "exit"
        completed["reason"] = "目的を達成できなかった。"
        del completed["proof"]
        self.assertIn("NO_SUCCESS_STATE", codes(doc))

    def test_success_must_be_reachable(self):
        doc = fixture()
        doc["transitions"] = [t for t in doc["transitions"] if t["to"] != "confirmed"]
        self.assertIn("NO_REACHABLE_SUCCESS", codes(doc))

    def test_terminal_cannot_restart_same_task(self):
        doc = fixture()
        doc["transitions"].append(local_transition("restart", "confirmed", "edit"))
        self.assertIn("TERMINAL_OUTGOING", codes(doc))

    def test_success_proof_and_exit_reason_required(self):
        for identifier, field in [("confirmed", "proof"), ("left", "reason")]:
            with self.subTest(identifier=identifier):
                doc = fixture()
                del by_id(doc["states"], identifier)[field]
                self.assertIn("FIELD_REQUIRED", codes(doc))

    def test_wait_requires_system_response(self):
        doc = fixture()
        doc["transitions"] = [t for t in doc["transitions"] if not (t["from"] == "sending" and t["actor"] == "system")]
        self.assertIn("WAIT_NO_SYSTEM", codes(doc))

    def test_wait_requires_matching_timer_event(self):
        doc = fixture()
        by_id(doc["transitions"], "timed_out")["event"] = "wrong_deadline"
        self.assertIn("WAIT_NO_TIMEOUT", codes(doc))

    def test_timeout_actor_cannot_be_user(self):
        doc = fixture()
        by_id(doc["transitions"], "timed_out")["actor"] = "user"
        self.assertIn("WAIT_NO_TIMEOUT", codes(doc))

    def test_wait_policy_and_operation_required(self):
        for field in ["wait_policy", "operation", "timeout_event"]:
            with self.subTest(field=field):
                doc = fixture()
                del by_id(doc["states"], "sending")[field]
                self.assertIn("FIELD_REQUIRED", codes(doc))

    def test_timeout_self_loop_cannot_rely_only_on_system_success(self):
        doc = fixture("report")
        by_id(doc["transitions"], "deadline")["to"] = "generating"
        doc["transitions"] = [t for t in doc["transitions"] if t["id"] != "leave_running"]
        self.assertIn("WAIT_TIMEOUT_STUCK", codes(doc))

    def test_timeout_wait_loop_with_user_escape_is_allowed(self):
        doc = fixture("report")
        # An additional timer self-loop has an explicit user exit; it is not a trap.
        extra = copy.deepcopy(by_id(doc["transitions"], "deadline"))
        extra.update(id="timer_repeat", to="generating", guard="利用者が短い待機継続を選択済み")
        doc["transitions"].append(extra)
        self.assertEqual(check_flow.validate(doc), [])

    def test_timeout_recovery_bridge_is_not_an_escape(self):
        doc = fixture("report")
        doc["transitions"] = [t for t in doc["transitions"] if t["id"] not in {"lookup", "leave_slow", "leave_running"}]
        for scenario in doc["scenarios"]:
            if scenario["category"] == "boundary":
                scenario.update(path=["start", "deadline", "keep_waiting", "ready"], expected_state="ready")
        self.assertIn("WAIT_TIMEOUT_STUCK", codes(doc))

    def test_timeout_task_bridge_is_not_an_escape(self):
        doc = fixture("report")
        doc["transitions"] = [t for t in doc["transitions"] if t["id"] not in {"lookup", "leave_slow", "leave_running"}]
        by_id(doc["states"], "slow")["kind"] = "task"
        by_id(doc["transitions"], "keep_waiting").update(actor="system", event="reset_wait")
        for scenario in doc["scenarios"]:
            if scenario["category"] == "boundary":
                scenario.update(path=["start", "deadline", "keep_waiting", "ready"], expected_state="ready")
        self.assertIn("WAIT_TIMEOUT_STUCK", codes(doc))

    def test_timeout_recovery_can_reach_exit_through_task(self):
        doc = fixture("report")
        doc["transitions"] = [t for t in doc["transitions"] if t["id"] not in {"lookup", "leave_slow", "leave_running"}]
        by_id(doc["transitions"], "keep_waiting").update(to="configure", event="return_to_configuration")
        for scenario in doc["scenarios"]:
            if scenario["category"] == "boundary":
                scenario.update(path=["start", "deadline", "keep_waiting", "leave"], expected_state="left")
        self.assertEqual(check_flow.validate(doc), [])

    def test_recovery_requires_user_action_out_of_state(self):
        doc = fixture()
        for transition in doc["transitions"]:
            if transition["from"] == "unknown":
                transition["actor"] = "system"
        self.assertIn("RECOVERY_NO_USER_EXIT", codes(doc))

    def test_recovery_self_loop_is_not_recovery(self):
        doc = fixture()
        for transition in doc["transitions"]:
            if transition["from"] == "invalid":
                transition["to"] = "invalid"
        self.assertIn("RECOVERY_NO_USER_EXIT", codes(doc))

    def test_same_guard_branch_is_rejected(self):
        doc = fixture()
        extra = copy.deepcopy(by_id(doc["transitions"], "review_input"))
        extra.update(id="duplicate_branch", to="left")
        doc["transitions"].append(extra)
        self.assertIn("DUPLICATE_TRANSITION", codes(doc))

    def test_guard_outer_whitespace_does_not_hide_duplicate(self):
        doc = fixture()
        extra = copy.deepcopy(by_id(doc["transitions"], "review_input"))
        extra.update(id="duplicate_branch", guard="  " + extra["guard"] + "\n")
        doc["transitions"].append(extra)
        self.assertIn("DUPLICATE_TRANSITION", codes(doc))

    def test_distinct_guards_are_not_evaluated(self):
        doc = fixture()
        by_id(doc["transitions"], "validate_invalid")["guard"] = "A and not A"
        self.assertEqual(check_flow.validate(doc), [])
        self.assertTrue(any("guards are not evaluated" in line for line in check_flow.LIMITATIONS))

    def test_write_cannot_use_safe_read(self):
        doc = fixture()
        doc["operations"][0]["retry"] = "safe_read"
        self.assertIn("RETRY_UNSAFE_READ", codes(doc))

    def test_same_key_requires_server_key(self):
        for idempotency in ["none", "inherent"]:
            with self.subTest(idempotency=idempotency):
                doc = fixture()
                doc["operations"][0]["idempotency"] = idempotency
                self.assertIn("RETRY_NO_SERVER_KEY", codes(doc))

    def test_reconcile_first_requires_lookup(self):
        doc = fixture()
        doc["operations"][0].update(retry="reconcile_first", outcome_lookup=False)
        self.assertIn("RETRY_NO_LOOKUP", codes(doc))

    def test_reconcile_effect_requires_lookup(self):
        doc = fixture("report")
        doc["operations"][0]["outcome_lookup"] = False
        self.assertIn("RECONCILE_NO_LOOKUP", codes(doc))

    def test_server_write_cannot_reference_read_operation(self):
        doc = fixture()
        doc["operations"][0].update(side_effect="read", retry="safe_read", idempotency="inherent")
        self.assertIn("SIDE_EFFECT_MISMATCH", codes(doc))

    def test_server_cancel_requires_server_contract(self):
        for policy in ["local_only", "unavailable"]:
            with self.subTest(policy=policy):
                doc = fixture()
                doc["operations"][0]["cancel"] = policy
                self.assertIn("CANCEL_UNSUPPORTED", codes(doc))

    def test_server_effect_operation_is_required(self):
        doc = fixture()
        del by_id(doc["transitions"], "submit")["operation"]
        self.assertIn("FIELD_REQUIRED", codes(doc))

    def test_scenario_transition_reference(self):
        doc = fixture()
        doc["scenarios"][0]["path"][0] = "missing"
        self.assertIn("BAD_REFERENCE", codes(doc))

    def test_scenario_trace_starts_at_entry(self):
        doc = fixture()
        doc["scenarios"][0]["path"] = ["submit", "accepted"]
        self.assertIn("TRACE_DISCONTINUOUS", codes(doc))

    def test_scenario_trace_is_continuous(self):
        doc = fixture()
        doc["scenarios"][0]["path"] = ["review_input", "accepted"]
        self.assertIn("TRACE_DISCONTINUOUS", codes(doc))

    def test_scenario_expected_state_matches_trace(self):
        doc = fixture()
        doc["scenarios"][0]["expected_state"] = "left"
        self.assertIn("TRACE_FINAL_STATE", codes(doc))

    def test_all_three_evaluation_categories_are_required(self):
        for category in ["normal", "error", "boundary"]:
            with self.subTest(category=category):
                doc = fixture()
                doc["scenarios"] = [s for s in doc["scenarios"] if s["category"] != category]
                self.assertIn("MISSING_SCENARIO_CATEGORY", codes(doc))

    def test_path_and_assertions_cannot_be_empty(self):
        for field in ["path", "assertions"]:
            with self.subTest(field=field):
                doc = fixture()
                doc["scenarios"][0][field] = []
                self.assertIn("ARRAY_EMPTY", codes(doc))

    def test_text_arrays_validate_each_element(self):
        for value in [1, True, None, {}, [], " "]:
            with self.subTest(value=value):
                doc = fixture()
                doc["transitions"][0]["preserves"].append(value)
                self.assertTrue(codes(doc).intersection({"TYPE", "STRING_EMPTY"}))

    def test_long_valid_flow_does_not_hit_python_recursion_limit(self):
        doc = fixture("report")
        first = by_id(doc["transitions"], "start")
        first["to"] = "chain_0"
        for index in range(1100):
            source = f"chain_{index}"
            target = f"chain_{index+1}" if index < 1099 else "generating"
            doc["states"].append({"id": source, "kind": "task", "description": "境界テストの長い経路。"})
            doc["transitions"].append(local_transition(f"step_{index}", source, target))
        for scenario in doc["scenarios"]:
            expanded = []
            for step in scenario["path"]:
                expanded.append(step)
                if step == "start":
                    expanded.extend(f"step_{index}" for index in range(1100))
            scenario["path"] = expanded
        self.assertEqual(check_flow.validate(doc), [])

    def test_diagnostics_have_actionable_shape(self):
        result = check_flow.validate({})
        self.assertGreater(len(result), 0)
        for item in result:
            self.assertEqual(set(item), {"code", "location", "message"})
            self.assertTrue(all(isinstance(value, str) and value for value in item.values()))


class CommandLineTests(unittest.TestCase):
    def run_cli(self, value=None, *, raw=None, file_bytes=None, stdin=False):
        text = json.dumps(value, ensure_ascii=False) if raw is None else raw
        if stdin:
            return subprocess.run([sys.executable, str(CHECKER), "--json", "-"], input=text, capture_output=True, text=True)
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "flow.json"
            path.write_bytes(file_bytes if file_bytes is not None else text.encode("utf-8"))
            return subprocess.run([sys.executable, str(CHECKER), str(path), "--json"], capture_output=True, text=True)

    def assert_response(self, result, exit_code, status, code=None):
        self.assertEqual(result.returncode, exit_code, result.stderr + result.stdout)
        body = json.loads(result.stdout)
        self.assertEqual(body["status"], status)
        self.assertEqual(body["ok"], exit_code == 0)
        self.assertIn("limitations", body)
        if code:
            self.assertIn(code, {issue["code"] for issue in body["issues"]})
        self.assertNotIn("Traceback", result.stderr)
        return body

    def test_valid_json_exit_zero(self):
        self.assert_response(self.run_cli(fixture()), 0, "pass")

    def test_contract_error_exit_one(self):
        self.assert_response(self.run_cli({"schema": "wrong-version"}), 1, "fail", "SCHEMA_UNSUPPORTED")

    def test_syntactically_valid_non_object_is_contract_error(self):
        self.assert_response(self.run_cli([1, 2]), 1, "fail", "TYPE")

    def test_invalid_json_exit_two(self):
        self.assert_response(self.run_cli(raw="not JSON"), 2, "error", "JSON_DECODE")

    def test_empty_input_exit_two(self):
        for raw in ["", " \n\t"]:
            with self.subTest(raw=raw):
                self.assert_response(self.run_cli(raw=raw), 2, "error", "JSON_EMPTY")

    def test_trailing_json_is_not_silently_ignored(self):
        self.assert_response(self.run_cli(raw='{} {}'), 2, "error", "JSON_DECODE")

    def test_duplicate_json_keys_are_rejected_with_location(self):
        raw = json.dumps(fixture()).replace('"outcome_lookup": true', '"outcome_lookup": false, "outcome_lookup": true', 1)
        body = self.assert_response(self.run_cli(raw=raw), 1, "fail", "DUPLICATE_KEY")
        item = next(item for item in body["issues"] if item["code"] == "DUPLICATE_KEY")
        self.assertEqual(item["location"], "$.operations[0].outcome_lookup")

    def test_nonfinite_constants_are_not_valid_json(self):
        for constant in ["NaN", "Infinity", "-Infinity"]:
            with self.subTest(constant=constant):
                self.assert_response(self.run_cli(raw='{"x":' + constant + '}'), 2, "error", "JSON_DECODE")

    def test_invalid_unicode_is_input_error(self):
        self.assert_response(self.run_cli(file_bytes=b'\xff\xfe'), 2, "error", "INPUT_READ")

    def test_missing_file_is_input_error(self):
        with tempfile.TemporaryDirectory() as directory:
            result = subprocess.run([sys.executable, str(CHECKER), str(Path(directory) / "missing.json"), "--json"], capture_output=True, text=True)
        self.assert_response(result, 2, "error", "INPUT_READ")

    def test_missing_cli_argument_still_returns_json(self):
        result = subprocess.run([sys.executable, str(CHECKER), "--json"], capture_output=True, text=True)
        self.assert_response(result, 2, "error", "CLI_ARGUMENT")

    def test_stdin_is_supported(self):
        self.assert_response(self.run_cli(fixture("report"), stdin=True), 0, "pass")

    def test_deep_json_does_not_print_traceback(self):
        result = self.run_cli(raw="[" * 1500 + "0" + "]" * 1500)
        # Decoder depth limits vary across supported Python versions. A decoded
        # array is a schema error; a decoder depth rejection is an input error.
        self.assertIn(result.returncode, (1, 2))
        if result.returncode == 1:
            self.assert_response(result, 1, "fail", "TYPE")
        else:
            self.assert_response(result, 2, "error", "JSON_DECODE")


if __name__ == "__main__":
    unittest.main()
