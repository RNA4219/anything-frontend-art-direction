#!/usr/bin/env python3
"""Regression proof using exact current runner AST and synthetic browser stubs.

No browser launch, fixture reads, or product-quality judgement is performed.
"""
import ast
import hashlib
import json
from pathlib import Path
import tempfile
import time

ROOT = Path(__file__).resolve().parents[3]
SOURCE = ROOT / 'extensions/D/checks/run_browser_checks.py'
source_bytes = SOURCE.read_bytes()
tree = ast.parse(source_bytes)


def branch(case_id):
    return next(n for n in ast.walk(tree) if isinstance(n, ast.If)
                and isinstance(n.test, ast.Compare)
                and any(isinstance(c, ast.Constant) and c.value == case_id
                        for c in n.test.comparators))


def execute(statements, namespace):
    exec(compile(ast.Module(body=statements, type_ignores=[]), str(SOURCE), 'exec'), namespace)


class Node:
    def __init__(self, page, key):
        self.page, self.key = page, key

    def check(self):
        pass

    def click(self):
        self.page.clicks.append(self.key)

    def input_value(self):
        return {'#name': '確認 太郎', '#email': 'qa@example.test', '#seats': self.page.seats}[self.key]

    def inner_text(self):
        return {'#status': '通信失敗' if len(self.page.clicks) == 1 else self.page.receipt,
                '#count': '0' if len(self.page.clicks) == 1 else self.page.count_after_retry,
                '#summary': '8件の依頼', '#page': self.page.page_number}[self.key]

    def count(self):
        return 3

    def all_text_contents(self):
        return self.page.row_ids


class Page:
    def __init__(self, seats='2', receipt='受付番号 C-001、2名', count_after_retry='1',
                 page_number='1 / 3', row_ids=None):
        self.seats, self.receipt, self.count_after_retry = seats, receipt, count_after_retry
        self.page_number = page_number
        self.row_ids = row_ids or ['R-101', 'R-102', 'R-103']
        self.clicks, self.waits = [], []

    def get_by_label(self, label, **kwargs):
        return Node(self, label)

    def get_by_role(self, role, name, **kwargs):
        return Node(self, name)

    def locator(self, selector):
        return Node(self, selector)

    def wait_for_function(self, expression):
        self.waits.append(expression)


records = []


def check_case(label, case_id, statements, page, expected):
    item = {'id': case_id, 'steps': []}
    execute(statements, {'page': page, 'item': item})
    assert item['requirement_met'] is expected, (label, item)
    records.append({'probe': label, 'expected_requirement_met': expected,
                    'actual_requirement_met': item['requirement_met'],
                    'observed': item['observed'], 'clicks': page.clicks})
    return page, item


recovery = branch('registration-failure-recovery').body
check_case('R1 lost seats rejected', 'registration-failure-recovery', recovery,
           Page(seats=''), False)
page, _ = check_case('R1 successful synthetic retry accepted', 'registration-failure-recovery',
                     recovery, Page(), True)
assert len(page.clicks) == 2
assert any('受付番号' in x for x in page.waits)
check_case('R1 duplicate retry rejected', 'registration-failure-recovery', recovery,
           Page(count_after_retry='2'), False)
check_case('R1 wrong party size rejected', 'registration-failure-recovery', recovery,
           Page(receipt='受付番号 C-001、1名'), False)

normal = branch('requests-empty-recovery').orelse
check_case('R2 next no-op rejected', 'requests-normal', normal, Page(), False)
check_case('R2 wrong identities rejected', 'requests-normal', normal,
           Page(page_number='2 / 3'), False)
check_case('R2 synthetic next page accepted', 'requests-normal', normal,
           Page(page_number='2 / 3', row_ids=['R-104', 'R-105', 'R-106']), True)


class BrokenResource:
    def close(self):
        raise RuntimeError('synthetic close failure')

    def stop(self, **kwargs):
        raise RuntimeError('synthetic stop failure')

    @property
    def tracing(self):
        return self


tries = [n for n in ast.walk(tree) if isinstance(n, ast.Try) and n.finalbody]
outer = next(n for n in tries if any('browser.close' in ast.unparse(s) for s in n.finalbody))
per_case = next(n for n in tries if any('ctx.close' in ast.unparse(s) for s in n.finalbody))
with tempfile.TemporaryDirectory(prefix='qa-runner-postfix-') as temporary:
    out = Path(temporary)
    item = {'id': 'synthetic-case', 'status': 'failed', 'requirement_met': False,
            'observed': {'preserved': 'synthetic observation'}}
    execute(per_case.finalbody, {'item': item, 'ctx': BrokenResource(), 'out': out})
    assert item['status'] == 'blocked'
    assert len(item['cleanup_errors']) == 2
    assert item['observed']['preserved'] == 'synthetic observation'
    result = {'status': 'FAIL', 'cases': [item]}
    execute(outer.finalbody, {'browser': BrokenResource(), 'pw': BrokenResource(),
                             'result': result, 'out': out, 'time': time,
                             'started': time.monotonic(), 'hashlib': hashlib,
                             'Path': Path, '__file__': str(SOURCE), 'json': json})
    persisted = json.loads((out / 'result.json').read_text())
    assert persisted['status'] == 'BLOCKED'
    assert len(persisted['cleanup_errors']) == 2
    assert persisted['cases'][0]['observed']['preserved'] == 'synthetic observation'
    records.append({'probe': 'R3 all cleanup exceptions persisted', 'result_json_written': True,
                    'status': persisted['status'], 'cleanup_errors': persisted['cleanup_errors'],
                    'case_cleanup_errors': persisted['cases'][0]['cleanup_errors'],
                    'observations_preserved': True})

print(json.dumps({'scope': 'synthetic assertion/control-flow checks; no real browser or UI evaluated',
                  'runner_sha256': hashlib.sha256(source_bytes).hexdigest(),
                  'assertions_succeeded': True, 'probes': records}, ensure_ascii=False, indent=2))
