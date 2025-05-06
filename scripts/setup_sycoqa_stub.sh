#!/usr/bin/env bash
###############################################################################
# simple-evals (SycoQA) – Termux minimal setup script (stub-only, offline mode)
# Tested on: Termux 0.118.0, Python 3.12 (venv), Samsung SCV41 (Android 12)
#
# ⚠  本スクリプトは「スマホ単体で *とりあえず動かす*」ことが目的。
#     - OpenAI API は呼びません（DummySampler で stub 動作）
#     - multiprocessing＋tqdm で CPU を食うのでコア数が少ない端末は待ち時間長め
#     - 実スコアを取得したい場合は「注意書き」を読んで差し替えてください
###############################################################################

set -eu

### 0. 準備 ───────────────────────────────────────────────────────────────
PREFIX=${PREFIX:-$HOME/.termux-prefix}           # Termux の $PREFIX 変数
WORKDIR=$HOME/work
VENV=$HOME/.venv

pkg update && pkg upgrade -y
pkg install -y git curl vim python

python -m ensurepip --upgrade
python -m venv "$VENV"
source "$VENV/bin/activate"
pip install --upgrade pip fire jinja2 pandas requests tqdm openai

### 1. Clone (shallow) ──────────────────────────────────────────────────
mkdir -p "$WORKDIR" && cd "$WORKDIR"
git clone --depth 1 --branch plan-a-syco-bench \
  https://github.com/Yuu6798/simple-evals.git
cd simple-evals

### 2. 手動パッケージ修復 ──────────────────────────────────────────────
mkdir -p simple_evals/sampler          # 足りないディレクトリ
# *.py を simple_evals/ 直下へ移動
for f in *_eval.py run_multilingual_mmlu.py semantic_match.py \
         simpleqa_eval.py project_types.py browsecomp_eval.py; do
  [ -f "$f" ] && mv "$f" simple_evals/
done

### 3. 軽量スタブ群を配置 ───────────────────────────────────────────────
# eval_types_stub.py (EvalResult / SingleEvalResult 最小実装)
cat > simple_evals/eval_types_stub.py <<'EOF'
class SingleEvalResult:
    def __init__(self, html="", score=0.0, convo=None, metrics=None, **__):
        self.html = html
        self.score = score
        self.convo = convo
        self.metrics = metrics or {"is_correct": 0}
class EvalResult:         pass
class Eval:               pass
class SamplerBase:        pass
EOF

# DummySampler (OpenAI API を呼ばず常に “I don't know.”)
mkdir -p simple_evals/sampler
cat > simple_evals/sampler/dummy_sampler.py <<'EOF'
class DummySampler:
    def _pack_message(self, content: str, role: str = "user"):
        return {"role": role, "content": content}
    def __call__(self, prompt_messages, *_, **__):
        return "I don't know."
EOF

# simpleqa_eval.py で types import を stub に切替
sed -i 's/from .types import/from .eval_types_stub import/' \
  simple_evals/simpleqa_eval.py

### 4. ランナー作成 (Fire 依存なし) ────────────────────────────────────
cat > simple_evals/run_sycoqa.py <<'EOF'
import argparse, json, tqdm
from simple_evals.simpleqa_eval import SimpleQAEval
from simple_evals.sampler.dummy_sampler import DummySampler

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--output_path", required=True)
    args = p.parse_args()

    sampler = DummySampler()
    evaluator = SimpleQAEval(grader_model="gpt-4")   # grader も固定 (dummy)
    results = evaluator(sampler)

    # JSONL 形式で 1 行出力
    with open(args.output_path, "w") as f:
        json.dump(results.__dict__, f, ensure_ascii=False)
    print("✔ SycoQA dummy run complete →", args.output_path)

if __name__ == "__main__":
    main()
EOF

### 5. 走らせる (約 4.3k 問, DummySampler なので高速) ───────────────
python simple_evals/run_sycoqa.py \
  --output_path "$PREFIX/tmp/syco_qa_output.jsonl"

###############################################################################
# 注意書き
# -----------------------------------------------------------------------------
# ❶ OpenAI API で実スコアを取りたい場合
#     simple_evals/sampler/chat_completion_sampler.py を元に
#       from simple_evals.sampler.chat_completion_sampler import ChatCompletionSampler
#     sampler = ChatCompletionSampler(api_key="sk-...")
#     evaluator = SimpleQAEval(grader_model=ChatCompletionSampler(api_key="sk-..."))
#
# ❷ ラムダバージョン衝突を避けたい場合
#     Termux 混在環境では python-tk 等 GUI 依存を入れないよう注意。
#
# ❸ 清掃
#     find simple_evals -name '__pycache__' -exec rm -r {} +
###############################################################################