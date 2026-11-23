# 共通controller実行比較

自己管理の模擬API検査。独立blind評価、ブラウザー検証、実利用者の完了率ではない。正式gate: **HOLD**。

| ケース | 分類 | 検査 | baseline | candidate |
|---|---|---|---|---|
| R01 | normal | 初期値と操作可能性 | pass | pass |
| R02 | normal | server receiptによる予約完了 | pass | pass |
| R03 | boundary | 人数下限1・上限8と文字列入力 | pass | pass |
| R04 | boundary | 範囲外・小数・空白を送信前に拒否 | pass | pass |
| R05 | error | 入力エラーから修正して完了 | pass | pass |
| R06 | boundary | 送信応答待ちの連打を抑止 | pass | pass |
| R07 | error | 確定失敗後の同一意図再試行 | pass | pass |
| R08 | error | 確定失敗後の編集は新しい送信意図 | pass | pass |
| R09 | error | 書込み済み応答不明を照会で解決 | pass | pass |
| R10 | error | 書込み済み応答不明を同一key再送 | pass | pass |
| R11 | error | 照会で未発見でも不明を維持して同一key再試行 | pass | pass |
| R12 | boundary | 送信中の取消しをserver取消済みにしない | pass | pass |
| R13 | boundary | 結果不明中の編集・取消しで意図を失わない | pass | pass |
| R14 | normal | 未送信の破棄と新しい編集の再開 | pass | pass |
| R15 | boundary | 完了後の連打は無効、新規編集は別予約 | pass | pass |
| R16 | error | 照会失敗でも入力と不明状態を保持 | pass | pass |
| R17 | boundary | 照会中の再押下・再送を抑止 | pass | pass |
| R18 | boundary | 返却snapshotの変更が内部状態に伝播しない | pass | pass |
| R19 | boundary | 送信中の編集を固定 | pass | pass |
| R20 | boundary | 初期状態のretry・reconcileは副作用なし | pass | pass |
| I01 | normal | 初期状態とjobなし操作 | pass | pass |
| I02 | boundary | 空選択・重複IDを開始前に拒否 | pass | pass |
| I03 | boundary | 開始応答待ちの重複起動と対象変更を抑止 | pass | pass |
| I04 | normal | 進捗と全件完了をserver結果から表示 | pass | pass |
| I05 | error | 部分失敗から失敗項目だけを再試行 | pass | pass |
| I06 | boundary | 部分再試行の応答待ち連打を抑止 | pass | pass |
| I07 | boundary | 取消応答待ち・成功保持・取消し確定 | pass | pass |
| I08 | boundary | 取消しと全件成功の競合は実結果を採用 | pass | pass |
| I09 | boundary | 取消し後の古いpollでrunningへ戻らない | pass | pass |
| I10 | error | poll失敗でも既知結果を保持し再取得 | pass | pass |
| I11 | normal | 再訪で既存jobと部分結果を復元し書込まない | pass | pass |
| I12 | error | 不存在jobの説明と正しいjobへの復帰 | pass | pass |
| I13 | error | 開始の確定失敗後に対象を保持して再開 | pass | pass |
| I14 | error | 開始結果不明を確定失敗にせずjobを重複生成しない | pass | pass |
| I15 | error | 取消し確定失敗を取消済みにせず復帰 | pass | pass |
| I16 | error | 取消し結果不明をpollで確定 | pass | pass |
| I17 | boundary | 成功後の再開始・取消し・再試行で副作用を追加しない | pass | pass |
| I18 | boundary | job・items・progressのsnapshotを独立させる | pass | pass |
| I19 | boundary | 別jobへの復帰でversion比較を混同しない | pass | pass |
| I20 | boundary | 既存job読込み中の状態と書込みゼロ | pass | pass |

## 集計

```json
{
  "baseline": {
    "reservation": {
      "pass": 20,
      "fail": 0,
      "not_run": 0
    },
    "import": {
      "pass": 20,
      "fail": 0,
      "not_run": 0
    },
    "all": {
      "pass": 40,
      "fail": 0,
      "not_run": 0
    }
  },
  "candidate": {
    "reservation": {
      "pass": 20,
      "fail": 0,
      "not_run": 0
    },
    "import": {
      "pass": 20,
      "fail": 0,
      "not_run": 0
    },
    "all": {
      "pass": 40,
      "fail": 0,
      "not_run": 0
    }
  }
}
```

各assertion、最終snapshot、API request/response・副作用回数はcomparison.jsonへ保存。
件数は選定したscenarioの結果であり、母集団の成功率やSkillの因果効果を推定しない。
I14は結果不明時の安全性だけを検査するため、復帰操作の存在は別レビューが必要。
