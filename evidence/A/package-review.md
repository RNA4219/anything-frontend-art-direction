# A パッケージの有限な整合監査

確認日: 2026-11-23

## 結論と監査の位置付け

原則の節構成と主要根拠への2ホップは整合している。一方、checkerには、到達不能な必須機能を含む案がPASSになる検査の抜けと、文書が要求する直接の正本参照を満たさないmergeがPASSになる相違がある。加えて、FAILとHOLDの優先順位に記述差がある。

これは方法資料の著者自身による有限の自己整合監査であり、独立評価ではない。利用者によるタスク成功、原則の効果、候補の採否は評価していない。凍結済みのSKILL、references、checker、例は変更していない。既知の軽微なEOF空行は対象外とした。

## 範囲と方法

- 読む範囲は`extensions/A/**`と、`evidence/A/coverage-matrix.md`、`source-index.md`、`sankai-extraction.md`に限定した。
- 主にSKILL、5件のreference文書、例、validator、checksのREADME、agent設定を確認した。renderer/probeは依存宣言・境界に関する静的な確認に限定した。既存テストやbriefの本文は使用していない。
- benchmark出力、evaluation、RASI、秘密の評価資料は読んでいない。外部検索や原典取得は追加していない。
- 節構成・原典への導線を機械的に照合し、checkerへ自作の小さなbrief/planをメモリ内で渡した。局所再現は下記6条件に限定した。実行時にファイルを生成していない。
- この監査による新規ファイルは本報告だけである。

## 整合していた項目

| 項目 | 確認結果 | 確認の限界 |
|---|---|---|
| 主要根拠への2ホップ | SKILL → 原則の方法資料 → 原典URLがA01〜A10すべてにある。SKILL → sources.md → 原典URLもある | 導線の静的確認。外部URLの再取得・引用再照合はしていない |
| 必須8節 | 10原則すべてにTrigger、Inputs、Decision Rules、Procedure、Output Contract、Failure Modes、Verification、Sourcesがある | 節の存在・順序であり、実用効果の証明ではない |
| Confidence / Limits | 10原則すべてにあり、対象・条件・未確認事項を記述している | 実タスクで限界条件を網羅できることまでは確認していない |
| 原典台帳との関係 | sources.mdにS01〜S20の20件があり、原典主張とSkill側の導出を区別している | source-indexの原典検証結果は既存記録。今回の監査で再実施した結果ではない |
| 必須の実行依存 | validatorのimportはPython標準ライブラリ。恒常的なimozuru・sankai・RASI依存は要求していない | 各利用環境へのPython導入までは検証していない |
| 任意のブラウザ検査 | Playwrightと`/usr/bin/chromium`の依存、sandbox付き起動、失敗時の記録が説明されている | 起動・インストール状態は確認していない。必須コアの依存と混同しない |
| 責務境界 | Aは機能判断・情報構造を扱い、状態遷移はB、部品等はC、評価はDへ引き渡す。共通renderer/probeは検査用投影と明記されている | 範囲外の既存Art Direction本文やB/C実装との比較はしていない |
| 適用制約 | 18Fは保存資料、NASAからUIへの利用は導出、WAI補足は非規範と明記。機能削減万能、普遍的な数の上限、美的な置換は採用していない | 各出典の現在の公開状態は今回再確認していない |

## PR1: 必須機能が到達不能でもPASSになる

- **重要度:** 高。意味解釈だけの問題ではなく、画面・機能・経路のIDから再現できる構造的な検査の抜け。
- **位置:** `extensions/A/checks/validate_plan.py`の152〜176行と202〜218行。関連する記述は`references/goals-and-features.md`のA02 Verification、A04 Verification、`references/information-architecture.md`のA06 Procedure / Output Contract、`references/plan-contract.md`の63行。
- **症状:** must目標を実現する唯一のkeep機能を、認可された入口から到達不能な別画面へ移してもPASSになる。
- **根拠:** checkerは「目標を参照するkeep機能が全体に存在する」「機能がどこかの画面にある」「宣言したgoal targetへ辿れる」「targetに必要情報がある」を個別に確認する。目標・役割・実現機能・機能所有画面の到達性を結合して確認しない。
- **影響:** 入力の必須機能を利用できない案でも、到達可能な情報表示だけで構造PASSになり得る。PASSをタスク成功の証明としないという注意書きだけでは、このID上の欠落を検出できない。
- **修正方向:** 凍結解除後、must目標と役割ごとに、対応するkeep正本を所有する画面が認可された入口から到達できることを検査する。必要な依存機能との関係も検討する。正当な複数画面タスクを壊さないよう、すべての機能をtarget画面へ同居させる条件にはしない。
- **再現:** 下記の`mandatory_feature_on_unreachable_screen`。入口`s`のfeature_idsを空にし、機能`f`だけを入口でもなくnavigationもない`isolated`へ移す。goal routeは`s → s`のまま。実測はPASS、issuesなし。

## PR2: keep正本へ直接向かわないmergeがPASSになる

- **重要度:** 中。機能喪失そのものではないが、出力の正規化契約がcheckerで保証されない。
- **位置:** `extensions/A/checks/validate_plan.py`の93〜104行と124〜130行。文書側は`references/goals-and-features.md`の82行、155行、169行、`references/plan-contract.md`の34行。
- **症状:** `alias2 → alias1 → f(keep)`の多段mergeがPASSになる。方法資料はkeep正本への直接対応、一段での到達を要求する。
- **根拠:** resolveはmergeを繰り返して最終keepへ到達し、属性・目標・要件も最終keepとのみ比較する。直近target自体がkeepであることは検査しない。
- **影響:** 直接の正本参照を前提にする後続処理や手動確認が、PASSだけでは契約成立を判断できない。今回の再現では最終機能は保持され、循環は作っていない。
- **修正方向:** 文書の意図を維持するなら、mergeの直近targetがkeepかを検査する。多段mergeを許す変更を選ぶ場合は、契約・方法資料・消費側を合わせて改訂する必要がある。今回はいずれも変更しない。
- **再現:** 下記の`direct_merge_control`は両aliasが直接`f`を参照しPASS。`alias2.target`だけを`alias1`へ変えた`multi_hop_merge`もPASS、issuesなし。

## PR3: blockerと構造エラーが共存した場合のstatus記述差

- **重要度:** 低。両結果とも非PASSであり、通過の抜けではない。
- **位置:** `references/plan-contract.md`の73行、`references/disclosure-and-verification.md`のA10 Decision Rules / Verificationと、`checks/validate_plan.py`の227行。
- **症状:** 文書はblocking=trueならHOLDと記述するが、checkerはerrorがあればFAILを優先する。
- **根拠・影響:** blockerだけならHOLD。必須情報欠落を併発するとFAILとなる。結果の集計・説明では、文書だけから予想するstatusと異なる。
- **修正方向:** FAIL優先を文書へ明記するか、総合statusと未解決blockerの有無を分けて説明する。blockingが消えたと読ませない。
- **再現:** 下記の`blocker_only`と`blocker_plus_structural_error`。後者ではHIDDEN_DECISION_INFORMATIONとUNRESOLVED_BLOCKERの両方が記録された。

## 局所再現の実測

| 条件 | status | issue code |
|---|---|---|
| baseline | PASS | なし |
| mandatory_feature_on_unreachable_screen | PASS | なし |
| direct_merge_control | PASS | なし |
| multi_hop_merge | PASS | なし |
| blocker_only | HOLD | UNRESOLVED_BLOCKER |
| blocker_plus_structural_error | FAIL | HIDDEN_DECISION_INFORMATION、UNRESOLVED_BLOCKER |

次は実測した条件を再現する自己完結コード。repo-Aを作業ディレクトリとして実行する。既存brief・benchmarkを読まず、ファイルを保存しない。

```bash
python3 -B - <<'PY'
from copy import deepcopy
from pathlib import Path
import json

path = Path('extensions/A/checks/validate_plan.py')
ns = {'__name__': 'package_review'}
exec(compile(path.read_text(), str(path), 'exec'), ns)
validate = ns['validate']
b = {
    'case_id': 'audit_probe', 'roles': [{'id': 'r', 'label': '担当'}],
    'goals': [{'id': 'g', 'role': 'r', 'outcome': 'obtain-report',
               'priority': 'must', 'needed_information': ['period']}],
    'requirements': [{'id': 'q', 'goal_ids': ['g'], 'mandatory': True,
                      'statement': '期間指定のレポートを入手する'}],
    'feature_requests': [{'id': 'f', 'label': 'レポート取得',
        'object': 'report', 'outcome': 'obtain-report', 'roles': ['r'],
        'goal_ids': ['g'], 'requirement_ids': ['q'],
        'dependencies': [], 'mandatory': True}],
    'visual_intent': {'id': 'v', 'constraints': []}}
f = {k: deepcopy(v) for k, v in b['feature_requests'][0].items() if k != 'mandatory'}
f.update(disposition='keep', target=None, reason='必須レポートの取得',
         priority='required', priority_basis='依頼で必須')
s = {'id': 's', 'title': 'レポート', 'purpose': '期間指定のレポートを入手する',
     'goal_ids': ['g'], 'feature_ids': ['f'], 'roles': ['r'], 'entry_for': ['r'],
     'information': [{'id': 'period', 'visibility': 'primary', 'reason': '対象期間を判断する'}]}
p = {'schema_version': '1.0', 'case_id': 'audit_probe', 'visual_intent_id': 'v',
     'features': [f], 'screens': [s], 'navigation': [],
     'goal_routes': [{'goal_id': 'g', 'start_screen': 's', 'target_screen': 's',
                      'notes': 'レポートを取得する'}], 'unresolved': [], 'decision_notes': []}
def show(name, brief, plan):
    result = validate(brief, plan)
    print(json.dumps({'case': name, 'status': result['status'],
        'codes': [i['code'] for i in result['issues']]}, ensure_ascii=False))
show('baseline', b, p)

x = deepcopy(p)
x['screens'][0]['feature_ids'] = []
isolated = deepcopy(s)
isolated.update(id='isolated', title='孤立した出力機能', entry_for=[])
x['screens'].append(isolated)
show('mandatory_feature_on_unreachable_screen', b, x)

bb, pp = deepcopy(b), deepcopy(p)
for alias in ('alias1', 'alias2'):
    request = deepcopy(b['feature_requests'][0])
    request.update(id=alias, mandatory=False)
    bb['feature_requests'].append(request)
    merged = deepcopy(f)
    merged.update(id=alias, disposition='merge', target='f')
    pp['features'].append(merged)
show('direct_merge_control', bb, pp)
pp['features'][-1]['target'] = 'alias1'
show('multi_hop_merge', bb, pp)

x = deepcopy(p)
x['unresolved'] = [{'id': 'u', 'category': 'interaction', 'owner': 'B',
    'impact': '結果確認が未確定', 'blocking': True, 'question': '結果確認を定義する'}]
show('blocker_only', b, x)
x['screens'][0]['information'] = []
show('blocker_plus_structural_error', b, x)
PY
```

## 残る確認範囲

上記以外の入力境界、任意ブラウザ検査の実行、原典の再取得、実利用者による発見性・判断精度は今回の対象外。新しい網羅的テストや候補改修は追加しない。PR1〜PR3を報告し、凍結を維持して監査を終了する。
