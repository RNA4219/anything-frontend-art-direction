# 再現可能な評価設計

## 異なる二つのタスク

`fixtures/task-brief.md` に登録・通信失敗からの復帰と、依頼一覧・ページ移動後の絞り込みを定義する。
同一HTML・同一brief・同一入力を両条件へ与える。画面の実装を比較間で変更しない。
baselineはルートArt Direction、candidateはルートArt DirectionとDを使ってレビューする。
これはQAのレビュー能力の比較であり、UIそのもののBefore/After改善実験ではない。

## 実行順と隔離

1. baseline SHA、入力hash、モデル条件、評価対象と採点方法を凍結する。
2. fresh-contextのレビュー担当へ同一briefを渡し、参照できるSkillのみ変える。
3. レビュー担当にはoracle、他条件の答案、採点結果を渡さない。
4. raw答案を保存してhashを確定した後、第三の評価者へ条件名を伏せた答案を渡す。
5. 同一の検証済ケースへ対応付け、検出数、根拠の充足、誤検出、断定過剰、未確認の管理を比較する。
6. 順序反転・複数試行・保護されたholdoutが未実施なら一般的な改善を主張しない。

同じファイルシステムを共有するため、allowed pathsはプロンプトによる分離にとどまる。
別agentであることだけを独立Oracle・アクセス不能なholdoutと呼ばない。
実ブラウザが起動できない条件では双方を同じソースレビュー条件にそろえ、ブラウザ未検証を維持する。

## 反証と検出用ケース

`checks/exercise_fixture_logic.mjs` はHTML中の実scriptを最小DOMモデルで動かす。
正常登録・一覧移動、通信失敗、重複submit、ページ移動後のfilterを比較する。
宣言された入力範囲はソース検査まで。レイアウト、native validation、focus、読み上げは評価しない。
first-pageのfilterが動くこと、0件表示とクリア手段があることを反証ケースとして保持する。
意図的なserif見出し、角の形、紙色を欠陥扱いしない。

## ブラウザによる実行

`python3 extensions/D/checks/run_browser_checks.py --output evidence/D/browser-fixtures`

PlaywrightとChromiumが許可された環境で実行する。依存を暗黙installしない。
起動不可は`BLOCKED`、未実施は`not_run`、fixture上で再現した要求違反は`failed`にする。
正常・異常・境界の各ケースにスクリーンショットとstate traceを残す。
検査結果と保存物のhashを`qa_gate.py`で検証する。

## 結果の読み方

unit probeのPASSは検出器が既知の挙動を捉えた意味であり、製品のPASSではない。
比較結果が1回ずつのソースレビューだけなら、探索的な記述として扱う。
未保護の独立性、ブラウザ未確認、未計測費用を残したまま正式昇格はしない。
