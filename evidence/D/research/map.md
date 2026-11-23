# map: design-qa-evaluation

問い: 既存の視覚表現・仕様索引を壊さず、LLMがデザイン批評を再現可能な証拠と比較Gateへ変換するには何を追加するか。
題: デザインQAの評価契約
読み: でざいんひょうか
最初の検索語: heuristic evaluation severity task success accessibility evaluation visual comparison

## 調査の論点
- [x] この分野の知見はどの一次媒体に集まっているか。
- [x] デザイン批評を位置・症状・影響・再現手順へ変換する元の評価方法は何か。
- [x] 完了性・復帰・境界・アクセシビリティをどこまで測定でき、何を見落とすか。
- [x] Before / Afterの比較を歪める条件と、視覚差分だけでは判定できないものは何か。
- [x] LLM評価の独立性と誤判定はどう制約されるか。
- [x] 既存Art Directionの視覚意図を維持し、機能・UX・視覚・実装の責務を分離する根拠は何か。

## 用語
- Heuristic evaluation / task success / severity / complete processes / visual regression / LLM-as-a-judge

## 人
- Jakob Nielsen / Raluca Budiu — Nielsen Norman Group（原典本文で確認）
- Kerry Rodden / Hilary Hutchinson / Xin Fu — HEART（原典本文で確認）
- Lianmin Zheng et al. — LLM-as-a-judge（原典本文で確認）

## 媒体
- W3C WAI / Nielsen Norman Group / U.S. Web Design System / Playwright / ACM CHI / NeurIPS

## 原文（sources/）
取得先は raw/sources/（手元での照合専用、再配布しない）。公開用証跡は sources.json と source-index.md。

## 次の手がかり
- WCAG-EM 2.0 は2026年更新。現行版と既存WCAG参照の役割を照合する。

## 論点と原文位置

| 論点 | 原典位置 |
|---|---|
| 媒体 | S07 W3C Recommendation、S17 CHI2010著者abstract、S18 NeurIPS2023 |
| 構造化批評 | S02 Step 2–3、S03 severity factors、S08 Step 5.1 |
| 完了・復帰・境界 | S04 Measuring Success、S06 input preservation、S07 5.2.3、S08 Step 4.2 |
| 比較条件と限界 | S14 Introduction/Generating screenshots、S16 automation warning |
| LLM評価 | S18 3.2/Appendix D.1、S19 PDF p11 |
| 視覚意図と責務 | S20 grouping/scale、既存references/visual-direction.md visual-acceptance |

各照合句・行は ../source-index.md と sources.json。
