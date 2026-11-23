# 評価プロトコル

[入口](../SKILL.md) · [出力契約](report-contract.md) · [原典index](../../../evidence/D/source-index.md)

## 目次

- [評価する差を決める](#評価する差を決める)
- [固定する条件](#固定する条件)
- [ケースの選定](#ケースの選定)
- [ブラウザの観察](#ブラウザの観察)
- [比較の実行](#比較の実行)
- [指標と判定](#指標と判定)
- [独立性](#独立性)
- [回帰と証拠保存](#回帰と証拠保存)

## 評価する差を決める

| 比較 | 変えるもの | 固定するもの | 結論の範囲 |
| --- | --- | --- | --- |
| 評価Skillの追加 | 評価者へ渡すSkill。baselineは既存Art Direction、candidateは既存Art Direction＋D。 | 同一UI、要求、内容、タスク、モデル、利用可能ツール、実行予算、可能な範囲の設定。 | 所見の妥当性・具体性・再現性、case/evidence coverageの差。UIは変えていない。 |
| UI修正のBefore/After | 承認済みの変更範囲にあるUI実装。 | 要求、内容、タスク、環境、測定手順、観察時点。 | 対象症状の解消/回帰。複数変更を単一要因の効果としない。 |

今回のD Campaignは第一行を主比較にする。DでA/B/Cの設計を修正して評価Skillの効果に混ぜない。既存Art Directionには既にQA知識があるため、baselineから関連referencesや手動checklistsを取り上げない。

`qa_gate.py compare`は第一行の同一artifact比較を検証する。UIのhashが異なる第二行を通すためにhashを揃えたり書き換えたりしない。第二行は変更一覧と個別reportを比較記録へまとめる。[既存の同条件比較](../../../references/visual-direction.md#visual-acceptance)・[S14](../../../evidence/D/source-index.md#s14)

## 固定する条件

実行前に入力manifestへ次を記録する。

1. repo/base SHA、対象artifact、要件・実内容・タスクbriefのpathとSHA-256。
2. baselineのルートSkillと読み込み可能なreferences、candidateに加えたD版のhash。
3. 実際の依頼文、出力先、利用可能ツール、実行時間/試行予算。片方だけ診断や期待解を与えない。
4. モデル識別と公開されたsampling設定。不可視のseed/temperatureはunknownとし、同じ設定だと断定しない。
5. browser/version/OS、viewport/DPR、font、locale/timezone、motion、固定data/clock、入力方式。
6. 正常・異常・境界の期待終端、操作数の数え方、採点rubric、除外範囲、未公開oracleの管理者。

ランダムに変わる値は固定データで再現可能にする。外部サイトを使う場合は取得日時・版の限界を明示し、変化を候補の効果としない。ブラウザ状態は各試行で初期化する。[S08](../../../evidence/D/source-index.md#s08)・[S14](../../../evidence/D/source-index.md#s14)

## ケースの選定

最低2種類の仕事を選ぶ。例えば取引/申請の完了と、一覧から対象を探して処理する仕事を選ぶ。単に同じフォームの色を変えた二例で済ませない。

| case | 選ぶ条件 | 観察するもの |
| --- | --- | --- |
| normal | 実際に多い開始状態と有効な入力。 | 主目的への到達、結果の一意性、操作数、状態の説明。 |
| error | 要求で想定される入力エラー・処理失敗・外部依存失敗。 | 問題の識別、入力保持、再試行/取消し、復帰後の終端。 |
| boundary | 最小/最大、空/一件/多数、長いラベル、狭幅、keyboard等、実際の契約の境界。 | 正しい拒否/許可、欠け・重なり、状態の整合、到達可能性。 |

無関係な異常を数合わせに追加しない。例えば完全に読取専用の画面で保存失敗を作らず、空結果・取得失敗・再読込のどれを対象にできるか決める。適用不能は理由を記録する。ただしv1の機械ゲートはnormal/error/boundaryを要求するので、意味のあるcaseを定義できないときは適用範囲を明示してHOLDとする。

利用者研究の課題briefには目的を示し、画面の正解ラベルやクリック順を教えない。一方、回帰テストと所見の再現には具体的な操作列を残す。この二つは別の文書にする。[S05](../../../evidence/D/source-index.md#s05)

## ブラウザの観察

### 実行面を明示する

| engine / 観察面 | 確認できる範囲 | 代替できないこと |
| --- | --- | --- |
| 対象artifactの実ブラウザ | 指定browserで実行した操作・DOM・layout・capture。 | 未実行の実機/OS/ATや人の使いやすさ。 |
| 別版の公開ページ | その公開URLで観察した画面と操作。 | ローカルfixtureやcandidate版の動作。 |
| minimal DOM logic harness | 模擬DOMとstubの範囲で実行したJavaScript分岐。 | native validation、CSS layout、focus、実機操作。 |
| source inspection | コード中の条件・属性・イベント処理の記述。 | 実際の描画や操作結果。 |

engineをreportのevaluation_mode、evidence description、実行ログへ記す。対象のブラウザ起動がsocket権限等で拒否された、またはfile URLがpolicyで拒否された場合、その制約を迂回しない。独立して可能なコード/ロジック確認を続け、ブラウザcaseはblocked/not_runとして残す。logic probeの成功とブラウザの未実行を一つのPASSにまとめない。

### 状態を作ってから撮る

同じartifactを開き、ケースの開始状態へ戻す。fontと画像の描画、非同期の終端を確認する。任意の長いsleepだけで状態到達を推定せず、要素や状態変化を確認する。pending自体を評価する場合はpendingを撮ったことを明示する。

画面全体で位置関係を確認し、必要なら症状のregionを補助画像で残す。ブラウザ・viewport・DPR・入力方式を画像と結び付ける。外部通知やアニメーション等をmaskするなら、対象region・理由・評価から外れた範囲を残す。[S14](../../../evidence/D/source-index.md#s14)

### 画像と操作を組み合わせる

各ケースで最低限、開始状態、問題が現れる状態、最終状態に対応する証拠を選ぶ。すべての操作ごとに画像を大量保存する必要はないが、所見と完了条件を証明できる状態は欠かさない。動作の所見にはtrace/test logを付ける。traceのconsole/network/DOM/screenshotのどれを観察したかを記す。[S15](../../../evidence/D/source-index.md#s15)

keyboardの場合はTab/Shift+Tab、必要なEnter/Space/Escape等を実際に使い、可視focus・順序・到達/退出を確認する。要素へスクリプトでfocusを当てたことだけでは通常のkeyboard到達を証明しない。ダイアログの開閉後は次に作業を続けられる位置を確認する。[S10](../../../evidence/D/source-index.md#s10)・[S12](../../../evidence/D/source-index.md#s12)

tableは必要な横スクロールを一律の欠陥にしない。対象セル・操作へ到達できるか、幅・入力方式・支援技術による条件を確かめる。原典側が例外付きの結果を記載している場合、その例外を消して全面合格にしない。[S13](../../../evidence/D/source-index.md#s13)

自動a11y検査を行った場合はツール/版・ルールsubset・検査対象状態を残す。未検査の支援技術や利用者参加を済んだことにしない。自動検査0件は全WCAG適合ではない。[S07](../../../evidence/D/source-index.md#s07)・[S11](../../../evidence/D/source-index.md#s11)・[S16](../../../evidence/D/source-index.md#s16)

## 比較の実行

1. 入力manifestとrubricを固定し、baseline/candidateを同じraw課題で実行する。Skillの追加以外の差は記録する。
2. 別のfresh contextを使い、前の条件の所見・疑い・意図した修正を渡さない。両出力を変更前に保存する。
3. 原文の生出力を匿名IDで評価者へ渡す。比較順を入れ替えた確認も可能だが、二つの順序を独立した大標本と数えない。
4. 評価者がraw artifactと操作証拠を照合し、各所見の支持/反証/判定不能を記録する。正解集合が不完全ならrecallを全欠陥に対して計算しない。
5. 両出力を凍結した後で対応を開示し、差分・不一致・失敗試行・費用/不明を保存する。
6. 修正後は変更版のhashで関連するnegative/positive fixtureを再実行する。前の合格を新しい版へ自動継承しない。

baselineへD契約を与えずに比較する場合、baselineが自由文を返すこと自体を「UXの検出に失敗した」とは数えない。内容が具体的で再現可能なら支持された所見として採点し、機械処理可能な形式の差は別の指標にする。

## 指標と判定

| 指標 | 数え方 | 主張しないこと |
| --- | --- | --- |
| 支持された所見 | raw artifact/実操作/要求で裏付けられた原子的所見。重複は一件にまとめ、元IDを残す。 | 指摘が多いほど良い、少ないほどUIが良い。 |
| 誤検出 | 根拠に反する、症状が存在しない、適用外の規則を違反とした所見。 | 再現できないものを直ちに誤検出。再現環境が違う場合は判定不能。 |
| 未検出 | 固定oracleの既知で適用可能な欠陥に対する見逃し。 | oracleにない全欠陥の数。 |
| 所見の具体性 | 位置・症状・根拠・影響・修正方向・再現の6項目が意味を持って揃うか。 | 単に文字列があるだけで6点。 |
| タスク/case coverage | 選定caseの実行数、未実行、完了/失敗、復帰を別に報告。 | 自動case通過率を人間の成功率。 |
| 証拠の追跡 | artifact/証拠hash、状態、所見/実行からの参照が整合するか。 | hashが合えば所見も真。 |
| 操作数 | 事前定義した単位で数える。再試行・戻り・余分な操作を別記。 | タスクや入力方式が違う数を比較、クリック短縮だけで改善。 |

操作数の例: 一回の目的を持った入力欄への入力を1、明示的な選択を1、submitを1とする等、今回の数え方を明示する。キーストローク数を使うならpasteと一文字入力の違いを残す。普遍的な単位や上限として固定しない。

部分成功は理由付きの別状態として報告し、序数に任意の重みを付けて平均しない。固定fixture上の単発比較は記述的結果であり有意差・一般化の証明ではない。[S04](../../../evidence/D/source-index.md#s04)

## 独立性

| 成立しているもの | 言えること |
| --- | --- |
| 作者が自分の成果物を確認 | self-check、回帰の観察。独立評価ではない。 |
| fresh contextの別agent、診断/他者所見を未提供 | 文脈を分けた評価。共有OSならファイルアクセスの隔離は未証明。 |
| 別の評価者と明示されたblind手順 | 相互影響を抑えた評価。モデル共通の誤りや順序効果は残り得る。 |
| 上記に加えアクセス制御されたholdout、信頼できるreceipt | protected blindの実施条件を満たした範囲の昇格証拠。真正性を別途監査。 |

S18は会話応答を扱う研究なので、UIレビューが同じ精度になる根拠にはしない。匿名化・順序反転は予防措置として採用し、実際のartifactと操作を優先する。[S18](../../../evidence/D/source-index.md#s18)

このCampaignでprotected blindが成立しない場合、所見比較や局所試験を保存しても正式昇格はHOLDにする。Candidateがoracleを見ていないという自己申告だけを隔離証拠にしない。[S02](../../../evidence/D/source-index.md#s02)・[S19](../../../evidence/D/source-index.md#s19)

## 回帰と証拠保存

repoルートで契約検査を実行し、stdout/stderr・終了コード・対象hashを保存する。

```bash
python3 -m unittest discover -s extensions/D/tests -p 'test_*.py'
python3 extensions/D/checks/qa_gate.py report REPORT.json --root .
python3 extensions/D/checks/qa_gate.py compare BASELINE.json CANDIDATE.json --root .
python3 extensions/D/checks/qa_gate.py verify-manifest MANIFEST.json --root .
```

境界・異常のfixtureを使い、欠けた証拠、hash改変、未知status、重大所見、独立性不足を拒否/保留できることを確認する。新しいルールを通すためだけの実装追従テストにせず、誤った受入を防ぐ条件を検査する。

保存順は、入力 → 生出力 → 実行trace/画像 → 照合結果 → report → 外部receipt → gate結果とする。修正したら新しい試行を追加し、失敗した試行を消さない。保存先はCampaignごとに独立させる。

R-ASIのCLIを確認し、利用可能なcampaign/input/CAS/receipt/cost/gate機能だけを使う。execute/evaluate/promoteが未接続なら外部の試験実績を記録する。独自adapterの実行をR-ASIの改善器や独立oracleと呼ばない。費用が取得できなければunknownを残し、0円と推測しない。
