# Plan-A (syco-bench) – 進捗メモ

| フェーズ | 状態 | 完了したこと | 残タスク |
|---------|------|-------------|-----------|
| **0. ブランチ作成**<br>`plan-a-syco-bench` | ✅ 完了 | • fork & 作業ブランチ生成 | — |
| **1. PoC 動作**<br>*ローカル／Termux stub* | ✅ 完了 | • `setup_sycoqa_stub.sh` で venv + 依存ゼロ実行<br>• SycoQA 全問を DummySampler で走破 | — |
| **2. 正式依存解決** | ⏳ 着手前 | — | ▢ `sentence-transformers` + `torch` を optional-deps 化<br>▢ `ChatCompletionSampler` を実装し API キー切替 |
| **3. コード整理** | ⏳ 未着手 | — | ▢ stub を `scripts/` 隔離<br>▢ `simple_evals/` をクリーンに保つ |
| **4. CI 組込** | ⏳ 未着手 | — | ▢ GH Actions で smoke-test (stub / full) |
| **5. ドキュメント & PR** | ⏳ 未着手 | — | ▢ README に SycoBench 概要追記<br>▢ Upstream → PR |

---

---

## 次の TODO (優先度順)

1. **本番 Sampler/Grader 置換**  
2. **依存管理を extras で整理**  
3. **stub 隔離 & CI smoke-test**  
4. **README に簡潔な実行例を追加**  
5. **Upstream 規約に合わせたコード整形**

---

> **メモ**  
> * “PoC” はスマホ単体でも動作確認済み。  
> * OpenAI API を用いた実スコア測定は `ChatCompletionSampler` 差し替え後に実施する。

