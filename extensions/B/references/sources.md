# 原典と適用範囲

確認日: 2026-11-23（Asia/Tokyo）。18原典・19参照箇所。S17とS19は同一書籍なので原典数に二重計上しない。

confidenceは原文と採用条件の対応についての判断であり、Skillの効果量ではない。`high`も無条件の一般化や本番保証を意味しない。公式解説と規範要件、著者の意見と観測結果、今回の設計推論を区別する。

<a id="s01"></a>
## S01 — User Journeys vs. User Flows — Kate Kaplan, NN/G

- URL: [User Journeys vs. User Flows — Kate Kaplan, NN/G](https://www.nngroup.com/articles/user-journeys-vs-user-flows/)
- 箇所: What Is a User Flow?; Combining User Journeys and User Flows
- 種別 / 確信度: 著者の実務ガイド / medium
- 原典の主張: journeyは複数接点・時間をまたぐ体験、flowは特定製品内の目的へ向かう操作列を扱う。
- 本Skillの推論・採用範囲: 今回のtask境界をjourney内に示し、開始・完了・外部引継ぎを契約化する。
- 既存との関係: 追加

<a id="s02"></a>
## S02 — Task Analysis: Support Users in Achieving Their Goals — Maria Rosala, NN/G

- URL: [Task Analysis: Support Users in Achieving Their Goals — Maria Rosala, NN/G](https://www.nngroup.com/articles/task-analysis/)
- 箇所: Stage 1: Gather Information; Stage 2: Analyze Tasks
- 種別 / 確信度: 著者の実務ガイド / medium
- 原典の主張: 利用者の目標と作業を観察し、順序・階層・条件を整理する。自己申告やsimulationのみには依存しない。
- 本Skillの推論・採用範囲: 観察済み/仮説を区別し、条件付き操作と完了predicateを出力する。
- 既存との関係: 追加

<a id="s03"></a>
## S03 — Cancel vs Close: Design to Distinguish the Difference — Aurora Harley, NN/G

- URL: [Cancel vs Close: Design to Distinguish the Difference — Aurora Harley, NN/G](https://www.nngroup.com/articles/cancel-vs-close/)
- 箇所: Avoid Losing Users’ Work; Use Explicit Labels
- 種別 / 確信度: 著者の実務ガイドと掲載事例 / medium
- 原典の主張: closeとcancelの曖昧さが未保存作業の喪失を招く。意味の明確なラベルや必要な確認を用いる。
- 本Skillの推論・採用範囲: 戻る・閉じる・破棄・server取消・undoを別の状態遷移として定義する。
- 既存との関係: 既存取消原則の具体化

<a id="s04"></a>
## S04 — Multi-page Forms — W3C WAI Forms Tutorial

- URL: [Multi-page Forms — W3C WAI Forms Tutorial](https://www.w3.org/WAI/tutorials/forms/multi-page/)
- 箇所: Overview; Indicating progress
- 種別 / 確信度: 公式チュートリアル（非規範） / medium
- 原典の主張: 長いフォームは論理的な段階に分け、現在位置と任意段階を示す。必要な制限時間には調整手段を提供する。
- 本Skillの推論・採用範囲: 条件分岐でstep数が変わる場合は確定しない総数を断言せず、保持値と戻り先を定義する。
- 既存との関係: 既存G2等を再利用し多段flowへ拡張

<a id="s05"></a>
## S05 — User Notification — W3C WAI Forms Tutorial

- URL: [User Notification — W3C WAI Forms Tutorial](https://www.w3.org/WAI/tutorials/forms/notifications/)
- 箇所: Overall feedback; Listing errors; In-line feedback
- 種別 / 確信度: 公式チュートリアル（非規範） / medium
- 原典の主張: 送信の成功・エラーを知らせ、誤りの項目と修正方法を示す。通知時機を操作に合わせる。
- 本Skillの推論・採用範囲: 検証失敗と通信結果不明を別状態にし、正常入力を保持して修正箇所へ戻す。
- 既存との関係: 既存C2/G2の再利用

<a id="s06"></a>
## S06 — Understanding SC 4.1.3: Status Messages — W3C WAI

- URL: [Understanding SC 4.1.3: Status Messages — W3C WAI](https://www.w3.org/WAI/WCAG22/Understanding/status-messages.html)
- 箇所: Intent; Examples of changes that are not status messages
- 種別 / 確信度: 公式解説（非規範） / high
- 原典の主張: 状態通知をフォーカス移動なしで支援技術が提示できるようにする。全てのcontent changeに新通知を強制する規則ではない。
- 本Skillの推論・採用範囲: Bは通知時機・内容・復帰先を指定し、ARIAとfocusの実装はCに委任する。
- 既存との関係: 既存アクセシビリティ責務と接続

<a id="s07"></a>
## S07 — Step indicator — U.S. Web Design System

- URL: [Step indicator — U.S. Web Design System](https://designsystem.digital.gov/components/step-indicator/)
- 箇所: Guidance: When to use / consider something else / Usability guidance
- 種別 / 確信度: 公式Design Systemの部品ガイド / medium
- 原典の主張: USWDSのstep indicatorは複数段の線形進行に適し、navigationそのものではない。条件分岐や非線形・短いフォームは別方式を検討する。
- 本Skillの推論・採用範囲: 進捗表示と戻る/次へを別契約にし、3段という部品固有条件を全製品の普遍規則にしない。
- 既存との関係: 追加

<a id="s08"></a>
## S08 — Notifications — Carbon Design System

- URL: [Notifications — Carbon Design System](https://www.carbondesignsystem.com/building-blocks/core/patterns/notifications)
- 箇所: Designing with notifications: Task-generated / System-generated / When not to use
- 種別 / 確信度: 公式Design Systemのパターン / medium
- 原典の主張: 操作由来の通知と背景処理由来の通知を分け、関連する場所へ必要な通知を置く。
- 本Skillの推論・採用範囲: 全画面alertを毎回出さず、ユーザー操作に結びつく結果とbackground jobの状態を区別する。
- 既存との関係: 追加

<a id="s09"></a>
## S09 — Loading — Carbon Design System

- URL: [Loading — Carbon Design System](https://www.carbondesignsystem.com/building-blocks/core/patterns/loading)
- 箇所: Loading indicators; Full-screen loading; Inline loading
- 種別 / 確信度: 公式Design Systemのパターン / medium
- 原典の主張: loadingは処理中を示す。全体処理と一部部品処理で通知の範囲を分ける。
- 本Skillの推論・採用範囲: 影響範囲に応じてpending領域を限定し、他の独立作業を不必要に塞がない。
- 既存との関係: 既存K5/Dの具体化

<a id="s10"></a>
## S10 — Progress indicators — Apple Human Interface Guidelines

- URL: [Progress indicators — Apple Human Interface Guidelines](https://developer.apple.com/design/human-interface-guidelines/progress-indicators.md)
- 箇所: Best practices
- 種別 / 確信度: 公式HIG / medium
- 原典の主張: 実測可能ならdeterminateを用い、進行を正確に伝える。停止による悪影響がある場合は説明し、可能なら中断手段を提供する。
- 本Skillの推論・採用範囲: 架空percentを表示せず、取消要求と取消確定を別状態にする。形状やplatform固有指定はC/Art Directionに任せる。
- 既存との関係: 既存K5の具体化

<a id="s11"></a>
## S11 — Wait UX — Microsoft Fluent 2

- URL: [Wait UX — Microsoft Fluent 2](https://fluent2.microsoft.design/wait-ux)
- 箇所: Communicate clearly and honestly; Maintain context; Visual patterns
- 種別 / 確信度: 公式Design Systemの実務ガイド / medium
- 原典の主張: Microsoft 365/Copilot等の待機体験で、正確な通知、文脈保持、関連するfeedbackを推奨する。
- 本Skillの推論・採用範囲: ブランド固有shimmerや時間閾値を輸入せず、待機・復帰・通知の条件だけ採用する。
- 既存との関係: 追加

<a id="s12"></a>
## S12 — Making retries safe with idempotent APIs — Malcolm Featonby, Amazon Builders’ Library

- URL: [Making retries safe with idempotent APIs — Malcolm Featonby, Amazon Builders’ Library](https://aws.amazon.com/builders-library/making-retries-safe-with-idempotent-APIs/)
- 箇所: Retrying and side effects; Client request identifier; Late arriving requests; Same client request ID, different intent
- 種別 / 確信度: 実装者の一次技術解説 / high
- 原典の主張: 応答喪失後の再送は副作用を重複させ得る。同一意図を識別するcaller tokenとserver側の原子的契約により安全な再試行を構成する。
- 本Skillの推論・採用範囲: 結果不明では再照会または保証された同一key再試行を選ぶ。disableボタンだけで二重確定防止としない。
- 既存との関係: 追加

<a id="s13"></a>
## S13 — Using GOMS for User Interface Design and Evaluation: Which Technique? — John & Kieras (1996)

- URL: [Using GOMS for User Interface Design and Evaluation: Which Technique? — John & Kieras (1996)](https://web.eecs.umich.edu/~kieras/docs/GOMS/Which-GOMS.pdf)
- 箇所: §2.2.4 Learning time; §2.2.5 Error recovery support; §2.2.6 Informal understanding (PDF pp.13–14)
- 種別 / 確信度: 査読論文・著者公開版 / medium
- 原典の主張: 既知の重要な誤りから回復する方法を、他の目標と同様に分析できる。手順モデルの予測と操作の発見性・誤り予測は別である。
- 本Skillの推論・採用範囲: エラーのたびにrecovery goalと必要操作を列挙する。状態グラフ検査を人間の完了率に置き換えない。
- 既存との関係: 追加

<a id="s14"></a>
## S14 — Giving undo attention — Abowd & Dix (1992)

- URL: [Giving undo attention — Abowd & Dix (1992)](https://www.alandix.com/academic/papers/undo92/undo.pdf)
- 箇所: Introduction: Undo—a system function? (PDF pp.1–2); user intention
- 種別 / 確信度: 査読論文・著者公開版 / medium
- 原典の主張: 共同編集でundoを単一システム関数に還元せず、利用者が誤った状態から回復する意図として扱う。
- 本Skillの推論・採用範囲: 通信のabort、過去操作の逆操作、補償処理を同一視しない。共同編集の方式を一般の取引へ無条件に移植しない。
- 既存との関係: 追加

<a id="s15"></a>
## S15 — Rethinking the Progress Bar — Harrison, Amento, Kuznetsov & Bell (UIST 2007)

- URL: [Rethinking the Progress Bar — Harrison, Amento, Kuznetsov & Bell (UIST 2007)](https://chrisharrison.net/projects/progressbars/ProgBarHarrison.pdf)
- 箇所: Experimental design; Analysis and results (PDF pp.2–3)
- 種別 / 確信度: 査読実験研究 / medium
- 原典の主張: 22名が同じ5.5秒の複数進捗表示を比較し、知覚速度の差と提示順序の影響を観察した。
- 本Skillの推論・採用範囲: 知覚速度を実処理速度や完了率と混ぜない。偽の進捗表示を正当化する実験ではない。
- 既存との関係: 追加

<a id="s16"></a>
## S16 — The Eight Golden Rules of Interface Design — Ben Shneiderman

- URL: [The Eight Golden Rules of Interface Design — Ben Shneiderman](https://www.cs.umd.edu/users/ben/goldenrules.html)
- 箇所: Rules 3–6; final applicability paragraph
- 種別 / 確信度: 著者大学公開の教科書抜粋 / medium
- 原典の主張: 応答・操作のまとまりの完了・誤り修正・反転可能性を推奨し、文脈に応じた解釈を求める。
- 本Skillの推論・採用範囲: 開始/中間/完了と回復経路を出力契約化する。過去からある原則を新発見扱いしない。
- 既存との関係: 既存source065 / K1-13–16を再利用

<a id="s17"></a>
## S17 — Task-Centered User Interface Design — Lewis & Rieman (1993/1994), Chapter 4

- URL: [Task-Centered User Interface Design — Lewis & Rieman (1993/1994), Chapter 4](https://hcibib.perlman.hosting.acm.org/tcuid/chap-4.html)
- 箇所: §4.1.2 prerequisites; §4.1.3 walkthrough questions
- 種別 / 確信度: 著者公開書籍・ACMホスト / medium
- 原典の主張: 利用者・タスク・画面・正しい操作列を用意し、操作の意図、発見、意味の理解、結果feedbackを一手ずつ検討する。
- 本Skillの推論・採用範囲: Bでgraphに対応するwalkthroughを行う。正しい経路の存在だけで操作を発見できると断定しない。
- 既存との関係: 既存C4の近接原典

<a id="s18"></a>
## S18 — Web Content Accessibility Guidelines (WCAG) 2.2 — W3C Recommendation (2024-12-12)

- URL: [Web Content Accessibility Guidelines (WCAG) 2.2 — W3C Recommendation (2024-12-12)](https://www.w3.org/TR/WCAG22/)
- 箇所: SC3.3.1/3.3.3/3.3.4/3.3.7; SC4.1.3; §5.2.3 Complete processes
- 種別 / 確信度: 規範仕様 / high
- 原典の主張: 3.3.4の対象にはreversible/checked/confirmedの少なくとも1つが必要。3.3.7には必須性・security・情報失効の例外がある。適合はprocess全体を対象とする。
- 本Skillの推論・採用範囲: 全送信への確認画面義務に変えない。Bの一部検査だけでWCAG全適合を宣言しない。
- 既存との関係: 既存source002を再利用

<a id="s19"></a>
## S19 — Task-Centered User Interface Design — Lewis & Rieman (1993/1994), Chapter 5

- URL: [Task-Centered User Interface Design — Lewis & Rieman (1993/1994), Chapter 5](https://hcibib.perlman.hosting.acm.org/tcuid/chap-5.html)
- 箇所: §5.2 Selecting Tasks; §5.3 Mockups; §5.6.2 Comparing alternatives
- 種別 / 確信度: 著者公開書籍・ACMホスト / medium
- 原典の主張: 実際のタスクに近い課題を使い、作ったUIに都合よく課題を曲げない。正常経路だけのmockupでは回復のデータは得られない。
- 本Skillの推論・採用範囲: 同一要件の2課題で正常/異常/境界を比較する。人間を使わない検査はユーザビリティ研究とは呼ばない。
- 既存との関係: S17と同一原典の別章
