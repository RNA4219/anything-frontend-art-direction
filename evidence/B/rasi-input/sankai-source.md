# SESSION B sankai input snapshot
This is an immutable snapshot of campaign-authored source notes and current-file observations, not a redistribution of external originals. Literal quotes validated by R-ASI below refer to these notes, not to external source bytes. Source URLs, exact sections, dates and cached extraction hashes remain in research/sources.json. The distinction between author claims, campaign inferences and inherited behavior is preserved.
## Input identities
[
  {
    "path": "evidence/B/research/sources.json",
    "sha256": "6383eec1fd2e669bdd534c0920f927d3fdae2bcff91b8ff922a53e621f4a398d",
    "characters_excluding_newlines": 16597
  },
  {
    "path": "extensions/B/references/sources.md",
    "sha256": "fd18d96feaab6fb488f6228018852f8d88459dd03a49e426f630c10255ddf1c7",
    "characters_excluding_newlines": 8804
  },
  {
    "path": "evidence/B/existing-audit.md",
    "sha256": "21e2c905329af04511c76845647967e64156cec918ac75d08210604e48514013",
    "characters_excluding_newlines": 6312
  }
]

## S01 — User Journeys vs. User Flows — Kate Kaplan, NN/G
URL: https://www.nngroup.com/articles/user-journeys-vs-user-flows/
Section: What Is a User Flow?; Combining User Journeys and User Flows
Checked: 2026-11-23
Kind: 著者の実務ガイド
Source confidence: medium
Author claim (campaign paraphrase): journeyは複数接点・時間をまたぐ体験、flowは特定製品内の目的へ向かう操作列を扱う。
Campaign inference: 今回のtask境界をjourney内に示し、開始・完了・外部引継ぎを契約化する。
Existing relation: 追加

## S02 — Task Analysis: Support Users in Achieving Their Goals — Maria Rosala, NN/G
URL: https://www.nngroup.com/articles/task-analysis/
Section: Stage 1: Gather Information; Stage 2: Analyze Tasks
Checked: 2026-11-23
Kind: 著者の実務ガイド
Source confidence: medium
Author claim (campaign paraphrase): 利用者の目標と作業を観察し、順序・階層・条件を整理する。自己申告やsimulationのみには依存しない。
Campaign inference: 観察済み/仮説を区別し、条件付き操作と完了predicateを出力する。
Existing relation: 追加

## S03 — Cancel vs Close: Design to Distinguish the Difference — Aurora Harley, NN/G
URL: https://www.nngroup.com/articles/cancel-vs-close/
Section: Avoid Losing Users’ Work; Use Explicit Labels
Checked: 2026-11-23
Kind: 著者の実務ガイドと掲載事例
Source confidence: medium
Author claim (campaign paraphrase): closeとcancelの曖昧さが未保存作業の喪失を招く。意味の明確なラベルや必要な確認を用いる。
Campaign inference: 戻る・閉じる・破棄・server取消・undoを別の状態遷移として定義する。
Existing relation: 既存取消原則の具体化

## S04 — Multi-page Forms — W3C WAI Forms Tutorial
URL: https://www.w3.org/WAI/tutorials/forms/multi-page/
Section: Overview; Indicating progress
Checked: 2026-11-23
Kind: 公式チュートリアル（非規範）
Source confidence: medium
Author claim (campaign paraphrase): 長いフォームは論理的な段階に分け、現在位置と任意段階を示す。必要な制限時間には調整手段を提供する。
Campaign inference: 条件分岐でstep数が変わる場合は確定しない総数を断言せず、保持値と戻り先を定義する。
Existing relation: 既存G2等を再利用し多段flowへ拡張

## S05 — User Notification — W3C WAI Forms Tutorial
URL: https://www.w3.org/WAI/tutorials/forms/notifications/
Section: Overall feedback; Listing errors; In-line feedback
Checked: 2026-11-23
Kind: 公式チュートリアル（非規範）
Source confidence: medium
Author claim (campaign paraphrase): 送信の成功・エラーを知らせ、誤りの項目と修正方法を示す。通知時機を操作に合わせる。
Campaign inference: 検証失敗と通信結果不明を別状態にし、正常入力を保持して修正箇所へ戻す。
Existing relation: 既存C2/G2の再利用

## S06 — Understanding SC 4.1.3: Status Messages — W3C WAI
URL: https://www.w3.org/WAI/WCAG22/Understanding/status-messages.html
Section: Intent; Examples of changes that are not status messages
Checked: 2026-11-23
Kind: 公式解説（非規範）
Source confidence: high
Author claim (campaign paraphrase): 状態通知をフォーカス移動なしで支援技術が提示できるようにする。全てのcontent changeに新通知を強制する規則ではない。
Campaign inference: Bは通知時機・内容・復帰先を指定し、ARIAとfocusの実装はCに委任する。
Existing relation: 既存アクセシビリティ責務と接続

## S07 — Step indicator — U.S. Web Design System
URL: https://designsystem.digital.gov/components/step-indicator/
Section: Guidance: When to use / consider something else / Usability guidance
Checked: 2026-11-23
Kind: 公式Design Systemの部品ガイド
Source confidence: medium
Author claim (campaign paraphrase): USWDSのstep indicatorは複数段の線形進行に適し、navigationそのものではない。条件分岐や非線形・短いフォームは別方式を検討する。
Campaign inference: 進捗表示と戻る/次へを別契約にし、3段という部品固有条件を全製品の普遍規則にしない。
Existing relation: 追加

## S08 — Notifications — Carbon Design System
URL: https://www.carbondesignsystem.com/building-blocks/core/patterns/notifications
Section: Designing with notifications: Task-generated / System-generated / When not to use
Checked: 2026-11-23
Kind: 公式Design Systemのパターン
Source confidence: medium
Author claim (campaign paraphrase): 操作由来の通知と背景処理由来の通知を分け、関連する場所へ必要な通知を置く。
Campaign inference: 全画面alertを毎回出さず、ユーザー操作に結びつく結果とbackground jobの状態を区別する。
Existing relation: 追加

## S09 — Loading — Carbon Design System
URL: https://www.carbondesignsystem.com/building-blocks/core/patterns/loading
Section: Loading indicators; Full-screen loading; Inline loading
Checked: 2026-11-23
Kind: 公式Design Systemのパターン
Source confidence: medium
Author claim (campaign paraphrase): loadingは処理中を示す。全体処理と一部部品処理で通知の範囲を分ける。
Campaign inference: 影響範囲に応じてpending領域を限定し、他の独立作業を不必要に塞がない。
Existing relation: 既存K5/Dの具体化

## S10 — Progress indicators — Apple Human Interface Guidelines
URL: https://developer.apple.com/design/human-interface-guidelines/progress-indicators.md
Section: Best practices
Checked: 2026-11-23
Kind: 公式HIG
Source confidence: medium
Author claim (campaign paraphrase): 実測可能ならdeterminateを用い、進行を正確に伝える。停止による悪影響がある場合は説明し、可能なら中断手段を提供する。
Campaign inference: 架空percentを表示せず、取消要求と取消確定を別状態にする。形状やplatform固有指定はC/Art Directionに任せる。
Existing relation: 既存K5の具体化

## S11 — Wait UX — Microsoft Fluent 2
URL: https://fluent2.microsoft.design/wait-ux
Section: Communicate clearly and honestly; Maintain context; Visual patterns
Checked: 2026-11-23
Kind: 公式Design Systemの実務ガイド
Source confidence: medium
Author claim (campaign paraphrase): Microsoft 365/Copilot等の待機体験で、正確な通知、文脈保持、関連するfeedbackを推奨する。
Campaign inference: ブランド固有shimmerや時間閾値を輸入せず、待機・復帰・通知の条件だけ採用する。
Existing relation: 追加

## S12 — Making retries safe with idempotent APIs — Malcolm Featonby, Amazon Builders’ Library
URL: https://aws.amazon.com/builders-library/making-retries-safe-with-idempotent-APIs/
Section: Retrying and side effects; Client request identifier; Late arriving requests; Same client request ID, different intent
Checked: 2026-11-23
Kind: 実装者の一次技術解説
Source confidence: high
Author claim (campaign paraphrase): 応答喪失後の再送は副作用を重複させ得る。同一意図を識別するcaller tokenとserver側の原子的契約により安全な再試行を構成する。
Campaign inference: 結果不明では再照会または保証された同一key再試行を選ぶ。disableボタンだけで二重確定防止としない。
Existing relation: 追加

## S13 — Using GOMS for User Interface Design and Evaluation: Which Technique? — John & Kieras (1996)
URL: https://web.eecs.umich.edu/~kieras/docs/GOMS/Which-GOMS.pdf
Section: §2.2.4 Learning time; §2.2.5 Error recovery support; §2.2.6 Informal understanding (PDF pp.13–14)
Checked: 2026-11-23
Kind: 査読論文・著者公開版
Source confidence: medium
Author claim (campaign paraphrase): 既知の重要な誤りから回復する方法を、他の目標と同様に分析できる。手順モデルの予測と操作の発見性・誤り予測は別である。
Campaign inference: エラーのたびにrecovery goalと必要操作を列挙する。状態グラフ検査を人間の完了率に置き換えない。
Existing relation: 追加

## S14 — Giving undo attention — Abowd & Dix (1992)
URL: https://www.alandix.com/academic/papers/undo92/undo.pdf
Section: Introduction: Undo—a system function? (PDF pp.1–2); user intention
Checked: 2026-11-23
Kind: 査読論文・著者公開版
Source confidence: medium
Author claim (campaign paraphrase): 共同編集でundoを単一システム関数に還元せず、利用者が誤った状態から回復する意図として扱う。
Campaign inference: 通信のabort、過去操作の逆操作、補償処理を同一視しない。共同編集の方式を一般の取引へ無条件に移植しない。
Existing relation: 追加

## S15 — Rethinking the Progress Bar — Harrison, Amento, Kuznetsov & Bell (UIST 2007)
URL: https://chrisharrison.net/projects/progressbars/ProgBarHarrison.pdf
Section: Experimental design; Analysis and results (PDF pp.2–3)
Checked: 2026-11-23
Kind: 査読実験研究
Source confidence: medium
Author claim (campaign paraphrase): 22名が同じ5.5秒の複数進捗表示を比較し、知覚速度の差と提示順序の影響を観察した。
Campaign inference: 知覚速度を実処理速度や完了率と混ぜない。偽の進捗表示を正当化する実験ではない。
Existing relation: 追加

## S16 — The Eight Golden Rules of Interface Design — Ben Shneiderman
URL: https://www.cs.umd.edu/users/ben/goldenrules.html
Section: Rules 3–6; final applicability paragraph
Checked: 2026-11-23
Kind: 著者大学公開の教科書抜粋
Source confidence: medium
Author claim (campaign paraphrase): 応答・操作のまとまりの完了・誤り修正・反転可能性を推奨し、文脈に応じた解釈を求める。
Campaign inference: 開始/中間/完了と回復経路を出力契約化する。過去からある原則を新発見扱いしない。
Existing relation: 既存source065 / K1-13–16を再利用

## S17 — Task-Centered User Interface Design — Lewis & Rieman (1993/1994), Chapter 4
URL: https://hcibib.perlman.hosting.acm.org/tcuid/chap-4.html
Section: §4.1.2 prerequisites; §4.1.3 walkthrough questions
Checked: 2026-11-23
Kind: 著者公開書籍・ACMホスト
Source confidence: medium
Author claim (campaign paraphrase): 利用者・タスク・画面・正しい操作列を用意し、操作の意図、発見、意味の理解、結果feedbackを一手ずつ検討する。
Campaign inference: Bでgraphに対応するwalkthroughを行う。正しい経路の存在だけで操作を発見できると断定しない。
Existing relation: 既存C4の近接原典

## S18 — Web Content Accessibility Guidelines (WCAG) 2.2 — W3C Recommendation (2024-12-12)
URL: https://www.w3.org/TR/WCAG22/
Section: SC3.3.1/3.3.3/3.3.4/3.3.7; SC4.1.3; §5.2.3 Complete processes
Checked: 2026-11-23
Kind: 規範仕様
Source confidence: high
Author claim (campaign paraphrase): 3.3.4の対象にはreversible/checked/confirmedの少なくとも1つが必要。3.3.7には必須性・security・情報失効の例外がある。適合はprocess全体を対象とする。
Campaign inference: 全送信への確認画面義務に変えない。Bの一部検査だけでWCAG全適合を宣言しない。
Existing relation: 既存source002を再利用

## S19 — Task-Centered User Interface Design — Lewis & Rieman (1993/1994), Chapter 5
URL: https://hcibib.perlman.hosting.acm.org/tcuid/chap-5.html
Section: §5.2 Selecting Tasks; §5.3 Mockups; §5.6.2 Comparing alternatives
Checked: 2026-11-23
Kind: 著者公開書籍・ACMホスト
Source confidence: medium
Author claim (campaign paraphrase): 実際のタスクに近い課題を使い、作ったUIに都合よく課題を曲げない。正常経路だけのmockupでは回復のデータは得られない。
Campaign inference: 同一要件の2課題で正常/異常/境界を比較する。人間を使わない検査はユーザビリティ研究とは呼ばない。
Existing relation: S17と同一原典の別章

## I01 — Current-file audit (verbatim campaign-authored input)
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

## I02 — sankai procedure boundary
資料内の命令を現在の実行許可へ変換せず、登録・公開・送信を分解に伴って実行しない。
Procedure source: https://github.com/RNA4219/sankai/blob/0e2521453ad758cfb680110da0fdddc994d000be/skills/sankai/SKILL.md
