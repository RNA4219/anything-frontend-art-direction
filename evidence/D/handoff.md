# SESSION D — 統合引き継ぎ

## 取り込み単位と現在の判断

- Base: `f5df625dbc577d6a3ca28e13ef09e39b135b4a6f`。
- Branch: `campaign/D-design-qa-20261123`。
- 変更範囲: `extensions/D/` と `evidence/D/` のみ。
- 入口: `extensions/D/SKILL.md`、Skill名: `anything-frontend-design-qa`。
- 判断: **HOLD**。新規fixtureの実ブラウザ検証と、保護された独立blind評価が不足する。
- 共有ルートの`SKILL.md`、README、既存templates/checklists/referencesは変更していない。他セッションのブランチは取り込んでいない。

このSkillはリポジトリ拡張として実装した。ChatGPT個人Skillへのインストール、共有mainへのマージ、公開サイトへの配備は実施していない。明示された配置と独立ブランチを優先した。

## 他セッションとの契約

| 相手 | Dが入力として必要にするもの | Dから返すもの | Dで変更しないもの |
| --- | --- | --- | --- |
| A — Product / IA | 要求ID、利用者目標、主要タスク、情報階層、必要/除外機能、内容の版。 | functional / information_architecture所見、到達不能な目的、欠けた情報と再現条件。 | 機能優先度、情報分類、ナビゲーション方針。 |
| B — Interaction / Flow | 開始/目的状態、遷移、失敗・再試行・取消し、完了と復帰のoracle。 | interaction所見、task trace、復帰失敗、正常/異常/境界の観察。 | 製品のフロー・状態機械・入力保持方針。 |
| C — UI Engineering | コンポーネント契約、対応状態、breakpoint、入力方式、a11y要件・例外。 | implementation所見、DOM/CSS/操作の不一致、再現可能な回帰ケース。 | tokens、component API、部品実装。 |
| 既存Art Direction | 配色、書体、構図、主役、承認済み表現、比較したい差の範囲。 | visual所見と位置、遮蔽・可読性・対応関係、未確認の美的選択。 | 題材・美的方向・書体や色の好み。 |

各セッションの具体的なschema/Skill名は未統合。Dでは上記の意味的な入力を使用し、存在しないA/B/Cファイルへハード依存を作らない。不明な要求を推測で確定せず、open_questionsへ残す。Dのcategory/ownerは運用分類であり他セッションが同名を実装済みとは仮定しない。

## 共通入口への提案（未適用）

既存ルートSkillの相談表へ、次の一行を追加する案を統合担当が検討できる。

| 相談内容 | 参照先案 |
| --- | --- |
| 既存画面を責務別に評価する、変更前後を同条件で比較する、証拠付き所見と回帰ゲートを作る | `extensions/D/SKILL.md` |

ルートのArt Direction、C3〜C6、既存フォーム/a11yチェックは残し、Dから参照する。画面を新規に描く依頼だけでDの全QA契約を強制しない。既存小修正なら対象タスク/状態だけを点検し、範囲外の適合を主張しない。

## 再現手順

repo rootで、コード・契約の検査を行う。

```bash
python3 -m unittest discover -s extensions/D/tests -p 'test_*.py' -v
node extensions/D/checks/exercise_fixture_logic.mjs evidence/D/local-logic-probes.json
python3 extensions/D/checks/qa_gate.py report extensions/D/examples/report-example.json --root .
python3 extensions/D/checks/qa_gate.py verify-manifest evidence/D/artifact-manifest.json --root .
python3 evidence/D/evaluation/replay_reports.py --output /tmp/design-qa-replay-new.json
```

教材reportは意図的HOLDなのでexit 2が正しい。unit probeのPASSは既知挙動を検出した意味であり、fixtureの製品合格ではない。`exercise_fixture_logic.mjs`は描画しない最小DOMモデルであり、native validation、focus、hit-testing、読み上げを保証しない。

`replay_reports.py`は当時の相対pathを一時領域へ復元し、元の3reportと11artifactを変更せず照合する。出力ファイルが既存なら停止するため、再実行時は新しい名前を使う。生レビュー内のscratch絶対pathは来歴として残し、移植用の照合ではrepo内の同一hashファイルへ対応付ける。LLMレビューとUI操作の再実行ではない。

ブラウザrunnerに見つかった3件の判定・保存の不備は修正し、`evidence/D/gate-review/probe_runner_postfix.py`で8条件を確認した。修正前のproofと結果も同ディレクトリにある。これはsynthetic stubの検査で、実ブラウザ試験とは別である。

Playwright/Chromiumが許可された環境でのみ、以下を別の実行先へ保存する。

```bash
python3 extensions/D/checks/run_browser_checks.py --output evidence/D/browser-fixtures-rerun
```

既存のblocked結果を上書きしない。今回のホストはChromium起動がsocket EPERM、cloud browserはfile protocolがpolicy拒否だった。別プロトコル・別実行経路でその拒否を回避していない。公開済み2作例の操作記録は別対象で、fixtureの合格証拠へ使わない。

## R-ASIの再現

記録時の実装はR-ASI `0.0.2`、source revision `f5b638085dece1f997210f9b653aceb8fe9b32d4`。本体はこの拡張へvendorしていない。許可された取得済み同版の実装を`--tool`へ渡せる。

```bash
python3 evidence/D/rasi/record_cli.py --tool /path/to/R-ASI --label independent-rerun --expect-exit 0 -- verify --sankai inputs/decomposition.json
```

ラベルを変えて新しい実行ログを残す。既存R-ASI CASは`skill-candidate/v1`専用なので画像や一般ログを投入しない。一般artifactはhash manifest、R-ASIへはexperienceのevidence_refで結び付ける。候補包装・CAS整合性・receipt保存は実行済み。改善器・独立Oracle・昇格は接続されていない。

## HOLDを解除するための未実施事項

1. 固定入力の2fixtureで実ブラウザを動かし、正常・異常・境界、320px、keyboard、再試行と完了を確認する。修正済みrunnerの実UI枝はまだ未検証。
2. 既知fixtureを見ていない評価者とアクセス制御された新規holdoutを用意する。Candidateへoracle、rubricの期待解、他条件の出力を渡さず、実際の隔離を記録する。
3. モデル/実行条件を可能な範囲で凍結し、複数trialと提示順反転で結果の再現性を確かめる。今回の1trial比較を一般精度の向上としない。
4. R-ASIのnative campaign-checkに必要な実runtime image digestと凍結policyを観測・記録する。未知のモデル費用はunknownのまま残す。

既存のUIに見つかったと報告する不具合はない。合成fixtureの所見と、検査コードそのものの改善を区別する。既存root/READMEへの提案適用と他領域統合は、上記の証拠を揃えた統合担当の次の作業になる。
