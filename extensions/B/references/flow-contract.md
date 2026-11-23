# Flow output contract — ux-flow/v1

この契約はタスクを状態・イベント・結果へ変換するためのもの。画面一覧、画面の美しさ、自然言語guardの正しさを自動証明しない。

## 必須成果物

1. **Task contract**: actor、goal、開始条件、完了を観察するpredicate、サービス/権限の前提、離脱条件を短く記す。調査済みのjourneyと推測したjourneyを区別する。
2. **Flow JSON**: 下記形式で保存する。ユーザー操作とシステムイベントを混ぜない。
3. **Decision log**: 原則ID、入力、採用/不採用、例外、原典ID、残る不明点を1判断1行で記す。
4. **Test traces**: 正常・異常・境界の操作列、期待状態、実際の表示/サーバー結果、検証方法、証拠パスを残す。未実行は `not_run` とする。

## JSON fields

```json
{
  "schema": "ux-flow/v1",
  "id": "task-name",
  "actor": "利用者",
  "goal": "観察可能な目的",
  "entry_condition": "開始前に成立していること",
  "entry_state": "edit",
  "success_predicate": "成功を示す具体的な事実",
  "assumptions": ["API仕様で確認済みの前提。または未確認と明記"],
  "operations": [],
  "states": [],
  "transitions": [],
  "scenarios": []
}
```

| Field | Contract |
|---|---|
| `states[].id` | 空でない一意のID。画面IDと同じである必要はない。 |
| `states[].kind` | `task`, `wait`, `recovery`, `success`, `exit` のいずれか。 |
| `states[].description` | 利用者が何をでき、何が確定しているか。 |
| `states[].proof` | `success` に必須。receipt、保存済みversion、読取結果などの観察対象。 |
| `states[].reason` | `exit` に必須。未完了の理由と次の手段。exitを成功率へ加えない。 |
| `states[].operation` | `wait` に必須。`operations[].id` を参照。 |
| `states[].timeout_event` | `wait` に必須。有限な待機判断を生む `timer` 遷移のevent。固定秒数を普遍規則にしない。 |
| `states[].wait_policy` | `wait` に必須。応答期限・再確認方法・利用者の待機解除/退出を説明。 |
| `transitions[].id` | 一意のID。テストtraceから参照する。 |
| `transitions[].from`, `to` | 実在state ID。 |
| `transitions[].event` | 操作/応答/期限などの発火条件。 |
| `transitions[].actor` | `user`, `system`, `timer`。 |
| `transitions[].guard` | 空でない条件。無条件は `always`。自然言語をevalしない。 |
| `transitions[].effect` | `none`, `local`, `server_write`, `reconcile`, `server_cancel`, `compensate`。 |
| `transitions[].operation` | server系effectでは必須。定義済みoperationを参照する。 |
| `transitions[].feedback` | 利用者へ伝える結果。通知不要なら理由も文字列で記す。 |
| `transitions[].preserves` | 保持する入力・文脈の配列。不要なら空配列にし、decision logで理由を記す。 |
| `operations[].id` | 一意のoperation ID。 |
| `operations[].side_effect` | `read` または `write`。 |
| `operations[].retry` | `safe_read`, `same_key`, `reconcile_first`, `never`。writeに `safe_read` を使用しない。 |
| `operations[].idempotency` | `server_key`, `inherent`, `none`。宣言だけでバックエンド保証があるとは扱わない。 |
| `operations[].outcome_lookup` | boolean。受理結果を調べられるAPIが実在するか。 |
| `operations[].cancel` | `server_confirmed`, `local_only`, `unavailable`。 |
| `operations[].stale_response` | 古い応答・取消し後の応答を識別して扱う方法。 |
| `operations[].contract_evidence` | API契約/コード/未確認事項の場所。 |
| `scenarios[].id` | 一意のID。 |
| `scenarios[].category` | `normal`, `error`, `boundary`。最低各1件。 |
| `scenarios[].path` | entry_stateから辿るtransition IDの配列。空配列は許可しない。 |
| `scenarios[].expected_state` | traceの最終state。 |
| `scenarios[].assertions` | UI/データ/回数/保持値を検査する空でない文字列配列。 |

## 機械検査と人の確認を分ける

`python checks/check_flow.py flow.json` は構造、参照整合性、到達不能状態、終了へ到達しない状態、出口のない待機、成功条件、危険なretry宣言、traceの連続性を検査する。`--json` で結果をJSONにする。

成功・離脱stateはこのタスクの終端とする。最低1つのsuccessを定義し、entryから到達可能にする。全exitしか設計できない場合は、目的未達の阻害要因を記してHOLDにする。その後の別タスクは別contractへ渡す。修正のための循環は許すが、成功または説明付き離脱へ抜ける経路を持たせる。到達可能でもguardが両立しなければ利用者は進めない。checkerが成功しても、guard充足性、APIの冪等性、操作の発見しやすさ、実ユーザーの完了性は未証明である。

`wait` はsystem応答経路と、指定したtimeout_eventを使うtimer経路を必須とする。timeout先からuser/timerの遷移だけでsuccessまたは説明付きexitへ抜ける経路を検査する。途中にtask/recoveryを挟んでも、またwaitへ戻るだけなら退出可能とは扱わない。待機継続・照会だけでなく、未確定作業の状態を説明して待機を終える経路を設計する。画面を退出してもserver処理の取消し完了とは限らない。タイマーは通信や処理が失敗した証明ではない。

この限定検査では、ローカルなsystemイベントと外部サービスの応答を区別できない。正当な退出経路がローカルsystem遷移を必要とする場合も自動判定は通らないことがある。その場合はactorを偽って通さず、未解決の判定として実装traceを添えてレビューする。guardの充足性・実API・実行時の進行保証は引き続き別検証である。

同じfrom/event/actorの分岐は、guardを相互排他的かつ必要な入力域を覆う形に設計する。同じguardを重複して記した遷移は検査エラー。異なるguardの完全性・排他性はレビューと実行例で確認する。

`same_key` はserverの冪等性保証があり、キーの範囲・payload固定・期限・異payload衝突の契約を確認できた場合だけ使う。`reconcile_first` はoutcome_lookupがtrueの場合だけ使う。どちらもなければ `never` として、手動確認などの回復経路を設ける。送信ボタンのdisableはサーバーの重複防止を証明しない。

## 指摘の形式

`ID / 分類 / 位置(state・transition・画面要素) / 再現入力と手順 / 観察 / 期待と根拠 / 影響 / 修正方向 / 検証状態` を残す。分類は `functional`, `information`, `interaction`, `visual`, `implementation`。本文の好みを欠陥にしない。文字量・ラベル・欠落が操作に影響したときは、影響を再現して責務を示す。
