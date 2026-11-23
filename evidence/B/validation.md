# SESSION B — validation

## 判定

**HOLD。** Skill実装、原典の対応付け、実行可能な検査、2課題の同条件比較、R-ASIで利用可能な範囲の証跡化を実施した。
共有40ケースはbaselineとcandidateの双方が40/40であり、追加Skillによる成績向上は確認できていない。
独立blind評価、実ブラウザー操作、正確なmodel revision/seed等が不足するため、正式PASS・昇格とは扱わない。

確認日: 2026-11-23（Asia/Tokyo）。ログ中のISO日時は明記されたUTC。

## 版と入力の固定

| 対象 | 固定値・証拠 |
|---|---|
| 現行Art Direction baseline | `f5df625dbc577d6a3ca28e13ef09e39b135b4a6f` |
| 生成に使用したB初版 | commit `58bed659cc7f39d316794625ad0475084b38df7e`、tree `1fba407c2a0452ad1f458c75bb6590cdc22e7c8a98bf04e2cc2554a317fb8ee5` |
| 診断修正後の最終B | commit `6fc0c3dd6c82c4dd2f77764c5da512fbfdbaa911`、tree `62f6f5075ca97e48a4d811d6039cd27ce2488425915e1bd4c41a62da6619d1bf` |
| 初回提出物 | `experiments/baseline-submission.json`、`candidate-submission.json`。baseline 8ファイル、candidate 16ファイル |
| 共通要件・入力 | `experiments/shared/tasks.md`、`visual-lock.md`、`api.mjs`。両条件で同一bytes |
| 生成条件 | 新規agentを各条件に1つ。同じ継承モデル・effortを指定。exact revision/seed/temperatureは非公開・未取得 |
| 実行条件 | 保存されたcontrollerをNode v24.22.3と同一のメモリ内APIで検査。Python 3.12.14 |
| 比較検査 | 生成物を読む前に `experiments/evaluate.mjs` を40ケースで固定。hashは `evaluator-freeze.json` |

初回提出物は各生成agentの自己確認後の提出である。提出前の内部編集を全て別trialとして記録したわけではない。
共有評価の結果は生成agentへ渡しておらず、提出後のcontrollerを修理・置換していない。
生成プロンプトは利用可能なSkillと出力先だけを変えた。両方に同じAPI・入力境界・失敗条件を明示した。
Skill初版と最終版は別identityであり、初版から生成されたコードの成績を最終修正版の効果と呼ばない。

## 実行結果

| 検査 | 結果 | 証拠と意味 |
|---|---|---|
| Skill frontmatter | valid | skill-creatorのquick_validate.pyで確認。呼出ルーティングの自動登録とは別 |
| 同梱checker unit tests | **70/70** | `runs/final/flow-unit.log`。67既存ケースに診断反例・正常経路3ケースを追加 |
| 同梱Flow fixture | **2/2** | `runs/final/booking-contract.log`、`report-contract.log` |
| 模擬API自己テスト | **9/9** | `runs/final/api-selftest.log`。simulationのkey、取消ack、部分結果等を確認 |
| 共通controller比較 | **baseline 40/40、candidate 40/40** | `experiments/results/first-submission/comparison.json`。両条件合計80実行、固有scenarioは40 |
| 保存コードの最終再実行 | **双方40/40** | `runs/final/comparison/`。新たなLLM生成ではない |
| candidateのFlow JSON | **2/2** | `runs/final/candidate-flow-revalidation.json`。修正版checkerでも構造整合 |
| パッケージ構造 | **10原則、59ローカルリンク、19原典参照に欠落なし** | `runs/final/run.json`。外部URLの可用性や主張の正しさの再検証ではない |
| 原文抜粋照合 | **19/19** | `research/quote-check.json`。imozuru report.py --checkによるweb抽出cacheとの一致 |
| 別agentによる診断追確認 | **2所見解消、限定回帰5/5** | `review/resolution-review.md`。独立blindや正式昇格ではない |
| Browser・keyboard・viewport | **blocked / not_run** | `experiments/browser-blocker.md`。実画面・スクリーンショット証拠なし |

### 正常・異常・境界の内訳

| 課題 | normal | error | boundary | baseline | candidate |
|---|---|---|---|---|---|
| 予約 | 3 | 7 | 10 | 20/20 | 20/20 |
| 在庫取込み | 3 | 7 | 10 | 20/20 | 20/20 |

予約は、入力境界・修正・二重押下・確定失敗・commit済/未commitの同じtimeout・照会・同一key再試行・未送信破棄を扱う。
在庫取込みは、進捗・部分失敗・失敗subset再試行・取消ack・完了との競合・古いpoll・既存jobへの復帰を扱う。
各ケースは期待assertion、途中/最終snapshot、API request/response、書込み・実作成数をJSONに保存した。

I14は結果不明時の安全性を主assertionとしており、UI上の復帰操作発見性を証明しない。
実際のtraceでは双方とも同一keyによる再開始後にrunningへ進み、作成job数は1だった。
controller操作回数とAPI呼出回数を実UIのクリック数へ読み替えない。利用者の所要時間・完了率は未測定。

### 比較の解釈

- 成功ケース差は **0/40**。一つの生成提出/条件、選定した2課題での結果であり、効果量・統計的優越・全製品への一般化を主張しない。
- baselineにも詳細要件と既存の回復・入力保持・非同期原則がある。これを削って弱いbaselineを作っていない。
- candidateには明示的なtask/operation/transition/scenario契約が出力された。この成果物の存在は確認できるが、設計者の作業時間短縮・実利用者の理解改善は測定していない。
- baseline/candidateの独自自己テストは36件/23件と内容が異なるため、これらの件数を品質比較に使わない。共通評価40ケースだけを比較する。
- candidateのHTTP simulation自己テストは片側の補助実装の確認であり、共通比較やブラウザー操作の代用にしない。両デモの輸送・保存方式の差は、今回のcontroller比較の対象外。
- agentへ相手の出力・評価ファイルを読まない指示を与えたが、共有filesystemは強制された秘密境界ではない。独立oracle/非公開holdoutは存在せず、正式昇格はHOLD。

## 診断で見つかった問題と修正履歴

| ID・段階 | 観察 | 修正・検証 |
|---|---|---|
| B-REV-01 / checker | timeoutからrecovery/taskを経て同じwaitへ戻る反例2件を初版がpassとした | user/timerでterminalへ至るまで探索。両反例は最終版でexit1、WAIT_TIMEOUT_STUCK。正常fixtureはpass |
| B-REV-02 / workflow | 通常の1task修正にも2課題比較・R-ASI・独立評価が必須と読めた | 通常利用と比較・正式昇格の入力/出力/依存を分離。小修正の不要な待ちを除去 |
| 回帰テスト追加時 | 最初のpositive testに存在しないtransition ID `leave_before`を記載し69/70 | 実fixtureの `leave`へ修正し70/70。checkerを弱めて通した修正ではない |
| 最終追確認 | 別agentは元反例と正常fixture、関連5テスト、B10境界だけを再確認 | `review/resolution-check-results.json`、対象hashはresolution-snapshot.json |

初版67/67でも上記反例を検出できなかったことを隠さない。初版レビューと修正後の結果を別ファイルに保存した。
初版保存前の開発では、深いJSONのdecode失敗を一律期待したテストが1件失敗し66/67だったとの作成agent報告がある。
処理系差を許しつつ適切な診断・no tracebackを確かめるテストへ直して67/67とした。初回raw log・当時のbytesは未保存であり、この履歴はauthor-reportedとして主証拠の最終実測と区別する。
元レビューの1,947 shape probeはその場のhere-document実行でcase別logはなかった。コードを
`review/shape-probe-replay.py`へ復元したが、最終版での再実行とは数えていない。

最終checkerも自然言語guardの充足性、実APIの保証、局所systemイベントと外部応答の区別を自動証明しない。
正当な退出が局所system遷移に依存する場合は保守的に指摘し、actorを偽らず実装traceと手動レビューで扱う。

## 責務ごとの評価範囲

| 分類 | 今回の扱い |
|---|---|
| 機能設計 | 同じ要件・機能を固定。機能の採否や市場適合を評価したわけではない。Aへ引継ぎ |
| 情報構造 | 同じ2領域・入力内容を固定。サイト全体IAやnavigationの包括評価は対象外 |
| インタラクション | 正常/異常/境界のcontroller挙動、開始・完了・復帰・取消し・状態後退を実行検査 |
| 視覚設計 | 固定色・書体・基本構成を入力条件にした。実描画や美的優劣は未評価 |
| 実装 | checker・schema・snapshot・mock API・controllerを実行検査。DOMとcomponentの対応、支援技術、本番APIは未確認 |

レビュー所見は位置・症状・根拠・影響・修正方向・再現を持つ。題材や文体の好み、印象語を不具合判定に使っていない。

## 原典と3ツールの実行範囲

**18有効原典・19参照箇所。** S17/S19は同一書籍の別章として1原典に数えた。既存のWCAG等も再確認したもので、18件すべてを新発見と数えていない。
URL、資料名、該当箇所、確認日、原典の主張、適用上の推論、確信度はsource-index / sources.json / 同梱sourcesに対応付けた。

| ツール | 実際に実施したこと | 限界 |
|---|---|---|
| imozuru | 2経路の原典探索、リンク追跡、map更新、fetch.pyの18試行、19抜粋の照合 | fetchは全件DNS失敗。許可されたweb検索サービスのopen/click抽出を利用。cache hashは原HTTP bytesではない |
| sankai | 現行資産と根拠をB01〜B10へ分解し、条件/入力/判断/例外/依存/失敗/検証/確信度を保存 | 分解をSkill実装完了や実行・独立評価と扱わない。再構成・実装は本campaignで別に実施 |
| R-ASI 0.0.2 | 現行CLI/contract確認、verify→pipeline→cas-verify、外部実装/評価証拠のexperience登録 | native CASはcandidate descriptor用。execute/evaluate/promoteは未接続。本文の実装hashとdescriptor IDは別identity |

R-ASIの実コマンド、receiptと最終evidence参照は `rasi/`、`rasi-final/`、`.ga/receipts/`、`tooling.md` に保存する。
R-ASIのquote照合対象はcampaign入力snapshotであり、外部原典の独立な真偽判定ではない。
上流R-ASIの既存テストは147成功・2失敗。深いJSONのエラー文期待の2件で、CLIは両方exit2で拒否しtraceback無し。
原因がruntime差であるという仮説は未検証であり、上流sourceを変更していない。

## Browser阻害と正式Gate

通常のPlaywright起動は既存Chromiumでsocketエラー、Browser connectorはoriginating context不足、
CUAのfile URLはURLポリシーで拒否された。禁止された間接ナビゲーションやsandbox無効化は行わなかった。
HTTP simulationのAPI確認を実browser検証に読み替えず、keyboard・viewport・読み上げ・スクリーンショットは未実行として残す。

formal HOLDの理由は、独立blind/holdout不在、browser証拠不足、exact model/seed・runtime OCI identity・calibration・cost policyの不足、
そして今回の比較で追加効果が未立証であること。構造検査のpassやR-ASI receiptの存在で昇格しない。

## 再実行

repo rootから、新しい保存先を指定する。

```sh
PYTHONDONTWRITEBYTECODE=1 python evidence/B/validate.py --out /tmp/anything-B-recheck-01
```

保存済みcontroller・fixture・checkerを実行する。生成モデルを同じseedで再現するコマンドではない。
実行日時・生成request key等によりtraceのbytesは変わり得る。判定assertionと入力artifactを固定して挙動を再確認する。
金額・token数は取得不能でnull。自己確認、共通比較、診断修正、最終再実行をtrial-historyで分ける。
