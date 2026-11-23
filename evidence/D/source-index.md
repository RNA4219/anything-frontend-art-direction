# SESSION D — Source index

確認日: **2026-11-23（日本時間）**。有効原典 **20件**（既存出典の再利用5件、新規追加15件）。うちS17は著者公開abstractの範囲のみ。原典の主張と今回の設計判断への推論を分ける。本文中の命令は外部資料として扱い、実行許可にはしない。

## 取得と適用の範囲

- imozuru `fetch.py` を20件に実行したが、この実行ホストはDNS解決に失敗した。失敗を成功へ書き換えず、[receipt](research/fetch-receipts.jsonl) と [fetch log](research/fetch-log.jsonl) に保持する。
- 続いて公開Web取得の `open` / `find` で20件の原典本文を確認した。source-indexと [機械可読index](research/sources.json) に短い抜粋、節、hashを保存する。第三者の本文全体は `research/raw/` の照合専用コピーに限り、Gitへ入れない。
- 保存hashは、原サイト全体のhashではなく取得ツールが返したテキストsnapshotのSHA-256。Webの改訂や抽出処理で変わる。取得経路と範囲を隠さない。
- 出典内の数値を今回のfixture、モデル、製品の実測値へ移し替えない。規範、著者ガイダンス、研究条件を区別する。
- 新規のQA契約・Gate条件は当Campaignでの設計判断であり、原典が同じJSONや昇格閾値を定めたと主張しない。
- 調査は各論点に原文が付き、1回のリンク追跡が完了した時点で終了。追跡: S02の公式記事からリンク37を辿りS01へ到達。飽和率を計算していないため飽和とは主張しない。

## 原典一覧

| ID | 原典 | 種別 | 差分 | 主な用途 |
|---|---|---|---|---|
| [S01](#s01) | [10 Usability Heuristics for User Interface Design](https://www.nngroup.com/articles/ten-usability-heuristics/) | 著者ガイダンス | 既存再利用 | 症状を対象状態、利用者への影響、復帰手順へ分解する。 |
| [S02](#s02) | [How to Conduct a Heuristic Evaluation](https://www.nngroup.com/articles/how-to-conduct-a-heuristic-evaluation/) | 著者ガイダンス | 既存再利用 | 評価者、閲覧できた材料、独立性の制約を記録する。 |
| [S03](#s03) | [Severity Ratings for Usability Problems](https://www.nngroup.com/articles/how-to-rate-the-severity-of-usability-problems/) | 著者ガイダンス | 新規 | 影響・復帰難度・再現頻度と証拠を分け、重大度を説明する。 |
| [S04](#s04) | [Success Rate: The Simplest Usability Metric](https://www.nngroup.com/articles/success-rate-the-simplest-usability-metric/) | 著者ガイダンス | 新規 | 正常・失敗・部分完了・未実行を分離し、分母と成功条件を先に凍結する。 |
| [S05](#s05) | [Write Better Qualitative Usability Tasks](https://www.nngroup.com/articles/better-usability-tasks/) | 著者ガイダンス | 新規 | 目的のbriefと実行手順を別項目にし、盲検評価者に候補の狙いを渡さない。 |
| [S06](#s06) | [Error-Message Guidelines](https://www.nngroup.com/articles/error-message-guidelines/) | 著者ガイダンス | 既存再利用 | 失敗後の入力保持、次の行動、再試行と完了までを試す。 |
| [S07](#s07) | [Web Content Accessibility Guidelines (WCAG) 2.2](https://www.w3.org/TR/WCAG22/) | 規範 | 既存再利用 | SC番号、対象、例外、実行環境を所見に付け、範囲外を未検証とする。 |
| [S08](#s08) | [WCAG Evaluation Methodology (WCAG-EM) 2.0](https://www.w3.org/TR/2026/NOTE-wcag-em-2-20260723/) | 公式手法（非規範Group Note） | 新規 | ケースのstate/input/viewportと証跡一覧を固定し、結果と未確認を記録する。 |
| [S09](#s09) | [Evaluating Web Accessibility Overview](https://www.w3.org/WAI/test-evaluate/) | 公式ガイダンス | 新規 | 早期の小検査と変更後の回帰検査を実行順序へ組み込む。 |
| [S10](#s10) | [Easy Checks – A First Review of Web Accessibility](https://www.w3.org/WAI/test-evaluate/preliminary/) | 公式ガイダンス | 新規 | keyboard、focus、zoomなど実行済み項目と未実施項目を明記する。 |
| [S11](#s11) | [Accessibility](https://designsystem.digital.gov/documentation/accessibility/) | 公式実務ガイダンス | 新規 | 対応入力と端末の行列を定義し自動・手動を別欄に記録する。 |
| [S12](#s12) | [Button accessibility tests](https://designsystem.digital.gov/components/button/accessibility-tests/) | 公式コンポーネント試験 | 新規 | 名前、役割、順序、Enter/Space、focusを対象ページで確認する。 |
| [S13](#s13) | [Table accessibility tests](https://designsystem.digital.gov/components/table/accessibility-tests/) | 公式コンポーネント試験 | 新規 | sort/filter後の状態、focus、横スクロール境界と読めるセルを試す。 |
| [S14](#s14) | [Visual comparisons](https://playwright.dev/docs/test-snapshots) | 公式実装資料 | 新規 | 同じviewport/DPR/font/stateで撮影し、基準更新に理由とreviewを要求する。 |
| [S15](#s15) | [Trace viewer](https://playwright.dev/docs/trace-viewer) | 公式実装資料 | 新規 | スクリーンショット、DOM、操作列、console、networkを所見の再現証拠として関連付ける。 |
| [S16](#s16) | [Accessibility testing](https://playwright.dev/docs/accessibility-testing) | 公式実装資料 | 新規 | 機械検査のrule subsetとmanual/inclusive未実施を結果に残す。 |
| [S17](#s17) | [Measuring the User Experience on a Large Scale: User-Centered Metrics for Web Applications](https://research.google/pubs/measuring-the-user-experience-on-a-large-scale-user-centered-metrics-for-web-applications/) | 査読研究（著者公開abstractを確認） | 新規 | 何を改善したいかを先に固定し、タスク指標をその目標へ紐付ける。 |
| [S18](#s18) | [Judging LLM-as-a-Judge with MT-Bench and Chatbot Arena](https://proceedings.neurips.cc/paper_files/paper/2023/file/91f18a1287b398d378ef22505bf41832-Paper-Datasets_and_Benchmarks.pdf) | 査読実験 | 新規 | 案名を伏せ、順番を入れ替え、根拠不足と一致しない判定をHOLDにする設計上の予防策に使う。 |
| [S19](#s19) | [ScreenAudit: Detecting Screen Reader Accessibility Errors in Mobile Apps Using Large Language Models](https://faculty.washington.edu/wobbrock/pubs/chi-25.02.pdf) | 査読実験 | 既存再利用 | LLMの所見候補を実操作で再現し、動かしていない機能の断定を禁止する。 |
| [S20](#s20) | [Visual Hierarchy in UX: Definition](https://www.nngroup.com/articles/visual-hierarchy-ux-definition/) | 著者ガイダンス | 新規 | Art Directionが定めた主役と操作を基準に、競合、近接、整列、隠れを位置付きで指摘する。 |

<a id="s01"></a>

## S01

**[10 Usability Heuristics for User Interface Design](https://www.nngroup.com/articles/ten-usability-heuristics/)** — Nielsen Norman Group / Jakob Nielsen

- 該当箇所: 1 Visibility of System Status; 3 User Control and Freedom; 9 Help Users Recognize, Diagnose, and Recover from Errors
- 確認日・種別: 2026-11-23 / 著者ガイダンス
- 原典での主張: 状態を知らせ、取消し・復帰可能な出口を設け、エラーを問題と解決行動に結び付ける。
- 適用条件・限界: 高水準の経験則でありWCAGの適合判定そのものではない。操作していない批評は仮説のまま扱う。
- このSkillへの推論: 症状を対象状態、利用者への影響、復帰手順へ分解する。
- 信頼度: 原典本文の当該主張は高。対象製品・LLMへ移す際の有効性は別途試験が必要。
- 短い原文照合句: “clearly marked "emergency exit"”
- 取得証拠: `research/raw/sources/S01-web.txt`（ローカル照合専用・配布外）, 該当行 L105, SHA-256 `09a3d191735c812ce75d21ca63e6e282e7935163975cb8269cd01ed4adb3869f`。原典URLと節を安定参照とする。
- 既存との対応: `references/c-usability.md`, `sources.md`

<a id="s02"></a>

## S02

**[How to Conduct a Heuristic Evaluation](https://www.nngroup.com/articles/how-to-conduct-a-heuristic-evaluation/)** — Nielsen Norman Group / Kate Moran, Kelley Gordon

- 該当箇所: Choosing a Set of Heuristics; Step 2 Evaluate Independently; Step 3 Consolidate Identified Issues
- 確認日・種別: 2026-11-23 / 著者ガイダンス
- 原典での主張: 評価範囲と記録方法を揃え、まず個別に評価してから問題を統合する。ヒューリスティック評価は利用者研究の代替ではない。
- 適用条件・限界: 人の複数評価者を推奨する方法。同一モデルの複数agentを人の独立研究と同等とは扱えない。
- このSkillへの推論: 評価者、閲覧できた材料、独立性の制約を記録する。
- 信頼度: 原典本文の当該主張は高。対象製品・LLMへ移す際の有効性は別途試験が必要。
- 短い原文照合句: “each team member should evaluate the interface on their own”
- 取得証拠: `research/raw/sources/S02-web.txt`（ローカル照合専用・配布外）, 該当行 L100, SHA-256 `77e01fba03645ba7add3a04531e7893b6a613afd45b42126f5baff337c2c69bb`。原典URLと節を安定参照とする。
- 既存との対応: `references/c-usability.md`, `sources.md`

<a id="s03"></a>

## S03

**[Severity Ratings for Usability Problems](https://www.nngroup.com/articles/how-to-rate-the-severity-of-usability-problems/)** — Nielsen Norman Group / Jakob Nielsen

- 該当箇所: The severity of a usability problem; Severity Ratings in Heuristic Evaluation
- 確認日・種別: 2026-11-23 / 著者ガイダンス
- 原典での主張: 頻度、遭遇時の影響、反復性を考慮して重大度を判断し、評価者の個別採点を保持する。
- 適用条件・限界: 頻度の母数は観察がない限り未知。尺度は経験的な優先順位付けでありGate閾値はプロジェクトで定める。
- このSkillへの推論: 影響・復帰難度・再現頻度と証拠を分け、重大度を説明する。
- 信頼度: 原典本文の当該主張は高。対象製品・LLMへ移す際の有効性は別途試験が必要。
- 短い原文照合句: “The severity of a usability problem is a combination”
- 取得証拠: `research/raw/sources/S03-web.txt`（ローカル照合専用・配布外）, 該当行 L52, SHA-256 `634e4f8781d3cfcb1b93115bf532c859b23908b0ba8b0ecdbcf5cb65b9c55662`。原典URLと節を安定参照とする。
- 既存との対応: 現行baseのreferences/checklists/sources.mdにこのURLは未掲載。

<a id="s04"></a>

## S04

**[Success Rate: The Simplest Usability Metric](https://www.nngroup.com/articles/success-rate-the-simplest-usability-metric/)** — Nielsen Norman Group / Jakob Nielsen, Raluca Budiu

- 該当箇所: Measuring Success; Levels of Success; Do Not Use Numbers for Success Levels
- 確認日・種別: 2026-11-23 / 著者ガイダンス
- 原典での主張: 目的の状態に到達できた参加者割合を完了率とし、部分成功は定義別に報告する。序数に便宜的な点数を付けて平均しない。
- 適用条件・限界: 試験数と参加者数を混同しない。自動化シナリオの通過率は人の完了率ではない。少数試行で母集団の改善率を断定しない。
- このSkillへの推論: 正常・失敗・部分完了・未実行を分離し、分母と成功条件を先に凍結する。
- 信頼度: 原典本文の当該主張は高。対象製品・LLMへ移す際の有効性は別途試験が必要。
- 短い原文照合句: “ordinal scale, not an interval or ratio scale”
- 取得証拠: `research/raw/sources/S04-web.txt`（ローカル照合専用・配布外）, 該当行 L115, SHA-256 `5c62e3261ea9f82942006f73a3625ac0981846912e50ef4281bc56e4bef37ffc`。原典URLと節を安定参照とする。
- 既存との対応: 現行baseのreferences/checklists/sources.mdにこのURLは未掲載。

<a id="s05"></a>

## S05

**[Write Better Qualitative Usability Tasks](https://www.nngroup.com/articles/better-usability-tasks/)** — Nielsen Norman Group / Amy Schade

- 該当箇所: 1 Telling Users Where to Go; 2 Telling Users What to Do; Tip Start with the End Goal
- 確認日・種別: 2026-11-23 / 著者ガイダンス
- 原典での主張: 利用者が達成したい目的を課題にし、画面上のラベルや手順で正解を誘導しない。
- 適用条件・限界: 参加者調査の課題文と自動回帰の詳細操作列は用途が異なる。再現手順自体を削除する理由にはしない。
- このSkillへの推論: 目的のbriefと実行手順を別項目にし、盲検評価者に候補の狙いを渡さない。
- 信頼度: 原典本文の当該主張は高。対象製品・LLMへ移す際の有効性は別途試験が必要。
- 短い原文照合句: “Start with the End Goal”
- 取得証拠: `research/raw/sources/S05-web.txt`（ローカル照合専用・配布外）, 該当行 L152, L69, SHA-256 `bd5ab8bbc7537a647f18e104d9b58fad90892587ad48185972e01d7bf7141c90`。原典URLと節を安定参照とする。
- 既存との対応: 現行baseのreferences/checklists/sources.mdにこのURLは未掲載。

<a id="s06"></a>

## S06

**[Error-Message Guidelines](https://www.nngroup.com/articles/error-message-guidelines/)** — Nielsen Norman Group / Jakob Nielsen

- 該当箇所: Preserve the user’s input; error visibility and recovery guidance
- 確認日・種別: 2026-11-23 / 著者ガイダンス
- 原典での主張: エラー時に利用者の入力を保持し、最初からのやり直しではなく元の操作を訂正できるようにする。
- 適用条件・限界: 原因診断は状態と操作の観察で裏付ける。文体の好みだけは対象外。
- このSkillへの推論: 失敗後の入力保持、次の行動、再試行と完了までを試す。
- 信頼度: 原典本文の当該主張は高。対象製品・LLMへ移す際の有効性は別途試験が必要。
- 短い原文照合句: “Preserve the user's input”
- 取得証拠: `research/raw/sources/S06-web.txt`（ローカル照合専用・配布外）, 該当行 L94, SHA-256 `4273b983941461b99afb64a25f66265587051811838f32102b9c34be9ba6c136`。原典URLと節を安定参照とする。
- 既存との対応: `references/c-usability.md`, `sources.md`

<a id="s07"></a>

## S07

**[Web Content Accessibility Guidelines (WCAG) 2.2](https://www.w3.org/TR/WCAG22/)** — W3C Accessibility Guidelines Working Group

- 該当箇所: 1.4.10 Reflow; 2.1.1 Keyboard; 2.4.7 Focus Visible; 3.3.1 Error Identification; 4.1.3 Status Messages; 5.2.3 Complete processes
- 確認日・種別: 2026-11-23 / 規範
- 原典での主張: 要求レベルの適合には対象の全ページと完結した過程が含まれる。個別基準には対象と例外がある。
- 適用条件・限界: Dは基準への測定・証拠をCへ引き渡す。少数fixtureや自動ツールの成功を全WCAG適合の証明にしない。
- このSkillへの推論: SC番号、対象、例外、実行環境を所見に付け、範囲外を未検証とする。
- 信頼度: 原典本文の当該主張は高。対象製品・LLMへ移す際の有効性は別途試験が必要。
- 短い原文照合句: “all web pages in the process conform”
- 取得証拠: `research/raw/sources/S07-web.txt`（ローカル照合専用・配布外）, 該当行 L1498, SHA-256 `54ef00db88b3b6b53bbbbde051251d7e57f46d91ac7864927bbe194703d2c3c1`。原典URLと節を安定参照とする。
- 既存との対応: `references/k-studies.md`, `references/e-accessibility.md`, `sources.md`

<a id="s08"></a>

## S08

**[WCAG Evaluation Methodology (WCAG-EM) 2.0](https://www.w3.org/TR/2026/NOTE-wcag-em-2-20260723/)** — W3C Accessibility Guidelines Working Group

- 該当箇所: 2026-07-23版; Step 1 scope; Step 3 samples; Step 4.2 complete processes; Step 5.1 documentation
- 確認日・種別: 2026-11-23 / 公式手法（非規範Group Note）
- 原典での主張: 範囲を定義し、代表サンプルと全過程を評価する。通常経路・分岐、入力、確認、エラー、端末差を含め記録する。
- 適用条件・限界: WCAGの追加要件ではない。構造的・ランダムな標本の比較まで未実施なら完全なWCAG-EM評価とは呼ばない。
- このSkillへの推論: ケースのstate/input/viewportと証跡一覧を固定し、結果と未確認を記録する。
- 信頼度: 原典本文の当該主張は高。対象製品・LLMへ移す際の有効性は別途試験が必要。
- 短い原文照合句: “follow the identified default and branch sequences”
- 取得証拠: `research/raw/sources/S08-web.txt`（ローカル照合専用・配布外）, 該当行 L491, SHA-256 `a909d3aaeaf60a6e4baf0e2103b79f4492a78c5023cf7d6e51629de4950f427a`。原典URLと節を安定参照とする。
- 既存との対応: 現行baseのreferences/checklists/sources.mdにこのURLは未掲載。

<a id="s09"></a>

## S09

**[Evaluating Web Accessibility Overview](https://www.w3.org/WAI/test-evaluate/)** — W3C Web Accessibility Initiative

- 該当箇所: Introduction; Tools; Conformance Evaluation
- 確認日・種別: 2026-11-23 / 公式ガイダンス
- 原典での主張: 開発初期から反復して評価し、ツール・人の評価・利用者参加を組み合わせるための各方法を案内する。
- 適用条件・限界: 総覧であり個々の要件の合否根拠は個別WCAG資料に遡る。
- このSkillへの推論: 早期の小検査と変更後の回帰検査を実行順序へ組み込む。
- 信頼度: 原典本文の当該主張は高。対象製品・LLMへ移す際の有効性は別途試験が必要。
- 短い原文照合句: “Web accessibility evaluation tools are software programs”
- 取得証拠: `research/raw/sources/S09-web.txt`（ローカル照合専用・配布外）, 該当行 L88, SHA-256 `1f9b7a869e297759f6059330970c32a222b3e96168489eef83fbe4ed693a0e59`。原典URLと節を安定参照とする。
- 既存との対応: 現行baseのreferences/checklists/sources.mdにこのURLは未掲載。

<a id="s10"></a>

## S10

**[Easy Checks – A First Review of Web Accessibility](https://www.w3.org/WAI/test-evaluate/preliminary/)** — W3C Web Accessibility Initiative

- 該当箇所: Introduction; Keyboard Access and Visual Focus; Using these Easy Checks
- 確認日・種別: 2026-11-23 / 公式ガイダンス
- 原典での主張: 簡単な手動チェックは初期点検として使えるが、包括的で確定的な評価ではない。
- 適用条件・限界: 一部の古い補助ツール例を新規導入しない。現行ブラウザで操作を検査し、結果の範囲を限定する。
- このSkillへの推論: keyboard、focus、zoomなど実行済み項目と未実施項目を明記する。
- 信頼度: 原典本文の当該主張は高。対象製品・LLMへ移す際の有効性は別途試験が必要。
- 短い原文照合句: “not a complete evaluation of accessibility”
- 取得証拠: `research/raw/sources/S10-web.txt`（ローカル照合専用・配布外）, 該当行 L85, SHA-256 `af1738b34220fa0ef53acfcb4d829cdceea24833ea02f04f3a8863d366c0747f`。原典URLと節を安定参照とする。
- 既存との対応: 現行baseのreferences/checklists/sources.mdにこのURLは未掲載。

<a id="s11"></a>

## S11

**[Accessibility](https://designsystem.digital.gov/documentation/accessibility/)** — U.S. Web Design System

- 該当箇所: Our approach to accessibility; How we test
- 確認日・種別: 2026-11-23 / 公式実務ガイダンス
- 原典での主張: キーボード、拡大、タッチ、OS・ブラウザ差、スクリーンリーダーと自動検査を組み合わせる。
- 適用条件・限界: USWDS自身の運用を自分の検査実績として表示しない。製品側の適合性は別に確認する。
- このSkillへの推論: 対応入力と端末の行列を定義し自動・手動を別欄に記録する。
- 信頼度: 原典本文の当該主張は高。対象製品・LLMへ移す際の有効性は別途試験が必要。
- 短い原文照合句: “Test with keyboard-only navigation”
- 取得証拠: `research/raw/sources/S11-web.txt`（ローカル照合専用・配布外）, 該当行 L236, SHA-256 `d0e0a130b498ca33e0278021f46630dacf3aa5dbef73a87c92a1a3703be17dd2`。原典URLと節を安定参照とする。
- 既存との対応: 現行baseのreferences/checklists/sources.mdにこのURLは未掲載。

<a id="s12"></a>

## S12

**[Button accessibility tests](https://designsystem.digital.gov/components/button/accessibility-tests/)** — U.S. Web Design System

- 該当箇所: Test the button in your project; keyboard and screen reader tests
- 確認日・種別: 2026-11-23 / 公式コンポーネント試験
- 原典での主張: 単体部品での試験に加え、利用先のページ文脈でボタンを試験する必要がある。
- 適用条件・限界: USWDS v3.7.1等の掲載結果はその版・条件のもの。自作ボタンの通過とは独立。
- このSkillへの推論: 名前、役割、順序、Enter/Space、focusを対象ページで確認する。
- 信頼度: 原典本文の当該主張は高。対象製品・LLMへ移す際の有効性は別途試験が必要。
- 短い原文照合句: “test the button component in the context”
- 取得証拠: `research/raw/sources/S12-web.txt`（ローカル照合専用・配布外）, 該当行 L213, SHA-256 `8ad506ce86f13490ee3b5b7f4a73f46176f0a600d261c9a215c2b30e1df4dfb4`。原典URLと節を安定参照とする。
- 既存との対応: 現行baseのreferences/checklists/sources.mdにこのURLは未掲載。

<a id="s13"></a>

## S13

**[Table accessibility tests](https://designsystem.digital.gov/components/table/accessibility-tests/)** — U.S. Web Design System

- 該当箇所: Keyboard navigation tests; focus and scrollable table exception
- 確認日・種別: 2026-11-23 / 公式コンポーネント試験
- 原典での主張: キーボードで出入り・操作できることを確認する。掲載テーブルには特定支援技術で横スクロールしない例外を明示している。
- 適用条件・限界: 表全体の二次元性とページ全体の横あふれを分ける。特定製品での既知例外を一般のHTML表すべての不具合としない。
- このSkillへの推論: sort/filter後の状態、focus、横スクロール境界と読めるセルを試す。
- 信頼度: 原典本文の当該主張は高。対象製品・LLMへ移す際の有効性は別途試験が必要。
- 短い原文照合句: “Table cells do not trap focus”
- 取得証拠: `research/raw/sources/S13-web.txt`（ローカル照合専用・配布外）, 該当行 L323, SHA-256 `1ec3f9c44245f99a040a3aa150ecd9de20fda3aebcdd6a351955f5d8c19b640c`。原典URLと節を安定参照とする。
- 既存との対応: 現行baseのreferences/checklists/sources.mdにこのURLは未掲載。

<a id="s14"></a>

## S14

**[Visual comparisons](https://playwright.dev/docs/test-snapshots)** — Microsoft Playwright

- 該当箇所: Introduction; Generating screenshots; Updating screenshots; Hover effects
- 確認日・種別: 2026-11-23 / 公式実装資料
- 原典での主張: 画像比較は保存した基準に対して行い、OS・ブラウザ・フォント等の描画環境を揃える。スクリーンショットはhover状態も取り込む。
- 適用条件・限界: pixel差分自体は品質向上の証明ではない。意図的変更の承認と不意の変化の検知は別の判断。
- このSkillへの推論: 同じviewport/DPR/font/stateで撮影し、基準更新に理由とreviewを要求する。
- 信頼度: 原典本文の当該主張は高。対象製品・LLMへ移す際の有効性は別途試験が必要。
- 短い原文照合句: “run tests in the same environment”
- 取得証拠: `research/raw/sources/S14-web.txt`（ローカル照合専用・配布外）, 該当行 L98, SHA-256 `6a206d39aab24c42ba310f75a3b56d6984fd88cce605f964e976d694aa337bb9`。原典URLと節を安定参照とする。
- 既存との対応: 現行baseのreferences/checklists/sources.mdにこのURLは未掲載。

<a id="s15"></a>

## S15

**[Trace viewer](https://playwright.dev/docs/trace-viewer)** — Microsoft Playwright

- 該当箇所: Snapshots; Actions; Source; Network; Console
- 確認日・種別: 2026-11-23 / 公式実装資料
- 原典での主張: 操作前後のDOM snapshotや操作位置・ログを記録し、失敗した操作を遡って観察できる。
- 適用条件・限界: traceに含まれる認証情報や入力値は秘匿する。traceだけで利用者理解を測定したとしない。
- このSkillへの推論: スクリーンショット、DOM、操作列、console、networkを所見の再現証拠として関連付ける。
- 信頼度: 原典本文の当該主張は高。対象製品・LLMへ移す際の有効性は別途試験が必要。
- 短い原文照合句: “a set of complete DOM snapshots”
- 取得証拠: `research/raw/sources/S15-web.txt`（ローカル照合専用・配布外）, 該当行 L210, SHA-256 `cc4aa5d1f81e52ccdc038507d2634c0cbd4c82d7d2256f9068e789f484a0b449`。原典URLと節を安定参照とする。
- 既存との対応: 現行baseのreferences/checklists/sources.mdにこのURLは未掲載。

<a id="s16"></a>

## S16

**[Accessibility testing](https://playwright.dev/docs/accessibility-testing)** — Microsoft Playwright

- 該当箇所: Introduction; automated tests warning; Scanning for accessibility violations
- 確認日・種別: 2026-11-23 / 公式実装資料
- 原典での主張: 自動検査は一部の問題だけを検出するため、手動評価と多様な利用者による試験を併用する。
- 適用条件・限界: axe等に違反が出ないことは全適合やUX成功を保証しない。
- このSkillへの推論: 機械検査のrule subsetとmanual/inclusive未実施を結果に残す。
- 信頼度: 原典本文の当該主張は高。対象製品・LLMへ移す際の有効性は別途試験が必要。
- 短い原文照合句: “can only be discovered through manual testing”
- 取得証拠: `research/raw/sources/S16-web.txt`（ローカル照合専用・配布外）, 該当行 L90, SHA-256 `134987e87e90e899ee3e0b9733a53be7113abcda6cca6dba709892b0d00e31b9`。原典URLと節を安定参照とする。
- 既存との対応: 現行baseのreferences/checklists/sources.mdにこのURLは未掲載。

<a id="s17"></a>

## S17

**[Measuring the User Experience on a Large Scale: User-Centered Metrics for Web Applications](https://research.google/pubs/measuring-the-user-experience-on-a-large-scale-user-centered-metrics-for-web-applications/)** — Kerry Rodden, Hilary Hutchinson, Xin Fu / CHI 2010

- 該当箇所: Google Research Abstract
- 確認日・種別: 2026-11-23 / 査読研究（著者公開abstractを確認）
- 原典での主張: 著者らはHEARTと製品目標から指標へ対応付ける過程を提示し、社内の製品例で使用したと報告する。
- 適用条件・限界: 今回確認したのは著者公開abstractのみ。数値効果、本文の手法細部、他社一般化の強さは未確認。
- このSkillへの推論: 何を改善したいかを先に固定し、タスク指標をその目標へ紐付ける。
- 信頼度: 原典本文の当該主張は高。対象製品・LLMへ移す際の有効性は別途試験が必要。
- 短い原文照合句: “process for mapping product goals to metrics”
- 取得証拠: `research/raw/sources/S17-web.txt`（ローカル照合専用・配布外）, 該当行 L110, SHA-256 `3c92fce15562faac3a92738a82dcd6e8ae34efcf3b1573337688190858680272`。原典URLと節を安定参照とする。
- 既存との対応: 現行baseのreferences/checklists/sources.mdにこのURLは未掲載。

<a id="s18"></a>

## S18

**[Judging LLM-as-a-Judge with MT-Bench and Chatbot Arena](https://proceedings.neurips.cc/paper_files/paper/2023/file/91f18a1287b398d378ef22505bf41832-Paper-Datasets_and_Benchmarks.pdf)** — Lianmin Zheng et al. / NeurIPS 2023 Datasets and Benchmarks

- 該当箇所: Section 3.2 Limitations of LLM-as-a-Judge; Appendix D.1 position bias
- 確認日・種別: 2026-11-23 / 査読実験
- 原典での主張: 当該会話評価実験では順序、冗長さ、自己選好等の偏りと推論限界が観測された。
- 適用条件・限界: 2023年の会話回答評価。UI批評の精度や今回のモデルのバイアス量を直接示さない。
- このSkillへの推論: 案名を伏せ、順番を入れ替え、根拠不足と一致しない判定をHOLDにする設計上の予防策に使う。
- 信頼度: 原典本文の当該主張は高。対象製品・LLMへ移す際の有効性は別途試験が必要。
- 短い原文照合句: “position, verbosity, and self-enhancement”
- 取得証拠: `research/raw/sources/S18-web.txt`（ローカル照合専用・配布外）, 該当行 L11@P0, SHA-256 `78061803aa5f4b747d90e2315ab7e8f74bc6e9ca6687a1a37eddebeff57f470f`。原典URLと節を安定参照とする。
- 既存との対応: 現行baseのreferences/checklists/sources.mdにこのURLは未掲載。

<a id="s19"></a>

## S19

**[ScreenAudit: Detecting Screen Reader Accessibility Errors in Mobile Apps Using Large Language Models](https://faculty.washington.edu/wobbrock/pubs/chi-25.02.pdf)** — Mingyuan Zhong et al. / CHI 2025

- 該当箇所: Sections 5.3 / 6 / 7; PDF p11 context and functionality limitations
- 確認日・種別: 2026-11-23 / 査読実験
- 原典での主張: Androidの画面監査にLLMを使った実験で、文脈理解不足と実機能の直接試験ができない限界を評価者が挙げた。
- 適用条件・限界: 14画面と6専門家の対象設定。Web全体やDの精度を証明せず、既存索引K13を再利用する。
- このSkillへの推論: LLMの所見候補を実操作で再現し、動かしていない機能の断定を禁止する。
- 信頼度: 原典本文の当該主張は高。対象製品・LLMへ移す際の有効性は別途試験が必要。
- 短い原文照合句: “Unable to Test App Functionality”
- 取得証拠: `research/raw/sources/S19-web.txt`（ローカル照合専用・配布外）, 該当行 L905@P10, SHA-256 `c32c3a454094372e1cc84aaee3dbb21fa1156ca7858ffb6a22109e14f2652a9b`。原典URLと節を安定参照とする。
- 既存との対応: `references/k-studies.md`, `sources.md`

<a id="s20"></a>

## S20

**[Visual Hierarchy in UX: Definition](https://www.nngroup.com/articles/visual-hierarchy-ux-definition/)** — Nielsen Norman Group / Kelley Gordon

- 該当箇所: Definition; 1 Color and contrast; 2 Scale; 3 Grouping
- 確認日・種別: 2026-11-23 / 著者ガイダンス
- 原典での主張: 色・対比・大きさ・近接によるまとまりで、意図した重要度に沿って注目を導くと説明する。
- 適用条件・限界: 色数・字のサイズ数などの推奨値を普遍的なGateにしない。視覚的強調の実効性は対象タスクと実画面で確認する。
- このSkillへの推論: Art Directionが定めた主役と操作を基準に、競合、近接、整列、隠れを位置付きで指摘する。
- 信頼度: 原典本文の当該主張は高。対象製品・LLMへ移す際の有効性は別途試験が必要。
- 短い原文照合句: “organization of the design elements”
- 取得証拠: `research/raw/sources/S20-web.txt`（ローカル照合専用・配布外）, 該当行 L56, SHA-256 `23f9eb99b99f78361321100775d16b36006cf5775d613206d8c3d51e5c055d98`。原典URLと節を安定参照とする。
- 既存との対応: 現行baseのreferences/checklists/sources.mdにこのURLは未掲載。
