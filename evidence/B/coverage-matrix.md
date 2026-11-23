# SESSION B — coverage matrix

Base: `f5df625dbc577d6a3ca28e13ef09e39b135b4a6f`。確認日: 2026-11-23（Asia/Tokyo）。
「既存対応」は現行ファイルの静的確認、「追加」はこの変更セットの契約・手順・検査。
新しいUX原理を発見したという主張ではない。既知の知見を、入力から実行・検証へ接続した差分である。

| 原則・対象 | 既存対応 | 新規追加 | 根拠と検証 | 未解決・責務境界 |
|---|---|---|---|---|
| B01 目標・開始・完了 | C4の行動分解、K1-13完了表示 | actor/goal/entry/success predicate、journeyと今回taskの境界 | S01/S02/S17。flow必須項目とreceiptの実行検査 | 実利用者の目標・文脈は未観察。機能の採否はA |
| B02 状態・遷移 | G-06古い応答、G3履歴、K2画面と状態 | event/actor/guard/effect/feedback/preservation、到達性・行き止まり・循環・待機経路checker | S13/S16/S17と今回の形式化。booking/report、反例・回帰テスト | guardの充足性、環境の公平性、実APIの意味はgraphだけでは証明不能 |
| B03 入力・確認・送信 | native validation、Enter/submitter、draft、入力保持 | 入力→修正→確認の必要性判断→送信→確定を契約化 | S04/S05/S07/S18。人数境界・修正・連打の実行検査 | 確認画面は一律追加しない。実部品/支援技術はC |
| B04 戻る・閉じる・取消し・undo | C-04/K1-14/K5-09、dialogとfocus復帰 | ローカル破棄・通信中断・取消要求・取消ack・補償を分離 | S03/S14/S16。未送信取消し・取消ack・完了競合 | server取消し・補償APIの可否は適用先で確認 |
| B05 結果不明・安全な再試行 | rollback・repair・pending guardは既存 | definitive failureとunknown、同一key・照会・入力固定、未発見の扱い | S12。commit済/未commitの同じtimeoutを模擬 | productionのatomicity、key保持期間、payload同一性は別途契約が必要 |
| B06 非同期feedback | C-02/K5、optimistic templateのstatus/rollback | 受付・実行・完了を分離、期限後の選択、古い応答、測定可能な進捗 | S06/S08/S09/S10/S11/S15。pending/stale/progress検査 | ブラウザー・読み上げ・focusの実操作はblocked。数値時間閾値は普遍化しない |
| B07 エラー修復 | C2項目特定・入力保持・具体的説明 | validation/business/transport/unknown/auth等の分岐と戻り先・保持データ | S05/S16/S18。入力不正、確定失敗、照会失敗、poll失敗 | 認証切れ・権限変更は方法を記述したが、今回の実行fixtureには非搭載 |
| B08 中断・再訪・部分成功 | G3履歴、既存draft、修復原則 | task/job IDの再照会、確定結果保持、failed subset再試行、別jobのversion境界 | S04/S12/S16と編集推論。resume/partial/retry tests | 永続化・複数tab・複数端末・実際のreloadは未実行 |
| B09 不要操作・ループ | C4 walkthrough、K3情報量と移動回数 | 各操作の目的を明示し必要reviewを保持、通常/復帰経路の操作数とAPI回数を区別 | S02/S07/S13/S17。構造checkerとdecision log | 「最短クリックが最善」とはしない。実UI操作数・利用者時間は未測定 |
| B10 検証範囲・証跡 | 既存C3/C4/C5の独立点検・対照・観察 | B用の同条件2課題、生成input/outputのhash、正常/異常/境界trace、実行/未実行の分離 | S17/S19/S02、campaign運用要件。validation.mdとR-ASI receipt | 独立blind、秘密holdout、実browserの証拠不足。formal gateはHOLD |

## 明示的に実装しなかった領域

| 領域 | 扱い |
|---|---|
| 造形、配色、書体、構図、視覚的意図 | 既存Art Directionを保持。比較fixtureの視覚条件を固定した。美的評価の新規基準を追加しない |
| 機能統廃合、IA、サイト全体のnavigation | Aへの依存・所見として記録。Bが新機能を勝手に追加しない |
| component、token、responsive、WCAG全適合 | Cへ状態・event・通知時機・戻り先を渡す。DOM/browser未確認を適合PASSにしない |
| 横断的な評価尺度・正式昇格 | Dに検査結果と限界を渡す。印象語を不具合に使わない |
| 本番server、認証、分散transaction | fixtureはAPI契約のsimulation。production実装や保証と呼ばない |

## 現行treeで存在しなかった依頼対象

`findings.md`、`phase2-issues.md`、CAS、既存自動テストランナーはbase treeに非同梱。
過去に未実施・未修正とは断定していない。`data/typography/findings.csv` は別目的の現行資産。
詳細は [existing-audit.md](existing-audit.md)、原典は [source-index.md](source-index.md)、
今回の実測結果は [validation.md](validation.md) に分ける。
