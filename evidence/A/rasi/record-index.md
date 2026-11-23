# SESSION A — R-ASI実記録

Campaign正本ID: `anything-frontend-design-engineering-A-20261123`。
初回R-ASI記録の `anything-frontend-A-20261123` は同じSESSION Aの短縮aliasである。
[識別子対応](campaign-aliases.json)に対応を保存し、過去receipt・experience・CASのbytesは変更していない。

- [discovery-manifest.json](discovery-manifest.json): コンポーネントrevision、実行環境、取得照合の結果。
- [run-log.jsonl](run-log.jsonl): 実際のコマンド、stdout、stderr、終了コード。privateソースの絶対パスは記録しない。
- [inputs/tool-discovery.json](inputs/tool-discovery.json): discovery観察を記録するexperience入力。
- `.ga/experiences/`: R-ASIが実際に生成したexperience記録。
- `.ga/receipts/`: R-ASIが実際に生成した成功receipt。

`execute`、`evaluate`、`promote`は未接続のexit 3。失敗receiptは生成されないため、外部実行ログに終了コードを残す。baseline/candidateの設計成果物と独立評価は外部実行器の責務。R-ASIの記録があることを独立評価成立と扱わない。

## sankaiからCASへの実記録（v1履歴）

[sankai-cas-manifest.json](sankai-cas-manifest.json)に元文書・変換入力・receipt・CASの実hashを保存した。

| 実コマンド | 結果 | 確認した範囲 |
|---|---|---|
| `verify --sankai inputs/sankai.json` | exit 0 | 元bytesのSHA-256、117行、10単位、共通条件・未確定事項、引用の行範囲と文字列 |
| `pipeline --sankai inputs/sankai.json --store cas` | exit 0 | 未昇格candidateへの変換、CAS格納と内部再検証 |
| `cas-verify --sha256 13490c4a8a88f17c7d3a546dc26dbd91f66ed94aa1dd7e45bf81a0dec97eddb8 --store cas` | exit 0 | 格納bytesとhash、canonical JSON、candidate構造 |
| `experience-add --experience inputs/sankai-cas-experience.json` | exit 0 | 実観察とmanifest参照をR-ASIへ記録 |

変換元は `evidence/A/sankai-extraction.md` の同一bytes snapshotであり、原典本文ではない。エージェントが編集した知識分解結果として扱う。各unitの本文を保持し、入力内で合成されたラベルも保持した。元文書に独立した成果定義がない箇所の`outputs`は空配列で、推測して補っていない。

v1の`skill_revision`は実在するローカル実装commit `8181f6bbac7013ba5a7563d6a87e740ccb3ee3ca`。公開commitとの[tree同一性mapping](publication-mapping.json)を別記録にし、この入力とCASは遡及編集していない。

CAS candidateは `quarantined` / `UNTRUSTED_CANDIDATE`、`promoted=false`。**形式・整合性検証の成功であり、原典の主張の正しさ、設計品質、実利用上の有効性、独立評価の合格ではない。** 実行・評価・昇格は未接続のまま。このv1記録時点では外部試験の最終manifest待ちで、正式判断はHOLDだった。最終の外部結果は以下に追記した。

## 公開revisionへ対応した現在の記録（published-v2）

公開commit `97b19c29c0b63acfee9ad437f93af081ac0c6ef8` とローカルv1 commitについて、`git show -s --format=%T`を実行し、tree `9263d9eef085eb4678acab70fbd077986b7f7f20` が完全一致することを確認した。元の117行・10単位の内容は変えず、[published-v2入力](inputs/sankai-published-v2.json)の`skill_revision`を公開commitへ対応させた。

この入力で`verify`、`pipeline`、`cas-verify`、`experience-add`を実行し、すべてexit 0。現在のCAS SHA-256は **`890dad5d012d5bf7dc063d78e404014cfedd91b5522dbe1bb447578e3842426d`**。完全なhashとreceipt参照は[sankai-cas-published-manifest.json](sankai-cas-published-manifest.json)にある。

ブラウザ検証は環境制約で未実施。独立評価・利用者試験は未完了。候補の正式判断は引き続きHOLDであり、CAS検証の成功を昇格に読み替えない。

現在の入力を再実行:

```bash
PYTHONPATH="$RASI_SOURCE" python3 -m rasi --root evidence/A/rasi verify --sankai inputs/sankai-published-v2.json
PYTHONPATH="$RASI_SOURCE" python3 -m rasi --root evidence/A/rasi pipeline --sankai inputs/sankai-published-v2.json --store cas
PYTHONPATH="$RASI_SOURCE" python3 -m rasi --root evidence/A/rasi cas-verify --sha256 890dad5d012d5bf7dc063d78e404014cfedd91b5522dbe1bb447578e3842426d --store cas
```

## 最終の外部実験を取り込んだ記録

[外部実験manifest](../external-experiment-manifest.json)のSHA-256 **`3e5e62557578b74966c5492e1ead06c639f5262ef576570b210bdad36f135fcc`** を実bytesで照合した。列挙された97 artifactすべてのhash・サイズが一致し、凍結された4 planのhashも一致した。同一bytesの[manifest snapshot](inputs/external-experiment.snapshot.json)を保持し、[取込検証結果](external-experiment-ingestion.json)へ照合結果を保存した。

| 確認対象 | 実結果 | 解釈の限界 |
|---|---|---|
| validator v3の実行ログ | 40/40テスト成功、checker SHA `de5abbc23d003e5401830d6776bb043b21ee3912f82291389081068a98893e68` と一致 | 外部の実行ログを照合。取込時にテストを再実行したとは扱わない |
| 4 plan | すべて構造error 0 | 宣言された契約の整合性。実装・実利用の成功率ではない |
| course-catalog | baseline HOLD、candidateの機械status PASS | candidateの未解決blockingフラグ0を表す。提供・昇格PASSではない |
| support-triage | baseline HOLD、candidate HOLD | 入力の業務条件に未解決事項が残る |
| ラベルを伏せたモデルレビュー | 2ケースとも同等 | 独立Oracle・非公開holdout・利用者試験ではない |
| ブラウザ | 未実施、スクリーンショット0 | Chromium socket EPERM、Browserのoriginating contextなし、Cloud file URL不可。迂回なし |

生成は初回公開revision `97b19c29c0b63acfee9ad437f93af081ac0c6ef8` で各arm1回、各2ケース。raw planは不変。生成後のchecker修正・status文書明確化は外部manifestが参照する `post-generation-changes.json` に記録されている。blockingフラグ件数の違いを品質改善率に換算していない。

`experience-add --experience inputs/external-experiment-experience.json` を実際に実行し、exit 0。生成された[receipt](.ga/receipts/experience-add-c118c4bda390a77bb5ed4046379e036bc5882cee261257857b4bfdaff8570114.json)と[experience](.ga/experiences/A-external-experiment-20261123-final-v1.json)はCampaign正本IDを使用する。過去のalias記録は同一Campaignの履歴として維持した。成功receiptは合計10件、すべて実bytesと名前のhash一致を確認した。

費用、token数、runtime image digest、具体的なmodel識別子・sampling設定は未知。費用budgetや形式的なCampaign gateを成功扱いしていない。**正式判断はHOLD、昇格なし。** R-ASIが担当したのは実証跡の取込・整合性検証・CAS・receipt保存である。

再実行:

```bash
PYTHONPATH="$RASI_SOURCE" python3 -m rasi --root evidence/A/rasi experience-add --experience inputs/external-experiment-experience.json
```
