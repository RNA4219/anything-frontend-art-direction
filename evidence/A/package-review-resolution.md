# パッケージ監査の処置

元の [package-review.md](package-review.md) はv1に対する観察として保持した。生成者が作った4つのplanは変更していない。

| ID | 処置 | 実証 |
|---|---|---|
| PR1 必須機能の孤立を通す | v2でmandatory入力featureの正本をrole別に到達検査。v3でmandatory=falseの機能が唯一のmust達成能力を担う境界も検査 | 新37件をv1に当てて赤→v2で緑。さらに新40件をv2に当てて該当1件が赤→v3で40件すべて緑。別entry・role別配置・到達可能な代替は保持 |
| PR2 多段mergeを通す | targetが直接keep正本であることを検査。aliasを依存先として参照することは許可 | v2の多段拒否・直接alias依存の正例が成功。多段を許す旧テスト期待を文書に合わせて訂正 |
| PR3 FAIL/HOLDの記述差 | plan-contractとA10に、構造errorがあるとFAIL優先、blocking残件もissuesへ保持すると明記 | 既存status優先順位テストは維持。文書の差分を目視照合。生成入力snapshotは変更せず、後段の明確化として記録 |

最終checkerのSHA-256は `de5abbc23d003e5401830d6776bb043b21ee3912f82291389081068a98893e68`。
実テストと修正履歴は `runs/validator-v2-review-fixes.json`、`runs/validator-v3-goal-reachability.json`、`runs/validator-v3-tests.txt`。
v2の中間code bytesも `runs/checker-history/v2/` に保持した。これは当時の原本保存であり、そのコピー先がテストの実行ディレクトリではない。

旧checkerと最終checkerで4案を評価し、すべて構造エラー0件で変化なし。検査器修正が追加Skillの比較優位を作ったという結果ではない。
形式上の修正完了を、独立評価・実利用の効果・正式昇格へ読み替えない。キャンペーンGateはHOLD。
