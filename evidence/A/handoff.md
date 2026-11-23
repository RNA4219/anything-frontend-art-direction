# SESSION A — 統合引継ぎ

## 判断

**HOLD。独立ブランチに実装・試験・証跡を保存した。正式昇格とmainへの統合は行っていない。**
比較の実数と未検証事項は [validation.md](validation.md)、R-ASIの実行結果は [record-index.md](rasi/record-index.md) を参照する。

- 基準commit: `f5df625dbc577d6a3ca28e13ef09e39b135b4a6f`
- 独立branch: `campaign/A-product-ia-20261123`
- 初回公開実装commit: `97b19c29c0b63acfee9ad437f93af081ac0c6ef8`
- 作業範囲: `extensions/A/**` と `evidence/A/**` のみ。
- 共有rootのSKILL、README、既存テンプレート、既存referencesは変更していない。
- 個人用Skillへのインストール、mainへのmerge、他セッションのbranch変更は行っていない。

## 独立入口

入口は `extensions/A/SKILL.md`、Skill名は `anything-frontend-product-ia`。
このディレクトリをSkillとして読み込むか、既存のArt Directionと併せて入口を指定する。
生成したUIメタデータは `extensions/A/agents/openai.yaml`。

必要な入力は、役割、達成結果、必須要件、機能要求、データ例、既存の視覚意図。
機能の処置、優先理由、正本、画面責務、役割別経路、primary/secondary情報、未解決事項を返す。
小変更では文章・表を許容し、複数画面や機械検査ではplan契約を使う。
runtimeにimozuru・sankai・R-ASIは要求しない。validatorはPython標準ライブラリのみ。

## 他セッションとの境界

| 相手 | Aから渡すもの | 相手が決めること | Aで変更しないもの |
|---|---|---|---|
| B — Interaction Design | role/goal、screen purpose、入口と行先、依存、選択文脈、未決の業務条件 | 操作順、状態遷移、送信/取消、失敗/再試行、戻りと復帰、非同期処理 | 状態機械、フォーム送信実装 |
| C — UI Engineering | 既存visual_intent、同時参照情報、primary/secondary、役割、画面責務 | component契約、tokens、レスポンシブ、入力デバイス、WCAG/ARIA、認可実装との接続 | 配色・書体の変更、部品APIの固定 |
| D — Design QA | frozen brief/plan、原本hash、検査器、未解決事項、役割別経路、実行ログ | 独立課題/Oracle、評価の隔離、操作試験、画面比較、回帰gate | D全体の品質尺度の制定、独立評価PASSの代行 |
| 既存Art Direction | 判断のまとまり、情報の優先関係、同時比較の条件 | 造形、配色、タイポグラフィ、構図、意図の表現 | 既存の美的方針を別案へ差替え |

複数Skillが同じ問題を見つけた場合、問題IDと担当を共有する。
機能/情報構造はA、操作状態はB、部品・実装はC、試験・指摘管理はDへ渡す。
ラベルの理解可能性と、文字量による判断・配置への影響は評価できる。文章の題材や好みは不具合にしない。

## 共通入口への変更案（未適用）

rootの「利用目的・判断・必要情報を読む」手順の後に、次の条件分岐を追加する案とする。

> 機能の統合・削除・優先順位、情報分類、ナビゲーション、画面責務が未決なら、`extensions/A/SKILL.md`を読み、目標–要件–機能と情報構造を確定する。そこで得た視覚意図への制約を保持して、既存Art Directionへ戻る。意匠だけの変更ではこの追加手順を起動しない。

この提案をrootファイルへ書き込んでいない。B/C/Dの入口が揃った後に、統合担当がルーティング順と重複する入出力を確認する。

## 統合前に閉じる条件

1. Dが、本キャンペーンの生成者から隔離したOracle・未公開holdoutと採点条件を準備する。
2. 既存Skillと追加Skillを同じモデル・実行設定で比較し、改善の有無と回帰を再評価する。差がない場合も記録する。
3. ブラウザを利用できる環境で、保存したHTMLとprobeを実行する。今回の環境で実画面・操作・スクリーンショットを確認済みとは扱わない。
4. 分類とラベルの妥当性は対象利用者で検証する。LLM reviewと機械的な到達性を利用者のタスク成功率へ読み替えない。
5. R-ASIの実行・評価・昇格adapterが未接続であることを維持し、外部試験の実結果とhashを記録する。noise calibration、container digest、費用等が必要なgateは実データで補う。
6. rootとの重複がないこと、B/C/Dの契約との参照整合、`extensions/A`以外に実装変更がないことを統合時点のrevisionで確認する。

## 再現の入口

```bash
python3 -B -m unittest discover -s extensions/A/tests -p 'test_*.py' -v
python3 -B extensions/A/checks/compare_plans.py --briefs-dir extensions/A/tests/briefs --baseline-dir evidence/A/experiment/baseline --candidate-dir evidence/A/experiment/candidate --output /tmp/A-comparison.json
```

上の比較コマンドは構造と宣言された経路を報告する。品質昇格を行わない。
HTMLの生成とブラウザprobeのコマンドは [checks/README.md](../../extensions/A/checks/README.md) にある。
R-ASIの再実行には、記録したrevisionのR-ASI実装を別途用意する。private実装本体をこのpublic branchへ複製していない。
