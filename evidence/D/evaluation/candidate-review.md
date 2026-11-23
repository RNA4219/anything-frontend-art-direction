# 登録・依頼一覧のDesign QAレビュー（Candidate D）

## 結論

**登録の入力保持・重複受付・一覧のページ状態に、修正が必要な実装上の問題が3件ある。狭幅の見出し遮蔽は未確認の仮説1件とする。** 対象JavaScriptの確認済み重大所見に対する判定はREJECT。ブラウザでの受入確認はHOLD、Skillの正式昇格もHOLDである。

これは架空の合成fixtureのレビューであり、現行製品や実予約の不具合報告ではない。画面、共通入力、Gitは変更していない。紙色・黒鉛色・赤茶の罫線、serifの見出しとsans serifの実務情報、角形部品、非対称な構図は承認済みの意図として保った。コピーや題材の好みを欠陥にしていない。

## 1. 完了した確認と実行面

- 指定のArt Direction本体、関連するフォーム・アクセシビリティ確認表、意匠採用条件、Dのprinciples/report-contract/evaluation-protocol、examples、qa_gate.py、原典indexを参照した。
- 対象HTML全体とbriefを読んだ。HTMLのinline JavaScriptを変更せず抽出し、Node v24.22.3の最小DOMで9つの診断記録を得た。ハーネスとログを残した。
- ブラウザは起動していない。ローカル起動禁止・cloud browserのfile URL拒否は依頼時に提示された制約であり、この担当が拒否を再試行して観察したものではない。別のURL公開、別ブラウザ、スクリーンショット代替などによる迂回はしていない。
- source inspectionは属性と処理の記述、minimal DOMはstub上の分岐と値更新を確かめたもの。CSS、native validation、focus、pointer/keyboard、スクリーンリーダー、実画面は未観察である。ブラウザのnormal/error/boundaryはすべてblocked、completionと操作数はnullとした。
- 最小DOMのタイマーは手動で完了させた。ソースの350msは予約された遅延で、実測の待ち時間ではない。FormDataとresetはこの3入力だけのstubであり、resetの意味をHTML Standardとも照合した。

### 対象版・条件

| 項目 | 固定した内容／限界 |
| --- | --- |
| 受付の開始・終端 | リロード相当のaccepted=0から、標準入力で件数が1増え、受付番号を確認できること。模擬端末内の処理だけが対象。 |
| 一覧の開始・終端 | 固定8件・pageIndex=0からページを移動し、処理待ちR-101/R-104を見つけ、条件変更後も継続できること。 |
| 基準画面 | Desktop 1280×900、narrow 320×900、DPR1、ja-JP。いずれも目標条件で、実ブラウザへ適用済みではない。 |
| 環境 | Linux 6.18.57 x86_64、Node v24.22.3、workspace timezone Etc/UTC。ブラウザ・バージョン・実描画fontはunknown。 |
| モデル | セッション表示名GPT-6 Astra Pro。内部snapshot、temperature、seed、費用はunknown。 |
| 試行 | 1回のコード診断実行、9記録。再現環境はハーネスに明示。参加者試験0、ブラウザ操作0。 |
| 操作数 | 実操作を測っていないので未計測。将来計測する場合は「1欄への入力、1選択、1明示的操作を各1」とし、待機は数えない。 |
| 比較 | baselineその他のレビューやoracleを読んでいない。比較効果・検出率・UI改善率は算出していない。 |

| 対象 | SHA-256（実bytes、正規化なし） |
| --- | --- |
| `registration.html` | `37f5f73e7bda78cf6aaa511633b5c4d554d5205d06fbb1260e42cf06671a11dd` |
| `requests.html` | `d95eb231d500cd19e219eeb84b8614b3bcb52908daee9825bce43e0c45f90dc7` |
| `task-brief.md` | `41eb48894d02684dc049bf7ec61ad3f9849c4548998979f6b97dc1c9f42a2db4` |

content hashは各HTMLの全bytes、requirements hashはbriefの全bytes。manifestには対象と主要な評価入力、ハーネス、ログ、JSONのhashを記録した。対象HTMLのhashはprobe抽出時とreport作成時で一致した。

## 2. 重要な所見

重大度はDのblocker / major / minor / noteを用いる。majorは主要タスクの誤結果・強い妨げ、minorは完了可能な局所的負担。頻度の実測値はない。以下のconfirmedは**限定した実装契約の確認**であり、ブラウザのユーザー操作結果を観察済みという意味ではない。

| 優先順 | ID | 重大度／状態 | 一次責務 | 要点 |
| --- | --- | --- | --- | --- |
| 1 | D-REG-02 | major / confirmed（ロジック） | C・implementation | 完了前の重複呼出しで件数2、C-002になる。 |
| 2 | D-REG-01 | major / confirmed（ソース＋ロジック） | C・implementation | 通信失敗で名前・メールが消え、人数が1へ戻る。 |
| 3 | D-LIST-01 | major / confirmed（ロジック） | C・implementation | 3ページ目から処理待ちへ絞ると2件・0行・3 / 1になる。 |
| 4 | D-LIST-02 | minor / hypothesis | C・visual | 320pxで絶対配置ボタンが見出しを覆う可能性。画像なし。 |

### D-REG-02 — 同一入力の処理が並行に走り、受付済み件数が2増える。

**位置・条件：** `registration.html` の `#registration; #submit; #count; #status`。先の非同期処理が完了する前にsubmit listenerを2回呼んだ状態。登録はL8/L12、一覧の状態処理はL9–12、視覚仮説はL5/L7を参照。対象版は上記hash。

**期待：** 一度の申込意図による素早い反復操作で件数は1だけ増え、受付番号も一意に確定する。

**確認したこと：** L12は350msの待機前後に再入防止を持たず各呼出しでaccepted++する。REG-REPEATは待機完了前の2呼出しでqueued=2、完了後count=2、最終文言C-002を記録。実クリックの間隔や発火は未測定。

**利用者への影響と重大度理由：** 主要タスクの受付数が過大になる。利用者は最終番号しか確認できず、単にゆっくり押す以外の抑止がない。合成端末内処理であり実予約や課金の損失は発生していない。発生頻度は未測定。

**局所的な修正方向：** 待機開始前に処理中状態を確定し、重複submitを受け付けない。ボタン状態と処理のガードを整合させ、失敗時は再試行可能に戻す。

**根拠・確度：** task-brief.md 登録画面 — 正常時は1回の申込につき受付済み件数が1増える。素早い反復操作を対象とする。 確度 high。実ブラウザでの発現・復帰は未確認。証拠はE1/E2の該当ソースとE3の対応case。視覚仮説はE2のみ。

**再現・追加確認手順：**

1. リロードし標準データを入力、失敗指定をOFFにする。
2. 登録完了前に登録ボタンを2回素早く操作する。キーボードEnterの反復も別途確認する。
3. 終端で件数が1か2か、受付番号と文言が整合するか確認する。
4. 本実行では実操作はblocked。REG-REPEATは抽出したsubmit listenerを2回直接呼び、待機callbackを順に完了した。

### D-REG-01 — 失敗分岐が入力保持要件に反してフォームをresetする。

**位置・条件：** `registration.html` の `#registration; submit handler failure branch`。有効入力で通信失敗を指定した送信の失敗分岐。登録はL8/L12、一覧の状態処理はL9–12、視覚仮説はL5/L7を参照。対象版は上記hash。

**期待：** 失敗後も代表者名・メール・人数2を保持し、再入力せず同じ申込を再試行できる。

**確認したこと：** L12にform.reset()を確認。最小DOMのREG-ERROR-REENTRYでは名前とメールが空、人数が1、件数0、失敗指定falseとなった。これはstub上の値更新で、ブラウザ操作結果ではない。

**利用者への影響と重大度理由：** 主要な失敗回復で3項目を再入力させる。人数の初期値1を見落とすと別の申込内容になり得る。再入力による回避は可能なためblockerではない。遭遇頻度は未測定。

**局所的な修正方向：** 失敗分岐で入力を初期化しない。入力を残して再試行可能な状態へ戻し、同じ内容の成功時に件数が一度だけ増えることを確認する。

**根拠・確度：** task-brief.md 登録画面; HTML Standard 4.10.5 input reset algorithm — 通信失敗後は入力を維持し、同じ申込を再試行できる。resetはvalue属性または空文字へ戻す仕様。 確度 high。実ブラウザでの発現・復帰は未確認。証拠はE1/E2の該当ソースとE3の対応case。視覚仮説はE2のみ。

**再現・追加確認手順：**

1. リロードし確認 太郎、qa@example.test、人数2を入力する。
2. 次の通信を失敗させるを選び、登録を1回行い処理完了を待つ。
3. 3項目の値と件数を確認し、再入力なしで同じ申込を再試行できるか確認する。
4. 本実行ではこのブラウザ手順はblocked。probeのREG-ERROR-REENTRYはsubmit listenerの直接呼出しとreset stubで分岐だけを再現した。

### D-LIST-01 — 絞り込み後も古いpageIndexを使い、存在する依頼が0行になる。

**位置・条件：** `requests.html` の `#filter; #query; #rows; #page; render()`。2または3ページ目から結果数の少ない条件へ絞り込んだ状態。登録はL8/L12、一覧の状態処理はL9–12、視覚仮説はL5/L7を参照。対象版は上記hash。

**期待：** 処理待ち2件を見つけられ、件数・表示行・ページ範囲が矛盾しない。真の該当なしと範囲外を区別できる。

**確認したこと：** L12のfilter/changeとquery/inputはrenderだけを呼びpageIndexを補正しない。LIST-FILTER-AFTER-PAGEで3ページ目から待ちにすると2件、0行、3 / 1。前へ1回でも2 / 1で0行、2回でR-101/R-104が現れた。検索でも2ページ目から湯のみで1件、0行、2 / 1。

**利用者への影響と重大度理由：** 処理待ちを探す主要経路で対象があるのに空に見える。前へを2回、または条件をクリアで回復するが、不整合の理解と余分な操作が必要。真の0件は別途確認し混同していない。

**局所的な修正方向：** 条件変更時に有効なページ位置へ戻すか現在位置を範囲内へ補正し、補正後の同一結果集合から行とページ表示を作る。0件時は0件として扱う。

**根拠・確度：** task-brief.md 一覧画面 — 同じデータについて絞り込み件数と表示行が一致し、該当なしとページ範囲外を混同しない。 確度 high。実ブラウザでの発現・復帰は未確認。証拠はE1/E2の該当ソースとE3の対応case。視覚仮説はE2のみ。

**再現・追加確認手順：**

1. リロードし次へを2回操作して3 / 3へ進む。
2. 状態を処理待ちに変更し、件数、行、ページ表示を確認する。
3. 前へ1回と2回の両方を確認する。
4. 別の初期化後、次へ1回、検索欄に湯のみを入力する。
5. 本実行は最小DOMで該当ハンドラを直接呼んだ。実クリックと描画はblocked。

### D-LIST-02 — 狭幅で絶対配置の書き出しボタンが見出しを覆う可能性が高い。

**位置・条件：** `requests.html` の `header h1; .header-action#export`。320×900 CSS px、初期表示、実フォント未確認。登録はL8/L12、一覧の状態処理はL9–12、視覚仮説はL5/L7を参照。対象版は上記hash。

**期待：** 320 CSS px相当でも見出し・状態・主要操作が互いを覆わない。承認済みの非対称な上部構図は保持する。

**確認したこと：** L5にheader position:relative、header-action position:absolute/right:0/top:55px、h1 font-size:34px、body左右padding各24pxを確認。狭幅用の分岐や見出し側の予約領域はない。320px時の内容幅はCSS上272px。実際の重なり、字幅、占有矩形は未観察。

**利用者への影響と重大度理由：** 重なれば画面名の可読性とボタン周辺の理解を損なう。依頼探索の完了不能は未立証のため暫定minor。実画面の影響次第で重大度を見直す。

**局所的な修正方向：** まず320pxと1280pxで同一内容の矩形・スクリーンショットを取得する。重なりを確認した場合は狭幅だけ見出しと操作の領域を分け、紙色、赤茶罫線、書体差、角形、広幅の構図を維持する。

**根拠・確度：** task-brief.md 一覧画面; WCAG 2.2 SC 1.4.10（補助的な確認観点） — 広幅・狭幅で互いを覆わないこと。Reflowの二次元配置例外を表全体へ一律禁止として適用しない。今回WCAG違反は判定していない。 確度 medium。実ブラウザでの発現・復帰は未確認。証拠はE1/E2の該当ソースとE3の対応case。視覚仮説はE2のみ。

**再現・追加確認手順：**

1. DPR1・ja-JP・320×900 CSS pxでrequests.htmlを初期表示する。
2. headerの見出し全文と書き出しボタンの矩形・画像を記録し、覆われた文字と操作領域を特定する。
3. 同一内容を1280×900で確認し、Tabフォーカス時も読めるか比較する。
4. 本実行ではブラウザ禁止によりblocked。この手順は次回の確認手順で、実施済みではない。

## 3. 正常・失敗・境界の確認範囲

次表の「結果」はソースまたは最小DOMで確認した値である。ブラウザの業務タスクは全行blockedであり、合格扱いにしていない。9診断記録の成功数を人間の完了率へ変換しない。

| ケース | 種別 | コード／最小DOMで分かったこと | 未確認の実操作 |
| --- | --- | --- | --- |
| 標準入力を1回送信 | normal | REG-NORMAL: 名前・メール・人数2を保持し、件数1、C-001を生成。待機中は登録しています…を生成。 | クリック・Enterでの送信、読める完了表示、読み上げ。 |
| 通信失敗→再試行 | error | REG-ERROR-REENTRY: 名前とメール空、人数1、件数0。3項目を再入力後はC-001を生成。入力保持要件は満たさない。 | 失敗後に再入力せず同じ申込で復帰できるか。通常ブラウザでは空欄の再送信はnative validationの対象となる。 |
| 人数1・8 | boundary | REG-VALID-1/8: 既知の有効payloadをlistenerへ直接渡すとそれぞれ件数1。min=1、max=8、requiredを静的確認。 | native validationを経た成功、表示・訂正・再送信。 |
| 人数0・9・空・2.5／名前空／メール空・不正形式 | boundary/error | required、type=email、type=number、min/maxがあり、novalidate/formnovalidateはない。標準仕様上は通常submit前の制約検証が期待される。 | 実際の拒否、エラー内容、focus、訂正後のC-001到達。無効値をlistenerへ直送してnative検証欠陥とは判定していない。 |
| 完了前に2回送信 | boundary | REG-REPEAT: 同じpayload、待機2本、件数2、最終C-002。 | ダブルクリック、Enter連打、実際の間隔とイベント発火。 |
| 一覧の通常ページ移動 | normal | LIST-NORMAL: 8件、1/3→2/3→3/3。行はR-101〜103、104〜106、107〜108。端のdisabled値も生成。 | マウス・keyboardでページ移動し対象を発見できること。 |
| 真の該当なし→解除 | error | LIST-EMPTY-CLEAR: 存在しない依頼で0件、0行、1/1、前後disabled。クリアで8件・先頭3行へ復帰。 | 空状態の理解と解除ボタンへの到達。0件自体を不具合にしていない。 |
| 3ページ目→処理待ち | boundary | LIST-FILTER-AFTER-PAGE: 2件、0行、3/1。前へ1回も空、2回で待ち2件。D-LIST-01。 | 実際の一覧表示・focus・状態通知。 |
| 2ページ目→検索1件 | boundary | LIST-SEARCH-AFTER-PAGE: 湯のみで1件、0行、2/1。クリアで先頭へ復帰。D-LIST-01の同原因の別経路。 | 実入力での更新と条件解除。 |
| 広幅・320px | boundary | 絶対配置・固定offset・font指定・paddingを確認。重なりは予測のみ。 | 画像、矩形、折返し、横あふれ、表の各セル、ページ操作、focusの可視性。 |

### 良好な実装上の材料と過剰指摘を避けた点

登録はlabelのforとinputのidが対応し、fieldset/legend、required、email型、人数のmin/max、statusのroleとaria-live、focus-visibleのCSSを持つ。一覧はcaptionと列見出しscope、検索・状態ラベル、status領域、ページnavを持つ。これらはソースにある支援材料で、支援技術やキーボードで利用できたという合格証拠ではない。

人数のstep省略は直ちに小数許可ではない。Number状態の既定step=1とmin=1から2.5はstep mismatchとなる仕様を確認した。通常フォーム送信はsubmitイベントより前に制約検証するため、ハンドラ内にcheckValidityがないだけで入力検証欠落とは判定しない。[P1][P2]

## 4. 証拠と原典

| ID | ファイル／参照 | 支える範囲 |
| --- | --- | --- |
| E1 | `evaluation/common/subject/registration.html` L8–12 | 入力属性、submit処理、reset、非同期待機、受付数更新。 |
| E2 | `evaluation/common/subject/requests.html` L5、L7、L9–12 | 配置CSS、固定データ、filter、slice、pageIndex、条件解除。 |
| E3 | `candidate-logic-log.json` | 9件の最小DOM診断。ソースhash、入力、生成値、復帰条件、エンジンと限界。 |
| E4 | `candidate-logic-probe.cjs` | E3を再生成するハーネス。stubの範囲と直接listener呼出しを公開。 |
| E5 | `candidate-registration-desktop.json`、`candidate-requests-desktop.json`、`candidate-requests-narrow.json` | 1 task × 1目標viewport × 1レビュー試行の機械契約。ブラウザtask_runsはblocked。 |
| E6 | `candidate-gate-results.json`、`candidate-manifest.json`、`candidate-manifest-gate.json` | ゲートの実stdout・終了コード、実bytesのhashとサイズの照合。 |

主たる不具合根拠はtask-briefの明示要件である。以下の公開原典はこの実行で本文の該当節を取得した。原典indexに書かれた他の過去取得を、この担当の原典実読として数えていない。

- **[P1] WHATWG HTML Standard、4.10.5 input reset algorithm / 4.10.5.1.12 Number state**（取得2026-11-23、ページ記載更新2026-11-22）：[input](https://html.spec.whatwg.org/multipage/input.html)。resetはvalue属性または空文字へ戻す。numberの既定stepは1。これは仕様で、今回のブラウザ実測ではない。
- **[P2] WHATWG HTML Standard、4.10.22.3 Form submission algorithm / 4.10.21 Constraint validation**：[form control infrastructure](https://html.spec.whatwg.org/multipage/form-control-infrastructure.html#form-submission-algorithm)。通常送信は制約検証が不正ならsubmitイベントへ進まない。submit()等の別経路の例外を通常ボタンクリックと混同しない。
- **[P3] W3C WCAG 2.2、SC 1.4.10 Reflow**（ページ版2024-12-12）：[Reflow](https://www.w3.org/TR/WCAG22/#reflow)。320 CSS px相当での情報・機能の保持を確認する観点。必要な二次元配置の例外があり、表の横スクロールを一律に違反としない。本レビューは描画未観察のため適合・違反の宣言をしない。

## 5. 判定と次に必要な最小確認

| 記録 | contract_valid | target_decision | promotion_decision | CLI終了値 |
| --- | --- | --- | --- | --- |
| candidate-registration-desktop.json | true | REJECT | HOLD | 2 |
| candidate-requests-desktop.json | true | REJECT | HOLD | 2 |
| candidate-requests-narrow.json | true | HOLD | HOLD | 2 |

manifest照合は終了値0、integrity_verified=true。これはファイル同一性の検査であり、画面品質の合格ではない。reportゲートの終了値2は契約不正ではなく、有効な記録に対するREJECT/HOLDである。登録と一覧DesktopのREJECTは確認済みmajor実装所見、narrowのHOLDは画像のない仮説と未実行caseに由来する。

### HOLDを解くための確認

1. **Cへ3件の実装所見を引き渡す。** 失敗時の入力保持、処理中の重複受付防止、条件変更時のページ範囲の補正を、承認済みの意匠を保つ局所修正として扱う。このレビューでは修正していない。
2. **許可された環境で実ブラウザを1つ固定する。** バージョン、OS、実フォント、viewport、DPR、localeを記録し、現行または修正版hashと対応させる。ここでのpolicyを迂回する意味ではない。
3. **登録を終端まで確認する。** 標準1回、失敗後に入力を変えず再試行、1/8の成功、0/9/空/2.5と必須項目不正の拒否→訂正→成功、完了前の連打を実施する。件数と番号を照合する。
4. **一覧を終端まで確認する。** 1→3ページ、真の0件→解除、3ページ目→待ち2件、2ページ目→検索1件を実施し、件数・行・ページの同一データ整合を確かめる。
5. **広幅と320pxの画像・keyboardを確認する。** 見出し・書き出し・状態・表・ページ操作を同内容で撮り、Tab/Shift+Tab/Enter/Space、focusの可視性、読める文言を確かめる。visual所見のconfirmed化には実画像が必要。

スクリーンリーダー、実機touch、他OS/ブラウザ、利用者研究、総合WCAG適合は未実施。browser試験完了後も、その範囲を越える保証はしない。

**独立性：** この担当は別評価答案・oracle・親セッション証跡を参照していない。ただし同じ共有OSでアクセス遮断の証拠はなく、protected blindではない。このレビュー自身の契約確認は自己確認であり、独立評価receiptはない。Skillの正式昇格はHOLDのままとする。
