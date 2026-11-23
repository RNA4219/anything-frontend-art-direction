# SESSION B — integration handoff

## 状態

**Decision: HOLD。** B単独のSkill・再現fixture・実行証拠を独立ブランチへ保存する。
ブラウザー実操作と独立blind評価が成立していないため、正式な効果判定・昇格を承認しない。
実測件数・比較結果・修正履歴は [validation.md](validation.md) を正とする。

- 対象repo: `RNA4219/anything-frontend-art-direction`
- Base SHA: `f5df625dbc577d6a3ca28e13ef09e39b135b4a6f`
- Branch: `campaign/B-interaction-ux-flow`
- 比較生成に使用したSkill初版の保存commit: `58bed659cc7f39d316794625ad0475084b38df7e`
- 変更対象: `extensions/B/**` と `evidence/B/**` のみ。
- 共有mainへのmerge、他session branchの取り込み、root SKILL/READMEの変更は行っていない。
- Skill名: `anything-frontend-ux-flow`。`extensions/B` 内に入口・原典・契約・checker・fixtureを同梱。

最終変更セットはbaseからこのブランチ先端までの差分。取り込み側でbase SHAとパス範囲を確認し、
他sessionの変更と統合する。B単独のファイルを取り込んだことと、正式な効果評価PASSを区別する。

## 他セッションとの接続

| 相手 | Bへの入力 | Bから渡すもの | 統合時の確認 |
|---|---|---|---|
| A Product / IA | actor、goal、機能境界、入口、必要情報、成功条件 | task contract、目的が達成不能な箇所、冗長操作と必須前提 | 機能を削る判断と、Bの経路を短くする判断を混同しない。UIに置けない機能問題はAへ返す |
| C UI Engineering | 部品契約、API adapter、native form、notification/focus、既存token | flow JSON、guard、side effect、保持データ、取消しの意味、待機/失敗表示の時機 | API idempotency/cancel/version保証、DOM状態とcontrollerの一致、keyboard、読み上げ、responsiveを実機確認 |
| D QA / Evaluation | 固定要件、評価環境、権限を分離したoracleとholdout、昇格基準 | 原典索引、hash、全trace、baseline/candidate出力、レビュー反例、blocked記録 | 候補にoracle/holdoutを公開しない。shared filesystemの別agentを完全blindと称さない。ブラウザー未実行を埋める |
| 既存Art Direction | 配色・書体・構図・余白・視覚意図 | 各状態で必要な情報と操作、statusの意味 | 再装飾をBの改善として計上しない。既存フォーム/楽観更新/履歴規則を維持 |

## 共通入口への提案（このブランチでは未適用）

1. ルートの用途選択に「目的を完了する操作フロー、入力から確定、取消し、非同期の失敗復帰」を追加し、`extensions/B/SKILL.md` へ接続する。
2. 既存D/G/C/K系の実装参照は削らず、Bのstate/event/guard契約から必要な規則へ戻れるようにする。
3. Aの出力をBの `actor / goal / entry_condition / success_predicate` へ、Bのstate表をCのcomponent state/feedback契約へ対応付ける。
4. Dの評価入力にflow JSON・test trace・API契約の未確認項目を加える。Bのchecker成功だけでDの品質gateを通さない。
5. 小さな既存flow修正では全A→B→C→Dを毎回強制しない。通常の実装検証と、Skillの正式昇格campaignを区別する。

## 残る確認事項

- 許可されたブラウザー環境で、1280/390px、keyboard、送信・取消し・復帰の実操作、スクリーンショットを記録する。
- UIのlabelと状態表示、誤操作時の理解、task完了性は利用者または独立評価者で点検する。
- exact model revision/seed、runtime OCI digest、cost計測、calibration、非公開holdoutを実値で固定したうえで正式比較を行う。
- R-ASI現行版のexecute/evaluate/promoteは未接続。将来接続されたCLI契約を確認し、descriptor登録のreceiptを実行PASSに置き換えない。
- 本番API adapterが異なる場合、同一key再試行、取消ack、progress、versionの保証を再確認し、今回のsimulation結果を移植保証にしない。

## 実行入口

```sh
PYTHONDONTWRITEBYTECODE=1 python -m unittest discover -s extensions/B/tests -p 'test_*.py' -v
python extensions/B/checks/check_flow.py extensions/B/tests/fixtures/booking.json --json
python extensions/B/checks/check_flow.py extensions/B/tests/fixtures/report.json --json
node --test evidence/B/experiments/shared/api.test.mjs
node evidence/B/experiments/evaluate.mjs /tmp/anything-B-comparison
```

比較の再実行は保存済みcontrollerを実行する。LLM生成を同じseedで再現するコマンドではない。
R-ASIの手順・実際のCLI output・機能境界は [tooling.md](tooling.md) を参照する。
