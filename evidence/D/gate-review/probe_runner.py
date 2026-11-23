#!/usr/bin/env python3
"""Extract exact runner statements and supply fake browser objects; no browser runs.

These probes assess assertion/control-flow coverage, not real fixture/UI quality.
Only the allowed runner source is read. All data below are synthetic.
"""
import ast
import json
from pathlib import Path
import tempfile

SOURCE = Path(__file__).with_name('runner-before.py')
tree = ast.parse(SOURCE.read_text())


def at(line):
    return next(n for n in ast.walk(tree) if isinstance(n, ast.If) and n.lineno == line)


def execute(statements, namespace):
    code = compile(ast.Module(body=statements, type_ignores=[]), str(SOURCE), 'exec')
    exec(code, namespace)


class Node:
    def __init__(self, page, key):
        self.page, self.key = page, key

    def check(self):
        self.page.events.append('check failure')

    def click(self):
        self.page.events.append('click ' + self.key)
        # Next deliberately does nothing; submit never reaches success.

    def input_value(self):
        return {'#name': '確認 太郎', '#email': 'qa@example.test', '#seats': ''}[self.key]

    def inner_text(self):
        return {'#status': '通信失敗。再試行不能', '#summary': '6件の依頼', '#page': '1 / 2'}[self.key]

    def count(self):
        return 3


class Page:
    def __init__(self):
        self.events = []

    def get_by_label(self, label, **kwargs):
        return Node(self, label)

    def get_by_role(self, role, name, **kwargs):
        return Node(self, name)

    def locator(self, selector):
        return Node(self, selector)

    def wait_for_function(self, expression):
        self.events.append('wait for failure')


findings = []
page = Page()
item = {'id': 'registration-failure-recovery', 'steps': []}
execute(at(75).body, {'page': page, 'item': item})
assert item['requirement_met'] is True
assert item['observed']['seats'] == ''
assert sum(event.startswith('click ') for event in page.events) == 1
findings.append({'id': 'R1', 'synthetic_only': True, 'requirement_met': item['requirement_met'],
                 'observed': item['observed'], 'events': page.events,
                 'proves': 'lost seats and no retry can satisfy recovery-case predicate'})

page = Page()
item = {'id': 'requests-normal', 'steps': []}
execute(at(120).orelse, {'page': page, 'item': item})
assert item['requirement_met'] is True and item['observed']['page'] == '1 / 2'
findings.append({'id': 'R2', 'synthetic_only': True, 'requirement_met': item['requirement_met'],
                 'observed': item['observed'], 'events': page.events,
                 'proves': 'next-page no-op still satisfies normal-case predicate'})

class BrokenBrowser:
    def close(self):
        raise RuntimeError('synthetic transport already closed')

outer = next(n for n in ast.walk(tree) if isinstance(n, ast.Try) and n.lineno == 49)
with tempfile.TemporaryDirectory(prefix='qa-runner-review-') as temporary:
    out = Path(temporary)
    try:
        execute(outer.finalbody, {'browser': BrokenBrowser(), 'pw': None,
                                  'result': {'status': 'BLOCKED'}, 'out': out})
    except RuntimeError as exc:
        cleanup_error = str(exc)
    else:
        raise AssertionError('expected cleanup failure')
    assert not (out / 'result.json').exists()
    findings.append({'id': 'R3', 'synthetic_only': True, 'error': cleanup_error,
                     'result_json_written': (out / 'result.json').exists(),
                     'proves': 'cleanup exception prevents result persistence'})

print(json.dumps({'scope': 'synthetic assertion/control-flow probes; no UI evaluated',
                  'findings': findings}, ensure_ascii=False, indent=2))
