# B 最終外部証拠 — R-ASI記録結果

**native `experience-add` はexit 0で完了した。正式昇格の判断はHOLDのまま。** 実際のSkill実行・比較評価は外部実行器で行い、R-ASIにはその参照とhashを持つexperienceを保存した。

## 記録先

- Experience ID: `B-UXFLOW-20261123-62f6f5075ca9-r1`
- Native record: `../.ga/experiences/B-UXFLOW-20261123-62f6f5075ca9-r1.json`
- Native receipt: `../.ga/receipts/experience-add-59822d0433b98d0efdc0b6c14a0d7bacd322453e528745fb07a1a5181e63bcb4.json`
- 参照する外部証拠: [evaluation-evidence.json](evaluation-evidence.json)
- 外部証拠SHA-256: `c53da7c072a8a40f2c2b594bf023f28df8743943310a628e83bdc0e63a2501e9`
- 実行コマンド・終了コード・stdout/stderr・前後照合: [registration-cli.json](registration-cli.json)
- 全identityとnative artifact hash: [registration-summary.json](registration-summary.json)

Native recordは入力experienceのcanonical bytesと一致した。Native receiptはファイル名に含むSHA-256と実bytesが一致した。登録前後に、参照する78 artifactと最終Skillの12ファイルを再照合し、変更されていないことを確認した。`experience-add`自体は参照先hashを検証しないため、この照合を外部の記録器が行った。hashの一致はbyte integrityの証拠であり、評価器の正しさや独立性の証明ではない。

## 分離したidentity

| 対象 | Git commit / SHA-256 |
| --- | --- |
| 生成に使ったB Skill | `58bed659cc7f39d316794625ad0475084b38df7e` / `1fba407c2a0452ad1f458c75bb6590cdc22e7c8a98bf04e2cc2554a317fb8ee5` |
| 修正後の最終B Skill | `6fc0c3dd6c82c4dd2f77764c5da512fbfdbaa911` / `62f6f5075ca97e48a4d811d6039cd27ce2488425915e1bd4c41a62da6619d1bf` |
| R-ASIの過去sankai descriptor | content ID `57d1b2372555c5493ab91e5ae679e2441581795c1998c1681fdc050b1abb7552` |
| 上記descriptorのnative CAS bytes | `5b35eb5daf879cffdb54114faa4b89af64b6094c008de756c49c4c1f8ed1da34` |

descriptorのIDを実装hashとして扱っていない。descriptorは過去の分解記録で、最終修正を遡及適用していない。最終Skillで新たに生成し直した試行も実施していない。

## 保存した観測結果

| 対象 | 結果 | 範囲 |
| --- | --- | --- |
| 最終checker unittest | 70/70 | 保存済みlog付きの実装検証 |
| 同梱Flow | 2/2 | 静的契約検査 |
| 共通API simulation | 9/9 | in-memory APIの検査 |
| 初回提出の共通比較 | baseline 40/40、candidate 40/40 | 各arm、予約20・取込み20。差0で追加効果未立証 |
| 最終比較再実行 | 両arm 40/40 | 同じ生成コードのreplay。新しいmodel試行ではない |
| 生成Flowの修正後checker再検査 | 2/2 | 元の生成JSONを変更していない |
| 別agentによる診断追確認 | 2所見解消、反例2件拒否、正常fixture2/2、限定回帰5/5 | 非blind。独立Oracleではない |
| Skill構造 | 59 local links、10原則、19 source records | 18原典。S17/S19は同じ書籍の別章 |
| 引用照合 | 19件一致 | Web抽出cacheとの一致。HTTP原bytesの認証ではない |
| ブラウザ | blocked / not_run | DOM・描画・keyboard・実UI完了性は未検証 |

candidate側だけのHTTP simulation self-test、生成者の独自self-check、過去の1,947 shape probe集計は共通比較の分母へ加えていない。shape probeの当初ケース別logはなく、復元scriptは今回再実行していない。

## 試行・費用履歴

[trial-history.json](trial-history.json) では、提出後に共通評価用の修復を行っていないこと、生成前self-checkの内部編集回数は未取得であること、初版生成と最終Skill修正を分離したことを記録した。

positive regression testの `leave_before` 誤参照により69/70となり、実fixtureの `leave` へ直して70/70になった履歴も残した。最初の69/70のraw logは保存されておらず、root報告と診断review内の記録に由来する。最終70/70は実logを保持している。

native登録後に追加で届いた初期checker開発の66/67→67/67は、**author-reported / not independently replayed** としてlive trial-historyへ追記した。当初失敗log・初期bytesはなく、最終gateの主証拠には使っていない。登録済みの [trial-history.snapshot.json](trial-history.snapshot.json) は改変していない。

[cost-history.json](cost-history.json) は上流suite、最終unittest、API suite、限定review、native登録subprocessの実測時間をそれぞれの範囲で保存する。金額・model token数・model revision・seed・campaign全体の時間は未知のためnullで、合計費用を捏造していない。native cost ledgerは予算契約未設定のため未登録。登録前の [cost-history.snapshot.json](cost-history.snapshot.json) と、登録後の実行時間を別に保全した。

## HOLDの理由

独立blind評価と強制隔離されたholdoutがない。ブラウザ確認は実行できていない。各armは初回提出1件で、正確なmodel revision/seedは不明。共通比較の差は0であり、B追加の効果を立証していない。修正版Skillでの新しい生成比較はしていない。R-ASIのformal campaign lock・policy・cost契約も未完成である。

experienceの `status=active` はストア上の状態だけを表す。`formal_gate=HOLD`、`promoted=false` を維持する。
