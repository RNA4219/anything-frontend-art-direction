# 生成agentへの追加入力

初期指示のbytesは `baseline-prompt.md` / `candidate-prompt.md`、各hashは `generation-inputs.json` に保存した。
生成は新規agent、fork_turns=none、モデル・effortのoverrideなし。指定したSkillと共通入力以外を読まない条件とした。
これは指示による分離であり、OSで強制した秘密境界ではない。

## 生成中の進行連絡

| 対象 | 内容 | 比較上の位置づけ |
|---|---|---|
| candidate | Skill初版をcommit `58bed659cc7f39d316794625ad0475084b38df7e` に保存したこと、生成完了まで親がSkillを書き換えないこと、自己確認コマンドの記録依頼 | 版の固定。評価ケース・点数・他条件のコードは未提供 |
| baseline | 現在の進行と残作業の確認、自己確認後の初回提出を保持すること、他arm・共有評価を読まないこと | 進行確認。修正指示・評価結果は未提供 |
| candidate | baselineの提出が終了したこと、decision logと自己確認をまとめて初回提出すること、追加調査や任意の検査拡大は不要であること | 提出順の情報は伝えた。baselineの内容・自己テスト数・成績は伝えていない |

この進行連絡まで完全に同一のprompt列だったとは主張しない。同一モデルの正確なserver revision・seedも取得できない。
初回提出後に共通40ケースを実行し、結果による生成物修正は行っていない。
保存済みcontrollerの再実行と、初版Skillからの確率的な生成の再現を区別する。
