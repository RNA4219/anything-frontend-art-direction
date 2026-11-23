# Design QAの出力契約

[入口](../SKILL.md) · [原則](principles.md) · [評価手順](evaluation-protocol.md) · [JSON例](../examples/report-example.json)

## 目次

- [記録単位](#記録単位)
- [必須フィールド](#必須フィールド)
- [所見](#所見)
- [タスク実行](#タスク実行)
- [重大度](#重大度)
- [独立評価receipt](#独立評価receipt)
- [ゲート結果](#ゲート結果)
- [比較とmanifest](#比較とmanifest)

## 記録単位

`design-qa-report/v1`を使う。**1 task × 1 viewport × 1試行**を1 reportとし、別幅・再試行・別タスクは別reportへ分ける。同じtask内にnormal/error/boundaryを一つずつ含める。未実行は空欄や偽のPASSにせず、明示的なnullとnot_run/blockedで表す。

既存Art Directionのレビューをbaselineとして評価するとき、baselineへこのschemaを要求してSkill効果を先取りしない。両者の生出力を保存し、事前に固定したrubricで比較する。機械比較用に変換する場合は、変換者・元出力・付け足した情報を記録し、元出力が備えていた能力として数えない。

JSON例は構造の説明用のHOLD例で、UIを観察した記録ではない。実績へコピーするときは全placeholder・hash・証拠・環境を今回の観察で置換する。未知の値は明示してopen_questionsに置き、見かけの完全性のために捏造しない。

実行面（engine）を`context.evaluation_mode`と証拠のdescriptionへ必ず記す。実ブラウザ、minimal DOM logic harness、source inspection、別版の公開サイトは別種の検証である。契約が文字列を受け付けても、意味の異なる実行面の値を一致させて比較しない。ブラウザを要求したcaseは代替のlogic probeだけでpassedにしない。

## 必須フィールド

| キー | 内容 |
| --- | --- |
| `schema` | 固定文字列`design-qa-report/v1`。 |
| `report_id` | このtask/viewport/試行に固有の非空文字列。 |
| `reviewed_artifacts` | 一件以上の`{path, sha256}`。評価したHTML等のrepo内相対pathと実bytesのSHA-256。 |
| `context` | 下記の凍結条件。 |
| `evidence` | 一件以上の`{id, path, sha256, kind, description}`。実在する証拠を参照。 |
| `findings` | 所見配列。該当なしは`[]`でよいが、未確認を「なし」としない。 |
| `task_runs` | 各scenarioの実行結果。欠けたscenarioはゲートでHOLD。 |
| `open_questions` | 未解決の質問・未検証事項の文字列配列。なければ`[]`。 |
| `independence` | 評価者とoracle隔離、外部receiptへの参照。 |

`path`は`--root`内のファイルを指す相対pathとする。`..`、絶対path、root外へ解決するsymlinkを使わない。SHA-256は小文字64桁。ファイルが存在しない、bytesが違う、JSONキーが重複する、数値がNaN/Infinityの入力は契約不正となる。

### context

| フィールド | 型・意味 |
| --- | --- |
| `task_id` | 非空文字列。task_runsと一致させる。 |
| `requirements_sha256`, `content_sha256` | 要求・実内容を凍結したbytesのSHA-256。対象ファイルとcanonicalization方法も検証記録へ残す。文字列の形式一致だけで内容同一性を主張しない。 |
| `environment.browser`, `.version`, `.os` | 実際の実行環境。未観察は明示的な文字列とopen questionにする。 |
| `environment.viewport` | `{width: 正整数, height: 正整数}`、CSS px。 |
| `environment.dpr` | 正の有限数。booleanは不可。 |
| `environment.locale`, `.timezone` | 実行設定。 |
| `environment.fonts` | 非空の文字列配列。指定fontか実描画確認かを記録し、CSS指定を実描画確認と呼ばない。 |
| `environment.animation` | motion設定とcapture時点の扱い。 |
| `environment.data_seed` | 非空文字列または整数。固定データの識別子。 |
| `environment.input_modes` | 非空の文字列配列。例: pointer、keyboard。実機touchとエミュレーションを分ける。 |
| `model.id` | 実行モデルの観測可能な識別。非公開内部snapshotを推測しない。 |
| `model.sampling` | 非空object。取得できた設定を記す。不可視なら例`{"observed": false, "reason": "not exposed"}`とし、同一設定の保証へ変換しない。 |
| `evaluation_mode` | 比較の両条件で同一の測定目的。例: 同一UIのレビュー品質。baseline/candidateの区別をこの欄に入れない。 |

## 所見

| 必須キー | 記録すること |
| --- | --- |
| `id` | report内で一意のID。 |
| `category` | `functional`, `information_architecture`, `interaction`, `visual`, `implementation`の一つ。 |
| `owner` | `A`, `B`, `C`, `D`, `art-direction`の一つ。 |
| `status` | `confirmed`, `hypothesis`, `preference`, `resolved`の一つ。 |
| `severity` | `blocker`, `major`, `minor`, `note`の一つ。 |
| `location` | `{artifact, selector, state, viewport}`。artifactはreviewed_artifactsのpath、viewportはcontextと一致。selectorは要素を再特定する値。画像しかない場合は画像内regionの位置と限界を文字列で明示する。 |
| `symptom` | 位置と状態に結び付いた具体的症状。 |
| `expected` | 要求・契約・意図に基づく期待。 |
| `observed` | 実際に見たこと。原因推測は区別して書く。 |
| `impact` | どのタスクがどう妨げられたか、重大度理由、回避/復帰手段、頻度が既知かを記す。 |
| `repair_direction` | 既存の意図を保つ修正方向。未確認の実装方法を確定解として押し付けない。 |
| `reproduction` | 一件以上の順序付き手順文字列。開始条件、入力、操作、観察点を含む。 |
| `basis` | `{kind, reference, clause}`。kindは`requirement`, `standard`, `heuristic`, `intent`。原典の種類・版・適用条件・例外・推論をreference/clauseに記す。 |
| `confidence` | `high`, `medium`, `low`。観察/原因の確度が違えば本文で区別。 |
| `evidence_ids` | evidence配列に実在するID。 |

confirmed/resolvedのvisual所見にはscreenshotが必要。interaction所見にはbrowser_traceまたはtest_logが必要。sourceだけから推測したinteractionはhypothesisとする。resolvedは現在のhashで症状が解消した証拠を付け、昔の修正commitを挙げるだけにしない。

`evidence.kind`は`screenshot`, `browser_trace`, `source`, `test_log`の四種類。descriptionには対象状態・取得方法・観察できる範囲を記す。種類名を偽装して静止画をtraceと扱わない。スクリプトはファイルの意味を自動認証しない。

minimal DOMでのtest_logは、その模擬環境のロジックを確認した証拠である。CSS layout、native validation、focus順序、OS/ATの挙動を支えない。公開サイトの画像/操作を使う場合は、その公開版との対応が確認できた範囲だけを記録する。別のローカルfixtureを観察済みにするため流用しない。

## タスク実行

| キー | 型・値 |
| --- | --- |
| `task_id` | context.task_idと一致。 |
| `scenario` | `normal`, `error`, `boundary`。同じ組合せを重複させない。 |
| `status` | `passed`, `failed`, `blocked`, `not_run`。 |
| `completion` | passedならtrue、failedならfalse、blocked/not_runならnull。 |
| `steps_count` | passedなら0以上の整数。未計測ならnull。blocked/not_runはnull。boolean不可。 |
| `recovery` | `passed`, `failed`, `not_applicable`, `not_run`。 |
| `evidence_ids` | 実行証拠のID。passed/failedや復帰の主張にはtraceまたはtest_logが必要。 |
| `observed` | 開始/終端、期待結果、実結果、保持した値、未確認を説明する。 |

completionが示す終端は事前に定める。「不正値が正しく拒否された」はその境界検査の成功であり、利用者の登録完了とは異なる。異常や境界を含む**業務完了**を測る場合は、拒否/失敗 → 訂正/再試行 → 目的状態まで実行する。検査成功数とユーザーのタスク完了率を別に報告する。[S04](../../../evidence/D/source-index.md#s04)

単なるsource解析やscreenshotでpassedを記録しない。環境不足ならblocked、実施しなかったならnot_run。失敗の再現はfailedで記録し、原因未確定の場合でも観察した失敗を隠さない。

## 重大度

次はDの運用尺度。NNGの元の0〜4尺度と同一ではない。頻度・影響・持続を検討する考え方を使い、各所見のimpactへ理由を残す。[S03](../../../evidence/D/source-index.md#s03)

| severity | 判断条件 |
| --- | --- |
| blocker | 必須タスクが完了不能、または取り返せない誤操作/情報損失が起き、対象条件に回避手段がない。 |
| major | 主要タスクで強い妨げ・誤結果・復帰困難が再現する。回避があっても通常経路の利用を大きく損なう。 |
| minor | タスクを完了でき、限定的で回避可能な負担や局所的な不一致がある。 |
| note | 好み、改善提案、追加観察。重大度の高い違反をnoteへ下げてゲートを通さない。 |

preferenceはnoteだけを使う。hypothesisには影響を仮定した重大度を付けてもよいが確定違反とは区別する。confirmedかつlow confidenceは追加確認が必要になる。

## 独立評価receipt

independenceは`{author_id, evaluator_id, blind, protected_holdout, evidence_ref}`を必須とする。前二つは非空文字列、二つのフラグはboolean、receiptがなければevidence_ref=null。same-agentは同じIDを使い、別名で独立性を作らない。

外部の信頼できる評価処理がreceiptを作る場合、schemaは`design-qa-independent-evaluation/v1`。必須項目は`report_id`, `report_sha256`, `author_id`, `evaluator_id`, `blind`, `protected_holdout`, `decision`, `evaluated_at`。decisionは`READY FOR INTEGRATION`, `HOLD`, `REJECT`、日時はtimezone付きISO 8601。ID・フラグはreportと一致し、report_sha256は**確定したreportファイル全bytes**を覆う。

report側へreceiptの相対pathを先に記し、reportを固定してから外部評価がhashとreceiptを作る。receipt作成後にreportを書き換えた場合は新しい版として再評価する。

receiptの形式とhashが正しくても、評価者の真正性・アクセス隔離・観察の真偽はこのCLIでは証明できない。共有OS上でプロンプトに「見ない」と書いただけならprotected_holdout=falseとする。非公開oracleやholdoutをCandidateへ読ませない。成立しなければpromotion HOLD。[S02](../../../evidence/D/source-index.md#s02)・[S18](../../../evidence/D/source-index.md#s18)

## ゲート結果

| 結果 | 意味 |
| --- | --- |
| `contract_valid=false` | schema、型、参照、hash等に不正。対象の品質は判断できない。 |
| `target_decision=REJECT` | confirmedのblocker/majorが未解決。 |
| `target_decision=HOLD` | hypothesis、未実行/失敗/復帰未確認、case不足、open questions等が残る。 |
| `target_decision=READY FOR INTEGRATION` | このreportの受入条件が満たされた。対象範囲を越えて保証しない。 |
| `promotion_decision=HOLD` | 独立性・blind・protected holdout・receiptまたは対象条件が不足。局所試験が通っても正式昇格はしない。 |
| `promotion_decision=REJECT` | 独立評価が成立し、対象またはreceiptがREJECT。 |
| `promotion_decision=READY FOR INTEGRATION` | 対象がREADYで、独立した信頼できる評価のreceiptもREADY。真正性/隔離の外部監査が別途必要。 |

CLI終了コード: 不正=1、有効だがpromotion HOLD/REJECT=2、promotion READY=0。`verify-manifest`のみ、0はファイル同一性検査の成功であって品質READYではない。数値の同じ0を意味の同じPASSとみなさない。

## 比較とmanifest

`compare`は**同一UIに対するレビュー方法の比較専用**。context全体とreviewed_artifactsのpath/hashを一致させる。件数差と操作数差は記述統計であり、真の検出率・誤検出率・UI改善を証明しない。修正前後でHTMLが異なる比較は手順書に従い別の比較記録を作り、このCLIへ無理に通すためhashを書き換えない。

`verify-manifest`のschemaは`design-qa-artifacts/v1`、`artifacts`に`{path, sha256, size_bytes}`を一件以上入れる。size_bytesは実際のbyte数。重複path・root外参照・hash不一致を拒否する。manifestが通ることと原典の主張や所見が正しいことは別である。
