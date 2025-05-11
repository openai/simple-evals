Plan-A (SycoBench) — 進捗レポート 2025-05-11 時点

フェーズ	現状	完了したこと	残タスク

0. ブランチ作成<br>plan-a-syco-bench	✅ 完了	• fork 済み・作業ブランチ生成	—
1. PoC 動作確認<br>ローカル／Termux stub	✅ 完了	• setup_sycoqa_stub.sh で venv + 依存ゼロ実行<br>• SycoQA 全問を DummySampler で走破	—
2. 正式依存解決	🟡 進行中	• simple_evals 側の構文エラー解消・API KEY 検証済み<br>• OpenAI 経由の実スコア測定に向け 環境／変数 整備	▢ sentence-transformers, torch を extras オプション化<br>▢ ChatCompletionSampler 実装（API KEY 切替対応）<br>▢ requirements.txt / pyproject.toml 整理
3. コード整理	⏳ 未着手	—	▢ stub & helper を scripts/ に隔離<br>▢ simple_evals/ をクリーンに保つ
4. CI 組込み	⏳ 未着手	—	▢ GH Actions で smoke-test (stub / full) ワークフロー作成<br>▢ API KEY の注入方法を機密管理
5. ドキュメント & PR	⏳ 未着手	—	▢ README に SycoBench 概要 & 実行例を追記<br>▢ Upstream へ PR（コード整形・規約準拠）



---

進捗率（概算）

フェーズ完了: 2 / 6

フェーズ進行中: 1
→ 約 35 % 完了



---

直近 TODO（優先度順）

1. 依存・Sampler 実装を固める

ChatCompletionSampler を差し替えて OpenAI 評価が通ることを確認

重量ライブラリを extras に分離、pip install .[full] 方式へ



2. stub 隔離 & コード整形

scripts/ ディレクトリへ移動、black / ruff でフォーマット



3. CI スモークテスト

stub と full の 2 job 構成で失敗早期検知



4. README 更新

最小実行例、環境変数サンプル、スマホ実行 Tips 追加



5. PR 作成

タイトル・本文テンプレ整備、ラベル・チェックリスト付与





---

補足

GPTme エージェント が今後のルーチンを担当予定。
→ 各タスクを小粒のコマンド／スクリプト単位で切り出して渡すと運用がスムーズです。

OpenAI API KEY は GH Actions の Secrets に登録し、safe_chat でも共有可能な変数名 (OPENAI_API_KEY) に統一すると後工程が楽になります。


以上が最新の進捗とタスク整理です。追加･修正があれば指示ください！


