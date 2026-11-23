# SESSION D — 既存対応・追加・未解決

基準版: `f5df625dbc577d6a3ca28e13ef09e39b135b4a6f`。確認日: 2026-11-23。ルートSkillとREADMEは変更対象外。既存の知識・手動手順を「未整備」と一括して扱わず、Dの追加は実行と評価の契約へ限定する。

「新規追加」は今回のD実装対象を示す。個々の実行成功・失敗は [validation.md](validation.md) を正とし、この表だけで試験済みと判断しない。原則番号は [sankai分解](decomposition.md) の番号。

| 要求領域 | 既存対応（基準版に存在） | 新規追加（Dの差分） | 未解決・他担当との関係 |
| --- | --- | --- | --- |
| Visual DesignとUXの責務別評価 | `visual-direction.md#visual-acceptance`: 見える差と計算・操作を別記。`c-usability.md`冒頭: 予測と利用者観察を分離。 | D01/D02: functional / information_architecture / interaction / visual / implementationの主責務、要求・タスク・意図への追跡。 | A/B/Cの契約を統合時に受領する。Dだけで各設計を置換しない。 |
| ヒューリスティックの根拠 | C-01〜12、C3-01〜11で基準選択、適用条件、独立観察、統合。 | D03: 出典種別・節・適用理由・例外・severity理由を所見へ接続。 | 自動欄検査で根拠の意味まで保証しない。未取得原典は別状態。 |
| 批評の具体化 | ルートSKILL「レビューでの使い方」、visual-direction末尾の制作メモ。 | D02: 位置・症状・根拠・影響・修正方向・再現の必須契約、仮説/確認済み/誤検出を区別。 | 題材・文章の好みは除外。ラベルや文量の操作影響は責務付きで扱う。 |
| タスク完了性 | C4-03/04/05/14で行動単位・初見操作・結果確認。K1-13で完了の明示。 | D04: 初期/終端、完了oracle、trace、実保存と模擬成功、未完了と判定不能の記録。 | 実利用者の完了率は別試験。Aの目標、Bの期待状態に依存。 |
| 操作回数 | K3-13/14で情報量、移動回数、探索を分ける。 | D04/D08: 操作単位の事前定義、同条件での数え方、再試行・逸脱も記録。 | クリックが少ないことを単独の改善理由にしない。自動時間を人の時間にしない。 |
| 復帰可能性 | C2-07/08/10/11、forms/motion checklist。optimistic例は失敗時rollbackと再操作抑制を実装。 | D05: 正常・異常・境界の行列、状態遷移・入力保持・再試行の証拠。 | 既存の模擬保存を実バックエンド耐性と見なさない。改善実装はB/C。 |
| 視覚階層・整列・密度 | visual-composition「発見と比較・操作で密度を変える」、広幅/狭幅、visual-craft「情報量で強弱を変える」。 | D06: taskとの対応を持つregion所見、幾何観察・認知影響仮説の分離。 | 意図的な非対称や密度を普遍的欠陥にしない。Art Directionの意図を維持。 |
| Before/After | visual-acceptanceに同じ目的・文言・データ・幅・状態での比較。局所修正の例外あり。 | D08: 固定manifest、内容hash、変更因子・モデル・全試行・比較単位の追跡。 | 比較は対象ケースの証拠。Skill追加の因果や一般化は独立評価・追加試行待ち。 |
| スクリーンショット | visual-directionで実画面、visual-compositionで実機/エミュレーション区別、visual-craftで実描画font確認。 | D07: 環境・状態・取得方法とhashの保存、画面とtraceの対応、境界状態capture。 | screenshotだけでは操作や読み上げ未確認。実機touch/複数OS/支援技術は実行範囲に応じて残す。 |
| ブラウザ検証 | 4種checklists、11個のオフラインHTML templates。dialogのfocus/Escape、formの不正値/draft、optimisticの模擬失敗を確認可能。 | D05/D07/D10: 再現可能な実行器、fixture、receipt、回帰ゲートへ接続。 | baseに自動テストrunnerは未同梱。既存手動テンプレートの不在とは言わない。 |
| LLM批評の構造化 | K13-04/19/21/23は検出範囲・原因/修正案の別検証・精度と再現率・反復一致の限界。K14-07/23/25は自動検査/構造/全体UXの分離。 | D02/D09: 原子的所見、反証、独立入力、アクセス/contamination申告、評価者manifest。 | 同一agentの自己評価、共有環境の非隔離試験を独立blindと呼ばない。 |
| 評価者差・誤検出 | C5-18/26/28/32/37、C6全体で分母、誤検出、独立所見、重複統合、深刻度の不一致を扱う。 | D03/D09: 指摘件数と妥当性/重要度を分け、既知欠陥と負例の両方で検証。 | 特定fixtureの検出率を全欠陥の再現率へ一般化しない。 |
| 回帰・品質ゲート | visual-acceptanceの保留と追加比較、K15-04/08で実利用の証拠蓄積。 | D10: current hashでの再確認、証拠不足HOLD、重大違反REJECT、要件満足時の統合判断。 | 閾値はCampaignの運用基準。正式PASSは独立評価なしでは認めない。 |
| R-ASI/CAS/receipt | このbaseの50追跡ファイルにはR-ASI実装、CAS、receiptは未同梱。履歴archiveのresearch/findingsには原文位置とCAS短縮hashがあり、research/casも存在する。 | D10: 今回の外部実行の実績と実在するR-ASI CLIへ渡す証拠を紐付ける。 | 履歴receiptの存在と今回実行した証拠を区別。未実装のexecute/evaluate/promoteを利用済みとしない。 |

## 既存資産の扱い

| 資産 | 確認方法と結果 | 扱い |
| --- | --- | --- |
| ルートSKILL/README | 指定baseの内容を読んだ。 | 原則とscopeを継承し、編集しない。 |
| findings.md | baseの50追跡ファイルに未同梱。履歴archiveのresearch/findings.mdでC3/C4/C5/C6/K13/K14の対応を確認。 | 履歴の事実台帳。現行referencesの限定・修正を正とし、新規発見や未修正不具合として数えない。 |
| phase2-issues.md | baseには未同梱。履歴archiveのresearch/phase2-issues.mdを通読。 | P2-I01/02/03は現行ルーティング・11例・4checklistsへ反映。P2-I08の評価根拠も現行C3〜C6に存在。Dは実行契約を加える。 |
| 実装テンプレート | templates/READMEの11例を確認。form/dialog/optimisticのコードを点検。 | 実行fixtureとして再利用可能。Dから元ファイルを修正しない。 |
| CAS | baseに未同梱。履歴archiveにはresearch/cas/objectsと台帳内の短縮hashあり。 | archiveの来歴確認と今回R-ASIに登録したreceiptを分離。CAS詳細点検は親セッションの記録を参照。 |
| 既存テスト | 4種の手動checklistsとテンプレートあり。tests/やpackage.json等のrunnerはbaseに未同梱。 | 手動検証の知識は継承。Dが実行可能検査と結果保存を追加する。 |

## 追加しないもの

配色、書体、造形の一般レシピ、装飾削減の一律規則、空白率やクリック数による単独合格基準は追加しない。Aの機能設計、Bのタスクフロー、Cの部品契約は担当へ戻す。Dの新規所見はその契約の検証と証拠を提供する。

ルートSkillへの導線と他セッションの取り込み順は [handoff.md](handoff.md) に提案し、この変更セットから共有入口を直接変更しない。

履歴archive: `anything-frontend-2026-11-21.zip`、SHA-256 `a72aed865f385941bef5ea67d68be7973308c34c1f7cf56d8efb59be26768657`。履歴P2-I08の強い単独評価禁止を新しい作業禁止として取り込まない。予備レビューと正式昇格の独立性要件を分離する。履歴K13-01の統計表現より、現行K13-01/25の集計条件の区別を優先する。
