# 共通課題・出力契約 v1

この文書、`api.mjs`、`visual-lock.md` は両条件へ同じ内容で渡す。
予約と在庫取込みの、実際に操作できる画面とフレームワーク非依存のcontrollerを実装する。
Node.js標準ESMのみを使い、npm依存やビルドを必要としない形にする。
既存のArt Directionが決めた見た目は `visual-lock.md` に固定する。

## 提出するモジュール

- `reservation.mjs` は `createReservationController(api)` をnamed exportする。
- `import-job.mjs` は `createImportController(api)` をnamed exportする。
- `index.html` は両方のタスクを操作できる実画面とする。故障注入・テスト結果・内部状態名・
  request key・API呼出し回数を利用者向け画面に表示しない。故障注入は外部test harnessで行う。
- モジュールは渡された `api` の公開メソッドだけを利用する。test control、テスト結果、
  別条件の実装、評価ファイルには依存しない。
- `snapshot()` は現在の状態をJSON互換の独立した値として返す。返却値の変更が内部状態を変えてはならない。
- 公開操作は利用者の連打や呼出し順の誤りで未処理Promise rejectionを出さない。
  APIの業務・通信エラーはsnapshotへ反映する。プログラマによる引数型の誤用はこの条件の対象外。
- 明示的な `poll()` で進捗を取得する。比較controllerに自動タイマーや無制限の再試行を入れない。

## 共通の状態語彙

`phase` は次の文字列だけを使う。これ以外のphase名や大文字表記は使用しない。

| phase | 意味 |
|---|---|
| `idle` | まだ入力・選択を始めていない |
| `editing` | 未送信の入力・項目を編集している |
| `loading` | 既存jobを最初に読み戻している（importのresume用） |
| `submitting` | 新規送信または再送の応答待ち |
| `running` | serverがjobを処理している |
| `partial` | jobの処理が終了し、少なくとも1項目が失敗した |
| `succeeded` | serverが目的の処理完了を返した |
| `failed` | 入力検証または確定した失敗。成功として表示しない |
| `uncertain` | 送信結果が不明。失敗・未実行・取消済みとは断定しない |
| `cancelling` | job取消しのserver応答待ち |
| `cancelled` | 未送信の入力を利用者が破棄した、またはserverがjob取消しを返した |

`error` は `null` または `{code: string, message: string, fields?: object}`。
messageは利用者に理解できる短い説明とし、色だけでエラーを区別しない。
APIの `SimulationError.outcome` は `definitive` または `unknown`。
`unknown` を通常の確定失敗と同一視しない。

## 課題1：ワークショップ参加予約

### 同一コンテンツ

- 見出し：`ワークショップ参加予約`
- 説明：`参加する人の名前と人数を入力してください。`
- 項目：`名前`、`参加人数（1〜8人）`
- 正常データ：`{name: "山田 太郎", people: 2}`
- 目的：指定の名前・人数で予約が1件確定し、予約番号を見直せること。

### 利用者要求

1. 名前は空白だけでは受け付けない。人数は1〜8の整数。無効入力を送信してもserverへの書込みを始めない。
2. 入力を修正して再度送信できる。検証エラーや通信失敗で入力内容を失わない。
3. 送信後は処理中であることが分かる。応答待ちに送信・再試行を連打しても重複した書込み要求を作らない。
4. serverが返したreceiptを成功表示の根拠にする。押下だけで予約完了にしない。
5. 応答が不明になったときは照会または同じ操作識別子による再試行を行える。
   その入力を新しい予約として送って二重予約にしない。照会で見つからない場合も、
   「最初の送信は絶対に実行されない」とは断定しない。同じ識別子で再試行できる。
6. まだ送信していない入力は取消せる。送信中・結果不明の画面を閉じることを、server側の予約取消しと表示しない。
7. 初期状態、人数0・1・8・9・小数、空白名、二重押下、確定失敗後、応答不明後を扱う。
8. 成功後にもう一度 `submit()` しても同じ予約を増やさない。成功・取消し後に利用者が
   `setDraft()` で新しい編集を開始する場合は別の予約を作れる。

### Controller interface

```ts
createReservationController(api) => {
  snapshot(): ReservationSnapshot,
  setDraft(patch: { name?: string, people?: number | string }): ReservationSnapshot,
  submit(): Promise<ReservationSnapshot>,
  retry(): Promise<ReservationSnapshot>,
  reconcile(): Promise<ReservationSnapshot>,
  cancel(): ReservationSnapshot
}
```

```ts
type ReservationSnapshot = {
  phase: Phase,
  draft: { name: string, people: number | string },
  receipt: Receipt | null,
  error: ErrorInfo | null,
  requestKey: string | null,
  canSubmit: boolean,
  canRetry: boolean,
  canReconcile: boolean,
  canCancel: boolean
}
```

- 初期状態は `idle`、draftは `{name:"", people:""}`、receipt/error/requestKeyはnull。
- `setDraft()` は未送信の入力を更新して `editing` にする。`submitting` または `uncertain` 中は
  入力と送信意図を変えない。無効入力への修正も受け付け、`canSubmit` はfalseにする。
- `submit()` は有効な編集から送信を始める。無効入力への直接呼出しは `failed` と入力エラーを返し、APIを呼ばない。
- 同じ送信意図の `retry()` は、最初のreserveに使ったrequestKeyと同じ内容を使う。
  利用者が入力を変更した後の新しい送信は、新しいrequestKeyを使う。
- `reconcile()` は現在のrequestKeyを照会する。receiptがあれば `succeeded`、なければ `uncertain` のままにする。
- `canRetry` は有効な送信済み意図について確定失敗・結果不明から再試行できるときtrue。
  `canReconcile` は結果不明でrequestKeyがあるときtrue。実際の呼出し進行中は重ねて呼ばない。
- `canCancel` は未送信の編集、またはserver未確定の予約が存在しない確定失敗から破棄できるときtrue。
  `cancel()` 成功時は `cancelled`。実行不能な操作はAPIを呼ばず現在のsnapshotを返す。
- 人数の入力文字列はフォームで許容するが、APIへ渡すときは整数にする。

### Reservation API

```ts
api.reserve({ key: string, draft: {name: string, people: number} }): Promise<Receipt>
api.lookup(key: string): Promise<{found: boolean, receipt: Receipt | null}>
type Receipt = {id: string, key: string, name: string, people: number, status: "confirmed"}
```

同じkey・同じ正規化入力のreserveは、同じreceiptを返して予約を増やさない。
同じkey・異なる入力は `KEY_CONFLICT`。lookupは書込みを行わない。
このAPIには予約を取り消すserver操作はない。

## 課題2：在庫データの非同期取込み

### 同一コンテンツ

- 見出し：`在庫データ取込み`
- 説明：`選んだ3件の在庫データを取り込みます。`
- 標準入力：`[{id:"a",name:"青いノート"},{id:"b",name:"赤い鉛筆"},{id:"c",name:"白い封筒"}]`
- 目的：各項目の結果を確認し、失敗項目を再試行して取込みを完了する。

### 利用者要求

1. 未選択・空配列・重複IDでは開始しない。標準入力の3件と名前を両条件で変えない。
2. 開始の応答待ちと処理中を区別する。開始を連打してもjobを増やさない。
3. 進捗と項目ごとの結果を見直せる。途中までの成功を、全件成功と表示しない。
4. 全項目の処理が終わっても失敗があれば `partial`。成功した項目を保持したまま、
   失敗した項目だけを `retryFailed()` で再試行する。
5. 取消しを要求してから応答が返るまでは `cancelling` とする。serverが返す結果を確認してから
   `cancelled` にする。すでに全件成功した後に取消し応答が到着する場合は、成功という実際の結果を表示する。
6. 取消済み・成功済みの状態が、遅れて届いた古いpoll応答で処理中に戻らない。
7. 画面を再読み込みした後、保持したjobIdを `resume(jobId)` に渡して既存jobと各項目の結果を読み戻せる。
   resumeで新しいjobや重複した取込みを作らない。
8. 空選択、全成功、部分失敗、再試行、取消し応答待ち、古い応答、存在しないjobIdを扱う。

### Controller interface

```ts
createImportController(api) => {
  snapshot(): ImportSnapshot,
  setItems(items: Array<{id: string, name: string}>): ImportSnapshot,
  start(): Promise<ImportSnapshot>,
  poll(): Promise<ImportSnapshot>,
  retryFailed(): Promise<ImportSnapshot>,
  cancel(): Promise<ImportSnapshot>,
  resume(jobId: string): Promise<ImportSnapshot>
}
```

```ts
type ImportSnapshot = {
  phase: Phase,
  items: Array<{id: string, name: string}>,
  job: Job | null,
  error: ErrorInfo | null,
  requestKey: string | null,
  progress: {processed: number, total: number},
  canStart: boolean,
  canPoll: boolean,
  canRetryFailed: boolean,
  canCancel: boolean
}
```

- 初期状態は `idle`、itemsは空、job/error/requestKeyはnull、progressは `{processed:0,total:0}`。
- `setItems()` は未開始の選択を更新して `editing` にする。実行中・取消応答待ちはjobの対象を変更しない。
- `start()` は有効な選択から `submitting`、応答後はserverのjob.phaseへ進む。
- `poll()` は現在のjobIdの読取りだけを行う。現在の表示を残して待ち、失敗時にも既知の結果を消さない。
  jobがない状態のpollはAPIを呼ばない。
- `retryFailed()` は `job.results` 中のfailed項目を対象とする。成功項目を再処理せず、
  応答前の再押下で再試行要求を増やさない。
- `cancel()` は処理中jobのserver取消しを要求する。取消し不能な状態の呼出しは現状を返す。
- `resume(jobId)` は `loading` からreadで復帰する。存在しないjobIdなら `failed` と説明を返す。
  復帰したitemsはjob内のid/nameに合わせる。
- job内の `version` は同じjob内で単調に増える。別jobへ復帰するときは、元のjobとの比較を混同しない。
- `canStart/canPoll/canRetryFailed/canCancel` はそのsnapshotで実際に可能な操作に一致させる。
  `canRetryFailed` は再試行可能なfailed項目があるとき、`canCancel` は処理中で取消し要求が未送信のときtrue。

### Import API

```ts
api.createJob({key: string, items: Item[]}): Promise<Job>
api.getJob(jobId: string): Promise<Job>
api.retryItems({jobId: string, key: string, itemIds: string[]}): Promise<Job>
api.cancelJob(jobId: string): Promise<Job>

type Job = {
  id: string, key: string,
  phase: "running" | "partial" | "succeeded" | "cancelled",
  version: number, generation: number,
  progress: {processed: number, total: number},
  results: Array<{id: string, name: string,
    status: "pending" | "succeeded" | "failed" | "cancelled", error: string | null}>
}
```

`processed` はsucceeded/failedの件数。再試行したfailed項目がpendingへ戻ればprocessedは減る。
`generation` は再試行batch数、`version` はjobの更新ごとに増える。
同じcreate key/入力またはretry key/対象の再送は副作用を増やさない。
cancelは未完了項目だけをcancelledにし、それ以前の成功結果を保持する。
全件成功後のcancelは成功jobを返す。APIによる進捗は時間で勝手に変わらず、外部fixtureが進める。

## 共通fixtureの使い方（実装用APIとtest controlの境界）

`api.mjs` の `createReservationHarness()` / `createImportHarness()` は `{api,control}` を返す。
controllerへ渡すのはapiだけ。controlは外部テスト・通常デモ進行を担当する別のコードで使う。

| control | 意味 |
|---|---|
| `plan(method, ...plans)` | そのメソッドへの次の呼出しから順に結果を設定する |
| `pending(method?)` | 未応答requestのid/method/argsを取得する |
| `release(requestId, override?)` | deferred requestを応答させる。overrideでその応答だけplanを変更できる |
| `inspect()` | request履歴、read/write呼出し回数、server状態を複製して返す |
| `completeItem(jobId,itemId,"succeeded"|"failed")` | importのserver処理を1項目進める。settled項目への遅い完了は無視する |

planは `{defer?:boolean,result?:string,code?:string,message?:string,value?:unknown}`。
既定は `{defer:false,result:"ok"}`。通常応答もmicrotaskで非同期に返る。

| result | このsimulationで起こること |
|---|---|
| `ok` | 応答時に操作を実行して結果を返す |
| `reject` | 副作用を実行せずdefinitive errorを返す。既定codeはUNAVAILABLE |
| `commit-unknown` | 操作を実行した後、TIMEOUT/outcome unknownを返す |
| `no-commit-unknown` | 操作を実行せず、同じTIMEOUT/outcome unknownを返す |
| `snapshot` | readだけで使用可。保存したvalueを返す。古いpollの再現に使用する |

defer=trueでは、releaseまでserver操作も実行しない。planはそれぞれ1回だけ消費する。
`inspect().writes` は書込み**呼出し**回数、`created` は実際に作られた予約/job数。
importの `itemAttempts[jobId][itemId]` は項目処理の開始回数、`jobHistory` はserver側の更新履歴。

## 比較の限界

fixtureはメモリ上のserverと輸送失敗を模擬する。実サービスの永続化、認証、ACID、ネットワーク、
支援技術、全ブラウザーへの保証ではない。同じkeyへの副作用抑止はこのAPIが提供する契約であり、
実環境でも提供されるかは別途確認が必要。
このfixture自身を検査する `api.test.mjs` は、候補Skillの独立評価や非公開holdoutではない。
実装出力の比較テスト、結果、評価者の独立性は別の記録に残す。
