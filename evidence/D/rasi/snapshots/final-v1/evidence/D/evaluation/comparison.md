# Baseline / Candidate — SESSION D

## 結論

**既知問題の検出と修正情報は同等。Candidateは一次責務・証拠・判定を明示する記録上の能力を加えた。検出精度の改善、製品UIの改善、正式昇格は確認していない。DecisionはHOLD。**

| 比較軸 | Baseline: 既存Art Direction | Candidate: 同じ入力＋D |
| --- | --- | --- |
| 既知の実装問題 | 3 / 3検出 | 3 / 3検出 |
| 6要素×3件（位置・症状・根拠・影響・修正方向・再現） | 18 / 18 | 18 / 18 |
| 証拠面を超えて観察済みと断定した対象所見 | 今回の裁定で特定0件 | 今回の裁定で特定0件 |
| 3件の一次責務・ownerの対 | 明示0 / 3 | implementation / Cを明示3 / 3 |
| 320pxでの見出しとボタンの重なり | 未確認の視覚仮説 | 未確認の視覚仮説 |
| 対象版との対応 | HTML2件のpath/hash、ログ、実行環境 | 同じ情報に加えbrief、主要入力、再実行harness、reportをmanifestで結合 |
| 記録・対象・昇格の分離 | 優先度、修正後条件、未確認事項を文章化。昇格の定義はない | contract_valid、target_decision、promotion_decisionを別値で出力 |
| 実ブラウザ完了、実操作数、利用者の成功率 | 未測定 | 未測定、JSONでもnull/blocked |

Baselineにも具体的な修正後条件や正常時の反例がある。Candidateの形式を満たさないことだけで、Baselineの所見を誤りとして採点していない。ゲートがないBaselineが誤って正式PASSを出したという観測もない。Candidateの記録量や診断回数を品質の代用にしていない。

## 対象と条件

- タスク1: 参加登録。正常受付、通信失敗後の入力保持・再試行、人数境界、非同期完了前の反復送信。
- タスク2: 固定8件の依頼一覧。通常のページ移動、真の該当なしと条件解除、ページ移動後のfilter/search、広幅と320px。
- 2条件は同一brief、同一HTML、同一内容、同一Art Directionを使用。Dの8ファイルと原典indexのみをCandidateへ追加した。
- 両担当はfresh context、親のモデルを継承、overrideなし、同じブラウザ制約と目安時間。provider snapshot、sampling、seed、費用はunknown。完全に同一の生成条件は保証できない。
- 各条件1 trial。比較は画面を変更する前後ではなく、同一画面をレビューするときのSkill追加前後である。

入力hashは[input-manifest.json](input-manifest.json)、D条件は[candidate-skill-manifest.json](candidate-skill-manifest.json)、実行依頼は[execution.json](execution.json)。元出力は[baseline-review.md](baseline-review.md)、[candidate-review.md](candidate-review.md)。元出力を後からD schemaへ変換してBaselineの能力を上積みしていない。

## 既知ケースとの対応

| 既知ケース | Baseline所見 | Candidate所見 | 扱い |
| --- | --- | --- | --- |
| REG-DUP | REG-01 | D-REG-02 | 完了前の2 handler呼出しでcount=2、C-002。最小DOMロジックの観察。 |
| REG-LOSS | REG-02 | D-REG-01 | 失敗分岐で名前・メールが空、人数1。ソースと限定したreset stub。 |
| LIST-PAGE | LIST-01 | D-LIST-01 | 同じ原因の範囲外ページ。Baselineは2ページ目、Candidateは3ページ目からfilterした別trace。重複加算しない。 |

0件という正常な検索結果、承認済み意匠、通常フォームに存在するnative validationを、両者ともそれ自体の欠陥としなかった。狭幅の重なりの真偽は実描画がないためunknown。検出成功・誤検出の分母に入れない。

## 別コンテキストでの裁定

[adjudication.md](adjudication.md)と[adjudication.json](adjudication.json)が別評価担当の生出力。条件名だけをマスクしたQ/R入力を作り、乱数で割り当てた。対応はQ=Baseline、R=Candidateで、評価担当には渡さず、裁定後にここで解いた。原出力は保存し、マスクされた派生コピーのhashを別に管理した。

判定担当は入力ディレクトリ内のみを読み、元レビュー、Skill、親のassignmentを読まないと申告した。ただし構造から方法を推測でき、共有OS上で物理的な読み取り遮断はない。**完全blind、protected holdout、独立Oracleによる正式評価とは呼ばない。** rubricはBaseline生成後・Candidate生成前に凍結したため、完全な事前登録ではない。提示順反転も未実施。

両者の3/3と18/18はこの固定ケース内の観測値であり、未知の製品に対する再現率・適合率・使いやすさの改善率ではない。全体点や勝者を設定していない。Candidateの引渡し情報の明示を採る実務上の根拠は得たが、読み手の作業時間やミス減少までは測っていない。

## 原記録の再検証

`replay_reports.py`はこのcheckoutの同一hashの11artifactを一時領域へ写し、当時の相対パスを再構成する。元reportを編集せず、3件のcontract_valid=true、対象REJECT/REJECT/HOLD、昇格全件HOLD、manifest整合性を再現した。これはrootによる外部照合であり、Candidate担当や裁定担当が行った実行として数えない。

```bash
python3 evidence/D/evaluation/replay_reports.py --output /tmp/design-qa-replay-new.json
```

既存出力は上書きせず新しいファイル名を使う。初回helperのpath選択不備は`replay-initial-results.json`に残し、修正後は`replay-results.json`に記録した。UI試験やLLM生成を再実行するコマンドではない。

正式昇格には、同一fixtureの実ブラウザ結果、未知のholdout、アクセス分離、複数trial・提示順の確認が残る。詳細は[validation.md](../validation.md)と[handoff.md](../handoff.md)を参照する。
