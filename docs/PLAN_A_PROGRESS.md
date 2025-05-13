# Plan-A SycoBench移植プロジェクト：残務タスク

## ✅ これまでに完了したこと
- [x] `simple-evals` をローカル移植し `plan-a-syco-bench` ブランチで作業開始
- [x] `ChatCompletionSampler` を正式実装（sample() ラッパー含む）
- [x] `pyproject.toml` に openai>=1.0 を追加、依存整理
- [x] smoke / full の2段階 CI ジョブを Actions に統合（gpt-4o 対応）
- [x] テスト通過を確認（OpenAI API キーの dummy / secrets 切替も成功）
- [x] README 整理 / コミット粒度整備

---

## 🟡 残務タスク（次回以降の再始動に向けて）

### 🔹 A. リファクタ＆ドキュメント系
- [ ] `chat_completion_sampler.py` に docstring を追加
- [ ] `tests/smoke/test_smoke_full.py` に追加ケース（PoR失敗／grv低スコア）を追加
- [ ] `README.md` に以下を追記  
  - 追加されたサンプラの説明  
  - GitHub Actions バッジ  
  - 必要な依存（openai）

### 🔹 B. PR 出力整備（openai/simple-evals 向け）
- [ ] `CHANGELOG.md` を追加し、`feat: ChatCompletionSampler` 系の記録を明記
- [ ] `pull_request_project.yaml` がある場合、更新するか不要なら削除
- [ ] PR テンプレート文（タイトル、本文、関連 Issue など）を生成する

### 🔹 C. SycoQA 拡張ロードマップ着手準備
- [ ] ΔE（semantic_match）を bge-large に切り替えて再評価
- [ ] grv（keyword_match）に KeyBERT + TF-IDF 重み付け導入
- [ ] 発火PoR数を評価出力に含める（文単位分割 or 閾値付きマルチ評価）
- [ ] UGH3 CSVエクスポート形式への変換準備

---

## 🔹 任意・低優先
- [ ] `tools/` や `agent.yml` を使った GPTme オートランテスト
- [ ] OpenAIモデル変更（gpt-3.5 比較）向けの簡易切替インターフェース

---

## 次回開始用メモ
- [ ] `cd ~/repos/simple-evals`
- [ ] `git checkout plan-a-syco-bench`
- [ ] `gptme chat -w ~/jp-agent`（常時日本語応答環境）