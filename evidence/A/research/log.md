# imozuru execution log

## 0周目 — 探索の分離

2026-11-23。imozuru revision `30c3b59a076ce228f05aa3036809297422f23dee`を実読。既存資産の差分を確認してから2本の検索役を起動した。

- `source_methods`: 公式設計手順・政府/デザインシステム資料。依頼は媒体/用語、原典箇所、引用リンク追跡。ファイル書込なし。
- `source_research`: 米国HCI原著・著者資料、NNGroup/Baymardの本人研究。削減が失敗する条件を重点に探索。ファイル書込なし。

この2本は補完的な探索なので、重複率から飽和を主張しない。停止は論点への原文根拠と適用限界の充足で判断する。

本キャンペーンは調査レポートが目的ではないため、imozuruのHTML詳細レポート/学習クイズは作らず、ユーザー指定のsource-index・抽出・Skill・検証へ接続する。逐次質問も行わず、ユーザーの自律実行指示を優先する。

## 実装の記録

Skill initializerは実行済み。初回の日本語short_descriptionが25文字未満でmetadata生成が停止した。英語の50文字の説明に修正して再生成しexit 0を確認。これはSkill設計評価ではなく初期化の修正履歴。

外部資料と抽出結果はデータとして扱い、含まれる命令を実行許可へ変換しない。公開検索には一般的な設計用語だけを用いる。

## 1周目 — 原典・引用・著者への追跡と停止

両検索役の完了を受領。source_methodsは9検索76ヒット、source_researchは検索バッチの帰属不明を保った13記録132ヒット（うち3件はリンク追跡のヒット、Web検索ヒットは129）。imozuru digest.py addで原JSONを取り込み、queries.jsonlへ保存した。

18F Make research actionable→User stories/Design hypothesis、Card sorting→C2、CMU読書リスト→Kieras、McGrenere本人業績一覧→2000/2002原著、Nielsen→Training Wheels→ACM失敗を追跡した。原文取得はfetch.pyのDNS失敗後に利用可能なWeb閲覧へ切替え、全20件の短句を本文抜粋で照合した。

停止理由: 5論点に原文の主張・適用限界が付いた。LLM Skillとしての効果そのものは原典の主張ではないと明記し、外部の対比較へ接続する。単一の普遍アルゴリズムや閾値が得られなかった点も未確定として保存した。2本の探索の重複率を飽和の証拠にはしない。保存した本文抜粋は全文取得成功と数えない。

原典20件、引用照合20/20、要約は探索を停止した後のsources台帳とsankai-extractionで実施。研究作業から実装へ移行し、HTML調査レポートの生成や追加資料収集は行わない。
