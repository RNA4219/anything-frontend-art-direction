# B Skill — 2所見の解消確認

## 結論

**B-REV-01とB-REV-02は、今回指定された限定的な再確認の範囲で解消した。**

- 保存済みの待機循環反例2件は、修正後にどちらも `WAIT_TIMEOUT_STUCK` / exit 1となった。
- 正常なbooking / report fixtureはどちらもexit 0のまま。
- 追加された3件と関連する既存2件の回帰テスト、計5件はすべて成功した。
- B10は通常taskと比較・正式昇格の入力、判断、処理、出力、依存を分けている。通常の小修正に第2taskやR-ASIを要求しないことが明記された。

これは前回と同じ別エージェントによる診断レビューの追確認である。**shared filesystem・共通モデルであり、独立blind holdoutでも正式昇格でもない。** `evidence/B/experiments` は引き続き一覧・本文・生成物・評価のいずれも未読。Skill本体を修正していない。新たな網羅試験、ブラウザー操作、原典再調査も行っていない。

## 対象revisionと証拠

| 項目 | 証拠 |
|---|---|
| 元レビュー | [skill-review.md](skill-review.md) |
| 元レビュー対象hash | [reviewed-snapshot.json](reviewed-snapshot.json) |
| 解消確認対象hash・時刻・Python版 | [resolution-snapshot.json](resolution-snapshot.json) |
| 今回のCLI完全出力・5件のテストログ | [resolution-check-results.json](resolution-check-results.json) |
| 元の反例実行結果 | [wait-counterexample-results.json](wait-counterexample-results.json) |

checkerのSHA-256:

```text
修正前: 22ea66ddbeb50f0cb91baa8562d2b3c8300ebb3bedb47f4a812f9347a83a196d
修正後: d3e18b0e94a4d8726841706a64b1fb67afc4c01feb49efa32c7827ca7662721b
```

元のレビュー文書・反例JSON・実行結果は変更していない。今回の結果を別ファイルへ保存した。

## B-REV-01 — 解消を確認

### コードと契約の確認

- `extensions/B/checks/check_flow.py:367`は、非waitに着いただけではescapeにせず、success / exitに至ることを求める。
- 同ファイル`:370`・`:371`で、task / recoveryを含めてuser / timerの遷移を探索する。元の「非wait bridgeを挟むだけでPASS」という経路は残っていない。
- `references/flow-contract.md:70`は、timeout先からuser / timerだけでsuccessまたは説明付きexitへ至るという検査条件を記載しており、コードと一致する。
- checkerのlimitations `:24`と契約`:72`に、ローカルsystemイベントと外部サービス応答を区別できない制限がある。正当なローカルsystem経路が機械判定を通らない場合、actorを書き換えて通さず、未解決判定と実装traceをレビューに残す方針を明記している。

### 再実行結果

| 入力 | 期待 | 実測 | 判定 |
|---|---|---|---|
| [wait-recovery-cycle.json](wait-recovery-cycle.json) | 応答がなければ同じ待機へ戻るだけのrecovery循環を拒否 | exit 1 / fail / `WAIT_TIMEOUT_STUCK` 1件 | 元所見を解消 |
| [wait-task-bridge-cycle.json](wait-task-bridge-cycle.json) | 非waitのtask状態を挟む自動待機循環を拒否 | exit 1 / fail / `WAIT_TIMEOUT_STUCK` 1件 | 元所見を解消 |
| 同梱 `tests/fixtures/booking.json` | 正常契約を受理 | exit 0 / pass / issues [] | 正常例を維持 |
| 同梱 `tests/fixtures/report.json` | 正常契約を受理 | exit 0 / pass / issues [] | 正常例を維持 |

`extensions/B`での再現コマンド:

```sh
python -B checks/check_flow.py ../../evidence/B/review/wait-recovery-cycle.json --json
python -B checks/check_flow.py ../../evidence/B/review/wait-task-bridge-cycle.json --json
python -B checks/check_flow.py tests/fixtures/booking.json --json
python -B checks/check_flow.py tests/fixtures/report.json --json
```

### 関連回帰テスト

以下の5件だけを指定して実行し、5/5成功を確認した。

- `test_timeout_recovery_bridge_is_not_an_escape`
- `test_timeout_task_bridge_is_not_an_escape`
- `test_timeout_recovery_can_reach_exit_through_task`
- `test_timeout_wait_loop_with_user_escape_is_allowed`
- `test_timeout_self_loop_cannot_rely_only_on_system_success`

最初の2件が反例、3件目がtaskを経由してuser操作でexitへ至る正常例であり、単に全bridgeを禁止する変更になっていない。残り2件は自己ループと、退出手段を持つ待機継続の既存境界である。詳細なコマンド・出力は結果JSONに保存した。

### 残る制限

この確認は、schema上のuser / timer経路についての構造検査に限る。guard充足性、本番API、実行時進行保証、利用者による操作発見性を証明しない。ローカルsystemイベントを必要とする正当な退出がfailになる可能性は残るが、その限界とレビューへの渡し方が明示されたため、元の「非wait bridgeで保証を満たしたように見える」問題とは区別する。

## B-REV-02 — 解消を確認

| 原所見の対象 | 修正後の位置・内容 | 判断 |
|---|---|---|
| 通常taskにも2課題比較を要求するように読めた | `references/principles.md:230`は通常taskの要件・成功predicate等を先に記し、比較または正式昇格依頼のときだけ複数task・baseline等を追加する。 | 解消 |
| 第2taskやR-ASI待ちで小修正の提出が止まり得た | `:232`は対象の実測結果・未検証事項で通常修正を提出でき、第2taskやR-ASI準備で停止しないと明記。`:238`も無関係な第2taskを作らない。 | 解消 |
| 通常成果物とSkill昇格の保留が混ざった | `:232`は独立性不足による保留を正式昇格に限定。`:234`・`:236`も通常の処理・出力と比較時の追加事項を分ける。 | 解消 |
| R-ASIが未定義のhard dependencyに見えた | `:244`は通常利用に不要な任意のcampaign証跡保管先と明記し、利用指定時だけ現行CLI / 契約を確認する。 | 解消 |

文書上の再現例として、元レビューの「1画面の戻る操作で入力が失われる」小修正を当てはめた。現在の記載では、そのtaskの正常・異常・境界と未検証事項を確認して提出でき、第2task・比較実験・R-ASIの準備は不要である。一方、Skillの正式昇格を依頼された場合は独立性等が必要となる。この分岐は単独利用・小修正の方針と整合している。実際の生成エージェント運用による停止率などは測定していない。

## 元レビューの1,947 shape probeの来歴

**元レビュー時は、ツール呼出しのshell here-document内でその場限りのPythonコードを実行した。スクリプトファイルやケース別の完全ログは、その時点では保存していなかった。** 観察結果はツール出力の `case_count: 1947`、`crashes: []` である。

今回、そのツール呼出しに残っている実行本体を [shape-probe-replay.py](shape-probe-replay.py) として保存した。追加したのは来歴・実行場所・限界を説明するheaderで、probe本体のロジックは元の呼出しと同じである。**今回、このshape probeは再実行していない。**

再実行する場合は`extensions/B`を作業ディレクトリとする。

```sh
python -B ../../evidence/B/review/shape-probe-replay.py
```

1,947件はreport fixtureの既存fieldを1項目ずつ異なる型・空値に置換した組合せ数であり、全JSON・全field組合せの網羅試験ではない。元結果は`reviewed-snapshot.json`のchecker / fixture hashに対応する。修正後checkerで再実行した結果を、元revisionの再現結果と呼ぶことはできない。

## 実行履歴の区別

親エージェントから、全体テスト70/70成功と、その前にpositive testで存在しない`leave_before`を使用して69/70となり、実fixtureの`leave`へ訂正した履歴の報告を受けている。過去の全体runログはこの解消確認では閲覧・再実行しておらず、70/70を当レビュアーの実測とは記載しない。今回の直接証拠は、保存した4件のCLI実行と5件の限定テストである。

限定範囲で新しい追加所見はなかった。この結論は2件の修正確認であり、未検証の実DOM・API・候補比較の結果や、Skill全体の正式昇格へ拡張しない。
