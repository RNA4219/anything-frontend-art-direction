# SESSION A — R-ASI実記録

Campaign識別子: `anything-frontend-A-20261123`

- [discovery-manifest.json](discovery-manifest.json): コンポーネントrevision、実行環境、取得照合の結果。
- [run-log.jsonl](run-log.jsonl): 実際のコマンド、stdout、stderr、終了コード。privateソースの絶対パスは記録しない。
- [inputs/tool-discovery.json](inputs/tool-discovery.json): discovery観察を記録するexperience入力。
- `.ga/experiences/`: R-ASIが実際に生成したexperience記録。
- `.ga/receipts/`: R-ASIが実際に生成した成功receipt。

`execute`、`evaluate`、`promote`は未接続のexit 3。失敗receiptは生成されないため、外部実行ログに終了コードを残す。baseline/candidateの設計成果物と独立評価は外部実行器の責務。R-ASIの記録があることを独立評価成立と扱わない。

現段階: tool discovery完了、設計成果物・外部試験の追記待ち。正式昇格は未実施。
