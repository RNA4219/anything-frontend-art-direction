# SESSION D — 実装・比較・検証結果

## Decision: HOLD

Design QA Skillと実行可能な検査・評価fixtureを実装した。既存Art Directionの理論と手動チェックを再利用し、追加は責務分離、証拠契約、比較条件、回帰ゲートに限定した。コード検査の成功は確認できたが、同じfixtureの実ブラウザ試験と、アクセスを保護した独立blind評価が不足している。正式な昇格PASSは付与しない。

- 実行日: 2026-11-23（日本時間）。Campaign: `anything-frontend-D-20261123`。
- Base SHA: `f5df625dbc577d6a3ca28e13ef09e39b135b4a6f`。
- 独立ブランチ: `campaign/D-design-qa-20261123`。
- 変更対象: `extensions/D/`、`evidence/D/`のみ。共有ルートSkill、README、既存テンプレートは変更しない。
- 入口: [Skill](../../extensions/D/SKILL.md)。[既存との差分](coverage-matrix.md)、[他セッションへの引渡し](handoff.md)。

## 実装と原典

10原則をTrigger → Inputs → Decision Rules → Procedure → Output Contract → Failure Modes → Verification → Sourcesで実装した。各原則に適用条件、例外、依存、確度を付けた。原典indexへ入口から1ホップ、元URLへ2ホップで到達できる。

原典は[20件](source-index.md)、既存5件を再利用し15件を追加した。sankaiは分解工程として適用し、その出力から当セッションがSkillを再構成した。imozuruの20件の直接fetchはDNS失敗を記録し、Web取得で原典を確認した。S17は著者公開abstractのみ。20件すべてを全文査読済みとは呼ばない。第三者本文の取得snapshotはローカル照合専用としGitに含めず、URL・節・短い照合句・取得hash・主張と推論を残した。

現行baseの50追跡ファイルに加え、過去archiveのfindings.md、phase2-issues.md、CASを確認した。履歴CASの205 objectはファイル名hashと一致し、619 receiptを確認した。現行版で既に反映済みの旧課題を未修正として再計上していない。詳細は[prior-assets.json](prior-assets.json)と[分解記録](decomposition.md)を参照する。

## 実行済み検証

| 検証 | 観察結果 | 証拠と意味 |
| --- | --- | --- |
| Skill構造検査 | 入口frontmatterはbundled validatorで有効。主要ファイル間の108ローカルリンクに欠落なし。 | `tooling/skill-structure.json`。意味的な原典適用の正しさまで証明するものではない。 |
| JSONゲートの単体・mutation検査 | **56 tests成功**。rootと別レビュー担当の実行で確認。 | `tooling/gate-tests-root.log`、`gate-tests.log`。型、重複、path escape、hash、証拠不足、比較条件、HOLD/REJECTなど。合成receiptを使うテストは独立評価ではない。 |
| 実HTML scriptのlogic probe | **10検査成功**。既知の3問題を検出。 | `evaluation/logic-probes.json`。Node vmと最小DOMでの限定実行。CSS、native validation、focus、実操作は未検証。 |
| 検査コードの別コンテキストレビュー | **3件検出し修正、修正後8条件を確認**。 | `gate-code-review.md`、`gate-review/postfix-results.json`。実ブラウザを使わないsynthetic stubによる判定・制御フローの検査。 |
| Candidateが出力したreport契約 | **3件ともcontract_valid=true**。対象はREJECT / REJECT / HOLD、昇格は全件HOLD。 | `evaluation/candidate-gate-results.json`。重大な既知欠陥を持つfixtureのREJECTと、QA Skillの昇格判断は別。 |
| Candidate artifact manifest | **11件照合、整合性確認**。 | `candidate-manifest-gate.json`。hash一致は画面品質の合格ではない。 |
| 別checkout向けのreport再照合 | 11 artifactの相対パスを一時領域へ復元し、元report bytesを変更せず上記3判定・manifestを再現。 | `evaluation/replay-results.json`。初回はreportをroot外から渡して拒否され、`replay-initial-results.json`に保持。helperを修正した後の実行は終了0。 |
| 固定fixtureのブラウザ試験 | **BLOCKED、8件すべてnot_run**。 | `browser-fixtures/result.json`、`browser-fixtures-run.log`。Chromium起動のsocket EPERM。修正後runnerの実ブラウザ枝も未検証。 |
| 公開済み2作例の実ブラウザ操作 | 映画の日付切替・詳細開閉、ラジオのmodal/Escape/focus復帰・選局・停止を観察。 | `browser-public/trace.json`と4枚の画像、DOM記録。別の公開対象であり固定fixtureやSkill効果の証明へ流用しない。 |

### 検査コードに加えた3修正

1. 失敗後の復帰判定を名前・メール保持だけで完了させず、人数も保持し、再入力なしの再試行後に件数1・人数2・受付番号C-001まで確かめる。
2. 一覧の「次へ」を行数3だけで合格させず、ページ番号・総件数・行IDを照合する。filterとclearも同じ集合の整合を確認する。
3. trace/context/browser/Playwrightの終了処理が失敗しても、観察とcleanup errorを残したBLOCKED JSONを保存する。

修正前runnerのSHA-256は`2b4fc653b5c553d97c2058f13356d53fca4ddbb40d8a7d59690d755e8586eb31`、修正後は`6b25a31324fa9ca465a73159d36167549d4a9ec31efd24d19df65dea1959df23`。変更したのはDの検査器であり、評価対象のHTMLは修正していない。修正前proofと結果も保存した。

## Baseline / Candidate比較

[比較表と解釈](evaluation/comparison.md)、[機械可読比較](evaluation/comparison.json)、[別コンテキストでの判定](evaluation/adjudication.md)を参照する。元レビュー・各入力のhash・実際の実行依頼は`evaluation/`に保存した。

代表タスクは、(1)参加登録・通信失敗・反復送信、(2)一覧・絞り込み・ページ範囲・狭幅の2種類。同一brief、同一HTMLと内容、同一Art Direction入力を使い、Candidate条件だけにD Skillを追加した。両者はfresh contextで親モデルを継承し、モデルoverrideなし。provider snapshot、sampling、seed、tokenと金額は観測できないためunknown。同一のブラウザ制約を与え、各1 trialを実施した。

両出力は既知の実装問題3件を検出し、320px遮蔽を未確認として扱った。検出件数の改善や実UIの改善は示していない。比較対象は追加Skill前後の**レビュー出力**であり、製品画面の修正前後ではない。タスクの実操作数・利用者の完了率・所要時間も測定していない。

2つのレビューの条件名をマスクして別評価コンテキストへ渡したが、構造と参照方法から推測可能である。共有OS上のprompt allowlistであり、アクセスを保護したblind試験ではない。rubricはbaseline出力後、candidate生成前に固定した探索的基準で、完全な事前登録ではない。提示順反転、複数trial、新しい非公開holdout、実利用者評価は未実施。元の候補担当へrubric・他条件の答案・判定結果は渡していない。

CandidateのJSONに対するゲート実行は自己確認、匿名化後の評価は別コンテキストによる確認である。どちらも独立Oracleの正式receiptへ昇格させない。

## ブラウザで観察した範囲

ローカルChromiumはsocket権限不足で起動できず、cloud browserのfile URLもpolicy拒否だった。この拒否を別URL公開や別実行経路で回避していない。既存READMEにある公開URL2件は別対象として操作した。

公開作例の環境は1363×936 CSS px、DPR1。browser versionと公開buildのGit SHAは未確認。4枚の画像は映画詳細の開閉、ラジオmodalと停止状態である。音声UI状態は見たが音響品質は評価していない。比較fixtureの320pxレイアウト、全keyboard経路、native validation、支援技術、実機touch、複数OSは未確認である。

## R-ASIと証跡

実装v0.0.2、source revision`f5b638085dece1f997210f9b653aceb8fe9b32d4`を隔離コピーしてCLI契約を確認した。`execute/evaluate/promote`は実行してexit3「未接続」。外部のLLMレビュー、Node検査、ブラウザ操作をR-ASIが実行したとは記載しない。

`verify → pipeline → cas-verify`は実行済み。10単位・14原文参照を検査し、未昇格候補を包装した。candidate IDは`1778284f75f9d348edfb33f41fe17aa725ef3be9597eb035053087609f9d186b`、CAS object SHA-256は`37b43571a69d9a6eccb2f6a17e011baafa425738d014fc7649a201412c387358`。candidateはquarantined / promoted=false。一般画像やログをcandidate専用CASへ偽装投入せず、hash manifestをexperienceのevidence_refで参照した。

初回の実績は[rasi/actual-recording.md](rasi/actual-recording.md)、最終比較を追加した記録は[rasi/final-recording.md](rasi/final-recording.md)を正とする。過去snapshotは変更しない。native receiptは`rasi/.ga/receipts/`、CLIの実stdout・stderr・終了値は`rasi/logs/`にある。

runtime image digestと凍結policyの未観測値を捏造しなかったため、native campaign-checkはexit2。費用台帳には測定できたCLI子processのwall timeと、未測定のtokens/USDを別々に記録した。unknown用の数値0 placeholderは実費0を意味しない。cost-reportもexit2で予算評価不能。総費用・費用対効果は算出していない。

## 最終受入条件との対応

| 条件 | 状態 | 証拠・残る制約 |
| --- | --- | --- |
| 既存Art Directionと不必要に重複しない | 実装済み | coverage-matrix。造形・配色・書体の原則を再実装しない。 |
| 具体的な入力から判断へ進める | 実装・適用済み | 10原則、依頼例、2タスクの実レビュー。 |
| 原典と判断を追跡できる | 実装済み | 20原典のURL、節、日付、主張・推論・制約。 |
| 呼び出し可能なSkill構造 | 実装済み | SKILL frontmatter、references/examples/checks/tests。個人Skillへのインストールは対象外。 |
| 実行可能な検証 | 実装・一部実行済み | 56契約検査、logic probe、browser runner。実fixtureのbrowser8件はblocked。 |
| 重大な矛盾・依存欠落 | 今回のレビュー範囲では残件なし | runner3件を修正。真正性・隔離・観察の意味はCLIで証明できない。 |
| 検証済みと未検証の区別 | 記録済み | actual browser / 別公開版 / 最小DOM / sourceを分離。 |
| 他セッションとの競合防止 | 隔離・範囲限定 | 独立clone・Dブランチ。root routingはhandoffへの提案のみ。 |
| R-ASIに実行範囲の証跡 | 記録済み・機能限界あり | 実CAS、receipt、experience、cost。実行器・Oracle・昇格は未接続。 |
| 正式昇格に十分な独立評価 | **不足** | protected blindと新規holdoutがないためHOLD。 |

HOLD解除に必要な最小作業と他領域の依存は[handoff.md](handoff.md)に記した。証拠不足をコード検査の成功で置き換えず、今回の成果は独立して取り込める変更セットとして保存する。
