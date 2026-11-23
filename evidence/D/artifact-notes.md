# Artifact integrity boundary

`artifact-manifest.json`は最終変更セットの`extensions/D/`と`evidence/D/`にあるGit追跡対象ファイルを列挙し、正規化しないbytesのSHA-256とサイズを持つ。

自己参照の循環を避けるため、manifest自身とその検証結果`artifact-integrity.json`は一覧から除外する。この2ファイルを含む変更セット全体は独立ブランチのGit commit/treeで特定する。Git commit SHAは最終報告を参照する。

第三者本文の全文snapshot（research/raw/）とPython cacheは配布対象外。原典にはURL・節・短い照合句と取得hashを付けた。raw-manifestの取得hashは、この配布物に全文が含まれるという意味ではない。

R-ASIの各manifestはその実行時点で確定した証拠のsubsetを扱う。初回16件と後続31件はimmutable snapshotへ対応し、同じ観察を重複した独立試行として数えない。生レビュー、匿名化コピー、R-ASI保存コピーも別試行ではない。

portable replayは元のreportを変更せず当時の相対pathを復元する。一方、匿名化コピーは表示用ラベルを書き換えた派生bytesであり、元reportのhashをそのまま適用しない。

```bash
python3 extensions/D/checks/qa_gate.py verify-manifest evidence/D/artifact-manifest.json --root .
```

成功が示すのは列挙artifactの整合性である。対象画面の品質、原典解釈の正しさ、評価者の真正性、アクセス隔離を認証するものではない。
