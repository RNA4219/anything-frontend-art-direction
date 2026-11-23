# SESSION B — 現行資産との差分監査

- 確認日: 2026-11-23（Asia/Tokyo）
- Repository: `RNA4219/anything-frontend-art-direction`
- Base SHA: `f5df625dbc577d6a3ca28e13ef09e39b135b4a6f`
- 対象: Interaction Design / UX Flow。以下は現行ファイルの静的観察であり、製品利用者テストや原典の再検証結果ではない。
- 変更範囲: この監査記録のみ。既存 root `SKILL.md`、README、reference、template は変更していない。

## 結論

現行Skillには既に、入力検証、送信者・Enter送信、取消、エラー修正、入力保持、楽観更新の巻戻し、古い応答への対処、履歴、フォーカス復帰、タスクの行動分解に関する索引と小さな実装例がある。「インタラクションが未整備」「エラー処理が無い」と一括判定してはいけない。

Bの追加価値は、これらを目的・開始条件・完了条件から設計する一つの手順へ接続し、操作とシステムイベントの遷移、許可条件、失敗分岐、復帰経路、終了判定を明示した契約と再現テストにすること。視覚的意図や既存実装規則の再定義は不要。

## 既存対応と追加対象

| Bの責務 | 現行で確認した対応 | 今回追加する差分 | 重複を避ける方法 |
| --- | --- | --- | --- |
| ジャーニー・タスクフロー | `references/c-usability.md` C4-03 は行動単位への分解、C4-04/05/14 は目標と操作・直後の結果の照合。`references/visual-composition.md`「まず主役と一緒に必要なものを決める」は判断に必要な情報と操作を対応付ける。 | actor、trigger、entry condition、goal、success predicate、abandonment、例外の契約。ジャーニー全体から今回扱うタスク境界を切り出す手順。 | 機能の採否・情報配置はA、造形は既存Art Directionへ返す。Bは決められた目的を遂行できる経路を扱う。 |
| 操作状態・遷移 | `references/g-state-forms.md` G-01–11 はReactの状態管理、特にG-06は古い応答。G3-01–43は履歴/Navigation API。`references/k-studies.md` K2-03は画面遷移と画面内状態の区別。 | framework非依存の状態表・遷移表、event/guard/effect、ユーザー操作と非同期イベントの区別、到達不能・行き止まり・閉じた循環の検査。 | API仕様を再録しない。実装時に既存G系列へ誘導する。 |
| 入力・確認・送信 | `checklists/forms.md` 全項目、G2-09–18、G5-01–47、G7-05/09。`templates/form.html` は1〜8人のnative validation、`formnovalidate` の下書き、`submitter` の分岐を実装。 | 項目修正→再確認→送信→受付確定までの状態契約。確認を必要とする結果の重大性/可逆性の判断、途中変更時に確認済み内容を無効化する条件、処理中の入力・送信可否。 | native form/Enter/requestSubmitの既存規則を保持する。全フォームへ一律に確認画面を追加しない。 |
| 取消・中断・再開 | `references/c-usability.md` C-04、`references/k-studies.md` K1-14、K5-09。`templates/dialog.html` はEscと「編集を続ける」「終了する」、close後の結果を扱う。E2-03/05は開始・復帰フォーカス。 | 戻る、未送信の破棄、通信待ちの中断、サーバー処理の取消、確定後のundoを別操作として定義。server commit確認前は成功/取消済みを断言しない。再訪時の再同期を設計。 | ダイアログ部品とキーボード契約はCへ渡し、Bはどの状態へ戻るか/何を保持するかを指定する。 |
| エラー・再試行・復帰 | C-10、C2-02/05/07/08/11は項目特定、早すぎる警告の回避、次行動、入力保持。D-31は修復手段への接続。 | validation、business rejection、transport failure、unknown outcome、authorization/session expiryを区別し、各々の戻り先/保持データ/再試行可否/問い合わせ先を決める。 | 「具体的なエラー文」「入力保持」は既存対応。新規原則として発見したと主張せず、分岐と検証への接続を追加とする。 |
| 非同期処理・feedback | D-34–44は楽観更新、D-37は巻戻し、D-38は古い再取得、D-41は競合。K5-01–09は待ち時間・進捗・中断、C-02は処理の可視性。`templates/optimistic.html` はpending中の操作guard、250msの模擬成功/失敗、rollback、status通知を実装。 | request identity、pending/slow/unknown/success/error/cancel_requested/cancelledの必要条件、deadline後の再同期、二重確定防止のバックエンド契約、stale応答/部分成功の扱いを操作フローへ接続。 | 「loadingを付ける」「rollbackする」を新発見扱いしない。進捗率が不明なら推定値を事実として表示しない。 |
| 完了可能性・余計な操作 | K1-13は完了表示、C4-14は次の操作と結果、K3-13/14は情報量・移動回数・最大手数を分離して検討。 | 各開始状態からsuccessまたは説明付きexitへ到達する証拠、失敗状態から継続/やり直し/離脱する経路、不要なループと二重入力、成功を判定するサーバー証跡のテスト。 | 最小クリック数を普遍的な正解にしない。必要な確認/復帰手段まで削らない。 |
| 評価の信頼性 | C3-04–06は専門家/利用者と独立点検、C4-26/28は対照と観察の照合、C5-17/18/37は参照問題の妥当性・分母・所見共有前の点検。 | B固有の正常/異常/境界fixture、共通条件baseline/candidate比較、モデル実行と機械検査の区別。 | Dの汎用QA方式を再実装しない。Bで検証したflow contractとtraceをDへ渡す。 |

## 現行実装を誤って欠陥扱いしないための留意点

1. `templates/form.html` はnative validationとdraft分岐を示す教材。server persistenceを持たないこと自体は、記載された目的の不具合ではない。
2. `templates/optimistic.html` は既にpending中の重複起動guard、直前確定値の保持、失敗rollback、`role="status"` の通知を実装している。追加のB fixtureにtimeout等を入れても、このテンプレートがそれらを実装済みと主張したことにはならない。
3. `templates/dialog.html` は汎用的な確認例。実データのdirty stateやserver cancelがないことを「未修正」と判定しない。
4. `references/visual-composition.md` には操作後も状態を残すこと、選択対象を結果へつなぐことが既にある。Bはその視覚表現を置き換えず、表示が表す事実と遷移を契約化する。
5. 既存索引に「確認すること」があるのと、機械が実行できる出力契約・テストがあるのは別。追加対象は後者を中心とする。

## 原典の再利用候補

以下は現行 `sources.md` に存在する出典。ここでの確認はリポジトリ内の記載と対応IDのみ。原典の現行内容・該当箇所・確認日は、新規source-index作成時に別途確認する。

| 既存出典ID | 原典 | Bで再利用する既存ID |
| --- | --- | --- |
| 001 | [NN/g — 10 Usability Heuristics](https://www.nngroup.com/articles/ten-usability-heuristics/) | C-02、C-04、C-06、C-07、C-10 |
| 047 | [NN/g — Error Message Guidelines](https://www.nngroup.com/articles/error-message-guidelines/) | C2-02、C2-05、C2-07、C2-08、C2-11 |
| 123 | [NN/g — Response Times](https://www.nngroup.com/articles/response-times-3-important-limits/) | K5-01–09 |
| 065 | [Shneiderman — Eight Golden Rules](https://www.cs.umd.edu/users/ben/goldenrules.html) | K1-13–16 |
| 100 | [Spencer — The Streamlined Cognitive Walkthrough Method](https://doi.org/10.1145/332040.332456) | C4-03–05、C4-14、C4-26–28 |
| 002 | [W3C — WCAG 2.2](https://www.w3.org/TR/WCAG22/) | E-09（同じ手続きでの入力再利用） |
| 006 | [WAI APG — Dialog Modal](https://www.w3.org/WAI/ARIA/apg/patterns/dialog-modal/) | E2-03、E2-05（Bは戻り先、Cは部品実装） |
| 036 | [TanStack Query — Optimistic Updates](https://raw.githubusercontent.com/tanstack/query/main/docs/framework/react/guides/optimistic-updates.md) | D-34–38 |
| 037 | [SWR — Mutation](https://swr.vercel.app/docs/mutation) | D-39–41 |
| 023 | [React — You Might Not Need an Effect](https://react.dev/learn/you-might-not-need-an-effect) | G-06 |
| 063 | [WHATWG HTML — Navigation and History](https://html.spec.whatwg.org/multipage/nav-history-apis.html) | G3-11/15/23/25/37–40 |
| 087、088、092 | [WHATWG HTML — Constraints](https://html.spec.whatwg.org/multipage/form-control-infrastructure.html#constraints)、[Submission](https://html.spec.whatwg.org/multipage/form-control-infrastructure.html#form-submission-2)、[form](https://html.spec.whatwg.org/multipage/forms.html#the-form-element) | G5-05–11/14/21、G7-05/09 |

## Inventoryと検査範囲

読み取り対象: root `SKILL.md`、`README.md`、`sources.md`、`references/d-interaction.md`、`references/g-state-forms.md`、`references/c-usability.md`、`references/e-accessibility.md`、`references/k-studies.md`、`references/visual-composition.md`、`checklists/forms.md`、`templates/README.md`、`templates/form.html`、`templates/optimistic.html`、`templates/dialog.html`。

次の探索を、B追加前の現行treeについて実施した。

```sh
git rev-parse HEAD
rg --files --hidden -g '!.git' -g 'AGENTS.md' -g '*finding*' -g '*phase2*' -g '*receipt*' -g '*manifest*' -g '*CAS*' -g '*cas*' -g '*test*' -g '*spec*' -g 'package.json' -g 'pyproject.toml' -g 'Makefile' -g '*.lock'
rg -n 'FSM|state machine|状態機械|journey|ジャーニ|到達|循環|行き止まり|retry|Retry|timeout|タイムアウト|二重送信|冪等|取消|復帰|flow|フロー' references checklists templates SKILL.md --glob '*.md' --glob '*.html'
```

- `findings.md`、`phase2-issues.md`、CAS、receipt、テストランナー、テストfixture、`AGENTS.md` はこのbase treeに非同梱。過去作業が未実施・未修正とは推定しない。
- 名前が近い `data/typography/findings.csv` は存在し、READMEに記載された書体調査データである。Bの課題台帳とは扱わない。
- 既存HTMLは手動確認方法付きの実装例。今回の監査では実行しておらず、動作PASSは付けていない。
- 本監査はBの差分候補を定義するもの。実際の追加・未解決・検証結果の最終状態は `coverage-matrix.md` と `validation.md` で管理する。
