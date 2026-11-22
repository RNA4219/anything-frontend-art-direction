# Anything Frontend

題材に合わせて配色・書体・余白・構図を決めるための、日本語のフロントエンドデザインスキルです。制作側の説明と実際の作品を見比べ、どの工夫を自分の画面に取り入れるかを考えます。実装やレビューで困ったときは、12分野・1,464項目の索引から仕様や研究の原文を引けます。

## 作例「潮待ち映画祭」

![潮待ち映画祭のPC画面。夕暮れの港に白い明朝体で映画祭名を掲げ、画面下部に会期・会場・上映日程へのリンクを置いている。](docs/shiomachi-film.png)

架空の港の野外映画祭です。映画祭名には太い「しっぽり明朝B1」、欧文の副題には Cormorant Garamond のイタリックを使いました。上映表では Noto Sans JP の開始時刻の隣に、明朝体で作品名を置いています。日付を選ぶと、その日の2作品を確認できます。

**[作例のHTMLをダウンロード](https://github.com/RNA4219/anything-frontend/raw/refs/heads/main/examples/shiomachi-film/index.html)**してブラウザーで開いてください。PC用・スマホ用の画像、書体、CSS、JavaScriptを1枚に収めているので、オフラインでも上映日の切り替えやあらすじの開閉を試せます。[HTMLのソース](examples/shiomachi-film/index.html)

## スキルを使う

1. [リポジトリをZIPでダウンロード](https://github.com/RNA4219/anything-frontend/archive/refs/heads/main.zip)して展開するか、`git clone https://github.com/RNA4219/anything-frontend.git` で取得します。
2. 展開したフォルダの名前を `anything-frontend` にし、利用するツールのスキルディレクトリにフォルダごと置きます。入口は [SKILL.md](SKILL.md) です。
3. たとえば「anything-frontend を使って港の野外映画祭のページを作って。映画祭名の書体を2案、実際の題名で比べて。スマホでも上映時刻を探せるようにして」と依頼します。

資料は通常のMarkdownとしても読めます。作品の画像や出典の原文は、各項目のリンクから公開元で確認できます。

| 調べたいこと | 入口 |
| --- | --- |
| 題材に合う見本を探し、配色・文字・構図を選ぶ | [制作手順](references/visual-direction.md)・[構図とスマホでの再配置](references/visual-composition.md)・[文字と色の表現](references/visual-craft.md) |
| 百貨店・ゲーム・商業デザインなどの制作例を探す | [世界の作品・資料247件](references/design-works.md) |
| 書体が、どの場面で、どんな理由で使われたか調べる | [書体の調査データと読み方](data/typography/README.md)。247作品・292記録をCSVとSQLiteで収録し、そのうち46作品では具体的な文字処理と制作側が述べた理由を照合しています。 |
| 実装上の問題を再現して確かめる | [11種類のHTMLテンプレート](templates/README.md)・[12分野の索引](SKILL.md)・[出典一覧](sources.md) |
| 画面をレビューする | [アクセシビリティ](checklists/accessibility.md)・[フォーム](checklists/forms.md)・[モーション](checklists/motion.md)・[性能](checklists/performance.md) |

## ライセンス

このリポジトリで作成した解説、調査データの編集・記述、テンプレート、作例のコードと画像は [MIT License](LICENSE) で配布します。

「潮待ち映画祭」に埋め込んだ3書体には、それぞれ **SIL Open Font License 1.1** が適用されます。作例のHTMLには、MITの著作権表示と許諾文、各書体の著作権表示とライセンス全文を収録しています。リンクで紹介する第三者の作品・資料の利用条件は各公開元で確認してください。[同梱物とライセンスの内訳](NOTICE.md)
