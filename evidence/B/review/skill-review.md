# B Skill 診断レビュー

## 結論

**修正を勧める所見は2件。High / Critical は今回の範囲では見つからず、Medium 2件。**

1. **B-REV-01:** timeout後に一度だけ非wait状態を挟むと、応答が来ない限り終了できない待機循環でもcheckerがPASSする。保存した2つの反例で再現した。
2. **B-REV-02:** B10が通常のflow修正とSkill比較・正式昇格を同じ適用節で扱い、2課題比較・独立評価・未定義のR-ASI契約を通常利用の依存とも読める。単独利用・小修正の説明と適用範囲を揃える必要がある。

本レビューは、別エージェントによる診断レビューである。ただし**shared filesystem・共通モデルを使用しており、独立blind holdoutではなく、正式昇格判定でもない**。同梱fixtureとcheckerテストは閲覧・実行した。`evidence/B/experiments` は一覧・本文・生成物・評価のいずれも読んでいない。原典の全文再調査、ブラウザー操作、他エージェント追加、Skill修正、ルート文書変更、commit / pushは行っていない。

## 対象と証拠の固定

- 対象: `extensions/B/` のSkill本文、同梱参照・例・checker・tests・fixtures・agent metadata。
- 比較対象: `/workspace/scratch/392a80e65402/anything-frontend-B-base` の現行Skill、対応する参照、`form.html`・`optimistic.html`・`dialog.html` とテンプレート索引。
- 研究索引: `evidence/B/source-index.md`、`evidence/B/research/sources.json`。本文キャッシュや実験領域には遡っていない。
- 読取時のSHA-256と実行環境: [reviewed-snapshot.json](reviewed-snapshot.json)。この報告はそのhashの内容に対するもの。後続修正へ自動的に判定を引き継がない。
- checker SHA-256: `22ea66ddbeb50f0cb91baa8562d2b3c8300ebb3bedb47f4a812f9347a83a196d`。
- 反例のCLI出力と判定根拠: [wait-counterexample-results.json](wait-counterexample-results.json)。

Severityは、High＝通常利用で重大な誤動作・保証の誤認が広く生じる、Medium＝限定条件で重要な検証漏れや手順・依存の不一致が生じる、Low＝局所的な説明不足、とした。実製品での発生頻度や損失額は未測定である。

## B-REV-01 — 非waitを一度挟む待機循環をtimeout検査が見逃す

| 項目 | 所見 |
|---|---|
| Severity | **Medium** |
| 分類 | implementation / checker保証範囲 |
| 主な位置 | `extensions/B/checks/check_flow.py:363` の `kind != "wait"`、続く `escape = True` と `break` |
| 関連位置 | 同ファイル `:346` のrecovery判定、`:356` の「missing system responseだけに依存しない」コメント、`references/flow-contract.md:66`・`:70`、`references/principles.md:56` |
| 症状 | timeout先に `recovery` または `task` が1つあるだけでescapeとする。そこから同じwaitに戻るしかない場合も、非wait以降の出口を確認しない。 |
| 影響 | 宣言上の非wait状態を挿入すると、「出口のない待機を検査する」という説明より弱い条件でPASSする。guardが未知だからではなく、既知のactorと遷移だけでも分かる待機循環が残る。 |
| 検証状態 | **再現済み。両反例ともCLI exit 0 / status pass / issues []。** |

### 原因と契約との差

checkerは通常の全graph到達性ではsystem応答を含めてsuccess / exitへの経路を求める。一方、timeout専用検査では欠けたsystem応答に依存しない回復を探す意図がコードコメントに書かれている。しかし探索は非wait stateに到達した時点で成功し、そのstateの出口は追わない。

`recovery`の追加検査も「自身とは異なるstateへ出るuser遷移が1つあること」だけなので、`recovery → wait`だけで条件を満たす。`task`にすればそのuser遷移要件もなくなる。いずれも全graphには「いつかsystem応答が来れば成功する」edgeがあるため、通常の到達性・閉循環検査はPASSする。

### 保存した反例

- [wait-recovery-cycle.json](wait-recovery-cycle.json): 同梱report fixtureを基に、`lookup`、`leave_slow`、`leave_running`を除去。`generating → timer deadline → slow(recovery) → user keep_waiting → generating`だけが、無応答中に辿れる経路になる。正常応答・エラー応答・0件応答は残す。
- [wait-task-bridge-cycle.json](wait-task-bridge-cycle.json): 上記から `slow.kind = task`、`keep_waiting.actor = system`・eventをローカルな `reset_wait` に変更。遅延表示を更新して自動的に元のwaitへ戻る。timerの後に一瞬だけ表示状態を挟む、退出操作のない待機循環である。

両方とも、正常・異常・境界scenarioの参照と連続性を保つため、境界traceを `start → deadline → keep_waiting → ready` に変更している。このtraceは「後から応答が来た場合」を表すもので、永久無応答を解決する証拠ではない。説明文字列も退出があるかのように残さず、待機へ戻るだけと明記した。

`generating`からuser / timerの遷移だけで到達するstateは、両方とも `generating` と `slow`。success / exitへの到達は0件だった。第2反例ではローカルなsystem resetを含めても同じ循環を繰り返し、外部サービスから応答が来ない限り終了できない。

### 再現コマンド

作業ディレクトリを `extensions/B` にする。

```sh
python -B checks/check_flow.py ../../evidence/B/review/wait-recovery-cycle.json --json
python -B checks/check_flow.py ../../evidence/B/review/wait-task-bridge-cycle.json --json
```

レビュー対象hashでの観察結果は、いずれも次のとおり。

```json
{"status": "pass", "ok": true, "issues": []}
```

これは出力の主要3項目の抜粋であり、実CLIにはschemaとlimitationsも出る。完全出力は結果JSONに保存した。

### 修正方向

timeout先のstate種別だけで探索を終了しない。少なくとも、非waitを経由しても結局同じwaitへ戻るだけのcomponentを反例として扱い、欠けたサービス応答に依存しない「待機を終える・退出する・意味のある回復を選べる」条件を定義する。

実装方法は、user / timerで辿れる明示的exitや、回復後の経路を追う検査、あるいはサービス応答とローカルsystemイベントをschema上で区別する方法が考えられる。ただし単純に全system edgeを禁止するとローカル処理まで除いてしまうため、何を機械判定できるかを先に限定する必要がある。採用する検査能力に合わせて `flow-contract.md:66` と `:70`、checkerのlimitationsも揃える。保存した2ケースを回帰テストへ追加し、userが明示的に待機継続と退出を選べる正常fixtureは引き続き通ることを確認する。

## B-REV-02 — B10の通常適用と比較・正式昇格の依存が混在する

| 項目 | 所見 |
|---|---|
| Severity | **Medium** |
| 分類 | interaction / workflow documentation / dependency scope |
| 主な位置 | `extensions/B/references/principles.md:228` のTrigger、`:230` のInputs、`:236` のOutput Contract、`:244` のDependencies |
| 関連位置 | `extensions/B/SKILL.md:51` の通常の提出手順、`references/integration.md:5` の単独利用、`:32` の小さなflow不具合への適用 |
| 症状 | 通常のflow設計・修正提出をTriggerに含む一方、2種類以上のtask、同一model・content、baseline/candidate比較、Dの独立評価・外部実行器・R-ASI契約を同じ節の入力・出力・依存として列挙する。比較実験または正式昇格のときだけ要求するという境界が明記されていない。 |
| 影響 | 単独Skillで小修正を扱う実行者が、存在しない第2課題やbaselineを作る、入手できないR-ASIやDを待つ、通常成果物の提出と正式昇格を混同する可能性がある。実際のエージェント停止は測定していない。 |
| 検証状態 | **文書照合で確認。解釈上の再現であり、runtime failureとしては主張しない。** |

### 再現条件と手順

1. 単独環境で「1画面の戻る操作で入力が失われる」という既存flowの修正を依頼する。比較実験、Skill昇格、第2課題、外部R-ASIの利用は依頼に含めない。
2. `integration.md:32` に従えば、Bと対象実装規則で対応できる。入口のB10ではFlow JSON、decision log、対象操作の検証を求めている。
3. 詳細原則B10へ進むと、Triggerには一般の「flow設計・実装の提出」が含まれ、Inputsは2種類以上のtask等を、Output Contractはbaseline/candidate比較等を、DependenciesはR-ASIの実装済み契約等を列挙している。
4. 同梱Skill・参照・例の中でR-ASIはFailure ModesとDependenciesのみに現れ、契約・呼出方法・通常利用で省略できる条件がない。

`principles.md:232` は「独立性がなければ正式昇格を保留する」と限定しており、これ自体は妥当である。そのため**全ての小修正が必ずHOLDされる**とは断定しない。問題は、その直前・直後の入力・出力・依存には同じ限定がなく、一般のB適用とcampaign運用条件を区別しにくいことにある。`:246` でcampaign運用要件と説明しているが、どのTriggerに適用するかまでは定まらない。

### 修正方向

B10内で条件を明示する。

- 通常のflow設計・修正: 対象taskの正常・異常・境界trace、観察結果、未検証事項、API依存を残せば提出できる。比較用の第2taskやR-ASIを必須としない。
- Skill効果の比較・正式昇格を依頼された場合: 固定した複数task、baseline/candidate、評価条件・hash・独立性を要求し、独立性不成立なら正式昇格だけを保留する。
- R-ASI: 実在する外部契約に依存する場合だけ、入口・最低要件・利用できない場合の扱いを参照で示す。同梱されない任意のcampaign機能なら、その旨をDependenciesにも記す。

これにより、通常の修正完了と、Skillそのものの有効性・正式昇格の証明を分けられる。独立評価を要求する方針そのものを弱める提案ではない。

## 問題が見つからなかった検査項目

| 検査 | 観察と判断 |
|---|---|
| 入口と原典の2ホップ | `SKILL.md`から`references/sources.md`へ1リンク、そこから19参照箇所の原典URLへ1リンク。全URLが直接掲載されている。最短入口経路として条件を満たす。原則を経由するとさらにリンクを踏むが、直接の入口が用意されている。 |
| 同梱ローカル参照 | Skill本文・参照・例にある59件のローカルMarkdownリンクを点検し、欠落ファイル・明示anchor欠落は0件。これは外部URLの再取得成功を示す検査ではない。 |
| 研究metadataの内部整合 | `sources.json`の19件について、title / URL / section / confidence / source_claim / campaign_inference / existing_relationが同梱sources本文に存在することを確認。不一致0件。18原典・19参照という数え方はS17とS19を同一書籍とする説明と整合する。原典の正確性を再証明したわけではない。 |
| 通常の適用・不適用 | descriptionにgoal未達・入力喪失・結果不明・待機やerrorの行き止まりを列挙。不適用例で静的書体選定、好みだけのラベル変更、短いフォームの不要分割などを明示。B10の範囲を除き、視覚意匠とflow責務は分けられている。 |
| Art Directionの保持 | `SKILL.md`の初期条件と`integration.md`に、造形・配色・書体・構図の維持と他領域への引継ぎを記載。Bの修正で美的好みを置換する指示は見つからない。 |
| checkerの過大な一般保証 | 冒頭・出力limitations・契約本文に、guardは評価しない、API冪等性・取消し・receiptは宣言である、WCAG適合・操作発見性・実利用者の完了性は未証明と記載。APIやUXを広く自動証明するという主張は見つからない。限定的な待機検査の説明はB-REV-01の対象。 |
| JSONと実行traceの区別 | Flow JSONのscenariosはpath / expected_state / assertionsを持つ設計trace。別成果物のTest tracesでは実際の表示・server結果・検証方法・証拠パス・not_runを求め、checker limitationsでも実行receiptではないと明記。checkerが実測ログを検査するとは読まない。 |
| 実行依存 | checker・同梱testsはPython標準ライブラリのみで実行できた。baseリポジトリや第三者パッケージをimportしない。構造検査の単独実行に欠落依存は見つからない。B10の文書上の外部依存は別所見。 |

## 現行基盤との重複の判断

**既存の知識を無かったことにして全面再実装する拡張には見えない。状態・operation・traceの出力契約を追加する必要性は認められる。**

| 現行基盤で確認した内容 | Bで追加される役割 | 判断 |
|---|---|---|
| `references/d-interaction.md:41`のD-31、`:44`以降のD-34〜44に修復、楽観更新、rollback、古い取得・競合がある。 | B05で結果不明、operation key、receipt、再照会、retry条件をtask全体に結び付ける。 | 既存の非同期対応を否定せず、その上に明示的なtask契約を加えている。 |
| `references/g-state-forms.md:16`のG-06、`:23`のフォーム入力支援、`:46`のURLと履歴に既存の実装規則がある。 | B03/B08で確認snapshot、戻る・再訪時の保持、再照会、部分結果を指定する。 | native validationや履歴APIを置換する内容ではない。 |
| `references/c-usability.md:28`以降のC2にはエラー説明と入力保持、`:68`以降のC4には行動分解・walkthroughがある。 | failure matrix、guard / effect / feedback、正常・異常・境界traceへ接続する。 | 基本原則の重複はあるが、出力と再現の形式化に役割差がある。 |
| `references/k-studies.md:23`以降のK1-13〜16、`:92`以降のK5に応答・完了・取消し・待機の指針がある。 | B01/B04/B06に適用条件・例外・検証手順を付ける。 | 既存原則の具体化と明示されており、新規発見扱いではない。 |
| `templates/form.html:23`のsubmit処理はlocal表示、`optimistic.html:25`のsaveは模擬Promise、`dialog.html:18`はdialog操作の限定例。 | 本番server契約を別途確認し、長いtaskのflowと回復を設計する。 | これらを本番予約・冪等API・server取消の完成実装と扱っていない。統合文書の説明と整合する。 |

## 実施した検証と限界

- `python -B -m unittest discover -s tests -p 'test_*.py' -v`: **67 tests、全件成功**。
- report fixtureの既存フィールドにJSONとして可能な異なる型・空値等を1項目ずつ代入する追加shape probe: **1,947ケース、未捕捉例外0件**。任意の入力・組合せでの完全な耐性を示すものではない。
- 上記59ローカルリンク・19原典metadataの内部照合。
- timeoutの2反例をCLIへ渡し、PASSの取りこぼしを保存・再現。
- 実DOM、API実装、人間の操作発見性、性能、WCAG適合、候補比較実験、生成物の効果量は検証していない。今回のスコープから外れており、未検証を合格として扱わない。

修正実装は親エージェントへ返す。修正後は保存したhashとの差分を残し、B-REV-01の反例と既存の正常fixture、B-REV-02の通常利用経路・正式昇格経路をそれぞれ再確認する必要がある。
