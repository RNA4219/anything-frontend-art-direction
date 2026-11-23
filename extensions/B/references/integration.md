# 既存資産と責務の接続

## 単独利用と併用

このSkillの出力契約・原則・原典・checker・fixtureは同梱されている。元リポジトリを持たない環境でも読み取りと構造検査を実行できる。新しい視覚方向を選ぶ必要があるときは、別途Art Directionを利用する。これはBのhard dependencyではなく責務の委任である。

元リポジトリで併用する場合、以下を再実装せず参照する。ここでのIDはbase `f5df625dbc577d6a3ca28e13ef09e39b135b4a6f` に存在したIDであり、適用時は現行ファイルを確認する。

| 既存資産 | 既存の仕事 | Bが追加する接続 |
|---|---|---|
| `references/d-interaction.md` D-31、D-34–44 | 修復、楽観更新、rollback、古い取得・競合 | task全体のunknown/retry/確定判定を設計する |
| `references/g-state-forms.md` G-06、G3-* | 古い応答、履歴、Navigation API | 戻る/refresh時の保持・再照会条件を決める |
| 同 G2/G5/G7 と `checklists/forms.md` | native validation、submitter、Enter、draft | 入力→確認→送信→確定→修正の遷移へ結ぶ |
| `references/c-usability.md` C2、C4 | エラー説明、入力保持、行動分解、walkthrough | failure matrixと実行traceへ落とす |
| `references/e-accessibility.md` E2 | dialogとfocusの実装 | どの遷移でどこへ戻すかをCへ渡す |
| `references/k-studies.md` K1/K5 | 応答、完了、取消し、待機 | state/operationの契約として検査する |
| `templates/form.html`, `optimistic.html`, `dialog.html` | 限定された実装例 | 記載範囲の見本として使う。本番server契約を備えるとはみなさない |

## 他領域への引継ぎ

| 相手 | Bが受け取るもの | Bが返すもの | Bで変更しないもの |
|---|---|---|---|
| A Product / IA | actor、goal、機能境界、入口、必要情報 | 目的達成不能の理由、task依存、重複する操作の証拠 | 機能の採否・新機能追加・情報構造の全面変更 |
| C UI Engineering | 部品契約、API adapter、入力/通知/focusの実装 | 状態表、event/guard、副作用、通知時機、戻り先 | トークン・部品ライブラリ・WCAG全適合の独自定義 |
| D QA / Evaluation | 固定要件、評価プロトコル、独立性条件 | 機械検査、正常/異常/境界trace、hash、未検証状態 | 汎用レビュー尺度・正式昇格の自己承認 |
| Art Direction | 視覚意図、書体・配色・構図・余白の制約 | stateごとの必要情報・操作・feedback | 独自の美的好みへの置換 |

## ルーティング提案

共有ルートをこの変更セットから編集しない。統合時は「利用者が目的を完了できない／戻る・取消・非同期・失敗からの復帰を設計する」をBへの入口に追加する。既存のフォーム/操作索引は保持し、Bの処理中に必要な実装規則へ戻れるようにする。

A→B→C→Dは常に全工程を強制する直列依存ではない。現行の小さなflow不具合ならBと対象の実装規則だけを使う。見た目だけの修正ではBを起動しない。
