#!/usr/bin/env python3
"""Reproducible browser checks of the two QA fixtures; never silently skip.

Requires a permitted local Chromium and the Python Playwright package.
No package installation, network service, or real submission is performed.
Exit: 0 observed checks pass, 1 observed requirement failures, 2 blocked.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import platform
import shutil
import time
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--chromium', default=None)
    args = parser.parse_args()
    out = args.output.resolve()
    out.mkdir(parents=True, exist_ok=True)
    fixtures = Path(__file__).resolve().parents[1] / 'tests' / 'fixtures'
    started = time.monotonic()
    cases = [
        ('registration-normal', 'registration', 'normal'),
        ('registration-failure-recovery', 'registration', 'error'),
        ('registration-bounds', 'registration', 'boundary'),
        ('registration-repeat', 'registration', 'boundary'),
        ('requests-normal', 'requests', 'normal'),
        ('requests-empty-recovery', 'requests', 'error'),
        ('requests-page-filter', 'requests', 'boundary'),
        ('requests-narrow', 'requests', 'boundary'),
    ]
    result = {'schema': 'design-qa-browser-run/v1', 'status': 'RUNNING',
              'environment': {'os': platform.platform(), 'viewport': [1280, 900],
                              'narrow_viewport': [320, 900], 'dpr': 1,
                              'locale': 'ja-JP', 'timezone': 'Asia/Tokyo'},
              'fixture_hashes': {p.name: hashlib.sha256(p.read_bytes()).hexdigest()
                                 for p in fixtures.glob('*.html')},
              'cases': [{'id': i, 'task': t, 'scenario': s, 'status': 'not_run'}
                        for i, t, s in cases],
              'limits': ['Synthetic cases only; no participant success rate.',
                         'Does not establish full WCAG conformance.',
                         'Requirements failures in seeded fixtures do not reject the QA skill.']}
    pw = browser = None
    try:
        from playwright.sync_api import sync_playwright
        pw = sync_playwright().start()
        chromium = args.chromium or shutil.which('chromium') or shutil.which('google-chrome')
        launch = {'headless': True}
        if chromium:
            launch['executable_path'] = chromium
        browser = pw.chromium.launch(**launch)
        result['environment']['browser'] = 'Chromium'
        result['environment']['version'] = browser.version
        for item in result['cases']:
            narrow = item['id'] == 'requests-narrow'
            ctx = browser.new_context(viewport={'width': 320 if narrow else 1280, 'height': 900},
                                      device_scale_factor=1, locale='ja-JP', timezone_id='Asia/Tokyo',
                                      reduced_motion='reduce')
            ctx.tracing.start(screenshots=True, snapshots=True, sources=True)
            page = ctx.new_page()
            item['steps'] = []
            try:
                page.goto((fixtures / (item['task'] + '.html')).as_uri())
                page.evaluate('document.fonts.ready')
                if item['task'] == 'registration':
                    page.get_by_label('代表者名').fill('確認 太郎')
                    page.get_by_label('メールアドレス').fill('qa@example.test')
                    page.get_by_label('参加人数（1〜8名）').fill('2')
                    item['steps'].append('fill valid name, email, seats=2')
                    if item['id'] == 'registration-failure-recovery':
                        page.get_by_label('次の通信を失敗させる').check()
                        page.get_by_role('button', name='参加を登録する').click()
                        page.wait_for_function("document.querySelector('#status').textContent.includes('失敗')")
                        item['observed'] = {'name': page.locator('#name').input_value(),
                                            'email': page.locator('#email').input_value(),
                                            'seats': page.locator('#seats').input_value(),
                                            'message': page.locator('#status').inner_text(),
                                            'count_after_failure': page.locator('#count').inner_text()}
                        item['steps'].append('select failure; submit; await failure; inspect retained values')
                        retained = (item['observed']['name'] == '確認 太郎'
                                    and item['observed']['email'] == 'qa@example.test'
                                    and item['observed']['seats'] == '2'
                                    and item['observed']['count_after_failure'] == '0')
                        item['observed']['all_values_retained'] = retained
                        if retained:
                            # No re-entry: the user's original task must reach its receipt.
                            page.get_by_role('button', name='参加を登録する').click()
                            page.wait_for_function("document.querySelector('#status').textContent.includes('受付番号')")
                            item['steps'].append('retry without re-entry; await one receipt')
                            item['observed']['count_after_retry'] = page.locator('#count').inner_text()
                            item['observed']['retry_message'] = page.locator('#status').inner_text()
                            item['requirement_met'] = (item['observed']['count_after_retry'] == '1'
                                                       and '2名' in item['observed']['retry_message']
                                                       and 'C-001' in item['observed']['retry_message'])
                        else:
                            item['observed']['retry'] = 'not_run: original input was lost'
                            item['requirement_met'] = False
                    elif item['id'] == 'registration-bounds':
                        page.locator('#seats').fill('9')
                        page.get_by_role('button', name='参加を登録する').click()
                        rejected = not page.locator('#seats').evaluate('(e)=>e.validity.valid')
                        count_before = page.locator('#count').inner_text()
                        page.locator('#seats').fill('8')
                        page.get_by_role('button', name='参加を登録する').click()
                        page.wait_for_function("document.querySelector('#status').textContent.includes('受付番号')")
                        item['observed'] = {'nine_rejected': rejected, 'count_before_correction': count_before,
                                            'count_after_correction': page.locator('#count').inner_text()}
                        item['steps'].append('submit 9; observe invalid; correct to 8; submit; observe receipt')
                        item['requirement_met'] = rejected and count_before == '0' and item['observed']['count_after_correction'] == '1'
                    else:
                        submit = page.get_by_role('button', name='参加を登録する')
                        if item['id'] == 'registration-repeat':
                            submit.dblclick()
                            item['steps'].append('double click submit before mock request resolves')
                        else:
                            submit.click()
                            item['steps'].append('click submit once')
                        page.wait_for_function("document.querySelector('#status').textContent.includes('受付番号')")
                        # Both callbacks use 350ms; wait until pending callbacks have settled.
                        page.wait_for_timeout(400)
                        item['observed'] = {'count': page.locator('#count').inner_text(),
                                            'message': page.locator('#status').inner_text()}
                        item['requirement_met'] = item['observed']['count'] == '1'
                elif item['id'] == 'requests-narrow':
                    heading = page.get_by_role('heading', level=1).bounding_box()
                    action = page.get_by_role('button', name='一覧を書き出す').bounding_box()
                    overlap = (max(0, min(heading['x'] + heading['width'], action['x'] + action['width']) - max(heading['x'], action['x']))
                               * max(0, min(heading['y'] + heading['height'], action['y'] + action['height']) - max(heading['y'], action['y'])))
                    item['observed'] = {'heading_box': heading, 'action_box': action, 'box_overlap_px2': overlap}
                    item['steps'].append('inspect heading and primary-action boxes at 320 CSS px')
                    item['requirement_met'] = overlap == 0
                    item['limits'] = ['Bounding-box overlap is a review signal; screenshot inspection is still required.']
                elif item['id'] == 'requests-empty-recovery':
                    page.get_by_label('依頼名で検索').fill('存在しない依頼')
                    empty = page.locator('#summary').inner_text()
                    page.get_by_role('button', name='条件をクリア').click()
                    item['observed'] = {'empty_summary': empty, 'recovered_rows': page.locator('#rows tr').count(),
                                        'recovered_page': page.locator('#page').inner_text(),
                                        'recovered_summary': page.locator('#summary').inner_text(),
                                        'row_ids': page.locator('#rows tr td:first-child').all_text_contents()}
                    item['steps'].append('search absent name; observe zero count; clear conditions')
                    item['requirement_met'] = (empty == '0件の依頼' and item['observed']['recovered_rows'] == 3
                                               and item['observed']['recovered_page'] == '1 / 3'
                                               and item['observed']['recovered_summary'] == '8件の依頼'
                                               and item['observed']['row_ids'] == ['R-101', 'R-102', 'R-103'])
                else:
                    page.get_by_role('button', name='次へ', exact=True).click()
                    item['steps'].append('next page')
                    if item['id'] == 'requests-page-filter':
                        page.get_by_label('状態', exact=True).select_option('待ち')
                        item['steps'].append('filter pending')
                    item['observed'] = {'summary': page.locator('#summary').inner_text(),
                                        'page': page.locator('#page').inner_text(),
                                        'row_count': page.locator('#rows tr').count(),
                                        'row_ids': page.locator('#rows tr td:first-child').all_text_contents()}
                    if item['id'] == 'requests-page-filter':
                        item['requirement_met'] = (item['observed']['row_count'] == 2
                                                   and item['observed']['row_ids'] == ['R-101', 'R-104']
                                                   and item['observed']['summary'] == '2件の依頼'
                                                   and item['observed']['page'] == '1 / 1')
                    else:
                        item['requirement_met'] = (item['observed']['row_count'] == 3
                                                   and item['observed']['row_ids'] == ['R-104', 'R-105', 'R-106']
                                                   and item['observed']['summary'] == '8件の依頼'
                                                   and item['observed']['page'] == '2 / 3')
                item['status'] = 'passed' if item['requirement_met'] else 'failed'
                image = out / (item['id'] + '.png')
                page.screenshot(path=str(image), full_page=True, animations='disabled')
                item['screenshot'] = image.name
            except Exception as exc:
                item['status'] = 'blocked'
                item['error'] = str(exc)
            finally:
                trace = out / (item['id'] + '.zip')
                try:
                    ctx.tracing.stop(path=str(trace))
                    item['trace'] = trace.name
                except Exception as exc:
                    item.setdefault('cleanup_errors', []).append('trace: ' + str(exc))
                    item['status'] = 'blocked'
                try:
                    ctx.close()
                except Exception as exc:
                    item.setdefault('cleanup_errors', []).append('context: ' + str(exc))
                    item['status'] = 'blocked'
        result['status'] = 'BLOCKED' if any(c['status'] == 'blocked' for c in result['cases']) else ('FAIL' if any(c['status'] == 'failed' for c in result['cases']) else 'PASS')
    except Exception as exc:
        result['status'] = 'BLOCKED'
        result['blocker'] = {'type': type(exc).__name__, 'message': str(exc)}
    finally:
        if browser:
            try:
                browser.close()
            except Exception as exc:
                result.setdefault('cleanup_errors', []).append('browser: ' + str(exc))
                result['status'] = 'BLOCKED'
        if pw:
            try:
                pw.stop()
            except Exception as exc:
                result.setdefault('cleanup_errors', []).append('playwright: ' + str(exc))
                result['status'] = 'BLOCKED'
        result['wall_seconds'] = time.monotonic() - started
        result['runner_sha256'] = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
        (out / 'result.json').write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps({'status': result['status'], 'cases': {c['id']: c['status'] for c in result['cases']},
                      'result': str(out / 'result.json')}, ensure_ascii=False))
    return 2 if result['status'] == 'BLOCKED' else (1 if result['status'] == 'FAIL' else 0)


if __name__ == '__main__':
    raise SystemExit(main())
