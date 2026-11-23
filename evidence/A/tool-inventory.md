# SESSION A — 使用ツールと実行境界

確認日: 2026-11-23。現行ファイル・CLIを確認した事実を記録する。

| ツール | 実体・取得元 | 固定revision | 使用方法 |
|---|---|---|---|
| imozuru | [MaryCache/imozuru](https://github.com/MaryCache/imozuru) の `skills/imozuru/` | `30c3b59a076ce228f05aa3036809297422f23dee` | Skillによる原典探索、`scripts/fetch.py`による取得・取得ログ、`scripts/digest.py add`による検索記録 |
| sankai | [RNA4219/sankai](https://github.com/RNA4219/sankai) の `skills/sankai/` | `0e2521453ad758cfb680110da0fdddc994d000be` | `SKILL.md`と分解・理解・溶解のreferenceをエージェントが適用。専用自動分解CLIはない |
| R-ASI | 認証済み接続で取得したprivate source snapshot。ソース本文はこの成果物に含めない | `f5b638085dece1f997210f9b653aceb8fe9b32d4` | Python module `rasi` version `0.0.2`。契約検証・candidate変換・CAS・receipt・experienceを実行 |

## 確認した結果

- R-ASIのruntime・schema・testの29ファイルは、固定revisionのGit blob SHAと照合して29/29一致した。
- `python3 -m rasi --version`は`0.0.2`、`--help`は18コマンドを返した。
- `execute` / `evaluate` / `promote`はそれぞれ実行してexit 3（未接続）を確認した。実行・独立評価・昇格をR-ASIが行ったとは扱わない。
- R-ASIは失敗したコマンドのreceiptを生成しない。失敗は[実行ログ](rasi/run-log.jsonl)と、ログを参照する実際の`experience-add` receiptに保存する。
- upstreamのpytestスイートはpytestがこの環境にないため未実行。READMEに記載された過去のテスト数を今回の成功数に転記していない。

## CASと評価の境界

`cas-store`が受理するのは`skill-candidate/v1`だけで、任意の画像・ログ・JSONを保存する汎用CASではない。元文書のSHA-256・行数・行範囲引用を備えた`rasi-sankai/v1`を`verify`と`pipeline`へ渡し、未昇格candidateを生成・保存する。外部試験と画面artifactは実bytesのSHA-256 manifestで関連付け、`experience-add`のprovenanceへ記録する。

R-ASIの`evaluation-policy/v1`はnoise calibration、統計方法、閾値、holdout identityを要求し、`rsi-lock/v1`はruntime container image digestを要求する。実測・確認できない項目を架空値で埋めない。Campaign gateを実行可能な条件が揃わなければHOLDとし、形式検証の成功を設計品質や正式昇格のPASSに読み替えない。

費用の実測値がない場合は未計測と記録する。ゼロ円・ゼロtokenとして報告しない。R-ASIのbudget判定に必要な換算係数・上限が未定義なら判定不可のままとする。

## 再実行の入口

R-ASI 0.0.2の上記revisionを利用可能にした環境で、リポジトリから次を実行する。`RASI_SOURCE`はprivate checkoutへのパスを利用者が指定する。

```bash
PYTHONPATH="$RASI_SOURCE" python3 -m rasi --root evidence/A/rasi --version
PYTHONPATH="$RASI_SOURCE" python3 -m rasi --root evidence/A/rasi experience-add --experience inputs/tool-discovery.json
```

記録一覧は[discovery manifest](rasi/discovery-manifest.json)および[R-ASI記録](rasi/record-index.md)を参照する。sankaiの10単位を公開実装revisionへ結び付けた[CAS実記録](rasi/sankai-cas-published-manifest.json)も保存した。格納されたexperienceの`status=active`は記録が有効という意味で、Skillの昇格・登録・独立評価合格を意味しない。
