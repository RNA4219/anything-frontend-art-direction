# SESSION B — source index

確認日: 2026-11-23（Asia/Tokyo）。**有効原典18件、確認箇所19件**。同一書籍のChapter 4/5は1原典。原典の主張・適用範囲・確信度はSkillに同梱した[原典一覧](../../extensions/B/references/sources.md)を正本とする。

imozuru `fetch.py` は18件ともDNS解決失敗。設定変更や制限回避は行わず、利用可能なWeb取得ツールで原文の該当箇所を取得・確認した。以下のhashは保存した**ツール抽出本文**のhashであり、元HTML/PDFバイト列のhashではない。長い資料は抽出が部分的なので全文取得とは称さない。原文写しは作業用キャッシュにのみ保持し、変更セットへ再配布しない。

| ID | 資料・原文URL | 該当箇所 | 確認済み短い抜粋 |
|---|---|---|---|
| S01 | [User Journeys vs. User Flows — Kate Kaplan, NN/G](https://www.nngroup.com/articles/user-journeys-vs-user-flows/) | What Is a User Flow?; Combining User Journeys and User Flows | specific, discrete interactions |
| S02 | [Task Analysis: Support Users in Achieving Their Goals — Maria Rosala, NN/G](https://www.nngroup.com/articles/task-analysis/) | Stage 1: Gather Information; Stage 2: Analyze Tasks | a start and an end point |
| S03 | [Cancel vs Close: Design to Distinguish the Difference — Aurora Harley, NN/G](https://www.nngroup.com/articles/cancel-vs-close/) | Avoid Losing Users’ Work; Use Explicit Labels | Use Explicit Labels |
| S04 | [Multi-page Forms — W3C WAI Forms Tutorial](https://www.w3.org/WAI/tutorials/forms/multi-page/) | Overview; Indicating progress | Make it easy to recognize and to skip optional stages. |
| S05 | [User Notification — W3C WAI Forms Tutorial](https://www.w3.org/WAI/tutorials/forms/notifications/) | Overall feedback; Listing errors; In-line feedback | Success messages are also important to confirm task completion. |
| S06 | [Understanding SC 4.1.3: Status Messages — W3C WAI](https://www.w3.org/WAI/WCAG22/Understanding/status-messages.html) | Intent; Examples of changes that are not status messages | without receiving focus |
| S07 | [Step indicator — U.S. Web Design System](https://designsystem.digital.gov/components/step-indicator/) | Guidance: When to use / consider something else / Usability guidance | Provide navigation separately. |
| S08 | [Notifications — Carbon Design System](https://www.carbondesignsystem.com/building-blocks/core/patterns/notifications) | Designing with notifications: Task-generated / System-generated / When not to use | task-generated and system-generated |
| S09 | [Loading — Carbon Design System](https://www.carbondesignsystem.com/building-blocks/core/patterns/loading) | Loading indicators; Full-screen loading; Inline loading | a single component is processing |
| S10 | [Progress indicators — Apple Human Interface Guidelines](https://developer.apple.com/design/human-interface-guidelines/progress-indicators.md) | Best practices | Be as accurate as possible |
| S11 | [Wait UX — Microsoft Fluent 2](https://fluent2.microsoft.design/wait-ux) | Communicate clearly and honestly; Maintain context; Visual patterns | Maintain context and limit simultaneous feedback |
| S12 | [Making retries safe with idempotent APIs — Malcolm Featonby, Amazon Builders’ Library](https://aws.amazon.com/builders-library/making-retries-safe-with-idempotent-APIs/) | Retrying and side effects; Client request identifier; Late arriving requests; Same client request ID, different intent | unique caller-provided client request identifier |
| S13 | [Using GOMS for User Interface Design and Evaluation: Which Technique? — John & Kieras (1996)](https://web.eecs.umich.edu/~kieras/docs/GOMS/Which-GOMS.pdf) | §2.2.4 Learning time; §2.2.5 Error recovery support; §2.2.6 Informal understanding (PDF pp.13–14) | RECOVER-FROM-ERROR |
| S14 | [Giving undo attention — Abowd & Dix (1992)](https://www.alandix.com/academic/papers/undo92/undo.pdf) | Introduction: Undo—a system function? (PDF pp.1–2); user intention | designers must focus on supplying tools to facilitate this recovery. |
| S15 | [Rethinking the Progress Bar — Harrison, Amento, Kuznetsov & Bell (UIST 2007)](https://chrisharrison.net/projects/progressbars/ProgBarHarrison.pdf) | Experimental design; Analysis and results (PDF pp.2–3) | We recruited 22 participants |
| S16 | [The Eight Golden Rules of Interface Design — Ben Shneiderman](https://www.cs.umd.edu/users/ben/goldenrules.html) | Rules 3–6; final applicability paragraph | Permit easy reversal of actions. |
| S17 | [Task-Centered User Interface Design — Lewis & Rieman (1993/1994), Chapter 4](https://hcibib.perlman.hosting.acm.org/tcuid/chap-4.html) | §4.1.2 prerequisites; §4.1.3 walkthrough questions | What's needed before you can do a walkthrough? |
| S18 | [Web Content Accessibility Guidelines (WCAG) 2.2 — W3C Recommendation (2024-12-12)](https://www.w3.org/TR/WCAG22/) | SC3.3.1/3.3.3/3.3.4/3.3.7; SC4.1.3; §5.2.3 Complete processes | Submissions are reversible. |
| S19 | [Task-Centered User Interface Design — Lewis & Rieman (1993/1994), Chapter 5](https://hcibib.perlman.hosting.acm.org/tcuid/chap-5.html) | §5.2 Selecting Tasks; §5.3 Mockups; §5.6.2 Comparing alternatives | Selecting Tasks for Testing |

## 取得証跡

機械可読の全metadata・確認日・原典の主張・推論・cache行・SHA-256: [sources.json](research/sources.json)。検索全ヒットは [practice](research/discovery-practice.json) と [academic](research/discovery-academic.json)。クエリ所属が返らなかったバッチは推測で割り当てていない。

| ID | 保存抽出ファイルと行 | SHA-256 |
|---|---|---|
| S01 | `nng-journeys-flows.md:60` | `a85fe8f9d4c0930ecd1fb60eb8cc919af55811c561ad368203da2ecd0a571b93` |
| S02 | `nng-task-analysis.md:56` | `1fb2b31474cd617ce29f51ed7e7f75fcfcaa7596baa2bed66a8a2b5e17618ce1` |
| S03 | `nng-cancel-close.md:61` | `e0b378d6573ee7bd9b44014e7ffbe4c2bc0550b5815488bec92f4834c57d2716` |
| S04 | `wai-multipage.md:97` | `33f0313472e6a53d989380047032dd14676ea07805122fda5d10e1bdd41b1d19` |
| S05 | `wai-notification.md:99` | `c647dd8499c38fa6817216423eccf1164ec7da8b16124e29cd682bb5ada94fe7` |
| S06 | `wai-status-messages.md:34` | `e80af5038b67a42e2540fb15a84103d74c4d8b493702469b3d3dd1dadbbd0174` |
| S07 | `uswds-step-indicator-details.md:277` | `ad37010a931a2ec73c9b749c961cb543483887336729a26c9f1f9e08d4d1f74a` |
| S08 | `carbon-notifications.md:84` | `0c21e11ed3ee5087e4b86b3acb0eefafe156cbd0b9d1130c06d82919386c3348` |
| S09 | `carbon-loading.md:90` | `9a62b4862df60ca6509382d772e5a6008cbb95e0b8ce8e08add3d471ffbfd353` |
| S10 | `apple-progress.md:45` | `274e7d8984934b9d793174bb046f5fb914a32f513d648e7e64a253faf0fb7609` |
| S11 | `fluent-wait.md:37` | `8460c5b8fab311a8dc3cc691a9fd1e9af88d245430de87789c18fe05071dcaa7` |
| S12 | `aws-idempotent.md:245` | `1e0193067d72ffaee5b87d315f814fb95c147e6811743859232bf866c6c7eb68` |
| S13 | `john-kieras-goms-error-recovery.md:129` | `c671abdc917e119fcef856b4a9de9828fe9a7caeca6605ea42b6803bfa38736d` |
| S14 | `abowd-dix-1992-undo.md:71` | `be0f3b696f0b070fb89ef9ff813a36de627e1f5d517e0625fb26e1955a1267cf` |
| S15 | `harrison-2007-progress.md:121` | `8698bad0af4930a5ce61f631d5f3a3a82c1665091e4f6bc721760dcc5284ae1b` |
| S16 | `shneiderman-golden-rules.md:38` | `fce69a78439eaeca1adb1cde0129377a7ab2c570a820c54a476ac03c2e8c44da` |
| S17 | `lewis-rieman-task-centered.md:13` | `2a267e01b23aa6f91c76528212816ea3cc11edbb08038febc025323bfe0000aa` |
| S18 | `w3c-wcag22-input-assistance.md:227` | `6adbcf1c29b19b8c6ead750a5aeeb6f1c8f2ef4abdfb7f1e36812f4b9e15ff8a` |
| S19 | `lewis-rieman-user-testing.md:11` | `818b4822f2b7df4b89ac760d81c00ddd087d6f8bcf439ead9de6b42b812f92a8` |

## 原典確認からの制限

- S15は知覚速度の小規模実験。一般的なタスク完了率の改善量や、架空進捗を表示する許可へ拡張しない。
- S13は1996年時点の手法適用範囲。人間のエラー予測研究の現状を2026年にも同じと断定しない。
- WCAGのAA/AAA・適用対象・例外を保持する。BのみでWCAG完全適合は評価しない。
- NNG・Design Systemsのguidanceを、全環境の規範仕様と扱わない。ブランド、書体、装飾は既存Art Directionを維持する。
