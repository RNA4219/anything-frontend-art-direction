# R/S ラベルを伏せた設計比較レビュー

## 結論

**support-triage、course-catalogとも「同等」です。** 提示briefに対する必須機能の保持、役割分離、情報構造、宣言された到達経路では、R/Sのいずれにも重大な欠陥は見つかりませんでした。実利用のしやすさや実装品質の優劣まで同じと主張する判定ではありません。

| ケース | 判定 | 設計案から確認できたこと | 判定の限界 |
|---|---|---|---|
| support-triage | 同等 | 着手判断、担当変更、解決済み検索と履歴、責任者専用の監査出力を保持 | 検索の同居/分離や履歴表示方式の実利用効果は未確認 |
| course-catalog | 同等 | 共通集合の探索、2講座比較、参加判断と申込先、保存、編集者専用公開を保持 | 保存ビュー/別画面の効果、実URL、公開・保存の実動作は未確認 |

確定した重大な設計問題はありません。後述の2件は、表示文脈で確認する局所的なラベルの課題です。案が明記する条件表示によって解消される可能性があるため、確定欠陥や優劣の根拠にはしていません。

## レビューの範囲と読み方

担当領域は **Product Design / Information Architecture**。指定されたbrief 2件、中立的なoutput-format.md、R/Sのplan 4件だけを読みました。参照位置はファイル名とJSON Pointerで示します。

これはラベルを伏せた別スレッドのモデルレビューです。真の独立Oracle、人による利用者評価、実装の検証ではありません。実HTML・CSS・実画面・操作ログは見ていません。案に含まれるSkill名や作成過程の記述から、Skill・モデルの由来を推測していません。

`output-format.md`はデータの形とprimary/secondaryの意味を確認する契約として使用しました。特定の画面構成を推奨する採点基準としては扱っていません。primaryは開示操作なしで読めるという意味で、スクロールは許されます。

経路はentry_forから始め、実際のfrom/to/rolesが一致するnavigationのみをたどりました。globalという種別だけから未記載リンクを補っていません。機能を同じ画面に置くことと、機能をmergeすることも分けて評価しています。

説明の長さ、画面数、リンク数、blockingの件数は優劣に使っていません。URLや担当ルール本文など、入力自体が持たない値を作って減点したり、未実装の挙動を成功したと扱ったりしていません。

## 1. support-triage

### 必須要件と義務の保持

- **r_triage**：両案とも入口の同じ候補一覧で ticket_id・summary・severity・due_at・owner・status を primary とする。期限と影響を別の詳細に分けていない。
  根拠：`support-triage.json#/requirements/0`。R：`R/support-triage.plan.json#/screens/0`。S：`S/support-triage.plan.json#/screens/0`。

- **r_assign**：両案とも f_assign と依存先 f_history を維持し、担当判断の画面に ticket_id・owner・assignment_policy を primary で置く。担当ルール本文の未提供は入力不足として分離する。
  根拠：`support-triage.json#/requirements/1`。R：`R/support-triage.plan.json#/features/2`、`R/support-triage.plan.json#/screens/2`。S：`S/support-triage.plan.json#/features/2`、`S/support-triage.plan.json#/screens/1`。

- **r_archive**：両案とも解決済みを含む検索能力、90日保持、検索から履歴を読む経路を保持する。検索0件でも条件と保持期間を確認する責務が宣言されている。
  根拠：`support-triage.json#/requirements/2`。R：`R/support-triage.plan.json#/features/3`、`R/support-triage.plan.json#/screens/1`、`R/support-triage.plan.json#/navigation/2`、`R/support-triage.plan.json#/navigation/5`。S：`S/support-triage.plan.json#/features/3`、`S/support-triage.plan.json#/screens/0`、`S/support-triage.plan.json#/navigation/2`、`S/support-triage.plan.json#/navigation/3`。

- **r_audit**：両案とも manager の専用入口に期間・保持・出力範囲を primary で置き、年4回でも f_export を required/keep とする。operator の画面・経路・機能権限に監査出力を追加していない。Rは共有詳細で履歴を読め、Sは監査画面内で読める。
  根拠：`support-triage.json#/requirements/3`。R：`R/support-triage.plan.json#/features/5`、`R/support-triage.plan.json#/screens/3`、`R/support-triage.plan.json#/navigation/9`、`R/support-triage.plan.json#/navigation/10`、`R/support-triage.plan.json#/decision_notes/2`。S：`S/support-triage.plan.json#/features/5`、`S/support-triage.plan.json#/screens/2`。

- **r_trends**：初回必須でない月別集計は両案とも明示的に延期する。g_trends の経路と monthly_counts を初回案に置かないことは、必須監査を削除したことにならない。
  根拠：`support-triage.json#/requirements/4`。R：`R/support-triage.plan.json#/features/6`、`R/support-triage.plan.json#/decision_notes/5`。S：`S/support-triage.plan.json#/features/6`、`S/support-triage.plan.json#/unresolved/2`。

f_my_queueは両案ともf_inboxへ統合し、「自分の担当」を同じチケット集合の条件として残しています。f_assign/f_exportからf_historyへの依存も維持されています。f_themeは目標・要件・依存がない任意要求のため、両案とも今回の構成から除外する理由を記録しています。実データの削除は指示していません。根拠は両案の`/features/1`、`/features/2/dependencies`、`/features/5/dependencies`、`/features/7`と、briefの対応feature_requestsです。

### 役割の入口からの具体的経路

| 目標・役割 | Rの明示経路 | Sの明示経路 | 到達先の必要情報 |
|---|---|---|---|
| g_triage / operator | s_triage | s_queue | ticket_id・summary・severity・due_at・owner・status：両案ともprimary |
| g_assign / operator | s_triage → s_ticket | s_queue → s_ticket | ticket_id・owner・assignment_policy：両案ともprimary |
| g_find / operator | s_triage → s_search → s_ticket | s_queue → s_queue → s_ticket | ticket_id・status・history：両案ともprimary |
| g_audit / manager | s_audit | s_audit | date_range・retention・export_scope：両案ともprimary |

Rの履歴検索は`/navigation/2`と`/navigation/5`で、s_triage → s_search → s_ticketをたどります。Sは`/navigation/2`の「解決済みも含めて検索」というs_queue内の経路に続いて、`/navigation/3`でs_ticketへ進みます。検索機能がどの画面に属するかまで確認しており、単に詳細画面が到達可能という理由だけで検索目標を充足したとはしていません。

責任者の監査入口は両案ともs_auditです。Rはs_audit → s_ticket → s_auditのmanager専用経路が`/navigation/9`、`/navigation/10`にあり、共有詳細のf_assignはoperator限定という`/decision_notes/2`の規定を保持しています。Sはs_audit自体にhistoryをprimaryとして置くため、責任者が担当者用詳細へ入る必要がありません。どちらもoperatorの監査出力権限を追加していません。

### 構成差の評価

- **information_architecture**：Rは着手一覧s_triageと解決済み検索s_searchを分け、双方からs_ticketへ進む。 Sは着手と検索をs_queueに同居させ、同画面で検索してs_ticketへ進む。 両案ともf_searchをkeepし、探索と選択の能力を失わない。Rは作業の区分、Sは共通条件の連続性を重視する案で、画面数やリンク数のみでは優劣を決められない。

- **information_architecture**：Rは監査画面のhistoryはsecondaryだが、manager用の明示経路でs_ticketのprimary履歴へ到達し、監査へ戻れる。 Sはs_audit内にhistoryをprimaryで置く。managerがs_ticketへ進む経路は必要としていない。 g_auditの必要情報date_range・retention・export_scopeは双方の監査画面でprimary。f_historyも双方で到達可能。Rの補足化だけを欠落、Sの一画面化だけを成功とは判定しない。

- **information_architecture**：Rはs_ticketでもretentionをprimaryとする。 Sはs_ticketのretentionはsecondaryとし、検索0件と監査の判断場所でprimaryを保持する。 保持期間が必要になる文脈は双方で確保されている。詳細内の開示差は、このbriefでは重大な優劣の根拠にならない。

ここでの「同等」は、両方に必須の判断材料と経路があるという判定です。T-104/T-105をどちらの構成で速く正確に選べるか、T-099の履歴を見つけやすいかは、実画面や利用者で確認していません。

## 2. course-catalog

### 必須要件と義務の保持

- **r_find**：両案とも f_topics と f_workshops を f_catalog へ直接統合し、トピック・レベル・日程・予算で同じ講座集合を探す。複数トピック所属を保持し、別のワークショップ集合を捏造していない。0件時の現在条件と見直す先も指定する。
  根拠：`course-catalog.json#/requirements/0`。R：`R/course-catalog.plan.json#/features/1`、`R/course-catalog.plan.json#/features/2`、`R/course-catalog.plan.json#/screens/0`、`R/course-catalog.plan.json#/navigation/2`。S：`S/course-catalog.plan.json#/features/1`、`S/course-catalog.plan.json#/features/2`、`S/course-catalog.plan.json#/screens/0`、`S/course-catalog.plan.json#/navigation/0`。

- **r_compare**：両案とも独立した比較能力を残し、2講座について title・level・schedule・price・prerequisites・venue を同じ比較画面の primary に指定する。前画面の値の記憶を要求しない構成で、候補1件時の追加先も宣言する。
  根拠：`course-catalog.json#/requirements/1`。R：`R/course-catalog.plan.json#/screens/1`、`R/course-catalog.plan.json#/navigation/5`。S：`S/course-catalog.plan.json#/screens/1`、`S/course-catalog.plan.json#/navigation/8`。

- **r_prereq**：両案とも比較と詳細の prerequisites・price・seats を primary とし、0円、残席0、長い参加前提を隠さない。探索や保存候補の判断でも必要情報を保持する。
  根拠：`course-catalog.json#/requirements/2`。R：`R/course-catalog.plan.json#/screens/0`、`R/course-catalog.plan.json#/screens/1`、`R/course-catalog.plan.json#/screens/2`。S：`S/course-catalog.plan.json#/screens/0`、`S/course-catalog.plan.json#/screens/1`、`S/course-catalog.plan.json#/screens/2`、`S/course-catalog.plan.json#/screens/3`。

- **r_enroll**：両案とも各講座の詳細に対応する enroll_link を primary で指定し、講座と申込先A/B/Cの対応を保持する。実URLが入力にないため、実遷移の成否や残席0時の受付可否は判定対象外とする。
  根拠：`course-catalog.json#/requirements/3`。R：`R/course-catalog.plan.json#/screens/2/information/8`、`R/course-catalog.plan.json#/unresolved/2`。S：`S/course-catalog.plan.json#/screens/2/information/5`、`S/course-catalog.plan.json#/unresolved/5`。

- **r_save**：両案とも f_wishlist を f_favorites に統合し、同じ利用者の同じ講座集合への保存関係を保持する。Rは共通一覧の保存済みビュー、Sは専用の保存候補画面を用い、どちらも保存候補から共通詳細に到達できる。
  根拠：`course-catalog.json#/requirements/4`。R：`R/course-catalog.plan.json#/features/5`、`R/course-catalog.plan.json#/features/6`、`R/course-catalog.plan.json#/navigation/1`、`R/course-catalog.plan.json#/navigation/4`。S：`S/course-catalog.plan.json#/features/5`、`S/course-catalog.plan.json#/features/6`、`S/course-catalog.plan.json#/navigation/3`、`S/course-catalog.plan.json#/navigation/5`。

- **r_publish**：両案とも f_publish を editor に限定し、専用の管理入口から更新・公開画面へ進める。title と publication_status を判断場所で primary とし、learner の経路には管理・公開を含めない。
  根拠：`course-catalog.json#/requirements/5`。R：`R/course-catalog.plan.json#/features/8`、`R/course-catalog.plan.json#/screens/3`、`R/course-catalog.plan.json#/screens/4`、`R/course-catalog.plan.json#/navigation/11`。S：`S/course-catalog.plan.json#/features/8`、`S/course-catalog.plan.json#/screens/4`、`S/course-catalog.plan.json#/screens/5`、`S/course-catalog.plan.json#/navigation/14`。

必須の探索・比較・詳細・公開は両案ともkeepです。トピック別講座とワークショップ検索は同じ講座集合の探索としてf_catalogへ、受講したいリストは同じ保存関係としてf_favoritesへ統合しています。比較と保存の成果を混同せず、保存を比較の前提にしていません。

### 役割の入口からの具体的経路

| 目標・役割 | Rの明示経路 | Sの明示経路 | 到達先の必要情報 |
|---|---|---|---|
| g_discover / learner | s_catalog | s_catalog | title・level・schedule・price・topic：両案ともprimary |
| g_compare / learner | s_catalog → s_compare | s_catalog → s_compare | title・level・schedule・price・prerequisites・venue：両案ともprimary |
| g_decide / learner | s_catalog → s_course | s_catalog → s_details | title・prerequisites・seats・price・schedule・enroll_link：両案ともprimary |
| g_saved / learner | s_catalog → s_catalog → s_course | s_catalog → s_saved → s_details | title・schedule・price：両案ともprimary |
| g_publish / editor | s_manage → s_edit | s_editor_catalog → s_editor_edit | title・publication_status：両案ともprimary |

Sのg_savedはgoal_routes上のtargetがs_savedですが、そこで必要情報を読め、`/navigation/5`から対象のs_detailsへ開く経路も明記されています。targetが詳細画面のIDでないことだけを理由に「後で開けない」とは判定しません。Rは保存した講座ビューへの自己遷移`/navigation/1`と詳細への`/navigation/4`で同じ成果を保っています。

候補1件の追加先は、Rの`/navigation/5`、Sの`/navigation/8`でs_catalogへつながります。比較画面では2講座の同じ属性を読み、長い前提条件、0円、残席0をprimaryで保持する指定があります。実描画で値が切れないことを確認したという意味ではありません。

編集者は専用入口から、Rの`/navigation/11`、Sの`/navigation/14`で編集・公開画面へ進みます。learnerの画面と経路にf_publishはありません。これは権限設計の確認であり、直接URLやデータ操作への認可が実装済みという評価ではありません。

### 構成差の評価

- **information_architecture**：Rは保存候補はs_catalogのローカルビューで読み、共通詳細s_courseへ進む。 Sは保存候補はs_savedで読み、共通詳細s_detailsやs_compareへ進む。 両案とも同じ利用者の同じ講座を参照する。Sの別画面は別データ集合を意味しない。Rの少ない画面数だけを利点にしない。

- **function**：Rはf_newsを今回の機能構成からremoveし、既存データの廃棄はしない。 Sはf_newsの初期提供設計をdeferし、必要な運営連絡や既存提供の有無を確認項目とする。 briefではf_newsは非必須で目標・要件・依存がない。Rの除外理由もSの延期理由も示されている。入力にない必須連絡義務を作ってRを減点せず、保留が多いだけでSを高評価にしない。将来の業務要件が加われば再検討する。

- **interaction**：Rは元の一覧や比較へ戻る経路を明示し、条件の保持方法をBへ渡す。 Sは探索・保存・比較への行先を明示し、候補や条件の保持をBへ渡す。 情報上の帰路は双方にある。条件復元や保存成功・失敗の実動作が完成したとは判定しない。

両案とも「はじめての木工／0円／申込先A」、長い題名の地域アーカイブ講座の「2000円／残席0／申込先B」、中級木工の「6000円／申込先C」という入力対応を保つ方針です。実URLがないことは両案に共通する入力の限界です。

## 3. 局所的な確認課題

以下は確定欠陥ではありません。症状を文書から再現できる範囲と、実画面が必要な範囲を分けています。

### OBS-SUPPORT-S-LABEL

- **対象**：support-triage / S。重大度：低。優劣判定への影響なし。
- **JSON位置**：`S/support-triage.plan.json#/navigation/0`、`S/support-triage.plan.json#/screens/0/information/5`、`S/support-triage.plan.json#/decision_notes/7`。
- **症状**：表示ラベル「全件」は、rationaleでは担当範囲だけを指す。解決済みや検索条件もすべて解除する意味と読まれないかは、実際の表示文脈で確認する余地がある。案は現在条件を併記するとしているため、現時点で誤解が生じるとは断定しない。
- **要件の根拠**：`support-triage.json#/contexts/normal`、`support-triage.json#/contexts/abnormal`。
- **影響**：担当条件と状態条件の区別が読めない表示になった場合、未解決だけの結果を保持対象の全記録と誤認する可能性がある。計画上の検索能力や到達経路は失われていない。
- **修正方向**：担当条件の区分名と現在の状態・検索条件を同時に示す。ラベル単独で表示するなら「すべての担当」など範囲を明示する表現を候補にする。
- **担当領域**：A / Product Design・Information Architecture。引継ぎ：C / 表示の具体化、D / 用語理解の確認。
- **確信度**：medium。ラベルと限定された意味の差は文書から確認できるが、現在条件の併記も宣言されており、利用者の誤解は未観測。

**文書上の再現手順**

1. S/support-triage.plan.jsonの/navigation/0/labelを読む。
2. 同じ要素のrationaleにある「全件は担当の範囲」を照合する。
3. /decision_notes/7と/screens/0/information/5に、状態・検索条件を別に表示する記述があることを確認する。
4. 画面は未提供なので、この補足が実際に十分近く読めるかは確認できないと記録する。

### OBS-COURSE-R-LABEL

- **対象**：course-catalog / R。重大度：低。優劣判定への影響なし。
- **JSON位置**：`R/course-catalog.plan.json#/navigation/0`、`R/course-catalog.plan.json#/decision_notes/5`、`R/course-catalog.plan.json#/screens/0/purpose`。
- **症状**：「すべての講座」はrationale上では保存済み条件だけを外す入口である。他のトピック・日程・予算条件も解除する入口と誤読されないかは確認余地がある。案は条件を区別して表示するとしており、機能欠落ではない。
- **要件の根拠**：`course-catalog.json#/requirements/0`、`course-catalog.json#/contexts/abnormal`。
- **影響**：保存済み条件を外しても他条件が残ることが読めない表示になった場合、全件表示だと思って候補を見落とす可能性がある。条件を見直す経路は別に宣言されている。
- **修正方向**：保存状態の切替であることを区分名で示すか、「保存済み条件を外す」など操作範囲が分かる表現を検討する。残っているトピック・レベル・日程・予算条件を引き続き読めるようにする。
- **担当領域**：A / Product Design・Information Architecture。引継ぎ：B / 条件変更時の状態、C / 表示の具体化、D / 用語理解の確認。
- **確信度**：medium。ラベル単独の広い意味と操作範囲の違いは確認できるが、案の条件併記によって解消される可能性がある。

**文書上の再現手順**

1. R/course-catalog.plan.jsonの/navigation/0のlabelとrationaleを照合する。
2. /decision_notes/5と/screens/0/purposeで保存済み条件と他条件の表示責務を確認する。
3. /navigation/2に「条件を見直す」の自己遷移があることを確認する。
4. 実画面はないため、複数条件の区別が利用者に伝わるかは未確認とする。

## 4. 入力不足として分離した事項

以下は案の欠陥ではなく、briefから確定できない提供条件です。どちらの案も未提供事項として扱っています。blocking=true/falseの使い方や件数の差は、この未確定内容の重要性と同一視しません。

### INPUT-SUPPORT-ASSIGNMENT

- **対象**：support-triage / R・S。分類：function。
- **JSON位置**：`R/support-triage.plan.json#/unresolved/0`、`S/support-triage.plan.json#/unresolved/0`、`R/support-triage.plan.json#/screens/2/information/6`、`S/support-triage.plan.json#/screens/1/information/6`。
- **不足の症状**：assignment_policyは必須情報として指定されているが、正式な担当ルール本文や割当可能な担当範囲はbriefにない。両案とも表示場所を確保して未提供を明記する。
- **briefの根拠**：`support-triage.json#/goals/1/needed_information`、`support-triage.json#/requirements/1`、`support-triage.json#/content`。
- **影響**：設計上の配置と経路は評価できるが、業務に適合した担当選択や変更の実提供は確認できない。
- **解消方向**：productが正式なルールと許可範囲を提示し、両案のs_ticketに配置する。Bへ変更条件を渡す。入力不足を理由に表示場所を撤去したり架空のルールを作ったりしない。
- **担当領域**：product / 業務ルールの確定。引継ぎ：A / 判断場所への配置、B / 担当変更の条件・状態。
- **確信度**：高。指定入力と両案の未解決事項から確認。正しい値やルールは推測していない。

**文書上の再現手順**

1. briefのg_assign/r_assignがassignment_policyを要求することを確認する。
2. briefのcontentに担当ルール本文がないことを確認する。
3. 両案のassignment_policyがprimaryであることと未解決事項を照合する。

### INPUT-SUPPORT-AUDIT

- **対象**：support-triage / R・S。分類：function。
- **JSON位置**：`R/support-triage.plan.json#/unresolved/1`、`S/support-triage.plan.json#/unresolved/1`。
- **不足の症状**：90日保持と年4回の監査は与えられているが、出力項目、監査対象の日時、期間境界、90日の起算点、監査記録独自の保持範囲はない。
- **briefの根拠**：`support-triage.json#/goals/3/needed_information`、`support-triage.json#/requirements/2`、`support-triage.json#/requirements/3`、`support-triage.json#/contexts/boundary`。
- **影響**：監査用記録の欠落があるとも、必要期間を必ず網羅できるとも断定できない。年4回を特定の四半期日程に読み替えて矛盾を作らない。
- **解消方向**：productがdate_rangeとexport_scope、保持の基準を定義する。その内容を両案の監査画面で読めるようにする。
- **担当領域**：product / 監査要件とデータ範囲。引継ぎ：A / 範囲の説明、C / 保存・取得と認可の実装。
- **確信度**：高。指定入力と両案の未解決事項から確認。正しい値やルールは推測していない。

**文書上の再現手順**

1. r_archiveの90日保持とcontexts.boundaryの年4回を読む。
2. briefに監査の具体的な期間・出力項目・起算点が指定されていないことを確認する。
3. 両案の監査画面がdate_range・retention・export_scopeをprimaryで指定し、未確定値を捏造していないことを確認する。

### INPUT-COURSE-ENROLL

- **対象**：course-catalog / R・S。分類：function。
- **JSON位置**：`R/course-catalog.plan.json#/unresolved/2`、`S/course-catalog.plan.json#/unresolved/5`、`R/course-catalog.plan.json#/screens/2/information/8`、`S/course-catalog.plan.json#/screens/2/information/5`。
- **不足の症状**：入力のenroll_linkは申込先A/B/Cという対応を示す値で、実URLがない。残席0の受付方針もない。両案とも講座との対応を維持する。
- **briefの根拠**：`course-catalog.json#/requirements/3`、`course-catalog.json#/content/0/enroll_link`、`course-catalog.json#/content/1/enroll_link`、`course-catalog.json#/content/2/enroll_link`、`course-catalog.json#/content/1/seats`。
- **影響**：申込先への実遷移や満席時の可能な行動は確認できない。実URLがないことを片方の設計欠陥に換算しない。
- **解消方向**：productが講座別の実URLと残席0時の案内方針を提示する。Bがその前提で導線の状態を設計する。キャンセル待ちなどの未指定機能は追加しない。
- **担当領域**：product / 申込先と受付方針。引継ぎ：A / 対象と出口の対応、B / 申込導線の状態。
- **確信度**：高。指定入力と両案の未解決事項から確認。正しい値やルールは推測していない。

**文書上の再現手順**

1. briefのcontentの各enroll_linkとseatsを確認する。
2. Rのs_courseとSのs_detailsで同じ講座に結び付くenroll_linkがprimaryであることを確認する。
3. 実URLや受付方針が両案の未解決事項に残っていることを確認する。

### INPUT-COURSE-PUBLISH

- **対象**：course-catalog / R・S。分類：function。
- **JSON位置**：`R/course-catalog.plan.json#/unresolved/4`、`S/course-catalog.plan.json#/unresolved/4`。
- **不足の症状**：publication_statusは必要情報だがサンプルcontentに値がない。正式な公開状態、編集可能範囲、公開業務ルールは未提供。両案ともeditor専用画面と表示箇所を確保する。
- **briefの根拠**：`course-catalog.json#/goals/4/needed_information`、`course-catalog.json#/requirements/5`、`course-catalog.json#/content`。
- **影響**：更新・公開の画面責務と権限分離は比較できるが、具体的な公開条件や実際の遷移が正しいかは判断できない。
- **解消方向**：productが状態値・編集可能項目・公開条件を示し、Bが状態遷移を具体化する。Aが未指定値を埋める必要はない。
- **担当領域**：product / 公開業務ルール。引継ぎ：A / 画面責務、B / 更新・公開の状態、C / 実認可。
- **確信度**：高。指定入力と両案の未解決事項から確認。正しい値やルールは推測していない。

**文書上の再現手順**

1. g_publishのneeded_informationとcontentを照合する。
2. 両案のeditor入口と編集画面のtitle/publication_statusを確認する。
3. learnerに公開機能を開放する経路がないことと、状態値が未確定であることを分けて記録する。

### INPUT-COURSE-IDENTITY-SAVE

- **対象**：course-catalog / R・S。分類：implementation。
- **JSON位置**：`R/course-catalog.plan.json#/unresolved/3`、`R/course-catalog.plan.json#/unresolved/4`、`S/course-catalog.plan.json#/unresolved/3`、`S/course-catalog.plan.json#/unresolved/6`。
- **不足の症状**：同じ利用者・同じ講座という関係は指定されているが、安定した講座ID、利用者識別、保存の永続化範囲はない。両案とも同じ講座を参照する設計とし、具体方式を未解決に残す。
- **briefの根拠**：`course-catalog.json#/requirements/4`、`course-catalog.json#/goals/3`、`course-catalog.json#/content`。
- **影響**：保存候補の再訪経路は成立しているが、再訪時や別端末の復元、同名講座の取り違え防止の実装は未確認。別端末対応を新たな必須要件にはしない。
- **解消方向**：productが保存の提供範囲を定め、Cが同一性のデータ契約を、Bが保存・解除・再訪の状態を具体化する。
- **担当領域**：product・C / 保存範囲と同一性のデータ契約。引継ぎ：A / 同一集合の情報構造、B / 保存・再訪の状態。
- **確信度**：高。指定入力と両案の未解決事項から確認。正しい値やルールは推測していない。

**文書上の再現手順**

1. r_saveが同じ利用者の同じ講座集合を要求することを確認する。
2. contentに安定IDがなく、利用者識別や保存方式もbriefに指定されていないことを確認する。
3. Rの保存済みビューとSのs_savedから共通詳細へ進む経路、および未解決事項を照合する。

### INPUT-COURSE-FILTER-DATA

- **対象**：course-catalog / R・S。分類：implementation。
- **JSON位置**：`R/course-catalog.plan.json#/unresolved/1`、`R/course-catalog.plan.json#/unresolved/0`、`S/course-catalog.plan.json#/unresolved/2`。
- **不足の症状**：日程と価格は表示用の文字列例が提供されている。実日付、反復開催、複数条件の意味、検索用データ契約までは確定していない。両案とも探索条件の配置を指定し、具体化を保留している。
- **briefの根拠**：`course-catalog.json#/requirements/0`、`course-catalog.json#/content`、`course-catalog.json#/contexts/boundary`。
- **影響**：提供例を使った情報構造の照合は可能だが、実データ全体に対する日程・予算検索の正確性や性能は確認できない。データ形式の詳細をAが書かなかったこと自体を必須機能の削除とは扱わない。
- **解消方向**：productとCが日程・価格の意味と提供契約を確定し、宣言された共通探索条件へ接続する。想定件数だけで性能方式を固定しない。
- **担当領域**：product・C / データ意味と検索契約。引継ぎ：A / 条件分類とラベル、B / 条件変更時の応答。
- **確信度**：高。指定入力と両案の未解決事項から確認。正しい値やルールは推測していない。

**文書上の再現手順**

1. r_findの4条件とサンプルschedule/priceを確認する。
2. 両案のs_catalogが4条件で同じ集合を探索する責務を持つことを確認する。
3. 具体的なデータ形式と実件数が未提供であることを未解決事項と照合する。

## 5. 領域別の判定と限界

| 領域 | 確認内容 | 判定・限界 |
|---|---|---|
| function | 必須の能力・依存・役割を両ケースとも保持。任意機能の統合・延期・除外には理由がある。 | 設計段階で要件保持 |
| information_architecture | 役割別入口から必要情報と機能へ明示経路がある。検索の同居/分離、保存候補のビュー/別画面には複数の成立案がある。 | 重大な到達不能なし。局所ラベルは確認課題 |
| interaction | 条件保持、比較候補、担当変更、保存、出力、公開などの状態はBへの引継ぎ。案が状態遷移を実装したとは扱わない。 | Aの責務外にある実動作は未確認 |
| visual | 両ケースとも指定visual_intent_idと既存の色・書体・装飾方針を維持する記述がある。 | 方針の整合のみ確認。実描画の一致・読みやすさは未確認 |
| implementation | 画面・機能の役割指定は適切。認可、データ保持、実リンク、公開状態、件数増加時の描画・検索性能は別途具体化が必要。 | 未実装事項を設計欠陥や実装済みの証拠に読み替えない |

シリアライズ契約については、4案とも必要項目、入力ID、機能の役割・依存・要件対応、統合先、画面参照に重大な不整合は見つかりません。任意で延期したg_trendsの経路が空であることは、briefが許す初回範囲と対応しています。

優劣をさらに判定するには、support-triageの着手と解決済み探索、course-catalogの保存候補再訪と複数条件の理解を、同じ情報内容の実画面で比較する必要があります。このレビューでは実施していません。

## 参照ファイル

- `support-triage.json`
- `course-catalog.json`
- `output-format.md`
- `R/support-triage.plan.json`
- `S/support-triage.plan.json`
- `R/course-catalog.plan.json`
- `S/course-catalog.plan.json`

読み込んだファイルの絶対パスはread-files.txt、各経路の情報IDとJSON Pointerはreview.jsonに記録しています。案の編集は行っていません。
