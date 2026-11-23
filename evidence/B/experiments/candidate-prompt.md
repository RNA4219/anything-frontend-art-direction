あなたは固定要件に基づく実装担当です。日本語で記録してください。
作業リポジトリ: /workspace/scratch/392a80e65402/anything-frontend-session-B
課題: evidence/B/experiments/shared/tasks.md と visual-lock.md を読み、同一ページの2課題を実装してください。
shared/api.mjs の公開APIのみをcontrollerへ渡し、Node標準ESMで動作させてください。
利用できる設計Skill: /workspace/scratch/392a80e65402/anything-frontend-B-base/SKILL.md と /workspace/scratch/392a80e65402/anything-frontend-session-B/extensions/B/SKILL.md
Skillの入口と、その入口からタスクに関連する参照先を読み、適用してください。
読取り許可: 共有課題・視覚条件・api.mjs、上記Skillとその参照先、書込み先の自作ファイル、Node/OSの通常ランタイム。
読取り禁止: 他条件の出力、evidence/Bの他の文書、評価用ファイル、agent通信、テストの内部control実装以外の未指定資料。
外部検索、別条件の推測、サブエージェント追加は不要です。既存Skillは現行ファイルを正としてください。
書込み先: /workspace/scratch/392a80e65402/anything-frontend-session-B/evidence/B/experiments/candidate
必要成果物: reservation.mjs、import-job.mjs、index.html、decisions.md。
Skillが要求する追加成果物は書込み先内に作成できます。
index.htmlは共通APIを相対importし、通常デモ進行をUIから分離してください。内部debug操作を製品UIへ入れないでください。
要件を満たすための自己確認は実施できますが、共通評価テストは読まず、他条件の出力は変更しないでください。
ブラウザー操作は既に環境・URLポリシーでブロックされているため試さず、画面確認成功を主張しないでください。
出力初版をそのまま比較します。root Skill/README/他ディレクトリの変更、git commit/pushは行わないでください。
終了時、作成ファイル、実行した確認、未検証事項を報告してください。比較点数や優劣は自己採点しないでください。
