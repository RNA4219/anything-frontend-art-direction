# 実装判断と確認記録 — 初回提出

## 提出内容

同じページに「ワークショップ参加予約」と「在庫データ取込み」を実装した。指定された配色・書体・文言を維持し、入力、操作、結果の順で読む構成にした。

controllerはNode標準ESMで動作する。外部パッケージ、ビルド、フレームワークを使用しない。controllerに渡すのは共通APIの公開メソッドだけで、test controlを参照しない。

- `reservation.mjs`: `createReservationController(api)`。
- `import-job.mjs`: `createImportController(api)`。
- `controller-utils.mjs`: JSONの複製、操作識別子、エラーの共通処理。
- `index.html` / `ui.mjs`: 実画面とDOM操作。内部状態名、操作識別子、API呼出し回数、故障注入を画面へ表示しない。
- `demo-server.mjs` / `demo-client.mjs`: 共通APIの内容を変更せずHTTPで送受信する。画面の再読み込みからAPIの存続期間を分離する。
- `demo-progress.mjs`: 通常デモの項目処理だけを進める。UIとcontrollerから分離した。故障注入は含まない。
- `reservation.flow.json` / `import.flow.json`: task contractと状態遷移。
- `self-check.mjs` / `self-check-results.json` / `self-check.log`: 自作の自己確認と実行trace。
- `structural-check-results.json`: Skill checkerと構文検査の結果。
- `manifest.json`: 提出ファイルと読取り対象のSHA-256、環境、未取得メタデータ。

比較評価の点数・優劣は付けていない。他条件の実装・共通比較テスト・評価結果は参照していない。

## 起動と通常操作

このディレクトリで次を実行する。

```sh
node demo-server.mjs
```

画面は `http://127.0.0.1:4173/candidate/index.html`。別ポートが必要なら `WORKSHOP_DEMO_PORT` を指定する。静的ファイルだけの配信ではAPIがないため、上記サーバーから利用する。

予約は名前と人数を入力して送信する。取込みは初期表示で標準3項目が選択されており、開始後に「進捗を更新」を押すと実際の項目別結果を読み込む。通常デモでは項目が順に成功する。処理を止める場合は未完了項目の取消しを要求し、応答を待つ。

取込みの処理番号だけを`sessionStorage`に保持する。画面を再読み込みすると`resume(jobId)`で既存jobを読み直す。APIを保持するNodeプロセスが終了した場合は記憶上のjobもなくなる。番号が見つからない場合は成功を推測せず、読取り失敗を表示する。

## 読んだ設計Skillと適用範囲

現行ファイルを入力とし、以下を読んだ。

| 入力 | 適用した範囲 |
|---|---|
| `anything-frontend-B-base/SKILL.md` | 固定されたArt Directionを保持し、小修正に必要な範囲を確認する |
| base `references/d-interaction.md` | D-31、D-34〜44の回復・古い応答・確定結果の扱い |
| base `references/g-state-forms.md` | G-06、G2、G5、G7、G8、G9の状態・ラベル・制約検証・送信 |
| base `checklists/forms.md` / `checklists/accessibility.md` | エラー時機、native form、Enter、フォーカス、狭幅に関する実装と未検証区分 |
| `extensions/B/SKILL.md` | B01〜B10のtask契約、状態、回復、完了根拠、証拠保存 |
| B `references/flow-contract.md` / `principles.md` / `integration.md` / `sources.md` | Flow JSON、guard、既存資産との役割分担、出典の適用範囲 |
| B `checks/check_flow.py` | Flow JSONの構造・到達性を検査 |

外部検索はしていない。後述のS番号はB Skill同梱の原典整理の参照IDであり、今回外部原典本文を新たに確認したという意味ではない。新しい視覚方向や書体の比較は行わず、`visual-lock.md`を採用条件とした。

## Task contract

| 項目 | 予約 | 在庫取込み |
|---|---|---|
| actor | ワークショップ参加を希望する利用者 | 在庫データを取り込む利用者 |
| goal | 指定の名前・人数の予約1件を確定し、予約番号を見直す | 項目別結果を確認し、失敗項目だけ再試行して全件完了する |
| entry | 名前・人数が空欄 | controllerは未選択。画面は標準3件を選択して開始する。保存jobIdがあれば読取りで復帰する |
| required inputs | 空白だけではない名前、1〜8の整数人数 | 空でない項目配列、空でないID/名前、重複しないID |
| observable success | APIから返ったconfirmed receiptと予約番号 | serverのsucceeded jobと全項目succeededの結果 |
| service effects | `reserve`。`lookup`は読取りだけ | `createJob`、failed subsetの`retryItems`、未完了分の`cancelJob` |
| exit | 未送信破棄。送信中・不明中の離脱は取消しとして扱わない | server確認済み取消し。画面離脱は取消しとして扱わずjobIdで復帰する |
| 前提と限界 | 同一key/同一入力の重複防止は共通APIの契約。予約取消APIは存在しない | 同一jobで単調増加するversionとgenerationを利用。実サービス永続化・認証はこのfixtureにない |

利用者観察は実施していない。上記のactorと操作順序は共通課題に基づく設計であり、観察済みjourneyとして記述しない。

## Decision log

| 原則 | 入力・判断対象 | 採用した判断 | 不採用・例外 | 参照ID | 残る不明点 |
|---|---|---|---|---|---|
| B01 | 予約・取込みの完了 | receipt / server jobを成功の根拠にする | ボタン押下や受付だけでは成功にしない | S01/S02/S16、共通API | 実サービスの完了契約は別確認 |
| B02 | 同一画面の複数状態 | controllerとDOMを分離し、公開操作をguardする | 無効な順序の操作はAPIを呼ばずsnapshotを返す | S02/S17 | 自然言語guardの全組合せはcheckerでは未証明 |
| B03 | 名前・人数の短いフォーム | native form、required/min/max/step、項目エラー、入力保持を使う | 一律の確認画面・stepperを追加しない | S04/S05/S07/S18、G5/G7 | Enter・nativeエラー・IMEは実ブラウザー未確認 |
| B04 | 未送信破棄と処理取消し | 予約は未送信破棄だけ。取込みは取消要求→server応答の順に表示する | 通信待ち解除や画面離脱を取消し済みにしない | S03/S10/S14 | 画面を離れた後の予約意図保存は対象外 |
| B05 | 結果不明と再送 | 送信意図のkeyとpayloadを固定する。unknown後のnot-foundや拒否だけでは未実行に戻さない | 新しいkeyによる盲目的な再送を禁止 | S12/S16、公開API | 冪等性保存期限はfixture寿命以外未確認 |
| B06 | 開始待ち・処理中・進捗照会 | 予約と取込みの待機をそれぞれの領域に表示。progressはserverの値を使用する | 架空percent・全画面ブロック・controller自動タイマーは使わない | S06/S08/S09/S10/S11 | 通知の読み上げ、実待機感は未検証 |
| B06 | 古い応答と別job | 同一jobのversion、表示epoch、確定済みphaseで古い応答を抑止する | 異なるjob間ではversion大小を比較しない | G-06、D-38、S12 | このAPI以外のversion保証は未確認 |
| B07 | 検証失敗・確定拒否・通信不明 | 入力/結果を保持し、修正・同一再試行・再照会を提供する | unknownを通常のfailedへ一括変換しない | S05/S13/S18 | 認証エラーは共通APIにない |
| B08 | 部分成功・再訪 | failed IDだけ再試行する。成功項目を保持。処理番号からreadで復帰する | 成功項目の再投入、resume時のcreateをしない | S03/S04/S12 | プロセス終了を越える永続化はない |
| B08 | デモページの再読込み | 共通APIをNodeプロセスで保持し、HTTP輸送層を追加する | ページごとに共通APIを作り直して復帰成功を装わない | 共通API、実装推論 | 実ブラウザーのreloadは未実行 |
| B09 | 操作の必要性 | 予約は入力→送信→結果。取込みは選択→開始→進捗確認→必要なら失敗分再試行 | 予約の確認画面、強制的な全件再入力、無目的な確認を追加しない | S02/S07/S17 | 発見しやすさ・所要時間は未測定 |
| B10 | 完了判定と証拠 | Node自己確認、HTTP確認、構造検査、未実行UI検査を分離する | 自己検査結果を独立評価、WCAG適合、利用者完了率とは扱わない | S17/S19 | 比較評価・実利用者の評価は未実施 |

### ラベルと文字量の変更

「未送信の入力を破棄」「同じ内容で再試行」「予約結果を確認する」「失敗した項目だけ再試行」「未完了の取込みを取り消す」を追加した。操作対象と副作用を区別するためのインタラクション変更である。元の見出し、説明、項目名、色、見出し書体は変更していない。狭幅では操作ボタンを折り返すCSSを指定したが、実描画での検証は未実行。

## 回復と保持の表

| 状況 | 次の操作 | 保持するもの | 副作用 |
|---|---|---|---|
| 予約の入力不正 | 該当欄を修正して送信 | 名前、人数 | 修正だけではなし |
| 予約の確定拒否 | 同じ意図のretry、入力変更、未送信破棄 | retry時は同じkey/入力 | API契約に従う同一再送 |
| 予約の結果不明 | lookup、同じ意図のretry | key、正規化入力、表示用入力 | lookupはなし、retryは同一意図 |
| lookupで見つからない | 再照会または同じ意図のretry | 以前の結果不明を保持 | 新規の予約意図を作らない |
| 取込み開始の結果不明 | `start()`で同じ意図を再送 | create key、項目配列 | 同一jobの取得 |
| pollの失敗 | 再度poll | job、progress、項目別結果 | 読取りだけ |
| 部分失敗 | failed IDだけretry | succeeded項目とjobId | failed項目だけを再処理 |
| 再試行の結果不明 | pollまたは同じretry key/対象で再送 | 前のgenerationとretry意図 | generation増加の確認で同一batchを解決 |
| 取消し結果不明 | pollまたは未完了分の取消し再要求 | 成功項目、jobId、既知の結果 | 取消しは未完了分だけ |
| 別jobの再開 | resume(jobId) | serverが返すid/name/results | 新規jobを作らない |

## 待機と離脱

controllerにはタイマーと自動再試行を入れていない。UIは応答待ちが12秒を超えた場合に説明を表示する。この12秒は処理時間の推定やエラー判定ではない。API応答が返るまで処理状態と送信意図を保持し、画面を離れても取消しにならないことを伝える。

Flow JSONの`slow_*`、`reading`、`checking`などは表示上の説明状態も表す。controllerの`phase`には共通課題の語彙だけを使う。成功・取消しの後に新しい編集を始める場合は別タスクとなるため、Flow JSONの終端からは遷移を出していない。

## 実行した確認

```sh
node self-check.mjs
python -B ../../../../extensions/B/checks/check_flow.py reservation.flow.json --json
python -B ../../../../extensions/B/checks/check_flow.py import.flow.json --json
```

各`.mjs`には`node --check`も実行した。詳細コマンドと終了コードは`structural-check-results.json`に保存した。

| 確認群 | 実行結果 | 証拠 |
|---|---|---|
| R01〜R08: 予約の初期値、境界、二重押下、確定拒否、不明、照会、破棄 | 8件pass | `self-check-results.json`、`self-check.log` |
| I01〜I14: 空/重複、部分失敗、再試行、取消し、古い応答、再開、通信不明 | 14件pass | 同上。各stepにsnapshotと共通fixtureの実結果を記録 |
| H01: HTTP輸送、公開画面ファイルの配信、新clientのresume | 1件pass | 同上。Node fetchの確認でありブラウザー操作ではない |
| reservation/import Flow | 2ファイルとも構造検査pass | `structural-check-results.json` |
| JavaScript構文 | 提出する実行モジュールを確認 | `structural-check-results.json` |

自己確認は23件実行し、23件pass、0件fail。構造検査の成功はguardの正しさ、バックエンド保証、操作発見性、WCAG適合を証明しない。共通評価テストは実行も参照もしていない。

## 未検証事項・未解決依存

| 分類 / 位置 | 再現条件・観察 | 期待と影響 | 確認方向 | 状態 |
|---|---|---|---|---|
| visual / 全画面 | ブラウザー操作が指示で禁止されている | 1280px・390pxで横スクロールなく入力→操作→結果を読める必要がある | 許可された環境で実画面の幅と文字折返しを確認 | `not_run` |
| implementation / フォーム | native form、required、min/max/step、label、focus-visibleを記述 | Enter、IME、無効入力の通知、キーボード順序が成立する必要がある | 実ブラウザーで通常/不正/境界を操作 | `not_run` |
| implementation / 通知 | statusとalert、項目エラーの関連付けを記述 | 色だけに依存せず変化を読める必要がある | 支援技術で通知とフォーカスを確認 | `not_run` |
| visual / 書体 | 指定の明朝系とsystem-uiをCSSで固定 | 実フォントと代替時の折返しはOSに依存 | 描画された実書体を確認 | `not_run` |
| interaction / reload | HTTP越しの新clientによるresumeを確認 | 同じNodeサーバーの存続中に既存jobへ復帰する | 実画面reload、sessionStorage利用不可、番号失効を操作 | `not_run`（HTTP境界はpass） |
| functional / 本番API | 共通APIはプロセス内メモリ | 再起動後の永続化、認証、複数利用者、実ネットワーク、ACIDの保証はない | 本番APIの契約に接続する段階で別途検証 | 対象外 / 未確認 |
| interaction / 予約中の離脱 | 予約意図・氏名はstorageへ保存していない | 画面を離れても予約を取り消したとは表示しないが、reload後の予約照会復帰は保証しない | 必要ならサービス側の予約検索・安全な復帰契約を別途定義 | 対象外 / 明示済み |

ブラウザー操作は試していない。スクリーンショット、実画面確認成功、利用者評価成功は主張しない。画面の確認制限を迂回していない。
