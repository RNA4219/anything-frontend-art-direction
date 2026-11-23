# Design QAの判断原則

[入口](../SKILL.md) · [出力契約](report-contract.md) · [原典index](../../../evidence/D/source-index.md)

## 目次

- [D01 対象と意図](#d01)
- [D02 原子的な所見](#d02)
- [D03 根拠と重大度](#d03)
- [D04 タスク完了](#d04)
- [D05 失敗と復帰](#d05)
- [D06 視覚階層・整列・密度](#d06)
- [D07 ブラウザと画像の証拠](#d07)
- [D08 同条件比較](#d08)
- [D09 LLM批評と独立評価](#d09)
- [D10 回帰とゲート](#d10)

## 共通の適用条件

これらは対象artifactのQA手順であり、視覚表現の制作レシピではない。原典で明示された要求と、本Skillが選んだJSON・hash・ゲート運用を区別する。すべての所見は原典主張、観察、推論を分け、対象版・タスク・状態に結び付ける。source-indexに原典名・URL・該当節・確認日・限界がある。研究値をそのまま手元のUIの性能に転用しない。

<a id="d01"></a>

## D01 — 評価対象と守る意図を固定する

- **Trigger:** 新規レビュー、改修比較、他担当からのQA依頼。
- **Inputs:** artifactと版、要求、主要タスク、利用者条件、実内容、Art Directionの意図、変更可能範囲。
- **Decision Rules:** 視覚的選択を欠陥にするには、要求・可読性・操作・明示した意図のいずれかとの不一致を示す。仕様不明は確定した不具合にしない。
- **Procedure:** 対象と除外範囲を書き、要求・タスク・意図を紐付ける。既存所見は現行版で再現する。評価後に基準を都合よく変更しない。
- **Output Contract:** scope、artifact hash、requirements/content hash、評価環境、対象外、open questions。
- **Failure Modes:** 好みを欠陥にする、過去issueを現行の未修正と断定する、A/B/Cの設計をDが書き換える。
- **Verification:** 各所見から対象・要求・タスクに戻れること。不明な入力を捏造しないこと。
- **Sources:** [S02 個別評価とscope](../../../evidence/D/source-index.md#s02)、[S08 評価範囲](../../../evidence/D/source-index.md#s08)、[既存の意匠採用条件](../../../references/visual-direction.md#visual-acceptance)。

**Constraints / Exceptions:** 小修正は対象部品に絞ってよい。範囲外は未確認として残し、全サイトへ合格を広げない。**Dependencies:** Aの目的、Bの期待状態、Cの契約、Art Directionの意図。未提供でも再現可能な局所所見は残せる。**Confidence:** 原典の方法と、この入力での観察を区別する。manifest項目は本Skillの運用設計。

<a id="d02"></a>

## D02 — 印象を一件一症状の所見へ変換する

- **Trigger:** 感想、目視の違和感、ツール警告、期待との不一致が出た。
- **Inputs:** 位置、状態、期待/実際、再現操作、証拠、根拠、影響するタスク。
- **Decision Rules:** 位置・症状・根拠・影響・修正方向・再現がない指摘を確定不具合にしない。「AI Slop」「ダサい」は不具合判定の根拠に使わない。
- **Procedure:** 一原因候補・一症状に分け、主責務を一つ定める。観察と原因仮説を分離し、反例を試す。別原因の問題は別IDにする。
- **Output Contract:** finding ID、category/owner、location、symptom、expected/observed、basis、impact、repair_direction、reproduction、evidence_ids、severityと理由、confidence、status。
- **Failure Modes:** 仮説を実測として書く、修正案を観察にする、欄が埋まれば正しいと扱う。
- **Verification:** 同じ版・状態で第三者が同じ症状を再現できるか。所見に参照した証拠が本当にその症状を示すか。
- **Sources:** [S01 状態・復帰](../../../evidence/D/source-index.md#s01)、[S02 所見記録](../../../evidence/D/source-index.md#s02)、[S19 原因と修正の検証限界](../../../evidence/D/source-index.md#s19)。

**Constraints / Exceptions:** 静止画の欠け・重なりは観察できるが、クリック結果は未確認。内容の好みを除き、ラベル理解・文量・必要情報の欠落が操作に影響する場合は扱う。**Dependencies:** 修正は主責務のA/B/C/Art Directionに委ねる。**Confidence:** 観察の確度と原因の確度を本文で分ける。

<a id="d03"></a>

## D03 — 根拠の適用条件と重大度理由を残す

- **Trigger:** heuristic、標準、論文を所見の根拠にする。
- **Inputs:** 出典の種類・版・節、対象と例外、観察証拠、タスク影響、再発/持続、回避可能性。
- **Decision Rules:** 規範、著者ガイダンス、実験、推論を区別する。heuristicから外れることを直ちにWCAG違反にしない。頻度が未測定なら未知とする。
- **Procedure:** 基準の適用理由と例外を確認し、影響・復帰・反復の証拠を並べる。severityは出力契約の運用尺度に沿って理由付きで決める。
- **Output Contract:** basis（kind/reference/clause）、適用理由、例外判定、severity、impact内の重大度理由、追加確認条件。
- **Failure Modes:** ガイドを義務へ変える、経験則の数値を絶対閾値にする、評価者の不一致を消す。
- **Verification:** 出典の節に戻り主張の強さと対象が一致するか確認する。研究の条件と分母を保持する。
- **Sources:** [S03 重大度](../../../evidence/D/source-index.md#s03)、[S07 WCAG 2.2](../../../evidence/D/source-index.md#s07)、[S08 非規範の評価手法](../../../evidence/D/source-index.md#s08)。

**Constraints / Exceptions:** S03の元尺度と本Skillの4段階は同一ではない。WCAG適合を述べるときは完全な過程と対象範囲が必要。**Dependencies:** Cの適合目標・コンポーネント契約。**Confidence:** 原典を読んだことと対象へ適用できることは別に判定する。

<a id="d04"></a>

## D04 — タスクを開始状態と終端条件で測る

- **Trigger:** 完了性、操作数、行き止まり、循環を評価する。
- **Inputs:** 開始状態、目的状態、利用者知識、入力方式、期待する保存/結果、許容される経路。
- **Decision Rules:** クリックや成功文言だけで完了としない。実状態と終端条件を照合する。操作数の減少を単独の改善理由にしない。
- **Procedure:** 開始から終了まで操作を記録し、期待・観察・分岐・戻り・再試行を対応させる。操作の数え方を事前に固定する。
- **Output Contract:** task_runs、completion、steps_count、status、結果証拠、逸脱と未確認。
- **Failure Modes:** 模擬保存を実保存と呼ぶ、人の参加者数と自動試行数を混同する、未完了を分母から消す。
- **Verification:** 同じ入力・状態からtraceを再生し、業務終端または明示した模擬終端を確認する。
- **Sources:** [S04 完了率](../../../evidence/D/source-index.md#s04)、[S05 課題の目的](../../../evidence/D/source-index.md#s05)、[S17 目的とUX指標の接続](../../../evidence/D/source-index.md#s17)、[既存K3-13/14](../../../references/k-studies.md#k3-13)。

**Constraints / Exceptions:** S17は著者公開abstractだけを確認しており、未読本文の詳細手法を追加しない。自動ブラウザの時間は人の所要時間ではない。部分成功を便宜的に0.5として平均しない。**Dependencies:** Aの目的、Bの完了条件。**Confidence:** 成功はその試行の観察であり、利用者一般の成功率ではない。

<a id="d05"></a>

## D05 — 失敗から目的へ復帰できるか測る

- **Trigger:** フォーム、保存、非同期処理、取消し、再試行がある。
- **Inputs:** 正常・異常・境界ケース、失敗注入方法、期待復帰状態、入力/保存状態、再試行経路。
- **Decision Rules:** エラーメッセージの表示と復帰可能性を別に判定する。失敗前後の情報保持、操作可能性、重複実行を確認する。
- **Procedure:** 初期 → pending → success/error → retry/cancelを試す。失敗後に実際に再試行し、期待した最終状態まで確かめる。
- **Output Contract:** scenario、task trace、recovery、保持/喪失情報、入力/状態の証拠、未実施分岐。
- **Failure Modes:** 正常系だけで合格、値の見かけだけで保存成功、エラー後の再試行未実施。
- **Verification:** 同じ異常を再現し、復帰後の値・状態を契約へ照合する。境界値は内側・外側の期待を分ける。
- **Sources:** [S01 取消しと復帰](../../../evidence/D/source-index.md#s01)、[S06 入力保持](../../../evidence/D/source-index.md#s06)、[S08 分岐と全過程](../../../evidence/D/source-index.md#s08)、[既存forms checklist](../../../checklists/forms.md)。

**Constraints / Exceptions:** 模擬処理で確認できるのは模擬契約まで。取消不可の業務なら事前確認と状態説明を評価し、勝手にundoを要件化しない。**Dependencies:** B/Cの期待状態と復帰契約。**Confidence:** 経路未実施はnot_run、外部依存で到達できない場合はblockedとして証拠を残す。

<a id="d06"></a>

## D06 — 階層・整列・密度を必要情報との関係で検査する

- **Trigger:** 主操作の埋没、関連情報の分離、欠け、重なり、狭幅の崩れを疑う。
- **Inputs:** タスク、Art Directionの主役と意図、実文量、関連する情報組、viewport、状態。
- **Decision Rules:** 位置・大きさ・間隔の差だけで欠陥にしない。意図した非対称を保持し、情報対応や読解・操作が壊れた箇所を対象にする。
- **Procedure:** 主役、必要な数値/条件、次の操作を特定する。ラベルと値、エラーと欄、商品と価格の対応を確認し、幅・文量・選択状態を変えて遮蔽・欠け・折返しを観察する。
- **Output Contract:** region/selector、viewport、状態、視覚症状、screenshot参照、影響、原因仮説。
- **Failure Modes:** 空白率や色数だけで採点、すべて中央/左揃えへ矯正、目視から視線計測結果を捏造。
- **Verification:** 該当位置の同じ状態を再取得する。修正を評価する場合は意図を保つ局所比較で症状が消えたかを見る。
- **Sources:** [S20 視覚階層](../../../evidence/D/source-index.md#s20)、[S07 Reflow等の適用範囲](../../../evidence/D/source-index.md#s07)、[既存visual-composition](../../../references/visual-composition.md)。

**Constraints / Exceptions:** 表や地図の必要な二次元配置を一律禁止しない。具体的WCAG基準の対象・例外に従う。主役を初期表示に置くことと全操作を詰めることは異なる。**Dependencies:** Aの情報優先、Cの配置契約、Art Directionの意図。**Confidence:** 幾何は測定できるが、認知影響は利用者観察がなければ仮説。

<a id="d07"></a>

## D07 — 画像と操作の証拠条件を固定する

- **Trigger:** screenshot、ブラウザ再現、visual regressionを根拠にする。
- **Inputs:** artifact hash、browser/version/OS、viewport/DPR、locale/timezone、font、data、motion、入力方式、到達状態。
- **Decision Rules:** 画像はその瞬間の視覚証拠で、操作や読み上げの代替ではない。PCの幅変更・エミュレーション・実機を区別する。
- **Procedure:** 既知状態から操作し、font/画像/非同期の到達条件を確認する。画像、DOM/trace、test logを対応付けhashを記録する。maskは対象欠陥を隠さず範囲と理由を残す。
- **Output Contract:** environment、reviewed_artifacts、typed evidence、取得状態・手順・hash、未観察の入力/支援技術。
- **Failure Modes:** 別OSのfont差を退行と断定、maskで主操作を除外、traceだけで使いやすさを保証。
- **Verification:** 同条件で取得した状態と証拠を照合する。差分率だけで改善や劣化を決めない。
- **Sources:** [S10 手動初期点検](../../../evidence/D/source-index.md#s10)、[S11 実務の試験組合せ](../../../evidence/D/source-index.md#s11)、[S14 画像比較](../../../evidence/D/source-index.md#s14)、[S15 trace](../../../evidence/D/source-index.md#s15)。

**Constraints / Exceptions:** screenshot一致は同じ欠陥の再現も含む。AT/OS固有例外を記録し、Passed with exceptionsを全面PASSへ置換しない。**Dependencies:** ブラウザ/アプリと必要なfont。**Confidence:** 実行済みと未実施を分離する。単一環境の結果を全環境へ外挿しない。

<a id="d08"></a>

## D08 — 同じ入力で変更因子を比較する

- **Trigger:** baseline/candidate、修正前後、Skill追加の効果を比べる。
- **Inputs:** 両artifact、要求/content hash、指示、モデル/設定、環境、評価単位、試行順、差分。
- **Decision Rules:** 要求・内容・モデル・条件を可能な限り同じにする。不一致は明示し、Skillへの因果帰属を限定する。同一UIへのレビュー品質の差をUI改善と呼ばない。
- **Procedure:** 変更因子を固定し、事前に選んだ同一rubricで比較する。順序、再試行、失敗、費用の不明を含め全試行を残す。
- **Output Contract:** paired comparison、同条件/相違条件、観測値・分母、全試行、限定した結論。
- **Failure Modes:** candidateだけ追加要件、成功試行だけ採用、モデル差の隠蔽、UI不変なのに完了率改善を主張。
- **Verification:** hash/要求/環境/モデルを機械照合し、不一致をHOLD理由にする。異なる指標の意味を混ぜない。
- **Sources:** [S04 成功の測定単位](../../../evidence/D/source-index.md#s04)、[S14 同条件の画像比較](../../../evidence/D/source-index.md#s14)、[既存の比較条件](../../../references/visual-direction.md#visual-acceptance)、[既存K14-03/07/25](../../../references/k-studies.md#k14-03)。

**Constraints / Exceptions:** 不可視のtemperature/seedを推測しない。条件が揃わなくても探索的比較は残せるが正式な改善証明にしない。**Dependencies:** 凍結したbaseline/candidate指示。**Confidence:** 単発の比較は記述的結果であり統計的優越を証明しない。

<a id="d09"></a>

## D09 — LLMの批評を再現・反証・独立性へ接続する

- **Trigger:** LLM所見を採用する、複数評価者を統合する、blind評価で昇格を判断する。
- **Inputs:** 生artifact、目的、固定rubric、評価者identity、閲覧材料、モデル/設定、oracleのアクセス境界。
- **Decision Rules:** LLMの自信を証拠にしない。自己採点を独立評価と呼ばない。別agentでも期待解や他者所見を先に見たらblindではない。
- **Procedure:** 所見を操作/仕様/反例で確かめる。初期結果を独立に固定してから統合し、匿名化や提示順反転を補助的に使う。Candidateから非公開oracle/holdoutを実際に遮断する。
- **Output Contract:** evaluator/independence、access制限の証拠、汚染申告、所見の妥当性・重複・不一致。
- **Failure Modes:** 同じ共有ディスクで隠したファイル名を隔離と呼ぶ、正解例の漏洩、LLM多数決を人間評価と同等にする。
- **Verification:** 作成者と判定者、入力とoracleの来歴を追う。アクセス遮断のreceiptがなければprotected blind不成立としてpromotion HOLD。
- **Sources:** [S02 独立観察](../../../evidence/D/source-index.md#s02)、[S18 LLM judgeの偏り](../../../evidence/D/source-index.md#s18)、[S19 実操作と検出限界](../../../evidence/D/source-index.md#s19)。

**Constraints / Exceptions:** S18は会話応答の評価研究でありUI批評の精度を示さない。匿名化/順序反転の採用は本Skillの予防的な推論。同一モデルの別agentには共通誤りが残る。**Dependencies:** 独立実行器、アクセス制御、未公開oracle。**Confidence:** context分離と実アクセス隔離を別項目にし、成立しなければ昇格は暫定扱い。

<a id="d10"></a>

## D10 — 証拠の範囲で回帰とゲートを判定する

- **Trigger:** 統合、リリース、Skill昇格、修正済み所見の再確認。
- **Inputs:** 事前受入条件、current artifact hash、所見状態、全case結果、証拠manifest、独立評価receipt。
- **Decision Rules:** 記録の妥当性、対象UI、Skill昇格を分ける。重大な確認済み未解決違反はREJECT。必須証拠・case・独立性の不足はHOLD。必要条件を満たした範囲だけREADY FOR INTEGRATION。
- **Procedure:** current hashで所見を再確認し、修正済み/再発/未確認を区別する。case coverageと証拠を突き合わせ、結果とreceiptを保存する。
- **Output Contract:** contract_valid、target_decision、promotion_decision、理由、証拠、未達条件と最小の追加確認。
- **Failure Modes:** 未実行をPASS、古いhashで修正済み、機械構造チェック通過を全UX/WCAGの適合と表示、R-ASI未実装機能を利用済みにする。
- **Verification:** 欠落証拠、改変hash、未知status、重大所見、独立性不足をnegative fixtureとしてゲートの挙動を試す。
- **Sources:** [S08 記録と評価範囲](../../../evidence/D/source-index.md#s08)、[S09 継続評価](../../../evidence/D/source-index.md#s09)、[S12 buttonの実試験](../../../evidence/D/source-index.md#s12)、[S13 tableの実試験と例外](../../../evidence/D/source-index.md#s13)、[S16 自動検査の限界](../../../evidence/D/source-index.md#s16)。

**Constraints / Exceptions:** 上記ゲート名と閾値はCampaignの運用契約。R-ASIが制御・記録のみなら外部検証結果を登録し、その範囲を明示する。**Dependencies:** `qa_gate.py`、実際のreceipt/manifest、独立評価器。**Confidence:** hashは同一性の検証であり意味的正しさの証明ではない。
