# SESSION A — 実装・比較・検証結果

## 結論

**HOLD。Skill実装、原典追跡、実際のbaseline/candidate生成、機械検査、ラベルを伏せたモデルレビュー、R-ASIへの証跡登録を行った。追加Skillの改善効果と正式昇格は未成立。**

最終validatorの40テストはすべて成功した。比較した4案の構造エラーはすべて0件だった。別スレッドのレビューは2ケースとも「同等」。ブラウザの実画面・操作・スクリーンショットは環境とURLポリシーにより確認できなかった。これらを正式PASSへ読み替えない。

## 実装と既存資産

- Skill: `extensions/A/SKILL.md`、名前 `anything-frontend-product-ia`。
- 10原則: 達成内容、双方向追跡、統合/削除/延期/非表示、必須条件を守る優先順位、分類と正本、role別ナビゲーション、画面責務、段階的開示、情報密度、検査範囲の報告。
- 方法資料、入出力契約、原典索引、8つの適用/反例/不適用例、validator、比較・描画・ブラウザprobe、再現用briefとテストを実装。
- 原典20件。出典URL、資料名、該当箇所、確認日、原典の主張、資料の種類、適用限界を [source-index.md](source-index.md) から追跡できる。
- 20件の短い引用は取得した本文抜粋と照合済み。HTTP fetchのDNS失敗は保存し、Web取得の抜粋を用いた。全資料の完全なHTML/PDFを保存したという意味ではない。
- 基準 `f5df625dbc577d6a3ca28e13ef09e39b135b4a6f` の既存50ファイルはすべて変更なし。root SKILL/READMEも変更していない。
- 全10原則に指定8節とConfidence/Limitsがあり、主要な原典URLへ入口から2ホップで到達する。Skillのローカルリンクに欠落なし。frontmatter検証も成功。

具体的な既存対応との差分は [coverage-matrix.md](coverage-matrix.md)、機械的なパッケージ確認は [package-integrity.json](runs/package-integrity.json)。

## 比較条件

[protocol.md](experiment/protocol.md) と [run-manifest.json](experiment/run-manifest.json) に条件を記録した。

| 条件 | 実際の扱い |
|---|---|
| タスク | 問い合わせ対応・監査 / 講座探索・比較・公開の2種類 |
| baseline | 固定した既存Art Directionと共通brief/中立的JSON出力形式 |
| candidate | 同じ入力にAのSkill・方法参照・例を追加 |
| モデル | 両方とも新規スレッド、親と同じ継承モデル、overrideなし。具体的モデルID・sampling設定は実行器から未提供 |
| コンテンツ・要件・視覚意図 | 両armで同一bytesを確認。処理後の原本もhashで凍結 |
| 生成試行 | 各arm 1回、各回2ケース。評価結果を渡して設計案を修正する試行は行っていない |
| 分離 | 各生成者は自身の入力ディレクトリだけを読む指示。親履歴・他案・checker・test・reviewは渡していない。OSによる読取隔離ではない |
| 課題の性質 | 公開された開発用fixture。非公開holdoutではない |
| 費用・token・実行image digest | 未提供。0とは記録しない |

生成に使用したSkillの公開revisionは `97b19c29c0b63acfee9ad437f93af081ac0c6ef8`。
生成後の変更は検査器の欠陥修正と、FAIL/HOLD優先順位の文書明確化。凍結した生成入力・出力は変更していない。
各差分と検証範囲を [post-generation-changes.json](experiment/post-generation-changes.json) に記録する。最終文書の変更を加えたモデル生成を再実行したとは主張しない。

## baseline / candidateの実結果

[comparison.json](experiment/comparison.json) は最終validatorで再生成した。個別ログは [validator-v3](experiment/validator-v3)、旧版の結果は [validator-v1](experiment/validator-v1) に保持した。

| ケース | baselineの構造エラー | candidateの構造エラー | baseline機械status | candidate機械status | ラベルを伏せたレビュー |
|---|---:|---:|---|---|---|
| support-triage | 0 | 0 | HOLD：blocking残件3件 | HOLD：blocking残件2件 | 同等 |
| course-catalog | 0 | 0 | HOLD：blocking残件4件 | PASS：blockingフラグ0件 | 同等 |

このPASSはID・依存・到達性・必要情報の宣言などの機械検査だけを意味する。candidateの講座案にも、実申込先、公開状態の値、講座ID等の入力不足は明記されている。blockingの分類差を改善効果に数えない。どの案も業務提供や昇格の正式PASSではない。

| ケース | baselineの画面 / navigation宣言数 | candidateの画面 / navigation宣言数 | 機能判断の差 |
|---|---|---|---|
| support-triage | 4 / 11 | 3 / 6 | keep 5・merge 1・defer 1・remove 1で一致 |
| course-catalog | 5 / 13 | 6 / 16 | keep 5・merge 3で一致。お知らせはbaselineがremove、candidateがdefer |

画面数・リンク数は記述値であり、少なさに加点していない。比較スクリプトの最短距離も、宣言グラフ上の辺数であり、検索条件入力や比較対象選択を含む実タスクの操作回数ではない。
主要な統合判断は既存Art Directionだけでも成立していた。今回の2ケースから追加Skillの品質向上を主張しない。

## 検査器の回帰試験と改善履歴

最終validator SHA-256:

`de5abbc23d003e5401830d6776bb043b21ee3912f82291389081068a98893e68`

| 版 | 実行結果 | 見つかったこと・変更 |
|---|---|---|
| v1 | 32/32成功 | その後の有限監査が、既存テストで覆えていなかった到達性と多段mergeの抜けを発見 |
| v2 | 新37件をv1に当てると3テストメソッド・4失敗イベント。修正後37/37成功 | 必須入力featureのrole別到達性、直接keep正本へのmergeを検査。旧テストの多段mergeを許す期待も契約に合わせて訂正 |
| v3 | 新40件をv2に当てると1件失敗。修正後40/40成功 | feature要求がmandatory=falseでも、must goalを担う到達可能な機能が必要。到達可能な代替は許可し、shouldへmust条件を強制しない |

主な正常系は2種類の独立して作成した小規模plan、同画面での達成、正当な戻り経路、直接aliasへの依存、別entry・role別の配置。
異常系は要件喪失、必須機能の削除、依存喪失、権限拡張、到達不能、必要情報のsecondary化、統合循環・多段統合、壊れたID/shape/enum、未宣言機能、CLIの不正入力。
境界は低頻度の必須監査、0辺の同画面経路、複数入口、shouldの延期、必須目標を任意指定の機能が担う場合など。

実ログ: [v1](runs/validator-tests.txt)、[v2](runs/validator-v2-tests.txt)、[v3](runs/validator-v3-tests.txt)。
修正理由とred/green記録: [初期改善](runs/validator-iteration.json)、[v2](runs/validator-v2-review-fixes.json)、[v3](runs/validator-v3-goal-reachability.json)。
[パッケージ監査](package-review.md) のPR1/PR2/PR3に対する処置は [resolution](package-review-resolution.md) に記録した。
これらは実装の検査であり、LLMによる設計の効果測定や独立品質判定ではない。

## ブラウザ・表示に関する証拠

- 共通rendererで4つのHTMLを生成。両armで同じCSS・データ投影規則・色の近似値を使う。
- 4/4で埋込brief・planが凍結原本と一致し、4/4で埋込JavaScriptの構文確認が成功。[projection-checks.json](experiment/projection-checks.json)
- 通常・0件・1件・反復40行の表示モードとrole切替を検査ハーネスとして実装した。反復40行は新しい実データではなく、5000/10000件の性能試験でもない。
- ローカルChromiumは `socket() failed: Operation not permitted` で起動失敗。sandboxは無効化していない。
- 接続済みBrowserはoriginating contextが利用できず、Cloud Browserは `file://` URLを自動URLポリシーで拒否した。拒否後の迂回は行っていない。
- **実画面、クリック、JS実行時エラー、overflow、レスポンシブ、スクリーンショット、読み上げは未検証。** JS構文確認やHTML生成をブラウザ検証と数えない。

失敗の実ログと各経路の状態は [browser-availability.json](experiment/browser-availability.json) と [browser_probe_result.json](experiment/browser/baseline-support-triage/browser_probe_result.json)。他の3HTMLについて同じ起動失敗を繰り返して実測件数を増やしていない。
生成物は [projections](experiment/projections)、再実行方法は [checks/README.md](../../extensions/A/checks/README.md)。業務の送信・保存・公開を実装したアプリではなく、情報構造の共通投影である。

## ラベルを伏せたレビュー

両案を凍結してからR/Sへ無作為に対応させ、JSONのキー順と字下げのみを揃えた。レビュー担当は新規スレッドで、7入力ファイルだけを読む指示。実際の対応はR=baseline、S=candidateだった。
[入力manifest](experiment/review-input-manifest.json)、[対応と限界](experiment/review-mapping.json)、[レビュー原本](experiment/label-review/review.md)を保存した。

- 2ケースとも「同等」。重大な設計欠陥の認定0件。
- 確認課題2件: candidate問い合わせ案の「全件」、baseline講座案の「すべての講座」が、解除する条件の範囲を伝えるか。どちらも条件併記の計画があり、確定欠陥にはしていない。
- 入力不足6件を設計不良から分離。担当ルール、保持・監査範囲、実申込先等を捏造して評価していない。

同じ継承モデル・共通filesystemであり、未公開holdoutはない。本文中の書き方や原則IDから条件が推測される可能性もある。共通rendererの作者がagent一覧でbaselineの高水準の完了要約を見たことも記録した。raw planを見ずに汎用投影器を作り、probe作者は別の履歴なしスレッドだったが、これを厳密なblind試験とは呼ばない。
**本結果はラベルを伏せたモデル文書レビューであり、独立Oracle、実利用者評価、正式昇格審査ではない。**

## 責務別の結果

| 責務 | 確認できたこと | 未確認 |
|---|---|---|
| 機能設計 | 要求の処置、正本、義務・依存・権限保持。比較レビューで重大な欠落なし | 実業務の充足、入力外の既存義務 |
| 情報構造 | IDとrole別到達性、primary宣言、機能配置。ラベルの確認課題2件 | 利用者の分類理解、発見可能性、実際の探索成功 |
| インタラクション | 開始/行先と担当外の残件を記録 | 状態遷移、戻る/取消、非同期、失敗/復帰。Bへ引継ぎ |
| 視覚設計 | visual_intent_idと同じ投影条件を保持 | 実画面での視覚意図、整列、可読性。Art Direction/C/Dへ引継ぎ |
| 実装 | validatorの40テスト、JSON・埋込JS構文、入力の一致 | production処理、認可、WCAG、レスポンシブ、ブラウザ実操作 |

## R-ASIとGate

実装revision `f5b638085dece1f997210f9b653aceb8fe9b32d4`、CLI 0.0.2を使用した。
`verify / pipeline / cas-verify / experience-add`の成功receiptとCASを保存。現在の抽出candidate CASは:

`890dad5d012d5bf7dc063d78e404014cfedd91b5522dbe1bb447578e3842426d`

R-ASIが検証した入力は、117行・10単位の編集済みsankai抽出artifactで、原典本文そのものではない。形式・行範囲・hashの整合性を検証したものである。
`execute / evaluate / promote`は実装上未接続でexit 3。モデル生成と比較・試験は外部で実行し、その実結果のartifact hashをR-ASIへ記録する。
詳細と最新receiptは [R-ASI record-index](rasi/record-index.md)。candidateは`UNTRUSTED_CANDIDATE` / `quarantined` / `promoted=false`のまま。

**READY FOR INTEGRATIONには昇格しない。** 独立評価、ブラウザ観察、対象利用者での分類・ラベル確認、同条件での追加課題が必要。改善がない結果も受け入れ、追加Skillの適用範囲・必要性を再評価する。統合担当への具体案は [handoff.md](handoff.md)。
