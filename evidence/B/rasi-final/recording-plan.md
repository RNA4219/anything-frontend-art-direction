# B 最終証跡の登録手順

この文書は準備段階で作成した登録契約と手順である。その後、最終Skill・実測結果を固定し、native `experience-add` を実行した。現在の観測結果は [registration-summary.md](registration-summary.md)、正確なhashとreceiptは [registration-summary.json](registration-summary.json) を正とする。formal gateは引き続き **HOLD**。下の「準備時点」「まだ実行していない」は、記録された準備工程の時点を指す。

## 1. 実際の experience-add 契約

確認した実装はR-ASI `f5b638085dece1f997210f9b653aceb8fe9b32d4`、`rasi/experience.py` の `validate_experience` / `add_experience` と `schemas/experience.schema.json`。

| 項目 | 実装が検査すること | このcampaignで付け加える確認 |
| --- | --- | --- |
| `schema` | `experience/v1` | 同じ |
| `experience_id` | 英数字から始まる英数字・`.`・`_`・`-`。保存先のID | 最終tree hashの短縮値と評価run番号を含む新しいIDを付ける |
| `content` | 非空文字列 | 実際の結果、評価条件、未検証事項、HOLDを記す |
| `provenance.campaign_id` / `evidence_ref` | 非空文字列のみ | `evidence_ref` の実在、参照先SHA-256、配下artifactのSHA-256を外部で確認する |
| `scope` | `task_family` / `skill_area` が文字列 | Bと2種類の代表タスクを明記する |
| `dependencies` | ID文字列配列。登録時は依存experienceの実在も確認 | 未登録のIDを作らない。今回は依存なしでよい |
| `status` | 構造上はactive/suspended/restored。新規追加はactiveのみ | activeは経験ストアへの登録状態。テストPASSや昇格を意味させない |
| `history` | action、ISO8601日時、reason、refs文字列配列 | 原稿作成、artifact固定、実測、登録を混同しない |

追加フィールドは許容される。ただし `provenance.evidence_sha256` や `implementation_tree_sha256` を付けても、R-ASIがそれらを実ファイルと照合するわけではない。今回の記録器が実bytesを照合した事実と実行ログを別に残す。

保存先は、rootが `evidence/B` の場合 `.ga/experiences/<id>.json`。同じIDと同一canonical bytesは再実行可能だが、同じIDで内容が違うと拒否される。登録後にファイルを直接上書きしない。新しい結果は新しいIDで記録する。

成功時のnative receiptは `.ga/receipts/experience-add-<receipt_sha256>.json` であり、payloadはID・status・依存数のみ。参照先の評価結果が正しいこと、独立していること、昇格してよいことは証明しない。

## 2. 混同しないidentity

| identity | 準備時点の値 / 状態 | 意味 |
| --- | --- | --- |
| baseline repository SHA | `f5df625dbc577d6a3ca28e13ef09e39b135b4a6f` | 比較元のArt Direction |
| generation input commit | `58bed659cc7f39d316794625ad0475084b38df7e` | 修正前に生成agentへ渡したB Skill |
| generation input tree SHA-256 | `1fba407c2a0452ad1f458c75bb6590cdc22e7c8a98bf04e2cc2554a317fb8ee5` | 12ファイルをcommit blobと照合済み |
| 最終Skill tree SHA-256 | null、修正後に確定 | `extensions/B` の実装内容。生成入力と異なれば両方を残す |
| evaluator SHA-256 | `e31b62a1edd0a95e765ddea89fc2ca8df43b31da39156e6345fda423babedd26` | 共有40 scenarioの実行器。準備時点でbytes一致を確認 |
| R-ASI descriptor content ID | `57d1b2372555c5493ab91e5ae679e2441581795c1998c1681fdc050b1abb7552` | sankai抽出指示を格納した候補記述の内部ID |
| R-ASI native CAS object SHA-256 | `5b35eb5daf879cffdb54114faa4b89af64b6094c008de756c49c4c1f8ed1da34` | 上記descriptorの保存bytes。Skill実装hashではない |

生成agentは修正前のSkillを読んでいる。後でcheckerやB10を修正しても、その修正版が既存の生成結果を生んだとは報告しない。生成に使った版の比較結果と、最終Skillに対するchecker回帰検証を分ける。

descriptorの `registered=false`、`promoted=false`、`execution_connected=false` 等はその固定形式の契約である。後にexperienceへ証拠を記録しても、このdescriptorを書き換えてtrueにしない。

## 3. 最終結果が届いてからの手順

1. 親が最終Skillを固定し、変更のない `extensions/B` の相対パス→ファイルSHA-256 mapを作る。生成時と同じcompact sorted JSONのSHA-256でtree identityを求める。metadata自身をhash対象へ含める循環は作らない。
2. 元の生成出力を保全し、baseline/candidateのartifact mapを別々に作る。生成後の修正があれば別revisionで記録する。最終Skillの修正を元出力へ遡及させない。
3. 最終Skillの機械検査、checker反例再検証、共有scenario比較、review解消、ブラウザの実行可否を、それぞれ元の結果ファイルのpath/hashで記録する。実行していない項目はnullと理由を残す。正常・異常・境界、対象数/成功数/失敗数を元ファイルと照合する。
4. `evaluation-evidence.template.json` から `evaluation-evidence.json` を作り、登録対象として固定する。各artifactのpath baseは `repository_root` または `evidence/B` と明記し、取り違えない。最終Skill commitと、その後の証跡commitは別概念なので自分自身のcommit SHAを捏造して埋めない。
5. `trial-history.json` のin_progress/plannedを実記録で更新する。初期試行、diagnostic修正、再検証、生成結果比較を別entryにする。試行回数はmodel生成の回数とassertion数を分離する。
6. `cost-history.json` に実測できた値だけ追加する。金額、正確なmodel revision、seed、token数が取得できなければnullを維持する。ステージ単位の11.86秒をcampaign全体の時間と扱わない。
7. `experience.template.json` から新IDの `experience.json` を作る。contentへ実結果と制約を記し、`provenance.evidence_ref` を `rasi-final/evaluation-evidence.json`、補助 `evidence_sha256` をその実bytesのSHA-256にする。`implementation_tree_sha256` は最終Skillの値にし、descriptor content IDは別欄のままにする。
8. 登録直前に参照manifestと全artifactのhashを再照合してから、native `experience-add` を実行する。stdout/stderr/終了コード/コマンドを `rasi-final/registration-cli.json` に保存する。成功後にnative保存recordとreceipt bytesを確認し、参照manifestのhashが登録前後で変化していないことを確認する。

```sh
PYTHONPATH=/absolute/path/to/R-ASI \
python -m rasi --root evidence/B experience-add \
  --experience rasi-final/experience.json
```

このnative commandは `evidence/B/.ga` に書き込む。現在の準備作業は `rasi-final` への記録とread-only構造確認のみで、このコマンドはまだ実行していない。

## 4. 費用・試行履歴の扱い

[trial-history.json](trial-history.json) は準備時点の状態を保存している。[cost-history.json](cost-history.json) は実測済みの限定値と取得不能な量を分けている。

Native `cost-event/v1` は `measured=false` でも数値 `amount_raw` を必須にする。未知の費用を0として流し込まない。さらに現campaignのcost_settingsは未設定なので、今回のnullを許す外部記録をnative cost ledgerと称さない。費用上限・換算規則・実測値が実在する場合にだけ別途native登録を行う。

## 5. 準備段階で行った確認

[preparation-check.json](preparation-check.json) に以下を記録した。

- experience templateに対するread-only `rasi.experience.validate_experience` の構造確認。
- generation inputの12ファイルと固定commit blobの照合。
- evaluator bytesと凍結hashの一致。
- descriptorのnative CAS bytesとSHA-256の一致。

構造確認は、存在しない `evidence_ref` でも通る契約である。したがってこの確認結果を最終証拠の保存成功、実装テスト成功、独立評価成功と読み替えない。最終のhash・テスト結果が届くまで **HOLD** を維持する。
