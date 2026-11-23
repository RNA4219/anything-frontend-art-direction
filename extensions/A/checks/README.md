# 共通JSON投影とブラウザ観察

両armで同じ `render_plan.py` と `browser_probe.py` を使う。入力planを描画する共通の評価ハーネスであり、生成された設計を修正する工程ではない。

## 凍結planの構造比較

```bash
python3 -B extensions/A/checks/compare_plans.py \
  --briefs-dir extensions/A/tests/briefs \
  --baseline-dir evidence/A/experiment/baseline \
  --candidate-dir evidence/A/experiment/candidate \
  --output /tmp/A-comparison.json
```

各planを同じvalidatorで確認し、ID・処置・画面数・宣言グラフ上の最短距離を報告する。距離は実操作回数ではない。
少ない画面、少ないリンク、少ない未解決事項に加点しない。比較スクリプトのexit 0はレポートの作成成功を示し、planのPASSや昇格ではない。
planごとの`validation.status`、issues、検査範囲を読む。FAILは構造エラーあり、HOLDは構造エラーなしでblocking残件あり、PASSはこの機械検査で両方を検出しなかった場合。

## HTMLとブラウザprobe

リポジトリのルートから実行する。

```bash
python3 -B extensions/A/checks/render_plan.py \
  --brief path/to/brief.json \
  --plan path/to/frozen-plan.json \
  --output path/to/projection.html

python3 -B extensions/A/checks/browser_probe.py \
  --html path/to/projection.html \
  --output-dir path/to/browser-observations \
  --timeout-seconds 90
```

rendererはPython標準ライブラリのみ。probeはインストール済みのPython Playwrightと `/usr/bin/chromium` を使用する。外部ページは開かない。

probeのJSONは出力先の `browser_probe_result.json`、PNGはcase・viewport・role・modeを含む名前で保存する。probeの終了コードは0=観察チェックにfail/errorなし、1=fail/error検出、2=入力・起動・実行の問題、3=時間上限。0でも設計の意味的な正しさを保証しない。

## 投影規則

- 画面のtitle/purpose、機能ラベル、情報ID、入口、navigation、goal routeをplanの宣言から表示する。画面の統合、導線の追加、情報の補完は行わない。
- `screen.information[].id` と `brief.content` の同名属性を直接対応させる。primaryは展開操作なし、secondaryは閉じたdetails内。数値0・false・文字列の実値を保つ。属性欠落・null・空文字は「未提供」と表示する。
- roleを変えると、そのroleに宣言された最初のentryを表示する。entryがなければ画面を選び直さない。roleに許可されない画面や存在しないtargetへの宣言リンクは、クリック時に拒否して診断を示す。
- entry・role・normal/empty/single/manyは評価ハーネスの試験コントロールとして明示する。emptyは0件、singleは実データの先頭1件、manyは実データを40行まで循環反復する。元データ0件なら、どのモードも0件。反復行を新しい実データとは扱わない。
- 保存・送信・取消・公開などの業務処理と、実サービスの認証・認可は未実装。機能一覧はラベルの投影である。
- HTMLは外部asset・外部フォントを必要としない。埋込JSONの `<`、`>`、`&`、行区切り文字をescapeし、データ値はtextContentで表示する。

## 共通の色・書体

入力briefは色名を指定し、数値tokenを提供していないため、次の近似色を両arm共通で固定する。いずれもシステム書体を使う。

| visual_intent.id | 背景 | 文字 | アクセント |
| --- | --- | --- | --- |
| ops-charcoal-01 | `#22252a` | `#f5f5f1` | `#d6a345` |
| catalog-paper-01 | `#f7f1e6` | `#1f314c` | `#b74632` |

未知のvisual_intentはシステム既定色を使い、色定義が未提供であることを表示する。planのvisual_intent_idを独自のbrand案に読み替えない。

## 観察の範囲

probeはdesktop 1440×900とmobile 390×844で、宣言entryとnavigationの実クリック、role別の到達と拒否、JS error、documentの横overflow、primary実値、0件/1件/多件、0値・長いtitleを観察する。宣言されたグラフで到達できないsourceへは、試験用の近道を追加しない。表内の横スクロールとdocument全体の横overflowは区別する。

ブラウザは最初に `chromium_sandbox=True` で起動する。起動できない場合はその理由をJSONへ記録し、自動的にsandboxを無効化しない。所要時間は `--timeout-seconds` で制限する。

結果JSONとviewport screenshotは構造・描画についての観察記録であり、意味上のUX成功率、利用者テスト、設計の優劣を測った結果ではない。共通rendererの生成物を独立したモデル実装と数えない。

主な検査用属性は `data-screen-id`、`data-entry-screen`、`data-nav-index`、`data-information-id`、`data-row-index`、`data-value-state`、`data-visibility`、`data-projection-status`。入力のbrief/planは `script#plan-data` にJSONとして残す。
