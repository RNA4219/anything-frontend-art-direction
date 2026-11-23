# imozuru map: interaction-ux-flow

確認日: 2026-11-23（Asia/Tokyo）。問い: 目的を完了できるかを、タスクフロー・状態遷移・失敗復帰の判断と実行可能な検査へ変換する。

## 探索・停止条件

0周目は公式実務ガイドと学術・一次研究の2役で探索。検索語と返却結果は discovery-practice.json / discovery-academic.json に保存。公開検索には非公開仕様・認証情報を含めなかった。
1周目はtask-centered design第4章のリンクから第5章へ進み、walkthroughと実利用者テスト・比較の責務の違いを確認した。18原典・19参照箇所でBの10原則を埋め、件数を増やす探索は終了。S17/S19は同一書籍の別章として1原典に数える。

## 論点と到達した判断

- [x] 媒体: NN/G、WAI/WCAG、USWDS、Carbon、Fluent、Apple、AWSの公式一次資料と著者公開論文。
- [x] 画面一覧との差分: actor/goal/entry/observable success、event/guard/effectを持つ状態遷移へ（S01/S02/S13/S17）。
- [x] 確認・取消し: 可逆性・検証・損失に応じて分岐。確認画面を全フォームへ強制しない（S03/S04/S07/S14/S18）。
- [x] 応答不明: definitive failureとunknownを分離。server契約がある場合の同一key再送・照会（S12）。
- [x] 中断・部分失敗: 保存済み結果と未確定作業の区別、再照会、失敗部分だけの再試行（S04/S12/S16と編集推論）。
- [x] 検証境界: graph構造・controller挙動・browser操作・実利用者テストを別の証拠として扱う（S13/S17/S19）。

## 用語

journey / task flow / guard / side effect / definitive failure / unknown outcome / idempotency / acknowledgement / partial success / stale response / cognitive walkthrough。Skill内では日本語の説明と契約項目へ落とし、曖昧な形容詞を品質gateに使わない。

## 著者・媒体の位置づけ

Kaplan/Rosala/HarleyのNN/G記事は実務上の説明。John/Kieras、Abowd/Dix、Harrisonらの研究は対象・実験条件を限定。Lewis/Riemanはtask-centeredな設計・評価方法。W3Cの規格本文、Understanding、tutorialを混同しない。デザインシステムの指針は対象製品の判断を示し、普遍的な造形規則としない。

## 確認した参照箇所

| ID | 資料 | URL | 採用先 |
|---|---|---|---|
| S01 | User Journeys vs. User Flows — Kate Kaplan, NN/G | https://www.nngroup.com/articles/user-journeys-vs-user-flows/ | source-index.md / extensions/B/references/sources.md |
| S02 | Task Analysis: Support Users in Achieving Their Goals — Maria Rosala, NN/G | https://www.nngroup.com/articles/task-analysis/ | source-index.md / extensions/B/references/sources.md |
| S03 | Cancel vs Close: Design to Distinguish the Difference — Aurora Harley, NN/G | https://www.nngroup.com/articles/cancel-vs-close/ | source-index.md / extensions/B/references/sources.md |
| S04 | Multi-page Forms — W3C WAI Forms Tutorial | https://www.w3.org/WAI/tutorials/forms/multi-page/ | source-index.md / extensions/B/references/sources.md |
| S05 | User Notification — W3C WAI Forms Tutorial | https://www.w3.org/WAI/tutorials/forms/notifications/ | source-index.md / extensions/B/references/sources.md |
| S06 | Understanding SC 4.1.3: Status Messages — W3C WAI | https://www.w3.org/WAI/WCAG22/Understanding/status-messages.html | source-index.md / extensions/B/references/sources.md |
| S07 | Step indicator — U.S. Web Design System | https://designsystem.digital.gov/components/step-indicator/ | source-index.md / extensions/B/references/sources.md |
| S08 | Notifications — Carbon Design System | https://www.carbondesignsystem.com/building-blocks/core/patterns/notifications | source-index.md / extensions/B/references/sources.md |
| S09 | Loading — Carbon Design System | https://www.carbondesignsystem.com/building-blocks/core/patterns/loading | source-index.md / extensions/B/references/sources.md |
| S10 | Progress indicators — Apple Human Interface Guidelines | https://developer.apple.com/design/human-interface-guidelines/progress-indicators.md | source-index.md / extensions/B/references/sources.md |
| S11 | Wait UX — Microsoft Fluent 2 | https://fluent2.microsoft.design/wait-ux | source-index.md / extensions/B/references/sources.md |
| S12 | Making retries safe with idempotent APIs — Malcolm Featonby, Amazon Builders’ Library | https://aws.amazon.com/builders-library/making-retries-safe-with-idempotent-APIs/ | source-index.md / extensions/B/references/sources.md |
| S13 | Using GOMS for User Interface Design and Evaluation: Which Technique? — John & Kieras (1996) | https://web.eecs.umich.edu/~kieras/docs/GOMS/Which-GOMS.pdf | source-index.md / extensions/B/references/sources.md |
| S14 | Giving undo attention — Abowd & Dix (1992) | https://www.alandix.com/academic/papers/undo92/undo.pdf | source-index.md / extensions/B/references/sources.md |
| S15 | Rethinking the Progress Bar — Harrison, Amento, Kuznetsov & Bell (UIST 2007) | https://chrisharrison.net/projects/progressbars/ProgBarHarrison.pdf | source-index.md / extensions/B/references/sources.md |
| S16 | The Eight Golden Rules of Interface Design — Ben Shneiderman | https://www.cs.umd.edu/users/ben/goldenrules.html | source-index.md / extensions/B/references/sources.md |
| S17 | Task-Centered User Interface Design — Lewis & Rieman (1993/1994), Chapter 4 | https://hcibib.perlman.hosting.acm.org/tcuid/chap-4.html | source-index.md / extensions/B/references/sources.md |
| S18 | Web Content Accessibility Guidelines (WCAG) 2.2 — W3C Recommendation (2024-12-12) | https://www.w3.org/TR/WCAG22/ | source-index.md / extensions/B/references/sources.md |
| S19 | Task-Centered User Interface Design — Lewis & Rieman (1993/1994), Chapter 5 | https://hcibib.perlman.hosting.acm.org/tcuid/chap-5.html | source-index.md / extensions/B/references/sources.md |

## 取得と確信度

imozuru fetch.pyの18試行はDNSエラーで失敗（fetch-attempts.json）。代替の許可されたweb検索サービスで原文抽出を確認した。抽出cacheのSHA-256と該当箇所、確認日はsources.jsonへ保存。hashはweb toolの抽出文であり、原サイトHTTP bytesではない。原文全文をリポジトリに再配布しない。
report.py --checkの19抜粋照合は quote-check.json に保存。規格の要件、著者の主張、今回の推論・形式化を source-index / principles / sankai-extraction で分けた。

## 未解決・追試

- 実利用者観察・独立blind評価が未実施。
- 原文cacheは一時作業用で、再取得結果は時期・抽出器により変わり得る。URL、章、短い抜粋、取得hashを追跡に使う。
- 本番APIの冪等性・取消保証は、模擬APIのテストで証明しない。
