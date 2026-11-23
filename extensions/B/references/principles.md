# 操作フローの10原則

## 目次

- [B01 タスクの開始と完了を観察可能にする](#b01)
- [B02 状態とイベントを画面から分離する](#b02)
- [B03 入力・確認・送信を影響に応じて組む](#b03)
- [B04 戻る・閉じる・取消し・undoを分ける](#b04)
- [B05 結果不明から安全に回復する](#b05)
- [B06 非同期処理の事実を適切な範囲で伝える](#b06)
- [B07 失敗を修復可能な次の目標へ変える](#b07)
- [B08 中断・履歴・部分結果を状態として扱う](#b08)
- [B09 不要な操作だけを減らす](#b09)
- [B10 検証した範囲だけを完了とする](#b10)

各原則は原典を条件付き作業へ編集したもの。原典に同じJSON schemaやcheckerがあるとは主張しない。観測、著者の指針、本Skillの推論は[原典一覧](sources.md)で区別する。

<a id="b01"></a>
## B01 — タスクの開始と完了を観察可能にする

**Trigger:** 画面や機能はあるが何を完了する経路か未定義。複数接点のjourneyから一操作を設計する。

**Inputs:** actor、目的、起点、前提データ・権限、外部接点、成功証跡、調査済み行動と仮説。

**Decision Rules:** 長期間・複数接点の体験をjourney、特定製品内の操作列をtask flowとして扱う。操作実行と目的達成を分ける。目的や機能の採否が未定ならAへ返す。

**Procedure:** 目的を1文にする。開始条件を記す。観察可能な成功predicateを定義する。成功、未完了の離脱、外部引継ぎを別にする。業務事実の不明点は仮説と確認先を残す。

**Output Contract:** actor/goal/entry_condition/entry_state/success_predicate、証跡の所在、journey内のtask境界。

**Constraints / Exceptions:** 送信受付だけが委託範囲なら受付を成功にしてよいが、審査完了や予約確定とは表示しない。外部承認を完了済みと推測しない。

**Failure Modes:** ボタン押下を成功扱いする。別接点の未完了を隠す。LLMが作ったpersonaや感情を観察事実と呼ぶ。

**Verification:** entryから成功証跡まで実行する。クリック完了でもserver receiptが無い場合を分ける。観察/仮説の区別を確認する。

**Dependencies:** Aの目標・機能境界、APIの結果定義、Art Directionの視覚制約。

**Sources:** [S01](sources.md#s01)、[S02](sources.md#s02)、[S16](sources.md#s16)。確信度: 中。task contractのschema化は本Skillの編集推論。

<a id="b02"></a>
## B02 — 状態とイベントを画面から分離する

**Trigger:** pending/error/編集状態が混ざる、戻る先が不明、行き止まりや閉じた循環が疑われる。

**Inputs:** B01、操作、system応答、timer、不変条件、副作用、guardに必要な値。

**Decision Rules:** 同じ画面でも可能な操作と確定事実が違えば状態を分ける。新画面の追加前に状態で表せるか確認する。修正ループは許し、出口のないループは不適合とする。

**Procedure:** stateを列挙する。各edgeにevent/actor/guard/effect/feedback/preservesを記す。同一eventの分岐を排他的・網羅的にする。entryからの到達とsuccess/exitへの出口を調べる。最低1つのsuccessを定義する。

**Output Contract:** ux-flow/v1のstates/transitions/scenarios、未確定guardと必要なbackend条件。

**Constraints / Exceptions:** 終了後の別taskは別contractにする。有限graphは履歴やデータの全組合せの証明ではない。自然言語guardをevalしない。全exitのみなら目的未達のHOLDとする。

**Failure Modes:** 画面一覧を経路とみなす。常にfalseのguardで見せかけの出口を作る。タイマーから永久に待機へ戻る。無意味な出口をsuccessと名付ける。

**Verification:** checkerで構造と到達性を検査する。guard成立/不成立例は実装テストで確認する。success proofを観察する。

**Dependencies:** B01、B05/B07、Cの実装state。

**Sources:** [S02](sources.md#s02)、[S13](sources.md#s13)、[S17](sources.md#s17)。確信度: 中。graphと静的検査は本Skillの設計であり、原典の実証済みUX尺度ではない。

<a id="b03"></a>
## B03 — 入力・確認・送信を影響に応じて組む

**Trigger:** フォーム、申請、設定変更、reviewからsubmit、送信後の修正がある。

**Inputs:** 項目制約、draftと確定の違い、可逆性、失敗時の損失、server validation、確認対象snapshot。

**Decision Rules:** 項目の誤りと修正方法を示す。重大な誤りを可逆性や検査で抑えられない場合は確認・修正機会を設ける。WCAG3.3.4を全フォームの確認画面必須と読み替えない。短いフォームをstepperのために分割しない。

**Procedure:** 項目を検証し、有効入力を保持する。reviewを採るなら送信payloadと一致させ、編集時に確認内容を更新する。Enter/クリック/プログラム送信を確認する。受理済み結果が返ってから完了を示す。

**Output Contract:** validation/review/submission/confirmationの遷移、保持値、確認を採る/採らない理由。

**Constraints / Exceptions:** draftは未入力でも保存可能な場合がある。再入力がsecurity上必須、情報失効、処理に不可欠なら例外を記す。client検証成功でserver検証を省かない。

**Failure Modes:** 毎回「本当に？」を追加する。review後にpayloadが変わる。送信失敗で全欄消去。未入力の初期状態から全項目をエラー強調する。

**Verification:** 空欄、最小/最大/範囲外、Enter、reviewから編集、server拒否→修正→成功を試す。

**Dependencies:** Cのフォーム/ラベル/エラー関連付け、既存forms checklist、B05。

**Sources:** [S04](sources.md#s04)、[S05](sources.md#s05)、[S07](sources.md#s07)、[S18](sources.md#s18)。確信度: 規範の適用条件は高、UI方式の選択は中。

<a id="b04"></a>
## B04 — 戻る・閉じる・取消し・undoを分ける

**Trigger:** cancel/back/close/delete/undo、処理中の離脱がある。

**Inputs:** 未保存データ、commit時点、server取消API、undoの期間・副作用、他者の変更、戻り先。

**Decision Rules:** 戻る=前段、閉じる=表示終了、破棄=未送信変更削除、取消要求=server処理の停止要求、undo=確定済み結果の逆/補償操作として分ける。close後も処理が続く場合は示す。

**Procedure:** 操作ごとに保持/破棄データと次stateを書く。取消しにrequested/acknowledged/too-lateを定義する。完了と取消しが競合したらserver結果を確認し、成功済みを取消済みに変えない。回復手段を示す。

**Output Contract:** 操作の意味表、取消し許可状態、確認条件、取消し拒否経路、focusの復帰先。

**Constraints / Exceptions:** 取消APIが無いなら「画面を閉じる」等の実態を示す。共同編集で他者の変更をまとめてrollbackしない。negative consequenceに応じて必要な確認を入れる。

**Failure Modes:** AbortControllerでserver rollbackできたとする。Xで入力を黙って破棄。取消要求直後に取消済み表示。確定結果をローカルだけで消す。

**Verification:** 未編集/編集済み/送信中/成功後に戻る・閉じる・取消しを試す。cancelとcompleteの順序を入れ替える。

**Dependencies:** APIの取消/補償契約、Cのdialog/focus復帰、B05。

**Sources:** [S03](sources.md#s03)、[S10](sources.md#s10)、[S14](sources.md#s14)、[S16](sources.md#s16)。確信度: 中。server取消raceの具体設計は編集推論。

<a id="b05"></a>
## B05 — 結果不明から安全に回復する

**Trigger:** 書込みAPI、二重送信、応答喪失、timeout、再送がある。

**Inputs:** operation ID、request key、payload identity、dedupe保証と期限、receipt/lookup API、明示的拒否と通信失敗。

**Decision Rules:** timeoutは非commitの証明ではない。readは契約に従ってretry。writeは保証済み冪等性なら同じ意図・payload・key、lookupがあれば先に照会、両方無ければ盲目的に再送せず確認手段を示す。異payloadを同じkeyに載せない。

**Procedure:** 論理操作ごとにidentityを作る。in-flight重複を抑える。結果不明をunknownにする。照会でfound/pending/authoritative-not-foundを分ける。receiptで成功を判定する。retry回数・間隔・中断条件をAPIに合わせる。

**Output Contract:** operation.retry/idempotency/outcome_lookup/contract_evidence、unknownからreconcile/retry/exitへの遷移。

**Constraints / Exceptions:** keyがあっても原子的記録・期限・異payload衝突が未確認なら保証しない。結果整合の遅れがあるnot-foundから新key再送しない。「書込みなし」の確定拒否はunknownと分ける。

**Failure Modes:** disableだけで二重確定防止とする。retryのたびにkey変更。404は必ず未処理と判断。pendingを成功表示。

**Verification:** commit後の応答喪失、二重起動、同一key再送、payload変更、late response、照会失敗を注入し、server確定数を数える。

**Dependencies:** backend contract（不明ならOpen）、B04/B07、Cの操作guard。

**Sources:** [S12](sources.md#s12)、[S16](sources.md#s16)。確信度: API原則は高、UI状態への移植は中。

<a id="b06"></a>
## B06 — 非同期処理の事実を適切な範囲で伝える

**Trigger:** loading、background job、待機、更新競合がある。

**Inputs:** 処理の影響範囲、実測進捗、予想時間と根拠、現在request/version、foreground/background。

**Decision Rules:** 局所処理は局所feedback、全体操作を本当に止める処理のみ全体pending。実測可能なら進捗、不可なら状態と確認手段を示す。旧request応答で新しい意図を上書きしない。

**Procedure:** 受理/処理中を示す。期限後にslow/unknownと復帰経路を出す。request identityを照合する。成功/失敗を終端まで伝える。background更新で入力中focusを奪わない。

**Output Contract:** pending範囲、timeout_event、wait_policy、stale_response、通知内容と時機。固定色・shimmer・秒数は要求しない。

**Constraints / Exceptions:** very-short処理のanimationを必須にしない。全content changeへstatus messageを追加しない。視覚の動きはArt DirectionとCのreduced-motion契約へ渡す。

**Failure Modes:** 無期限spinner、架空90%、一部保存で全画面を塞ぐ、background通知でfocusを奪う、古い結果で巻戻す。

**Verification:** 即時/遅延/無応答/逆順/離脱後の応答を注入する。進捗の分母・値と表示を比較する。実時間と知覚評価を分ける。

**Dependencies:** Cの通知/focus、APIのprogress/version、B05。

**Sources:** [S06](sources.md#s06)、[S08](sources.md#s08)、[S09](sources.md#s09)、[S10](sources.md#s10)、[S11](sources.md#s11)、[S15](sources.md#s15)。確信度: 中。S15を実速度改善や偽progressの根拠にしない。

<a id="b07"></a>
## B07 — 失敗を修復可能な次の目標へ変える

**Trigger:** error stateから進めない、retryで同じ失敗を繰り返す、入力が消える。

**Inputs:** 失敗分類、修正可能値、保持入力、確定副作用、retry可否、権限/認証状態。

**Decision Rules:** validationは項目修正、業務拒否は条件変更、transportはB05、認証切れは許可された再認証と復帰。回復不能でも理由と退出/支援先を示す。利用者の誤りとシステム失敗を混ぜない。

**Procedure:** エラーを分類する。保存済み事実を固定する。有効データを保持する。修正/照会/再試行/再開を提示する。再実行結果を確認し、成功または説明付き離脱までtraceを残す。

**Output Contract:** failure matrix: error class→次の操作→保持値→副作用→復帰state→ケース。

**Constraints / Exceptions:** security上詳細を出せないエラーは漏洩しない説明にする。失効値は再検証する。永続障害を無制限retryで隠さない。

**Failure Modes:** 「エラーです」だけ、入力全消去、修正しないretry、再認証で元taskを失う、部分成功を全失敗扱い。

**Verification:** error classごとに修正可能な入力で復帰する。初回入力と復帰後入力を比較する。

**Dependencies:** B05/B08、Cのerror association、Aの別経路/支援手段。

**Sources:** [S05](sources.md#s05)、[S13](sources.md#s13)、[S16](sources.md#s16)、[S18](sources.md#s18)。確信度: 中。

<a id="b08"></a>
## B08 — 中断・履歴・部分結果を状態として扱う

**Trigger:** 多段入力、戻る/再訪/refresh、長時間job、部分成功がある。

**Inputs:** task/job ID、保存寿命・機密性、再開可能状態、確定/失敗/未処理item IDs、server version。

**Decision Rules:** URL/履歴は表示位置、server stateは確定事実。再訪時は保存値だけで成功を復元せず再照会する。部分結果を成功/失敗/未処理に分け、retryは必要subsetへ限定する。

**Procedure:** 中断箇所ごとに保持/破棄/再取得を定義する。内容の保存可否を示し、機微情報を勝手に永続化しない。job IDで再開する。成功itemを再投入しない。全件完了または部分終了を明示する。

**Output Contract:** resume matrix、job receipt、item別結果、retry subset、保持期限・失効時の説明。

**Constraints / Exceptions:** 再開不可なら理由と最小のやり直し範囲を示す。保管可否はサービス契約に従う。部分成功の全体rollbackが無ければあると見せない。

**Failure Modes:** refreshでjob再作成、ローカル推測で保存済み扱い、成功itemをretryして二重登録、戻るで入力喪失、stale draftでserver上書き。

**Verification:** 成功/部分失敗/処理中で再訪する。job ID・確定数・失敗subsetが一致するか確認する。期限超過も扱う。

**Dependencies:** backend retention/job status、Cの履歴・storage、Aの再開入口。

**Sources:** [S03](sources.md#s03)、[S04](sources.md#s04)、[S12](sources.md#s12)、[S16](sources.md#s16)、[S18](sources.md#s18)。確信度: 中。partial job/resume matrixは原則からの明示的な編集推論。

<a id="b09"></a>
## B09 — 不要な操作だけを減らす

**Trigger:** 往復、重複入力、無目的な確認、終わらない循環がある。

**Inputs:** 同一goalの操作列、各操作の目的、熟練度、可逆性、失敗時の回復手数。

**Decision Rules:** 情報取得・意図確認・実行・修正・終了に寄与しない操作を候補にする。安全な確認や修正手段を手数だけのために消さない。非線形taskへ線形stepperを強制しない。

**Procedure:** 操作の存在理由を記す。候補を省いた経路と現行を同入力で比べる。必要情報・制御・完了証跡を維持する。初回利用者の操作発見性を点検する。

**Output Contract:** removed/retained stepと理由、通常/失敗経路の操作数、未測定の所要時間。

**Constraints / Exceptions:** 作業時間モデルは熟練や前提知識の条件付き。万人への3-click ruleや「最短=最高」を設定しない。

**Failure Modes:** 必要reviewを削る。短いラベルで意味を失う。loopの途中手数だけ改善して完了とする。

**Verification:** 同一goal・入力・環境で比較し成功/修正/退出を維持する。UI操作数とAPI call数を別に数える。

**Dependencies:** Aの機能重複判断、B02/B03/B10、Cの実装。

**Sources:** [S02](sources.md#s02)、[S07](sources.md#s07)、[S13](sources.md#s13)、[S17](sources.md#s17)。確信度: 中。

<a id="b10"></a>
## B10 — 検証した範囲だけを完了とする

**Trigger:** flow設計・実装の提出、baseline/candidate比較、統合判定。

**Inputs:** 通常の設計・修正では、対象taskの要件・成功predicate・正常/異常/境界の条件・実行環境を使う。Skill効果の比較または正式昇格を依頼された場合は、これに凍結した2種類以上のtask、baseline/candidate、同一content・model条件、artifact hashを追加する。

**Decision Rules:** 構造検査、controllerテスト、ブラウザ操作、利用者テスト、独立blind評価を分ける。通常の修正は対象の実測結果と未検証事項を明記して提出でき、比較用の第2taskやR-ASIの準備を理由に停止しない。Skillの正式昇格を求められた場合は自己採点を独立評価と呼ばず、独立性が成立しなければその昇格を保留する。Candidateへ独立oracle/非公開holdoutを渡さない。

**Procedure:** 通常は成功predicateを先に固定し、対象taskを実装・操作して、失敗位置とtrace、未検証の依存を残す。比較時は条件を凍結して初回提出物を保存し、同じfixtureを両方へ適用する。修正後は別revisionとして扱う。未実行・不明・費用非取得をnull/blockedで記録する。

**Output Contract:** 通常はtest matrix、実測結果、分類付きissue、環境、未検証事項。比較・正式昇格時だけbaseline/candidate比較、hash、評価者の独立性、Gate理由を追加する。

**Constraints / Exceptions:** artifactの再実行と確率的LLM生成の再現性は別。小fixtureで人間の完了率や全製品一般化を示さない。禁止/不通のbrowserを迂回しない。1画面の入力保持修正などでは無関係な2つ目のtaskを作らない。

**Failure Modes:** 未実行を0 failuresと記す。baselineを意図的に壊す。修正後を初回成功扱い。checker成功でUX全合格。R-ASI receiptを独立評価成功扱い。

**Verification:** traceと期待値を再実行し、評価者・入力・時刻・hashを照合する。model/費用/seedが取得不可なら明示する。

**Dependencies:** 通常利用のhard dependencyは対象の実行環境だけで、同梱checkerはPython標準ライブラリで動く。Dの横断QA/独立評価は正式昇格の担当がある場合に接続する。R-ASIは今回のcampaignで採用した任意の証跡保管先であり、通常のSkill利用には不要。利用を指定されたときだけ現行CLI/契約を確認し、未実装機能は実行済みと扱わず、外部実行ログの記録へ限定する。

**Sources:** [S17](sources.md#s17)、[S19](sources.md#s19)、[S02](sources.md#s02)。確信度: 中。holdout・artifact凍結・Gateはcampaign運用要件であり、HCI原典の効果と主張しない。
