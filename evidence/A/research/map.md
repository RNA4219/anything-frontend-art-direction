# map: product-design-information-architecture

問い: 既存Art Directionと重複せず、画面に機能を置く前のProduct Design / Information Architectureを実行可能な判断へ分解するには、どの一次資料と条件が必要か。
題: 機能と情報構造の設計
読み: きのう じょうほう こうぞう せっけい
最初の検索語: user needs task analysis information architecture feature prioritization

## 調査の論点

- [x] 知見が集まる媒体・原著はどこか。実務助言と実験結果をどう区別するか — S11/S13/S14/S15。著者公開原稿・研究誌/会議・公式ガイドを区別。索引とlimitsに版・観測条件を保存。
- [x] ユーザー目標と機能要件を対応付け、未充足/冗長な機能をどう検出するか — S01 §6.2.1.2.3、S11 Introduction、S12 §2.3。
- [x] 機能の削減/統合/段階的開示が失敗する条件は何か — S14 §7、S15 Limitations、S16 Usability criteria、S19 visibility改訂。
- [x] 分類・ナビゲーション・タスクに基づく画面構造を視覚意匠から切り分けてどう決めるか — S06 How to do it、S09 Task hierarchy、S17 Define IA、S18 filters/categories。
- [x] LLMが実務で使用可能な独立Skillとして何を検証でき、利用者調査なしには何を確認できないか — S03仮説と指標、S12代表タスクの限界。LLM固有のSkillの有効性は原典が立証せず、今回の外部試験でも限定的に確認する。

## 用語

- bidirectional traceability / self-derived requirement — S01
- user story / design hypothesis / task flow — S02/S03/S05
- task analysis / design of functionality — S11/S12
- objective/subjective bloat / adaptable interface — S14/S15
- IA / taxonomy / global/local / canonical destination — S09/S17。canonical ID契約は本Skillの導出。
- progressive / staged disclosure — S16
- overcategorization / category-specific attribute / comparison — S18/S19/S20

## 人

- David Kieras — S11の著者公開原稿。
- Clayton Lewis / John Rieman — S12の本人教科書。
- Thompson / Hamilton / Rust — S13の公開working paper。
- Joanna McGrenere / 共著者 — S14/S15の著者公開採択原稿。
- Jakob Nielsen / Jen Cardello — S16/S17の本人の方法論。
- Baymardの記事署名者 — S18/S19/S20の本人研究記事。

## 媒体

NASA Systems Engineering Handbook、旧18F公式文書の保存版とC2本人記録、USWDS、IBM Carbon、W3C/WAI、Michigan著者ページ、HCIBIB、MSI、Graphics Interface/ACM CHI著者原稿、NNGroup、Baymard。CMUの講義読書リストを入口にKierasをたどった。媒体の発見過程と未採用候補は2検索ログを参照。

## 原文（sources/）

原文全文は再配布しない。ネットワーク制約でfetch.pyは10件ともDNS失敗。Web閲覧による原典の本文抜粋をrepo外のresearch-A/sourcesへ保存し、完全なHTML/PDFとは区別した。公開成果にはsource-index、原文短句、該当箇所、snapshot hashを残す。

| source IDs | 確認した本文snapshot | 取得経路 |
|---|---|---|
| S01–S06 | parent_method_open1/2、parent_open7/8 | 検索→公式/保存版→リンク追跡 |
| S07–S10 | parent_method_open2、parent_open3/7/8 | 18Fの作例リンク、WAI元文書、公式パターン |
| S11–S15 | parent_open4/5/7/8 | CMU→著者、本人業績一覧→原著、MSI公開稿 |
| S16–S20 | parent_open3/6/7 | 本人記事→根拠/改訂/隣接研究 |

各引用が入るsnapshotはquote-verification.jsonの全20レコードに対応。原典の節とWeb抽出行番号はmethod-sources/research-sourcesに記録。

## 次の手がかり

探索停止。追加探索で実装を遅らせない。未取得のCarroll原研究、Feature Fatigue刊行版全文、Kieras版年は制約として残す。代表利用者での分類/探索検証と長期利用は統合後の別評価で扱う。
