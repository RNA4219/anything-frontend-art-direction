# GitHubへの保存と元のGit履歴

## 保存方法

通常の `git push` は `could not read Username for https://github.com` で失敗し、ghも未ログインだった。
接続済みGitHub connectorの正規Git Data APIで、同じ独立ブランチにファイルtreeを保存する。
mainを更新せず、他sessionのbranchをmerge・force updateしない。

APIはローカルcommitのauthor/dateを指定する契約を公開していないため、remote commit SHAは元のローカルSHAと異なる。
ファイル内容・modeとroot treeのGit SHAが一致することを保存時に照合する。最終remote SHAは実行終了時の報告を参照。
元の3 commitsを改変せず残すため、`original-history.bundle` を同梱した。
R-ASIに記録した生成時・最終Skillのcommit SHAは、このbundleで復元できる元のcommitを指す。

## 元の履歴

| 用途 | Git SHA |
|---|---|
| Base prerequisite | `f5df625dbc577d6a3ca28e13ef09e39b135b4a6f` |
| 生成入力Skill初版 | `58bed659cc7f39d316794625ad0475084b38df7e` |
| レビュー修正後の最終Skill | `6fc0c3dd6c82c4dd2f77764c5da512fbfdbaa911` |
| 検証・R-ASI証跡を含むローカル変更セット | `64e39c7e0cb580ba94620328729e8aba830b2773` |

Bundle SHA-256: `b5b1f3751833dd0aea9d812820793845d76915dfe518e8f247e3416c69e730dd`

このbundleはbaseをprerequisiteとする差分bundle。対象repoのcloneでbaseが存在することを確認してから使う。

```sh
git bundle verify evidence/B/original-history.bundle
git bundle unbundle evidence/B/original-history.bundle
git show 6fc0c3dd6c82c4dd2f77764c5da512fbfdbaa911:extensions/B/SKILL.md
```

`unbundle` は元commit objectsを復元し、branchの移動やmainへのmergeは行わない。

## 証跡の不変性

公開保存のために追加したファイルはこの説明とbundleだけ。
`final-scope.json` は公開保存前の126 pathsのsnapshotであり、公開変更セットはこの2ファイルを加えた128 paths。
全て `extensions/B/**` または `evidence/B/**` に収まる。
R-ASIの78 frozen artifactsと最終Skill12ファイル、両条件の生成物・比較結果は変更していない。
この配送方法の変更は再生成・再評価・正式昇格ではなく、判定は **HOLD** のままである。
