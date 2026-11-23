# Design QA 検証コードレビュー

## 結論

**修正前のブラウザrunnerに、誤った受入2件と結果保存の欠落1件を再現し、その後の修正版で3件の再発防止をsynthetic probeにより確認した。** `qa_gate.py` の既存56件の単体テストは成功した。今回確認した範囲では、JSONゲートについて追加の重大な誤受入を再現していない。

本レビューとproofはコードの判定・制御フローの確認であり、実UIの品質判定ではない。ブラウザは起動しておらず、実fixtureの動作は未確認。receiptの真正性と評価者の実際の独立性は、指定どおり対象外とした。

## R1 — 復帰ケースが入力保持の一部だけで成功する（中）

- 対象: `extensions/D/checks/run_browser_checks.py` 修正前75〜84行。
- 原因: `registration-failure-recovery` は通信失敗後のname/emailだけで `requirement_met` を決める。seatsは取得するが比較せず、再試行・受付完了・重複登録の有無も確認しない。
- 再現: 名前とメールは保持、seatsは空、状態は「通信失敗。再試行不能」を返すstubで、`requirement_met=true`。記録したsubmitは1回だけだった。
- 影響: 人数が消える、または失敗後に再登録できない実装でも、この復帰ケースの判定を通過し得る。`evaluation-protocol.md` のerrorケースが求める入力保持・復帰後終端をカバーしない。
- 最小修正: 3入力すべての保持を確認し、失敗スイッチを解除したうえで再送する。受付結果とcount=1まで観察する。入力保持と復帰完了は個別の結果として残す。

## R2 — ページ送りが無効でも正常ケースが成功する（中）

- 対象: 同runner修正前127〜136行。
- 原因: `requests-normal` で「次へ」を押した後、合否は `row_count == 3` だけで決まる。取得済みのpage表示を判定に使わず、行IDも照合しない。
- 再現: 次へボタンを完全なno-opにし、初期ページ表示 `1 / 2` と行数3を返すstubで、`requirement_met=true`。
- 影響: ページが進まない、または同じ3行を再描画する不具合を取りこぼす。行数はページ遷移や目的の情報への到達を証明しない。
- 最小修正: クリック前後のページと、期待する次ページの安定した行ID集合を照合する。filterケースも件数だけでなく対象行の属性・IDを確認する。

## R3 — 終了処理の例外で結果JSONが保存されない（中）

- 対象: 同runner修正前153〜159行。
- 原因: 外側 `finally` の先頭で `browser.close()` と `pw.stop()` を例外処理せず実行し、その後で `result.json` を保存する。
- 再現: `browser.close()` だけが `RuntimeError` を送出するstubを本体のfinallyへ渡すと、例外が外へ伝播し、`result.json` は存在しなかった。
- 影響: 接続断等の終了処理失敗で、すでに観察した各ケースの結果も永続化されず、規定のBLOCKED/終了コード2の報告に到達しない。
- 最小修正: close/stopを個別に保護し、例外を `cleanup_errors` へ追記する。保存処理は両cleanupの成否にかかわらず実行する。cleanup失敗は全体BLOCKEDとして保持し、既存ケースの観察結果を消さない。

## 検証と追跡

- `python3 extensions/D/tests/test_gate.py`: 56 tests、成功、終了コード0。これは契約コードの単体試験であり、UI品質のPASSではない。
- [probe_runner.py](gate-review/probe_runner.py): 許可されたrunnerソースからASTを抽出し、上記3箇所をsynthetic stubで実行。外部パッケージ・実ブラウザは使わない。修正前の行番号を固定した再現用である。修正後は保存済み `runner-before.py` を入力に固定した。
- [probe-results.json](gate-review/probe-results.json): 3件の再現結果。実行コマンドは `python3 evidence/D/gate-review/probe_runner.py`、終了コード0。この0は3件の欠陥の再現に成功したことだけを表す。
- 対象の依存関係不足を追加で確定する証拠は得ていない。Playwright/Chromium不足はrunner自身がBLOCKEDを返す設計であり、それだけでは欠陥に数えない。

## 修正後の再レビュー

root担当がrunnerを修正した後、同じ失敗条件をcurrent runnerのASTへ再適用した。結果は次のとおり。

| 対象 | 再確認した条件 | 判定 |
| --- | --- | --- |
| R1 | seats消失、再試行後のcount=2、人数が1名のreceipt | すべて `requirement_met=false` |
| R1 | 3値保持、失敗後count=0、再送後count=1・2名・C-001 | synthetic条件ではtrue。submitが2回、受付状態の待機が実行された |
| R2 | nextがno-op、ページ表示だけ2ページ目で行IDは初期のまま | どちらもfalse |
| R2 | 2 / 3、8件、R-104/R-105/R-106 | synthetic条件ではtrue |
| R3 | trace/context/browser/Playwrightの終了処理がすべて例外 | BLOCKEDのresult.jsonが保存され、4箇所のcleanup errorと既存の観察内容を保持 |

[probe_runner_postfix.py](gate-review/probe_runner_postfix.py) と [postfix-results.json](gate-review/postfix-results.json) に8条件の記録を保存した。`python3 evidence/D/gate-review/probe_runner_postfix.py` は終了コード0。修正版のSHA-256は同JSONの `runner_sha256` に固定している。

**3件は検査ロジックの修正として確認済み。実fixtureがブラウザで受入条件を満たすかは未確認のままである。** DOM API・trace保存・画面描画・タイミングの実動作について、stubの成功を代替証拠にしない。

閲覧した範囲は `qa_gate.py`、`run_browser_checks.py`、`tests/test_gate.py`、`report-contract.md`、`evaluation-protocol.md` の5ファイルと、その後に指定された修正前runnerの保存版・自作proof。baseline/candidateのレビュー出力、事前oracle、fixture本体は閲覧していない。レビュー担当は実装とgitを変更していない。
