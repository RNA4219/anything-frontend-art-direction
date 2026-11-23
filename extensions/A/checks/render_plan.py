#!/usr/bin/env python3
"""Project a neutral brief/plan JSON pair into one self-contained HTML file.

The same projection is used for every evaluation arm. It does not merge
features, add routes, supply missing data, or implement business operations.
Only the explicit --output file is written. No network access is performed.
"""
import argparse
import html
import json
from pathlib import Path
import re
import sys


# The briefs name colors but provide no numeric tokens. These fixed
# approximations are shared by every arm, rather than inferred from a plan.
PALETTES = {
    "ops-charcoal-01": {
        "background": "#22252a", "foreground": "#f5f5f1", "accent": "#d6a345",
        "note": "黒鉛色・白・琥珀色の固定近似色。色値の指定は未提供。",
    },
    "catalog-paper-01": {
        "background": "#f7f1e6", "foreground": "#1f314c", "accent": "#b74632",
        "note": "紙色・紺・朱色の固定近似色。色値の指定は未提供。",
    },
}


def script_json(value):
    """Encode data, not executable JS; even a literal closing script is safe."""
    return (json.dumps(value, ensure_ascii=False, allow_nan=False, separators=(",", ":"))
            .replace("&", "\\u0026").replace("<", "\\u003c").replace(">", "\\u003e")
            .replace("\u2028", "\\u2028").replace("\u2029", "\\u2029"))


TEMPLATE = r'''<!doctype html>
<html lang="ja" data-projection-ready="false">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta http-equiv="Content-Security-Policy" content="default-src 'none'; script-src 'unsafe-inline'; style-src 'unsafe-inline'; img-src data:; connect-src 'none'; font-src 'none'; base-uri 'none'; form-action 'none'">
  <title>@@TITLE@@</title>
  <style>
    :root { @@PALETTE@@ color-scheme: light dark; }
    * { box-sizing: border-box; }
    html, body { margin: 0; width: 100%; min-width: 0; }
    body { background: var(--background); color: var(--foreground); font: 15px/1.6 system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; }
    .shell { max-width: 1400px; margin: 0 auto; padding: 20px; min-width: 0; }
    h1, h2, h3, p, ul { margin-top: 0; }
    h1 { font-size: clamp(22px, 3vw, 30px); line-height: 1.3; margin-bottom: 10px; overflow-wrap: anywhere; }
    h2 { font-size: 18px; margin-bottom: 12px; }
    p, li, a, label, summary, td, th { overflow-wrap: anywhere; }
    .panel { border: 1px solid color-mix(in srgb, var(--foreground) 28%, transparent); border-radius: 4px; padding: 16px; margin-bottom: 18px; min-width: 0; }
    #evaluation-harness { border-left: 4px solid var(--accent); font-size: 13px; }
    #evaluation-harness h2 { font-size: 15px; margin-bottom: 6px; }
    #evaluation-harness p { margin-bottom: 8px; }
    .toolbar, .entry-list, .navigation-list { display: flex; flex-wrap: wrap; align-items: center; gap: 8px 12px; min-width: 0; }
    .toolbar { margin: 10px 0; }
    .toolbar label { display: flex; align-items: center; flex-wrap: wrap; gap: 6px; min-width: 0; }
    button, select, a.nav-link { font: inherit; color: inherit; background: var(--background); border: 1px solid color-mix(in srgb, var(--foreground) 45%, transparent); border-radius: 4px; padding: 7px 10px; min-height: 40px; max-width: 100%; }
    button, select, summary, a.nav-link { cursor: pointer; }
    button:hover, a.nav-link:hover { border-color: var(--accent); }
    button:focus-visible, select:focus-visible, summary:focus-visible, a:focus-visible { outline: 3px solid var(--accent); outline-offset: 2px; }
    a.nav-link { display: inline-flex; align-items: center; text-decoration: underline; }
    .entry-list { margin-bottom: 8px; }
    .entry-list button[aria-current="page"] { border-color: var(--accent); box-shadow: inset 0 -2px var(--accent); }
    .muted { opacity: .78; }
    .identifier { font-size: 12px; opacity: .8; }
    #projection-status { margin: 8px 0 0; }
    #projection-status:not([data-projection-status="ok"]) { font-weight: 600; }
    details { margin-top: 12px; }
    details > summary { padding: 6px 0; }
    details > :not(summary) { margin-top: 8px; }
    .screen-section { margin-top: 22px; min-width: 0; }
    .screen-purpose { font-size: 16px; }
    .table-scroll { max-width: 100%; overflow-x: auto; border: 1px solid color-mix(in srgb, var(--foreground) 25%, transparent); border-radius: 3px; }
    table { border-collapse: collapse; width: 100%; table-layout: fixed; }
    th, td { padding: 10px 12px; text-align: left; vertical-align: top; border-bottom: 1px solid color-mix(in srgb, var(--foreground) 20%, transparent); white-space: normal; }
    th { font-weight: 650; border-bottom-width: 2px; }
    tbody tr:last-child td { border-bottom: 0; }
    td[data-value-state="missing"] { opacity: .65; }
    .feature-list { padding-left: 22px; }
    .feature-list li { margin-bottom: 6px; }
    .navigation-list { list-style: none; margin: 0; padding: 0; align-items: stretch; }
    .navigation-list li { min-width: 0; max-width: 100%; }
    .route-list { margin: 0; padding-left: 20px; }
    .route-list li { margin-bottom: 5px; }
    [hidden] { display: none !important; }
    @media (max-width: 600px) {
      .shell { padding: 12px; }
      .panel { padding: 12px; }
      button, select, a.nav-link { min-height: 44px; }
      .toolbar { align-items: flex-start; }
      .toolbar label { flex: 1 1 140px; }
      .toolbar select { width: 100%; }
      th, td { padding: 9px 10px; }
    }
  </style>
</head>
<body>
<div class="shell">
  <aside id="evaluation-harness" class="panel" aria-label="評価ハーネス">
    <h2>評価ハーネス — 共通JSON投影</h2>
    <p>以下のrole・件数・入口コントロールは試験用です。製品の機能として追加したものではありません。</p>
    <p class="muted">構造と描画の確認用です。保存・送信・取消・公開などの業務処理、および実サービスの認証・認可は実装していません。</p>
    <div class="toolbar">
      <label>試験role <select id="harness-role" data-harness="role" aria-label="試験role"></select></label>
      <label>試験データ <select id="harness-data-mode" data-harness="data-mode" aria-label="試験データ件数">
        <option value="normal">normal — 提供データ</option>
        <option value="empty">empty — 0件</option>
        <option value="single">single — 先頭1件</option>
        <option value="many">many — 実データを40行まで反復</option>
      </select></label>
    </div>
    <p id="scenario-note" data-scenario-note></p>
    <p class="identifier">planで宣言された、このroleの入口</p>
    <div id="entry-list" class="entry-list" data-entry-list></div>
    <details id="projection-metadata">
      <summary>投影条件・宣言されたgoal route</summary>
      <p id="palette-note"></p>
      <p id="intent-note"></p>
      <ul id="goal-routes" class="route-list"></ul>
    </details>
    <p id="projection-status" data-projection-status="initializing" role="status" aria-live="polite"></p>
  </aside>
  <main id="screen-root" aria-label="planで宣言された画面"></main>
</div>
<script id="plan-data" type="application/json">@@PAYLOAD@@</script>
<script>
(function () {
  'use strict';
  const data = JSON.parse(document.getElementById('plan-data').textContent);
  const brief = data.brief;
  const plan = data.plan;
  const config = data.projection;
  const array = function (value) { return Array.isArray(value) ? value : []; };
  const record = function (value) { return value !== null && typeof value === 'object' && !Array.isArray(value); };
  const roles = array(brief.roles).filter(record);
  const screens = array(plan.screens).filter(record);
  const features = array(plan.features).filter(record);
  const goals = array(brief.goals).filter(record);
  // Keep original navigation indexes: a malformed record must not renumber later edges.
  const nav = array(plan.navigation);
  const content = array(brief.content);
  const state = {role: null, screen: null, mode: 'normal'};
  const root = document.getElementById('screen-root');
  const roleSelect = document.getElementById('harness-role');
  const modeSelect = document.getElementById('harness-data-mode');
  const entryList = document.getElementById('entry-list');
  const status = document.getElementById('projection-status');

  function element(tag, attributes, text) {
    const node = document.createElement(tag);
    Object.entries(attributes || {}).forEach(function (entry) {
      node.setAttribute(entry[0], String(entry[1]));
    });
    if (text !== undefined) node.textContent = String(text);
    return node;
  }

  function textOrMissing(value) {
    if (value === undefined || value === null || value === '') return '未提供';
    return typeof value === 'string' ? value : JSON.stringify(value);
  }

  function showStatus(code, message) {
    status.dataset.projectionStatus = code;
    status.textContent = message;
  }

  function rows() {
    if (state.mode === 'empty') return [];
    if (state.mode === 'single') return content.slice(0, 1);
    if (state.mode === 'many') {
      return content.length ? Array.from({length: config.many_count}, function (_, i) {
        return content[i % content.length];
      }) : [];
    }
    return content;
  }

  function scenarioNote() {
    const count = rows().length;
    const notes = {
      normal: '提供されたbrief.contentをそのまま表示します。',
      empty: '評価ハーネスが0件表示を試験しています。元データは変更しません。',
      single: '評価ハーネスが提供データの先頭1件を表示しています。',
      many: '評価ハーネスが提供データを最大40行まで反復しています。新しい実データは生成していません。'
    };
    document.getElementById('scenario-note').textContent = notes[state.mode] + ' 表示行数: ' + count;
    root.dataset.dataMode = state.mode;
    root.dataset.rowCount = String(count);
  }

  function currentEntries() {
    return screens.filter(function (s) { return array(s.entry_for).includes(state.role); });
  }

  function renderEntries() {
    entryList.replaceChildren();
    const entries = currentEntries();
    if (!entries.length) {
      entryList.append(element('span', {'data-no-entry': ''}, 'このroleの入口はplanに未提供です。'));
    }
    entries.forEach(function (s) {
      const button = element('button', {
        type: 'button', id: 'entry-' + screens.indexOf(s),
        'data-entry-screen': s.id, 'data-entry-role': state.role,
        'aria-current': state.screen && state.screen.id === s.id ? 'page' : 'false'
      }, textOrMissing(s.title) + ' (' + textOrMissing(s.id) + ')');
      button.addEventListener('click', function () { navigate(s.id); });
      entryList.append(button);
    });
  }

  function renderRoutes() {
    const list = document.getElementById('goal-routes');
    list.replaceChildren();
    array(plan.goal_routes).forEach(function (r, index) {
      if (!record(r)) return;
      const goal = goals.find(function (g) { return g.id === r.goal_id; });
      if (goal && goal.role !== state.role) return;
      list.append(element('li', {
        'data-goal-route-index': index, 'data-goal-id': r.goal_id,
        'data-start-screen': r.start_screen, 'data-target-screen': r.target_screen
      }, textOrMissing(r.goal_id) + ': ' + textOrMissing(r.start_screen) + ' → ' +
          textOrMissing(r.target_screen) + ' / ' + textOrMissing(r.notes)));
    });
    if (!list.children.length) list.append(element('li', {}, 'このroleのgoal routeはplanに未提供です。'));
  }

  function renderInformation(screen, visibility) {
    const fields = array(screen.information).filter(function (item) {
      return record(item) && item.visibility === visibility;
    });
    const section = element('section', {'class': 'screen-section', 'data-information-group': visibility});
    if (!fields.length) {
      section.append(element('p', {'data-no-information': visibility, 'class': 'muted'},
        visibility + 'として宣言された情報はありません。'));
      return section;
    }
    const available = rows();
    const scroll = element('div', {'class': 'table-scroll', 'data-table-scroll': visibility});
    const table = element('table', {id: 'information-' + screens.indexOf(screen) + '-' + visibility});
    table.style.minWidth = String(fields.length * 144) + 'px';
    const head = element('thead');
    const headings = element('tr');
    fields.forEach(function (field) {
      headings.append(element('th', {scope: 'col', 'data-information-id': field.id}, textOrMissing(field.id)));
    });
    head.append(headings);
    table.append(head);
    const body = element('tbody');
    available.forEach(function (value, rowIndex) {
      const row = element('tr', {
        'data-content-row': rowIndex, 'data-row-index': rowIndex, 'data-visibility': visibility,
        'data-source-row-index': content.length ? rowIndex % content.length : ''
      });
      fields.forEach(function (field, fieldIndex) {
        const supplied = record(value) && Object.prototype.hasOwnProperty.call(value, field.id);
        const cellValue = supplied ? value[field.id] : undefined;
        const missing = !supplied || cellValue === null || cellValue === undefined || cellValue === '';
        row.append(element('td', {
          id: 'cell-' + screens.indexOf(screen) + '-' + visibility + '-' + rowIndex + '-' + fieldIndex,
          'data-information-id': field.id, 'data-row-index': rowIndex,
          'data-value-state': missing ? 'missing' : 'provided',
          'data-visibility': visibility
        }, missing ? '未提供' : textOrMissing(cellValue)));
      });
      body.append(row);
    });
    table.append(body);
    scroll.append(table);
    section.append(scroll);
    if (!available.length) section.append(element('p', {'data-empty-state': visibility}, '表示するデータは0件です。'));
    return section;
  }

  function renderFeatureList(screen) {
    const section = element('section', {'class': 'screen-section'});
    section.append(element('h2', {}, '宣言された機能'));
    section.append(element('p', {'class': 'muted'}, '機能名の一覧です。業務操作の実装や実行を表すものではありません。'));
    const list = element('ul', {'class': 'feature-list', 'data-feature-list': ''});
    array(screen.feature_ids).forEach(function (featureId) {
      const feature = features.find(function (f) { return f.id === featureId; });
      list.append(element('li', {
        'data-feature-id': featureId,
        'data-disposition': feature ? feature.disposition : 'missing'
      }, feature ? textOrMissing(feature.label) : '未提供 (' + textOrMissing(featureId) + ')'));
    });
    if (!list.children.length) list.append(element('li', {'data-no-features': ''}, 'この画面に宣言された機能はありません。'));
    section.append(list);
    return section;
  }

  function renderNavigation(screen) {
    const section = element('nav', {'class': 'screen-section', 'aria-label': 'planで宣言された画面間ナビゲーション'});
    section.append(element('h2', {}, 'このroleに宣言されたナビゲーション'));
    const list = element('ul', {'class': 'navigation-list'});
    nav.forEach(function (edge, index) {
      if (!record(edge) || edge.from !== screen.id || !array(edge.roles).includes(state.role)) return;
      const target = screens.find(function (s) { return s.id === edge.to; });
      const permission = !target ? 'missing' : array(target.roles).includes(state.role) ? 'allowed' : 'denied';
      const link = element('a', {
        id: 'nav-' + index, 'class': 'nav-link', href: '#' + encodeURIComponent(String(edge.to)),
        'data-nav-index': index, 'data-from': edge.from, 'data-to': edge.to,
        'data-roles': JSON.stringify(array(edge.roles)), 'data-kind': edge.kind,
        'data-target-permission': permission
      }, textOrMissing(edge.label));
      link.addEventListener('click', function (event) {
        event.preventDefault();
        if (!state.screen || edge.from !== state.screen.id || !array(edge.roles).includes(state.role)) {
          showStatus('access-denied', 'このrole・画面からの移動はplanに宣言されていません。');
          return;
        }
        navigate(edge.to);
      });
      const item = element('li');
      item.append(link);
      list.append(item);
    });
    if (!list.children.length) list.append(element('li', {'data-no-navigation': '', 'class': 'muted'}, 'この画面からのナビゲーションは宣言されていません。'));
    section.append(list);
    return section;
  }

  function renderScreen() {
    root.replaceChildren();
    scenarioNote();
    if (!state.screen) return;
    const screen = state.screen;
    const section = element('section', {
      id: 'screen-' + screens.indexOf(screen), 'class': 'panel',
      'data-screen-id': screen.id, 'data-screen-role': state.role
    });
    section.append(element('p', {'class': 'identifier'}, '画面ID: ' + textOrMissing(screen.id)));
    section.append(element('h1', {'data-screen-title': ''}, textOrMissing(screen.title)));
    section.append(element('p', {'class': 'screen-purpose', 'data-screen-purpose': ''}, textOrMissing(screen.purpose)));
    section.append(element('h2', {}, '判断情報 (primary)'));
    section.append(renderInformation(screen, 'primary'));
    const secondary = array(screen.information).some(function (i) { return record(i) && i.visibility === 'secondary'; });
    if (secondary) {
      const details = element('details', {'data-secondary': ''});
      details.append(element('summary', {}, '補足情報 (secondary)'));
      details.append(renderInformation(screen, 'secondary'));
      section.append(details);
    }
    section.append(renderFeatureList(screen));
    section.append(renderNavigation(screen));
    root.append(section);
  }

  function navigate(screenId) {
    const screen = screens.find(function (s) { return s.id === screenId; });
    if (!screen) {
      showStatus('missing-target', '遷移先の画面はplanに未提供です: ' + textOrMissing(screenId));
      return false;
    }
    if (!array(screen.roles).includes(state.role)) {
      showStatus('access-denied', 'このroleは遷移先の画面を許可されていません: ' + textOrMissing(screenId));
      return false;
    }
    state.screen = screen;
    renderScreen();
    renderEntries();
    showStatus('ok', '表示中: ' + textOrMissing(screen.title) + ' / role: ' + textOrMissing(state.role));
    return true;
  }

  function changeRole() {
    state.role = roleSelect.value || null;
    state.screen = null;
    root.replaceChildren();
    root.dataset.role = state.role === null ? '' : state.role;
    scenarioNote();
    renderEntries();
    renderRoutes();
    const entries = currentEntries();
    if (entries.length) navigate(entries[0].id);
    else showStatus('no-entry', 'このroleの入口はplanに未提供です。別の画面への導線は補完しません。');
  }

  roles.forEach(function (role) {
    if (typeof role.id !== 'string') return;
    roleSelect.append(element('option', {value: role.id}, textOrMissing(role.label) + ' (' + role.id + ')'));
  });
  roleSelect.addEventListener('change', changeRole);
  modeSelect.addEventListener('change', function () {
    state.mode = modeSelect.value;
    renderScreen();
  });
  document.getElementById('palette-note').textContent = config.palette_note + ' システム書体を使用。';
  document.getElementById('intent-note').textContent = 'brief.visual_intent.id: ' + textOrMissing(brief.visual_intent && brief.visual_intent.id) +
    ' / plan.visual_intent_id: ' + textOrMissing(plan.visual_intent_id) +
    (brief.visual_intent && brief.visual_intent.id === plan.visual_intent_id ? '' : ' (不一致または未提供)');
  changeRole();
  document.documentElement.dataset.caseId = textOrMissing(brief.case_id);
  document.documentElement.dataset.projectionReady = 'true';
  window.__planProjection = Object.freeze({
    getState: function () {
      return {role: state.role, screen: state.screen ? state.screen.id : null, mode: state.mode, rowCount: rows().length};
    }
  });
})();
</script>
</body>
</html>
'''


def render_html(brief, plan):
    if not isinstance(brief, dict) or not isinstance(plan, dict):
        raise ValueError("brief and plan must be JSON objects")
    intent = brief.get("visual_intent")
    intent_id = intent.get("id") if isinstance(intent, dict) else None
    palette = PALETTES.get(intent_id, {
        "background": "Canvas", "foreground": "CanvasText", "accent": "LinkText",
        "note": "対応する色定義は未提供。システム既定色を使用。",
    })
    values = {
        "TITLE": html.escape(str(brief.get("case_id", "未提供")) + " — 共通JSON投影"),
        "PALETTE": "--background: {background}; --foreground: {foreground}; --accent: {accent};".format(**palette),
        "PAYLOAD": script_json({
            "brief": brief, "plan": plan,
            "projection": {"many_count": 40, "palette_note": palette["note"]},
        }),
    }
    return re.sub(r"@@(TITLE|PALETTE|PAYLOAD)@@", lambda match: values[match.group(1)], TEMPLATE)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--brief", required=True, type=Path)
    parser.add_argument("--plan", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    try:
        brief = json.loads(args.brief.read_text(encoding="utf-8"))
        plan = json.loads(args.plan.read_text(encoding="utf-8"))
        document = render_html(brief, plan)
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(document, encoding="utf-8")
    except (OSError, UnicodeError, json.JSONDecodeError, ValueError, TypeError) as error:
        print(json.dumps({"status": "INVALID_INPUT", "error": str(error)}, ensure_ascii=False), file=sys.stderr)
        return 2
    print(json.dumps({
        "status": "RENDERED", "case_id": brief.get("case_id"),
        "output": str(args.output.resolve()),
        "note": "Common structural projection; not a business-operation implementation or UX success measurement.",
    }, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
