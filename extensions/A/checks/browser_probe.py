#!/usr/bin/env python3
"""Bounded, local-only browser checks for an A projection HTML document.

Usage: browser_probe.py --html PATH --output-dir DIR [--timeout-seconds 90]

The checks describe observable DOM, values, navigation, and layout.  They are
not a semantic UX success rate.  Chromium's sandbox is mandatory; launch
failure is recorded and is never retried with weaker browser security.
"""

from __future__ import annotations

import argparse
import asyncio
from collections import Counter, deque
from datetime import datetime, timezone
import hashlib
import json
import multiprocessing
import os
from pathlib import Path
import re
import signal
import sys
import time
import traceback
from typing import Any
from urllib.parse import unquote, urlsplit


MAX_TIMEOUT_SECONDS = 300
RESULT_NAME = "browser_probe_result.json"
VIEWPORTS = (("desktop", 1440, 900), ("mobile", 390, 844))
MODES = ("normal", "empty", "single", "many")


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def safe_token(value: Any, fallback: str) -> str:
    raw = str(value)
    token = re.sub(r"[^A-Za-z0-9._-]+", "-", raw).strip(".-")
    if not token or token != raw or len(token) > 48:
        token = (token[:36] or fallback) + "-" + hashlib.sha256(raw.encode()).hexdigest()[:8]
    return token


def attr_selector(name: str, value: Any) -> str:
    # CSS string escaping is independent of JSON or shell escaping.
    escaped = "".join(
        f"\\{ord(char):x} " if ord(char) < 32 or char in '\\"' else char
        for char in str(value)
    )
    return f'[{name}="{escaped}"]'


def write_result(path: Path, report: dict[str, Any]) -> None:
    report["summary"] = {
        "checks_by_status": dict(Counter(item["status"] for item in report["checks"])),
        "page_error_count": len(report["page_errors"]),
        "blocked_request_count": len(report["network"]["blocked_requests"]),
        "screenshot_count": len(report["screenshots"]),
        "primary_cells_compared": sum(
            item.get("compared_cells", 0)
            for item in report["checks"]
            if item["check"] == "primary_values"
        ),
        "semantic_ux_success_rate": None,
    }
    temporary = path.with_name(path.name + ".tmp")
    temporary.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    os.replace(temporary, path)


def initial_report(html: Path, timeout_seconds: float) -> dict[str, Any]:
    return {
        "schema_version": "1.0",
        "probe_kind": "rendering_and_structure",
        "interpretation": (
            "Counts report observed structural/rendering checks only. Unreachable declarations, "
            "zero primary fields, and zero records are recorded explicitly; no semantic UX "
            "success rate is calculated."
        ),
        "started_at": utc_now(),
        "finished_at": None,
        "html": {"path": str(html)},
        "case_id": None,
        "configuration": {
            "timeout_seconds": timeout_seconds,
            "maximum_timeout_seconds": MAX_TIMEOUT_SECONDS,
            "termination_grace_seconds": 2,
            "chromium_executable": "/usr/bin/chromium",
            "chromium_sandbox": True,
            "sandbox_downgrade_attempted": False,
            "viewports": [{"name": name, "width": width, "height": height} for name, width, height in VIEWPORTS],
            "data_modes": list(MODES),
        },
        "execution": {"status": "starting", "current": {}},
        "network": {
            "allowed_document": html.as_uri(),
            "allowed_schemes": ["data", "blob"],
            "offline_context": True,
            "blocked_requests": [],
        },
        "checks": [],
        "coverage": [],
        "page_errors": [],
        "screenshots": [],
    }


class Probe:
    def __init__(self, config: dict[str, Any], report: dict[str, Any]) -> None:
        self.html = Path(config["html"])
        self.output_dir = Path(config["output_dir"])
        self.result_path = self.output_dir / RESULT_NAME
        self.report = report
        self.deadline = time.monotonic() + config["timeout_seconds"]
        self.current: dict[str, Any] = {}
        self.brief: dict[str, Any] = {}
        self.plan: dict[str, Any] = {}
        self.roles: list[str] = []
        self.screens: list[dict[str, Any]] = []
        self.by_screen: dict[str, dict[str, Any]] = {}
        self.navigation: list[dict[str, Any]] = []
        self.features: dict[str, dict[str, Any]] = {}
        self.content: list[dict[str, Any]] = []
        self.display_content: list[dict[str, dict[str, str]]] = []
        self.screenshot_keys: set[tuple[str, str, str]] = set()
        self.nav_checked: set[tuple[str, str, str, str | None]] = set()

    def timeout_ms(self, cap: int = 3000) -> int:
        remaining = self.deadline - time.monotonic()
        if remaining <= 0:
            raise asyncio.TimeoutError("The probe time budget was exhausted")
        return max(1, min(cap, int(remaining * 1000)))

    def set_current(self, **values: Any) -> None:
        self.current.update(values)
        self.report["execution"]["current"] = dict(self.current)

    def add(self, check: str, status: str, **details: Any) -> None:
        self.report["checks"].append({"check": check, "status": status, **self.current, **details})

    def save(self) -> None:
        write_result(self.result_path, self.report)

    async def active(self, page: Any) -> list[str]:
        return await page.locator("#screen-root [data-screen-id]").evaluate_all(
            "els => els.map(el => el.getAttribute('data-screen-id'))"
        )

    async def status(self, page: Any) -> list[dict[str, str]]:
        return await page.locator("[data-projection-status]").evaluate_all(
            "els => els.map(el => ({code: el.getAttribute('data-projection-status'), text: el.textContent || ''}))"
        )

    async def has_status(self, page: Any, expected: str) -> tuple[bool, list[dict[str, str]]]:
        statuses = await self.status(page)
        return any(item["code"] == expected or expected in item["text"] for item in statuses), statuses

    async def load_payload(self, page: Any) -> bool:
        scripts = page.locator('script#plan-data[type="application/json"]')
        count = await scripts.count()
        if count != 1:
            self.add("payload", "error", reason="expected_one_plan_data_script", observed_count=count)
            return False
        try:
            payload = json.loads(await scripts.text_content())
        except (TypeError, ValueError) as exc:
            self.add("payload", "error", reason="invalid_json", error=str(exc))
            return False
        if not isinstance(payload, dict) or not isinstance(payload.get("brief"), dict) or not isinstance(payload.get("plan"), dict):
            self.add("payload", "error", reason="expected_brief_and_plan_objects")
            return False
        self.brief, self.plan = payload["brief"], payload["plan"]
        required = {
            "brief.roles": self.brief.get("roles"),
            "brief.content": self.brief.get("content"),
            "plan.screens": self.plan.get("screens"),
            "plan.navigation": self.plan.get("navigation"),
            "plan.features": self.plan.get("features"),
        }
        invalid = [name for name, value in required.items() if not isinstance(value, list)]
        if invalid:
            self.add("payload", "error", reason="expected_lists", fields=invalid)
            return False
        invalid_records = [name for name, value in required.items() if any(not isinstance(item, dict) for item in value)]
        if invalid_records:
            self.add("payload", "error", reason="expected_object_records", fields=invalid_records)
            return False
        invalid_ids = [
            name for name, records in (("roles", self.brief["roles"]), ("screens", self.plan["screens"]), ("features", self.plan["features"]))
            if any(not isinstance(item.get("id"), str) for item in records)
        ]
        if invalid_ids:
            self.add("payload", "error", reason="expected_string_ids", fields=invalid_ids)
            return False
        self.roles = [role["id"] for role in self.brief["roles"]]
        self.screens = self.plan["screens"]
        self.navigation = self.plan["navigation"]
        self.content = self.brief["content"]
        for screen in self.screens:
            if not all(isinstance(screen.get(key), list) for key in ("roles", "entry_for", "information", "feature_ids")):
                self.add("payload", "error", reason="invalid_screen_lists", screen_id=screen["id"])
                return False
            if any(not isinstance(info, dict) or not isinstance(info.get("id"), str) or info.get("visibility") not in ("primary", "secondary") for info in screen["information"]):
                self.add("payload", "error", reason="invalid_information_declarations", screen_id=screen["id"])
                return False
            self.by_screen.setdefault(screen["id"], screen)
        for index, edge in enumerate(self.navigation):
            if not isinstance(edge.get("from"), str) or not isinstance(edge.get("to"), str) or not isinstance(edge.get("roles"), list):
                self.add("payload", "error", reason="invalid_navigation_declaration", nav_index=index)
                return False
        for feature in self.plan["features"]:
            self.features.setdefault(feature["id"], feature)
        for name, ids in (("role", self.roles), ("screen", [screen["id"] for screen in self.screens]), ("feature", [feature["id"] for feature in self.plan["features"]])):
            duplicates = [key for key, count in Counter(ids).items() if count > 1]
            if duplicates:
                self.add("duplicate_declarations", "diagnostic", kind=name, ids=duplicates, resolution="first_declaration_only_for_traversal")
        self.report["case_id"] = self.brief.get("case_id", self.plan.get("case_id", "case"))
        self.add("payload", "pass", role_count=len(self.roles), screen_count=len(self.screens), content_count=len(self.content), navigation_count=len(self.navigation))
        # The renderer contract specifies JSON.stringify for non-string values.
        # Compute the reference strings independently from the rendered cells.
        self.display_content = await page.evaluate(
            """records => records.map(row => Object.fromEntries(Object.entries(row).map(([key, value]) => [key, {
                state: value === null || value === undefined || value === '' ? 'missing' : 'provided',
                text: value === null || value === undefined || value === '' ? '' : typeof value === 'string' ? value : JSON.stringify(value)
            }])))""", self.content
        )
        return True

    def entries(self, role: str) -> list[dict[str, Any]]:
        return [screen for screen in self.screens if role in screen["entry_for"]]

    def paths(self, role: str) -> dict[str, tuple[str, list[int]]]:
        paths: dict[str, tuple[str, list[int]]] = {}
        queue: deque[str] = deque()
        for screen in self.entries(role):
            if role in screen["roles"] and screen["id"] not in paths:
                paths[screen["id"]] = (screen["id"], [])
                queue.append(screen["id"])
        while queue:
            source = queue.popleft()
            start, preceding = paths[source]
            for index, edge in enumerate(self.navigation):
                target = self.by_screen.get(edge["to"])
                if edge["from"] == source and role in edge["roles"] and target is not None and role in target["roles"] and edge["to"] not in paths:
                    paths[edge["to"]] = (start, preceding + [index])
                    queue.append(edge["to"])
        return paths

    async def select_role(self, page: Any, role: str) -> bool:
        self.set_current(role=role, data_mode="normal", screen_id=None, phase="select_role")
        control = page.locator('select[data-harness="role"]')
        if await control.count() != 1:
            self.add("role_control", "fail", reason="expected_one_role_select")
            return False
        try:
            await control.select_option(value=role, timeout=self.timeout_ms())
        except Exception as exc:
            self.add("role_control", "fail", error=str(exc)[:2500])
            return False
        entries = self.entries(role)
        first = entries[0] if entries else None
        expected = [first["id"]] if first and role in first["roles"] else []
        observed = await self.active(page)
        details: dict[str, Any] = {"expected_active_ids": expected, "observed_active_ids": observed}
        valid = observed == expected
        if first and role not in first["roles"]:
            rejected, statuses = await self.has_status(page, "access-denied")
            valid = valid and rejected
            details["projection_status"] = statuses
        if not entries:
            details["reason"] = "no_declared_entry_for_role"
        self.add("role_initial_entry", "pass" if valid else "fail", **details)
        self.set_current(screen_id=observed[0] if len(observed) == 1 else None)
        return True

    async def click_entry(self, page: Any, role: str, screen_id: str, purpose: str) -> bool:
        self.set_current(phase=purpose)
        before = await self.active(page)
        buttons = page.locator("button" + attr_selector("data-entry-screen", screen_id))
        count = await buttons.count()
        if count != 1:
            self.add("entry_click", "fail", entry_screen=screen_id, purpose=purpose, reason="expected_one_entry_button", observed_count=count)
            return False
        try:
            await buttons.click(timeout=self.timeout_ms())
        except Exception as exc:
            self.add("entry_click", "fail", entry_screen=screen_id, purpose=purpose, error=str(exc)[:2500])
            return False
        screen = self.by_screen.get(screen_id)
        allowed = screen is not None and role in screen["roles"]
        expected = [screen_id] if allowed else before
        observed = await self.active(page)
        valid = observed == expected
        details: dict[str, Any] = {"entry_screen": screen_id, "purpose": purpose, "expected_active_ids": expected, "observed_active_ids": observed}
        if not allowed:
            rejected, statuses = await self.has_status(page, "access-denied" if screen else "missing-target")
            valid = valid and rejected
            details["projection_status"] = statuses
        self.add("entry_click", "pass" if valid else "fail", **details)
        self.set_current(screen_id=observed[0] if len(observed) == 1 else None)
        return valid and allowed

    async def check_navigation_visibility(self, page: Any, role: str) -> None:
        active = await self.active(page)
        screen_id = active[0] if len(active) == 1 else None
        key = (self.current["viewport"], role, self.current["data_mode"], screen_id)
        if key in self.nav_checked:
            return
        self.nav_checked.add(key)
        observed = await page.locator("a[data-nav-index]").evaluate_all(
            "els => els.map(el => ({index: el.getAttribute('data-nav-index'), from: el.getAttribute('data-from'), to: el.getAttribute('data-to')}))"
        )
        expected = [
            {"index": str(index), "from": edge["from"], "to": edge["to"]}
            for index, edge in enumerate(self.navigation)
            if edge["from"] == screen_id and role in edge["roles"]
        ]
        self.add("navigation_visibility", "pass" if observed == expected else "fail", screen_id=screen_id, expected=expected, observed=observed)

    async def click_edge(self, page: Any, role: str, index: int, purpose: str) -> bool:
        edge = self.navigation[index]
        self.set_current(phase=purpose, screen_id=edge["from"])
        before = await self.active(page)
        if before != [edge["from"]]:
            self.add("navigation_click", "fail", nav_index=index, purpose=purpose, reason="source_not_active", observed_active_ids=before)
            return False
        await self.check_navigation_visibility(page, role)
        links = page.locator("a" + attr_selector("data-nav-index", index))
        count = await links.count()
        if count != 1:
            self.add("navigation_click", "fail", nav_index=index, purpose=purpose, reason="expected_one_navigation_link", observed_count=count)
            return False
        try:
            await links.click(timeout=self.timeout_ms())
        except Exception as exc:
            self.add("navigation_click", "fail", nav_index=index, purpose=purpose, error=str(exc)[:2500])
            return False
        target = self.by_screen.get(edge["to"])
        denial = "missing-target" if target is None else "access-denied" if role not in target["roles"] else None
        expected = before if denial else [edge["to"]]
        observed = await self.active(page)
        valid = observed == expected
        details: dict[str, Any] = {
            "nav_index": index, "purpose": purpose, "from": edge["from"], "to": edge["to"],
            "expected_active_ids": expected, "observed_active_ids": observed,
        }
        if denial:
            rejected, statuses = await self.has_status(page, denial)
            valid = valid and rejected
            details.update(expected_status=denial, projection_status=statuses)
        self.add("navigation_click", "pass" if valid else "fail", **details)
        self.set_current(screen_id=observed[0] if len(observed) == 1 else None)
        return valid and denial is None

    async def reach(self, page: Any, role: str, screen_id: str, paths: dict[str, tuple[str, list[int]]]) -> bool:
        entry, edges = paths[screen_id]
        if not await self.click_entry(page, role, entry, "bfs_entry"):
            return False
        for index in edges:
            if not await self.click_edge(page, role, index, "bfs_path"):
                self.add("bfs_path", "fail", target_screen=screen_id, entry_screen=entry, path=edges, failed_nav_index=index)
                return False
        return await self.active(page) == [screen_id]

    def record_indices(self, mode: str) -> list[int]:
        if mode == "empty" or not self.content:
            return []
        if mode == "single":
            return [0]
        if mode == "many":
            return [index % len(self.content) for index in range(40)]
        return list(range(len(self.content)))

    async def check_values(self, page: Any, screen: dict[str, Any], mode: str) -> None:
        self.set_current(screen_id=screen["id"], phase="values")
        observed = await page.locator("#screen-root [data-screen-id]").evaluate_all(
            """screens => {
                const root = screens[0];
                if (screens.length !== 1 || !root) return {activeCount: screens.length, cells: [], rows: [], details: [], features: []};
                const clipped = el => [el, ...el.querySelectorAll('*')].some(node => {
                    const s = getComputedStyle(node);
                    const horizontal = node.scrollWidth > node.clientWidth + 1;
                    const vertical = node.scrollHeight > node.clientHeight + 1;
                    return (horizontal && (['hidden','clip'].includes(s.overflowX) || s.textOverflow === 'ellipsis')) ||
                           (vertical && (['hidden','clip'].includes(s.overflowY) || (s.webkitLineClamp !== 'none' && s.webkitLineClamp !== '0')));
                });
                return {
                    activeCount: screens.length,
                    cells: [...root.querySelectorAll('td[data-information-id]')].map(el => ({
                        information_id: el.getAttribute('data-information-id'), row_index: el.getAttribute('data-row-index'),
                        value_state: el.getAttribute('data-value-state'), visibility: el.getAttribute('data-visibility'),
                        text: el.textContent || '', in_secondary_details: !!el.closest('details[data-secondary]'),
                        clipped: clipped(el)
                    })),
                    rows: [...root.querySelectorAll('tr[data-content-row]')].map(el => ({visibility: el.getAttribute('data-visibility'), row_index: el.getAttribute('data-row-index')})),
                    details: [...root.querySelectorAll('details[data-secondary]')].map(el => ({open: el.open})),
                    features: [...root.querySelectorAll('li[data-feature-id]')].map(el => ({id: el.getAttribute('data-feature-id'), text: el.textContent || ''}))
                };
            }"""
        )
        indices = self.record_indices(mode)
        unknown_cells = [cell for cell in observed["cells"] if cell["visibility"] not in ("primary", "secondary")]
        self.add("cell_visibility_attributes", "fail" if unknown_cells else "pass", invalid_cells=unknown_cells)
        for visibility in ("primary", "secondary"):
            information = [info for info in screen["information"] if info["visibility"] == visibility]
            cells = [cell for cell in observed["cells"] if cell["visibility"] == visibility]
            rows = [row for row in observed["rows"] if row["visibility"] == visibility]
            expected_row_count = len(indices) if information else 0
            self.add("content_rows", "pass" if len(rows) == expected_row_count else "fail", visibility=visibility, expected_rows=expected_row_count, observed_rows=len(rows), source_records=len(self.content), repeated_real_records=(mode == "many" and bool(self.content)))
            expected = []
            for row_index, source_index in enumerate(indices):
                for info in information:
                    value = self.display_content[source_index].get(info["id"], {"state": "missing", "text": ""})
                    expected.append({"information_id": info["id"], "row_index": str(row_index), "value_state": value["state"], "text": value["text"]})
            mismatches = []
            for index in range(max(len(expected), len(cells))):
                wanted = expected[index] if index < len(expected) else None
                actual = cells[index] if index < len(cells) else None
                if wanted is None or actual is None:
                    mismatches.append({"cell_index": index, "expected": wanted, "observed": actual, "reason": "cell_count"})
                    continue
                attributes_match = all(actual[key] == wanted[key] for key in ("information_id", "row_index", "value_state"))
                text_matches = actual["text"] == wanted["text"] if wanted["value_state"] == "provided" else "未提供" in actual["text"]
                if not attributes_match or not text_matches:
                    mismatches.append({"cell_index": index, "expected": wanted, "observed": actual, "reason": "attributes_or_value"})
            reason = "no_primary_information_declared" if visibility == "primary" and not information else "no_secondary_information_declared" if not information else "no_content_records_in_scenario" if not indices else None
            check_status = "fail" if mismatches else "diagnostic" if reason else "pass"
            self.add(visibility + "_values", check_status, declared_information_ids=[info["id"] for info in information], expected_cells=len(expected), observed_cells=len(cells), compared_cells=min(len(expected), len(cells)), reason=reason, mismatches=mismatches, zero_values_compared=sum(item["value_state"] == "provided" and item["text"] == "0" for item in expected), false_values_compared=sum(item["value_state"] == "provided" and item["text"] == "false" for item in expected), longest_provided_value_length=max((len(item["text"]) for item in expected if item["value_state"] == "provided"), default=0))
            if visibility == "primary":
                titles = [(index, item) for index, item in enumerate(expected) if item["information_id"] == "title" and item["value_state"] == "provided"]
                if titles:
                    index, longest = max(titles, key=lambda item: len(item[1]["text"]))
                    actual = cells[index] if index < len(cells) else None
                    valid = actual is not None and actual["text"] == longest["text"] and not actual["clipped"]
                    self.add("longest_primary_title", "pass" if valid else "fail", row_index=longest["row_index"], expected_length=len(longest["text"]), expected_text=longest["text"], observed=actual, selection="longest_provided_title_in_this_scenario_without_a_length_threshold")
        primary = [cell for cell in observed["cells"] if cell["visibility"] == "primary"]
        clipped_primary = [cell for cell in primary if cell["clipped"]]
        self.add("primary_text_not_clipped", "fail" if clipped_primary else "pass" if primary else "diagnostic", checked_cells=len(primary), clipped_cells=clipped_primary, reason=None if primary else "no_primary_cells")
        secondary = [cell for cell in observed["cells"] if cell["visibility"] == "secondary"]
        secondary_valid = all(cell["in_secondary_details"] for cell in secondary) and not any(detail["open"] for detail in observed["details"]) and not any(cell["in_secondary_details"] for cell in primary)
        self.add("secondary_disclosure", "pass" if secondary_valid else "fail", secondary_cells=len(secondary), details=observed["details"], cells_outside_details=[cell for cell in secondary if not cell["in_secondary_details"]])
        # Compare the raw declared projection. A noncanonical declaration is a
        # separate plan diagnostic, not a request for the renderer to repair it.
        expected_features = [
            {"id": feature_id, "text": (self.features[feature_id].get("label") or "未提供")
             if feature_id in self.features else f"未提供 ({feature_id})"}
            for feature_id in screen["feature_ids"]
        ]
        invalid_feature_ids = [feature_id for feature_id in screen["feature_ids"] if feature_id not in self.features or self.features[feature_id].get("disposition") != "keep"]
        if invalid_feature_ids:
            self.add("screen_feature_declarations", "diagnostic", invalid_or_non_kept_feature_ids=invalid_feature_ids)
        self.add("feature_labels", "pass" if observed["features"] == expected_features else "fail", expected=expected_features, observed=observed["features"])

    async def check_overflow(self, page: Any) -> None:
        observed = await page.evaluate(
            """() => {
                const doc = document.documentElement, body = document.body;
                const width = doc.clientWidth;
                const scrollWidth = Math.max(doc.scrollWidth, body ? body.scrollWidth : 0);
                return {client_width: width, scroll_width: scrollWidth, overflow_pixels: Math.max(0, scrollWidth - width),
                    offenders: [...document.querySelectorAll('body *')].filter(el => {
                        const r = el.getBoundingClientRect(); return r.width > 0 && (r.right > width + 1 || r.left < -1);
                    }).slice(0, 12).map(el => ({tag: el.tagName, id: el.id, class_name: String(el.className).slice(0, 160),
                        information_id: el.getAttribute('data-information-id'), right: el.getBoundingClientRect().right, left: el.getBoundingClientRect().left}))};
            }"""
        )
        self.add("document_horizontal_overflow", "pass" if observed["overflow_pixels"] <= 1 else "fail", **observed)

    async def screenshot(self, page: Any, role: str, mode: str) -> None:
        viewport = self.current["viewport"]
        key = (viewport, role, mode)
        if key in self.screenshot_keys:
            return
        filename = f"{safe_token(self.report['case_id'] or 'case', 'case')}--{viewport}--{safe_token(role or 'no-role', 'role')}--{mode}.png"
        path = self.output_dir / filename
        try:
            await page.screenshot(path=str(path), full_page=False, animations="disabled", timeout=self.timeout_ms(7000))
        except Exception as exc:
            self.add("screenshot", "error", path=str(path), error=str(exc)[:2500])
            return
        self.screenshot_keys.add(key)
        self.report["screenshots"].append({"path": str(path), "filename": filename, "viewport": viewport, "role": role or None, "data_mode": mode, "active_ids": await self.active(page), "bytes": path.stat().st_size, "sha256": hashlib.sha256(path.read_bytes()).hexdigest()})
        self.save()

    async def check_controls(self, page: Any) -> bool:
        harness = page.locator("#evaluation-harness")
        roots = await page.locator("main#screen-root").count()
        self.add("screen_root", "pass" if roots == 1 else "fail", observed_count=roots)
        harness_count = await harness.count()
        harness_text = await harness.inner_text() if harness_count == 1 else ""
        explicit_test_label = bool(re.search(r"試験|評価ハーネス|\btest\b|evaluation\s+harness", harness_text, re.IGNORECASE))
        self.add("explicit_test_harness", "pass" if harness_count == 1 and explicit_test_label else "fail", observed_count=harness_count, text=harness_text[:4000])
        valid = True
        for kind, expected in (("role", self.roles), ("data-mode", list(MODES))):
            control = page.locator("select" + attr_selector("data-harness", kind))
            count = await control.count()
            observed = await control.locator("option").evaluate_all("els => els.map(el => el.value)") if count == 1 else []
            matched = count == 1 and observed == expected
            self.add("harness_options", "pass" if matched else "fail", control=kind, expected=expected, observed=observed, observed_control_count=count)
            valid = valid and matched
        return valid and roots == 1

    async def exercise_viewport(self, page: Any, viewport: str) -> None:
        self.set_current(viewport=viewport, role=None, data_mode="normal", screen_id=None, phase="load_document")
        self.save()
        await page.goto(self.html.as_uri(), wait_until="load", timeout=self.timeout_ms(10000))
        await page.locator('html[data-projection-ready="true"]').wait_for(state="attached", timeout=self.timeout_ms())
        self.add("projection_ready", "pass")
        if not self.plan and not await self.load_payload(page):
            await self.screenshot(page, "", "normal")
            return
        if not await self.check_controls(page):
            await self.screenshot(page, "", "normal")
            await self.check_overflow(page)
            return
        if not self.roles:
            self.add("role_coverage", "diagnostic", reason="no_roles_declared")
            await self.screenshot(page, "", "normal")
            await self.check_overflow(page)
            return
        for role_number, role in enumerate(dict.fromkeys(self.roles)):
            self.set_current(role=role, data_mode="normal", screen_id=None)
            await page.locator('select[data-harness="data-mode"]').select_option("normal", timeout=self.timeout_ms())
            if not await self.select_role(page, role):
                continue
            if role_number == 0:
                await self.screenshot(page, role, "normal")
            paths = self.paths(role)
            entries = self.entries(role)
            eligible_edges = [index for index, edge in enumerate(self.navigation) if role in edge["roles"]]
            unreachable_edges = [index for index in eligible_edges if self.navigation[index]["from"] not in paths]
            permitted_screens = [screen["id"] for screen in self.screens if role in screen["roles"]]
            self.report["coverage"].append({"viewport": viewport, "role": role, "declared_entries": [screen["id"] for screen in entries], "reachable_screens": list(paths), "permitted_unreachable_screens": [screen_id for screen_id in permitted_screens if screen_id not in paths], "eligible_navigation_indices": eligible_edges, "unreachable_navigation_indices": unreachable_edges, "bfs_paths": {screen_id: {"entry": value[0], "navigation_indices": value[1]} for screen_id, value in paths.items()}})
            for screen in entries:
                if role not in screen["roles"]:
                    self.add("entry_role_declaration", "diagnostic", entry_screen=screen["id"], reason="entry_role_not_allowed_by_screen")
                await self.click_entry(page, role, screen["id"], "declared_entry_test")
            await self.check_navigation_visibility(page, role)
            for index in eligible_edges:
                edge = self.navigation[index]
                if edge["from"] not in paths:
                    self.add("navigation_click", "diagnostic", nav_index=index, purpose="declared_edge_test", from_screen=edge["from"], to_screen=edge["to"], reason="source_unreachable_from_declared_entries", clicked=False)
                    continue
                if await self.reach(page, role, edge["from"], paths):
                    await self.click_edge(page, role, index, "declared_edge_test")
            for mode in MODES:
                self.set_current(data_mode=mode, phase="select_data_mode")
                before = await self.active(page)
                await page.locator('select[data-harness="data-mode"]').select_option(mode, timeout=self.timeout_ms())
                after = await self.active(page)
                self.add("scenario_preserves_screen", "pass" if before == after else "fail", expected_active_ids=before, observed_active_ids=after)
                if not paths:
                    self.add("screen_value_coverage", "diagnostic", reason="no_reachable_screen_from_declared_entries", primary_cells_compared=0)
                    await self.check_navigation_visibility(page, role)
                    await self.check_overflow(page)
                for screen_id in permitted_screens:
                    if screen_id not in paths:
                        self.add("screen_value_coverage", "diagnostic", screen_id=screen_id, reason="screen_unreachable_from_declared_entries", primary_cells_compared=0)
                        continue
                    if not await self.reach(page, role, screen_id, paths):
                        self.add("screen_value_coverage", "fail", screen_id=screen_id, reason="declared_bfs_path_failed", primary_cells_compared=0)
                        continue
                    await self.check_navigation_visibility(page, role)
                    await self.check_values(page, self.by_screen[screen_id], mode)
                    await self.check_overflow(page)
                    if role_number == 0 and (viewport, role, mode) not in self.screenshot_keys:
                        await self.screenshot(page, role, mode)
                if role_number == 0:
                    await self.screenshot(page, role, mode)
                self.save()
            self.save()

    async def run(self) -> None:
        try:
            from playwright.async_api import async_playwright
        except ImportError as exc:
            self.add("playwright_dependency", "error", error=str(exc))
            self.report["execution"]["status"] = "dependency_unavailable"
            return
        self.report["execution"]["status"] = "running"
        document_bytes = self.html.read_bytes()
        self.report["html"].update(sha256=hashlib.sha256(document_bytes).hexdigest(), bytes=len(document_bytes))
        self.save()
        playwright = await async_playwright().start()
        browser = None
        try:
            try:
                browser = await playwright.chromium.launch(
                    executable_path="/usr/bin/chromium", headless=True, chromium_sandbox=True,
                    timeout=self.timeout_ms(15000),
                    args=["--disable-background-networking", "--disable-component-update", "--disable-sync", "--no-first-run"],
                )
            except Exception as exc:
                self.add("sandboxed_chromium_launch", "error", executable="/usr/bin/chromium", chromium_sandbox=True, security_downgrade_attempted=False, error=str(exc)[:16000])
                self.report["execution"]["status"] = "sandboxed_browser_launch_failed"
                self.report["execution"]["stopped_without_security_downgrade"] = True
                return
            self.add("sandboxed_chromium_launch", "pass", chromium_sandbox=True)
            for viewport, width, height in VIEWPORTS:
                context = await browser.new_context(viewport={"width": width, "height": height}, device_scale_factor=1, service_workers="block", accept_downloads=False)
                await context.set_offline(True)

                async def route_request(route: Any) -> None:
                    request = route.request
                    parsed = urlsplit(request.url)
                    allowed = parsed.scheme in ("data", "blob")
                    if parsed.scheme == "file" and parsed.netloc in ("", "localhost"):
                        allowed = Path(unquote(parsed.path)).resolve() == self.html
                    if allowed:
                        await route.continue_()
                    else:
                        self.report["network"]["blocked_requests"].append({**self.current, "url": request.url, "method": request.method, "resource_type": request.resource_type, "action": "route.abort"})
                        await route.abort("blockedbyclient")

                await context.route("**/*", route_request)
                if hasattr(context, "route_web_socket"):
                    async def block_websocket(route: Any) -> None:
                        self.report["network"]["blocked_requests"].append({**self.current, "url": route.url, "resource_type": "websocket", "action": "close_without_connecting"})
                        await route.close(code=1008, reason="Local projection probe forbids network access")
                    await context.route_web_socket("**/*", block_websocket)
                    self.report["network"]["websocket_policy"] = "closed_before_connect"
                else:
                    self.report["network"]["websocket_policy"] = "offline_context_guard_only"
                page = await context.new_page()
                page.set_default_timeout(self.timeout_ms())
                page.on("pageerror", lambda error: self.report["page_errors"].append({**self.current, "name": getattr(error, "name", type(error).__name__), "message": str(error), "stack": getattr(error, "stack", "")[:12000]}))
                page.on("dialog", lambda dialog: dialog.dismiss())
                page.on("crash", lambda _: self.add("page_crash", "error"))
                error_count = len(self.report["page_errors"])
                try:
                    await self.exercise_viewport(page, viewport)
                except asyncio.TimeoutError:
                    raise
                except Exception as exc:
                    self.add("viewport_execution", "error", viewport=viewport, error=str(exc)[:5000], traceback=traceback.format_exc()[-12000:])
                    await self.screenshot(page, self.current.get("role") or "", self.current.get("data_mode") or "normal")
                finally:
                    self.add("javascript_errors", "pass" if len(self.report["page_errors"]) == error_count else "fail", viewport=viewport, new_page_errors=len(self.report["page_errors"]) - error_count)
                    self.save()
                    await context.close()
            self.set_current(phase="complete")
            self.add("external_request_attempts", "fail" if self.report["network"]["blocked_requests"] else "pass", blocked_requests=len(self.report["network"]["blocked_requests"]))
            for viewport, _, _ in VIEWPORTS:
                count = sum(item["viewport"] == viewport for item in self.report["screenshots"])
                self.add("viewport_screenshot_coverage", "pass" if count else "fail", viewport=viewport, screenshots=count)
            self.report["execution"]["status"] = "completed"
        finally:
            if browser is not None:
                try:
                    await asyncio.wait_for(browser.close(), timeout=1)
                except Exception:
                    pass
            try:
                await asyncio.wait_for(playwright.stop(), timeout=1)
            except Exception:
                pass


def worker_entry(config: dict[str, Any], report: dict[str, Any]) -> None:
    # Isolate browser descendants so the supervisor can stop a hung run as a
    # process group. No browser-security fallback is performed in this path.
    if hasattr(os, "setsid"):
        try:
            os.setsid()
        except OSError:
            pass
    probe = Probe(config, report)
    try:
        asyncio.run(asyncio.wait_for(probe.run(), timeout=config["timeout_seconds"]))
    except (asyncio.TimeoutError, TimeoutError) as exc:
        report["execution"]["status"] = "timed_out"
        probe.add("execution_timeout", "error", error=str(exc), timeout_seconds=config["timeout_seconds"])
    except BaseException as exc:
        report["execution"]["status"] = "worker_error"
        probe.add("worker_exception", "error", error=str(exc)[:5000], traceback=traceback.format_exc()[-12000:])
    finally:
        report["finished_at"] = utc_now()
        probe.save()


def stop_worker(process: Any) -> None:
    def send(sig: int) -> None:
        try:
            if hasattr(os, "getpgid") and os.getpgid(process.pid) == process.pid:
                os.killpg(process.pid, sig)
            elif sig == signal.SIGTERM:
                process.terminate()
            else:
                process.kill()
        except (ProcessLookupError, OSError):
            pass
    send(signal.SIGTERM)
    process.join(1)
    # Kill the entire original group, including browser grandchildren, even
    # if its supervising Python process exited during the first grace period.
    try:
        os.killpg(process.pid, signal.SIGKILL)
    except (AttributeError, ProcessLookupError, OSError):
        if process.is_alive():
            send(signal.SIGKILL)
    process.join(1)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--html", type=Path, required=True, help="The self-contained local HTML document to inspect")
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--timeout-seconds", type=float, default=90, help=f"Total worker budget, greater than zero and at most {MAX_TIMEOUT_SECONDS} seconds (default: 90)")
    args = parser.parse_args(argv)
    if not 0 < args.timeout_seconds <= MAX_TIMEOUT_SECONDS:
        parser.error(f"--timeout-seconds must be greater than zero and at most {MAX_TIMEOUT_SECONDS}")
    html = args.html.expanduser().resolve()
    output_dir = args.output_dir.expanduser().resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    result_path = output_dir / RESULT_NAME
    report = initial_report(html, args.timeout_seconds)
    if not html.is_file():
        report["execution"]["status"] = "invalid_input"
        report["checks"].append({"check": "local_html_input", "status": "error", "reason": "input_is_not_a_regular_file", "path": str(html)})
        report["finished_at"] = utc_now()
        write_result(result_path, report)
        print(str(result_path))
        return 2
    write_result(result_path, report)
    config = {"html": str(html), "output_dir": str(output_dir), "timeout_seconds": args.timeout_seconds}
    process = multiprocessing.get_context("spawn").Process(target=worker_entry, args=(config, report), name="local-projection-probe")
    try:
        process.start()
        process.join(args.timeout_seconds)
        expired = process.is_alive()
        if expired:
            stop_worker(process)
        if result_path.is_file():
            report = json.loads(result_path.read_text(encoding="utf-8"))
        if expired:
            report["execution"]["status"] = "timed_out"
            report["checks"].append({"check": "supervisor_timeout", "status": "error", "timeout_seconds": args.timeout_seconds, "reason": "worker_and_browser_process_group_stopped"})
        elif process.exitcode != 0 or report["execution"]["status"] in ("starting", "running"):
            report["execution"]["status"] = "worker_error"
            report["checks"].append({"check": "worker_exit", "status": "error", "exit_code": process.exitcode})
    except KeyboardInterrupt:
        if process.pid:
            stop_worker(process)
        if result_path.is_file():
            report = json.loads(result_path.read_text(encoding="utf-8"))
        report["execution"]["status"] = "interrupted"
    except Exception as exc:
        if process.pid and process.is_alive():
            stop_worker(process)
        report["execution"]["status"] = "supervisor_error"
        report["checks"].append({"check": "supervisor_exception", "status": "error", "error": str(exc)[:5000]})
    report["finished_at"] = utc_now()
    status = report["execution"]["status"]
    exit_code = 3 if status == "timed_out" else 2 if status != "completed" else 1 if any(item["status"] in ("fail", "error") for item in report["checks"]) else 0
    report["execution"]["exit_code"] = exit_code
    write_result(result_path, report)
    print(str(result_path))
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
