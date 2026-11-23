#!/usr/bin/env python3
"""Check ux-flow/v1 structure; do not execute or interpret natural-language guards.

Exit codes: 0 = structurally valid, 1 = contract violation, 2 = input/CLI error.
This is a graph/contract checker, not an oracle for usability or backend guarantees.
Standard library only. Public API: validate(document) -> list[dict[str, str]].
"""

from __future__ import annotations

import argparse
from collections import defaultdict, deque
import json
from pathlib import Path
import sys


SCHEMA = "ux-flow/v1"
LIMITATIONS = [
    "Natural-language guards are not evaluated: graph reachability ignores guards.",
    "Backend idempotency, cancellation, receipts and lookup APIs are declarations, not verified facts.",
    "Passing this check does not establish task discoverability, WCAG conformance or user completion.",
    "normal/error/boundary scenarios are this skill's completion requirement; traces are not execution receipts.",
    "Timeout escape checks user/timer paths to success or explained exit; local system events are not distinguished from service responses.",
]
ROOT_FIELDS = {
    "schema", "id", "actor", "goal", "entry_condition", "entry_state",
    "success_predicate", "assumptions", "operations", "states", "transitions", "scenarios",
}
STATE_FIELDS = {
    "id", "kind", "description", "proof", "reason", "operation", "timeout_event", "wait_policy",
}
OP_FIELDS = {
    "id", "side_effect", "retry", "idempotency", "outcome_lookup", "cancel",
    "stale_response", "contract_evidence",
}
TRANSITION_FIELDS = {
    "id", "from", "to", "event", "actor", "guard", "effect", "operation", "feedback", "preserves",
}
SCENARIO_FIELDS = {"id", "category", "path", "expected_state", "assertions"}
KINDS = {"task", "wait", "recovery", "success", "exit"}
TERMINAL = ("success", "exit")
SERVER_EFFECTS = {"server_write", "reconcile", "server_cancel", "compensate"}


class _JSONObject(dict):
    """Preserve duplicate-key diagnostics instead of silently using the final key."""

    def __init__(self, pairs):
        super().__init__()
        self.duplicate_keys = []
        for key, value in pairs:
            if key in self:
                self.duplicate_keys.append(key)
            self[key] = value


def _json_path(parent, key):
    if type(key) is not str:
        return parent + "[" + repr(key) + "]"
    return parent + "." + key if key.isidentifier() else parent + "[" + json.dumps(key) + "]"


def _duplicate_keys(document):
    issues = []
    stack = [("$", document)]
    while stack:
        location, value = stack.pop()
        if isinstance(value, dict):
            for key in getattr(value, "duplicate_keys", []):
                issues.append({
                    "code": "DUPLICATE_KEY", "location": _json_path(location, key),
                    "message": "JSON object repeats this key; keep exactly one value.",
                })
            stack.extend((_json_path(location, key), child) for key, child in value.items())
        elif isinstance(value, list):
            stack.extend((f"{location}[{index}]", child) for index, child in enumerate(value))
    return issues


def _reachable(start, adjacency):
    seen = {start}
    queue = deque([start])
    while queue:
        for target in adjacency.get(queue.popleft(), ()):
            if target not in seen:
                seen.add(target)
                queue.append(target)
    return seen


def _components(nodes, adjacency):
    """Iterative Kosaraju: no recursion limit for long task graphs."""
    seen, order = set(), []
    for start in nodes:
        if start in seen:
            continue
        seen.add(start)
        stack = [(start, iter(adjacency.get(start, ())))]
        while stack:
            node, children = stack[-1]
            try:
                child = next(children)
            except StopIteration:
                order.append(node)
                stack.pop()
                continue
            if child not in seen:
                seen.add(child)
                stack.append((child, iter(adjacency.get(child, ()))))
    reverse = defaultdict(set)
    for source, targets in adjacency.items():
        for target in targets:
            reverse[target].add(source)
    seen.clear()
    for start in reversed(order):
        if start in seen:
            continue
        group, stack = set(), [start]
        seen.add(start)
        while stack:
            node = stack.pop()
            group.add(node)
            for parent in reverse.get(node, ()):
                if parent not in seen:
                    seen.add(parent)
                    stack.append(parent)
        yield group


def validate(document):
    """Return actionable issues for a decoded JSON value, including malformed shapes."""
    issues = _duplicate_keys(document)

    def issue(code, location, message):
        issues.append({"code": code, "location": location, "message": message})

    def fields(value, required, allowed, location):
        for key in sorted(required):
            if key not in value:
                issue("FIELD_REQUIRED", f"{location}.{key}", "Add the required field.")
        for key in sorted(set(value) - allowed, key=str):
            issue("UNKNOWN_FIELD", f"{location}.{key}", "Field is not part of ux-flow/v1; correct its name or remove it.")

    def string(value, location):
        if type(value) is not str:
            issue("TYPE", location, "Expected a string.")
            return False
        if not value.strip():
            issue("STRING_EMPTY", location, "Expected a non-empty, non-whitespace string.")
            return False
        return True

    def strings(value, location, nonempty=False):
        if type(value) is not list:
            issue("TYPE", location, "Expected an array of non-empty strings.")
            return False
        valid = True
        if nonempty and not value:
            issue("ARRAY_EMPTY", location, "At least one item is required.")
            valid = False
        for index, item in enumerate(value):
            valid = string(item, f"{location}[{index}]") and valid
        return valid

    def enum(value, options, location):
        if not string(value, location):
            return False
        if value not in options:
            issue("ENUM", location, "Use one of: " + ", ".join(sorted(options)) + ".")
            return False
        return True

    if not isinstance(document, dict):
        issue("TYPE", "$", "Expected a JSON object with schema ux-flow/v1.")
        return issues
    fields(document, ROOT_FIELDS, ROOT_FIELDS, "$")
    if "schema" in document:
        if not string(document["schema"], "$.schema"):
            return issues
        if document["schema"] != SCHEMA:
            issue("SCHEMA_UNSUPPORTED", "$.schema", "Supported schema is ux-flow/v1; no other version is interpreted.")
            return issues
    for key in ("id", "actor", "goal", "entry_condition", "entry_state", "success_predicate"):
        if key in document:
            string(document[key], f"$.{key}")
    if "assumptions" in document:
        strings(document["assumptions"], "$.assumptions")

    arrays = {}
    for name in ("operations", "states", "transitions", "scenarios"):
        value = document.get(name)
        arrays[name] = []
        if name not in document:
            continue
        if type(value) is not list:
            issue("TYPE", f"$.{name}", "Expected an array of objects.")
            continue
        if name in {"states", "scenarios"} and not value:
            issue("ARRAY_EMPTY", f"$.{name}", "At least one item is required.")
        for index, item in enumerate(value):
            location = f"$.{name}[{index}]"
            if not isinstance(item, dict):
                issue("TYPE", location, "Expected an object.")
                continue
            arrays[name].append((location, item))

    indexed = {}
    for name, items in arrays.items():
        indexed[name] = {}
        for location, item in items:
            if "id" not in item:
                continue  # The per-object required-field check supplies the diagnostic.
            identifier = item["id"]
            if type(identifier) is str and identifier.strip():
                if identifier in indexed[name]:
                    issue("DUPLICATE_ID", location + ".id", f"Duplicate {name} id {identifier!r}; choose a unique id.")
                else:
                    indexed[name][identifier] = (location, item)
    operations = indexed["operations"]
    states = indexed["states"]
    transitions = indexed["transitions"]

    for location, operation in arrays["operations"]:
        fields(operation, OP_FIELDS, OP_FIELDS, location)
        for key in ("id", "stale_response", "contract_evidence"):
            if key in operation:
                string(operation[key], f"{location}.{key}")
        for key, options in (
            ("side_effect", {"read", "write"}),
            ("retry", {"safe_read", "same_key", "reconcile_first", "never"}),
            ("idempotency", {"server_key", "inherent", "none"}),
            ("cancel", {"server_confirmed", "local_only", "unavailable"}),
        ):
            if key in operation:
                enum(operation[key], options, f"{location}.{key}")
        if "outcome_lookup" in operation and type(operation["outcome_lookup"]) is not bool:
            issue("TYPE", location + ".outcome_lookup", "Expected a JSON boolean, not 0, 1 or a string.")
        retry = operation.get("retry")
        if retry == "safe_read" and operation.get("side_effect") != "read":
            issue("RETRY_UNSAFE_READ", location + ".retry", "safe_read is only valid for a read operation; declare a write-safe policy.")
        if retry == "same_key" and operation.get("idempotency") != "server_key":
            issue("RETRY_NO_SERVER_KEY", location + ".idempotency", "same_key requires server_key and documented key scope/payload/expiry guarantees.")
        if retry == "reconcile_first" and operation.get("outcome_lookup") is not True:
            issue("RETRY_NO_LOOKUP", location + ".outcome_lookup", "reconcile_first requires a verified lookup API (true), otherwise use never.")

    for location, state in arrays["states"]:
        kind = state.get("kind")
        required = {"id", "kind", "description"}
        if kind == "success":
            required.add("proof")
        elif kind == "exit":
            required.add("reason")
        elif kind == "wait":
            required.update({"operation", "timeout_event", "wait_policy"})
        fields(state, required, STATE_FIELDS, location)
        for key in STATE_FIELDS - {"kind"}:
            if key in state:
                string(state[key], f"{location}.{key}")
        if "kind" in state:
            enum(kind, KINDS, location + ".kind")
        if "operation" in state and type(state["operation"]) is str and state["operation"] not in operations:
            issue("BAD_REFERENCE", location + ".operation", "Reference a defined operations[].id.")

    outgoing = defaultdict(list)
    adjacency = defaultdict(set)
    signatures = {}
    for location, transition in arrays["transitions"]:
        effect = transition.get("effect")
        required = TRANSITION_FIELDS - {"operation"}
        if type(effect) is str and effect in SERVER_EFFECTS:
            required = required | {"operation"}
        fields(transition, required, TRANSITION_FIELDS, location)
        for key in ("id", "from", "to", "event", "guard", "feedback", "operation"):
            if key in transition:
                string(transition[key], f"{location}.{key}")
        if "actor" in transition:
            enum(transition["actor"], {"user", "system", "timer"}, location + ".actor")
        if "effect" in transition:
            enum(effect, {"none", "local"} | SERVER_EFFECTS, location + ".effect")
        if "preserves" in transition:
            strings(transition["preserves"], location + ".preserves")
        for key in ("from", "to"):
            if key in transition and type(transition[key]) is str and transition[key] not in states:
                issue("BAD_REFERENCE", f"{location}.{key}", "Reference a defined states[].id.")
        op_id = transition.get("operation")
        if type(op_id) is str:
            if op_id not in operations:
                issue("BAD_REFERENCE", location + ".operation", "Reference a defined operations[].id.")
            else:
                operation = operations[op_id][1]
                if effect in ("server_write", "compensate") and operation.get("side_effect") != "write":
                    issue("SIDE_EFFECT_MISMATCH", location + ".operation", "This effect requires an operation declared as write.")
                if effect == "reconcile" and operation.get("outcome_lookup") is not True:
                    issue("RECONCILE_NO_LOOKUP", location + ".operation", "A reconcile effect requires outcome_lookup=true on the referenced operation.")
                if effect == "server_cancel" and operation.get("cancel") != "server_confirmed":
                    issue("CANCEL_UNSUPPORTED", location + ".operation", "server_cancel requires a server_confirmed cancellation contract, not local-only cancellation.")
        source, target = transition.get("from"), transition.get("to")
        if type(source) is str and type(target) is str and source in states and target in states:
            outgoing[source].append((location, transition))
            adjacency[source].add(target)
        signature_fields = [transition.get(key) for key in ("from", "event", "actor", "guard")]
        if all(type(value) is str and value.strip() for value in signature_fields):
            signature = tuple(value.strip() for value in signature_fields)
            if signature in signatures:
                issue("DUPLICATE_TRANSITION", location, "Same from/event/actor/guard as " + signatures[signature] + "; remove the duplicate or provide genuinely exclusive guards.")
            else:
                signatures[signature] = location

    entry = document.get("entry_state")
    reached = set()
    if type(entry) is str:
        if entry not in states:
            issue("BAD_REFERENCE", "$.entry_state", "Reference a defined states[].id.")
        else:
            reached = _reachable(entry, adjacency)
            for state_id, (location, _) in states.items():
                if state_id not in reached:
                    issue("UNREACHABLE_STATE", location + ".id", "State cannot be reached from entry_state even when guards are ignored.")
    successes = {sid for sid, (_, state) in states.items() if state.get("kind") == "success"}
    if not successes:
        issue("NO_SUCCESS_STATE", "$.states", "Include at least one success state with observable proof; an all-exit flow is incomplete.")
    elif type(entry) is str and entry in states and not successes.intersection(reached):
        issue("NO_REACHABLE_SUCCESS", "$.entry_state", "No success state is reachable from the entry; record the blocker and hold the task.")

    terminal = {sid for sid, (_, state) in states.items() if state.get("kind") in TERMINAL}
    reverse = defaultdict(set)
    for source, targets in adjacency.items():
        for target in targets:
            reverse[target].add(source)
    can_finish = set(terminal)
    queue = deque(terminal)
    while queue:
        for parent in reverse.get(queue.popleft(), ()):
            if parent not in can_finish:
                can_finish.add(parent)
                queue.append(parent)
    for state_id, (location, state) in states.items():
        kind = state.get("kind")
        edges = outgoing.get(state_id, [])
        if kind in TERMINAL and edges:
            issue("TERMINAL_OUTGOING", location, "success/exit ends this task; move subsequent work to a separate flow contract.")
        elif kind not in TERMINAL and not edges:
            issue("DEAD_END", location, "Non-terminal state has no valid outgoing transition; provide continuation, recovery or explained exit.")
        if state_id not in can_finish:
            issue("NO_TERMINAL_PATH", location, "No path leads to success or explained exit, even ignoring guards.")
        if kind == "recovery" and not any(t.get("actor") == "user" and t.get("to") != state_id for _, t in edges):
            issue("RECOVERY_NO_USER_EXIT", location, "Provide an actionable user transition to retry, reconcile, edit or leave this recovery state.")
        if kind != "wait":
            continue
        if not any(t.get("actor") == "system" for _, t in edges):
            issue("WAIT_NO_SYSTEM", location, "A wait state requires a system-response transition in addition to its timeout.")
        timer_edges = [(tl, t) for tl, t in edges if t.get("actor") == "timer" and t.get("event") == state.get("timeout_event")]
        if not timer_edges:
            issue("WAIT_NO_TIMEOUT", location + ".timeout_event", "Add a timer transition from this wait state with exactly this timeout_event.")
        for timer_location, timer_transition in timer_edges:
            # After a deadline, escape must not depend solely on the missing system response.
            pending, seen, escape = [timer_transition["to"]], set(), False
            while pending and not escape:
                current = pending.pop()
                if current in seen:
                    continue
                seen.add(current)
                # A recovery/task bridge can lead straight back to the same wait.
                # Only reaching a terminal counts as ending the wait without a
                # service response; guards are still not evaluated here.
                if states[current][1].get("kind") in TERMINAL:
                    escape = True
                    break
                for _, follow in outgoing.get(current, []):
                    if follow.get("actor") in ("user", "timer"):
                        pending.append(follow["to"])
            if not escape:
                issue("WAIT_TIMEOUT_STUCK", timer_location + ".to", "No user/timer path from timeout reaches success or explained exit. A recovery/task state that only returns to waiting is not an escape; system-only local paths need separate review.")

    for group in _components(states, adjacency):
        cyclical = len(group) > 1 or any(node in adjacency.get(node, ()) for node in group)
        exits = any(target not in group for node in group for target in adjacency.get(node, ()))
        if cyclical and not exits:
            representative = sorted(group)[0]
            issue("CLOSED_CYCLE", states[representative][0], "Cycle has no outgoing escape: " + ", ".join(sorted(group)) + ". Add a reachable success/recovery/exit path.")

    categories = set()
    for location, scenario in arrays["scenarios"]:
        fields(scenario, SCENARIO_FIELDS, SCENARIO_FIELDS, location)
        for key in ("id", "expected_state"):
            if key in scenario:
                string(scenario[key], f"{location}.{key}")
        category = scenario.get("category")
        if "category" in scenario and enum(category, {"normal", "error", "boundary"}, location + ".category"):
            categories.add(category)
        if "assertions" in scenario:
            strings(scenario["assertions"], location + ".assertions", nonempty=True)
        expected = scenario.get("expected_state")
        if type(expected) is str and expected not in states:
            issue("BAD_REFERENCE", location + ".expected_state", "Reference a defined states[].id.")
        if "path" not in scenario or not strings(scenario["path"], location + ".path", nonempty=True):
            continue
        current, continuous = entry, True
        for index, transition_id in enumerate(scenario["path"]):
            step_location = f"{location}.path[{index}]"
            if transition_id not in transitions:
                issue("BAD_REFERENCE", step_location, "Reference a defined transitions[].id.")
                continuous = False
                break
            transition = transitions[transition_id][1]
            if transition.get("from") != current:
                issue("TRACE_DISCONTINUOUS", step_location, f"Trace is at {current!r}, but {transition_id!r} starts at {transition.get('from')!r}.")
                continuous = False
                break
            current = transition.get("to")
        if continuous and current != expected:
            issue("TRACE_FINAL_STATE", location + ".expected_state", f"Trace ends at {current!r}; update the path or expected_state.")
    for category in sorted({"normal", "error", "boundary"} - categories):
        issue("MISSING_SCENARIO_CATEGORY", "$.scenarios", f"Add a {category} scenario for the skill's complete ux-flow/v1 evaluation contract.")
    return issues


def _result(issues, status):
    return {"schema": "ux-flow-check/v1", "status": status, "ok": not issues, "issues": issues, "limitations": LIMITATIONS}


def _emit(issues, status, as_json):
    if as_json:
        print(json.dumps(_result(issues, status), ensure_ascii=False, indent=2))
    else:
        print(f"{status.upper()}: {len(issues)} issue(s)")
        for item in issues:
            print(f"{item['code']} {item['location']}: {item['message']}")
        print("Scope: structure only; natural-language guards and backend guarantees are not evaluated.")


class _ArgumentParser(argparse.ArgumentParser):
    def error(self, message):
        raise ValueError(message)


def main(argv=None):
    args_list = list(sys.argv[1:] if argv is None else argv)
    parser = _ArgumentParser(description=__doc__)
    parser.add_argument("file", help="Flow JSON file; use - for standard input.")
    parser.add_argument("--json", action="store_true", help="Emit machine-readable diagnostics.")
    try:
        args = parser.parse_args(args_list)
    except ValueError as exc:
        _emit([{"code": "CLI_ARGUMENT", "location": "$", "message": str(exc)}], "error", "--json" in args_list)
        return 2
    try:
        raw = sys.stdin.read() if args.file == "-" else Path(args.file).read_text(encoding="utf-8")
    except (OSError, UnicodeError) as exc:
        _emit([{"code": "INPUT_READ", "location": "$", "message": str(exc)}], "error", args.json)
        return 2
    if not raw.strip():
        _emit([{"code": "JSON_EMPTY", "location": "$", "message": "The input is empty; supply a ux-flow/v1 JSON document."}], "error", args.json)
        return 2

    def reject_constant(value):
        raise ValueError("Non-finite JSON constant is not allowed: " + value)

    try:
        document = json.loads(raw, object_pairs_hook=_JSONObject, parse_constant=reject_constant)
    except (ValueError, RecursionError) as exc:
        location = "$"
        if isinstance(exc, json.JSONDecodeError):
            location = f"line {exc.lineno}, column {exc.colno}"
        _emit([{"code": "JSON_DECODE", "location": location, "message": str(exc)}], "error", args.json)
        return 2
    issues = validate(document)
    _emit(issues, "fail" if issues else "pass", args.json)
    return 1 if issues else 0


if __name__ == "__main__":
    raise SystemExit(main())
