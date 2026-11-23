# SESSION D — 最終R-ASI証跡の追記

## Decision: HOLD

最終比較・匿名化した別コンテキストでの判定・ブラウザ検査器の修正・report再照合を、新しいsnapshotとexperienceとして追記した。既存の構成文書、CAS、初回experience、receiptは変更していない。正式な独立評価receiptや昇格は作成していない。

- Campaign: `anything-frontend-D-20261123`
- 新experience: `D-final-evidence-20261123-02`
- 依存する既存experience: `D-preliminary-evidence-20261123-01`
- 最終manifest: [external-evidence-final-v1.json](external-evidence-final-v1.json)
- Manifest SHA-256: `e7947ae096731d01991121da2499cd5abb60fe7be46bc40caa777f7e4e954bcc`
- 凍結artifact: **31件**。元パス・snapshotパス・実hash・byte数を記録。
- 新native receipt: [experience-add-a016ed193481cbe72a705f53dfa1bce646972b7fe13a88a3df66a1ae87d2686e.json](.ga/receipts/experience-add-a016ed193481cbe72a705f53dfa1bce646972b7fe13a88a3df66a1ae87d2686e.json)
- 詳細な機械可読結果: [final-recording-summary.json](final-recording-summary.json)

## 実行したこと

| 処理 | 実結果 | 意味 |
| --- | --- | --- |
| final-v1 snapshot作成 | exit 0 | 確定した31 artifactを新しい保存先へ凍結 |
| Dのartifact manifest verifier | exit 0、integrity_verified=true | 31件のpath・SHA-256・sizeが一致。quality_evaluated=false |
| R-ASI `experience-add` | exit 0 | 最終外部証拠とHOLDをnative経験レコードに保存 |
| 既存artifactの前後照合 | **35/35不変** | 初回snapshot、CAS、receipt、experience、costと関連原文を保持 |

実コマンド・stdout・stderr・終了値は `logs/final-snapshot-build.json`、`logs/final-manifest-integrity.json`、`logs/experience-final-v1.json` に保存した。保全の詳細は [final-preservation-result.json](final-preservation-result.json) にある。experienceの`active`は記録の有効状態であり、Skillの昇格ではない。

## 比較で観察した差

[最終比較](../evaluation/comparison.json)の結果を、その限界ごと経験記録へ保存した。

| 指標 | Baseline | Candidate |
| --- | ---: | ---: |
| 既知ケースの検出 | 3/3 | 3/3 |
| 指摘の6要素の記載 | 18/18 | 18/18 |
| 一次責務とownerの明示 | 0/3 | 3/3 |

検出能力の改善は示されていない。今回観察した差は、責務・owner、artifactとの結合、contract / target / promotionの分離である。両条件とも同一UIに対するレビューであり、製品UIの改善や人間のタスク成功率向上ではない。

匿名化した資料を別コンテキストで評価したが、共有OSのprompt allowlistであり、保護されたblind・非公開holdoutは成立していない。出力形式から手法を推測でき、各条件は1 trial、rubricはbaseline後に固定、正確なprovider版・sampling・費用も不明である。これらの条件を正式な独立評価へ読み替えず、HOLDを維持した。

## 検査器の修正と再照合

Dのブラウザ検査器について検出した3件を修正し、修正後8条件の合成stub検査を保存した。復帰時の人数・受付番号・件数、一覧のページ番号と行ID、cleanup失敗時の結果保全を扱う。実fixtureのブラウザは依然BLOCKEDで、stubの成功は実画面の合格ではない。

Portable replayでは11 artifactの相対パスを一時領域に復元し、元report bytesを変更せず、3 reportの既存判定とmanifest整合性を再現した。初回はreport自体をroot外から渡して契約拒否となり、その結果も削除せず凍結した。成功はartifactと契約の再照合であり、ブラウザ再実行や新たなLLM評価ではない。

## 現在の記録件数

| 記録 | 累計 | 今回追加 |
| --- | ---: | ---: |
| Native R-ASI receipt | 9 | 1 |
| R-ASI CLI観測ログ | 22 | 1 |
| 外部包装・整合性の観測ログ | 3 | 2 |
| JSONログ全体 | 25 | 3 |
| Experience | 2 | 1 |
| Cost event | 4 | 0 |
| Candidate CAS object | 1 | 0 |

初回の費用台帳は変更していない。最終CLIのwall timeは今回の実行ログにあり、token/USDの実測やCampaign総費用を推定してはいない。R-ASIのexecute/evaluate/promote未接続、runtime lockと評価policy未成立、未計測費用によるbudget判定不可も、初回の実行証跡どおりである。

一般artifactはhash manifestへ、R-ASIにはそのmanifestを`provenance.evidence_ref`として保存した。一般画像やログをcandidate専用CASへ偽装していない。以前の未取得状態は過去時点の記録として保持し、この最終版が比較完了後の観察を追加する。
