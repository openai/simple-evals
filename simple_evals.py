import argparse
import json
import subprocess
from datetime import datetime

import pandas as pd

from . import common
from .browsecomp_eval import BrowseCompEval
from .drop_eval import DropEval
from .gpqa_eval import GPQAEval
from .healthbench_eval import HealthBenchEval
from .healthbench_meta_eval import HealthBenchMetaEval
from .math_eval import MathEval
from .mgsm_eval import MGSMEval
from .mmlu_eval import MMLUEval
from .humaneval_eval import HumanEval
from .sampler.chat_completion_sampler import (
    OPENAI_SYSTEM_MESSAGE_API,
    OPENAI_SYSTEM_MESSAGE_CHATGPT,
    ChatCompletionSampler,
)
from .sampler.claude_sampler import ClaudeCompletionSampler, CLAUDE_SYSTEM_MESSAGE_LMSYS
from .sampler.o_chat_completion_sampler import OChatCompletionSampler
from .sampler.responses_sampler import ResponsesSampler
from .simpleqa_eval import SimpleQAEval


def main():
    parser = argparse.ArgumentParser(
        description="Run sampling and evaluations using different samplers and evaluations."
    )
    parser.add_argument(
        "--list-models", action="store_true", help="List available models"
    )
    parser.add_argument(
        "--model",
        type=str,
        help="Select a model by name. Also accepts a comma-separated list of models.",
    )
    parser.add_argument(
        "--eval",
        type=str,
        help="Select an eval by name. Also accepts a comma-separated list of evals.",
    )
    parser.add_argument(
        "--n-repeats",
        type=int,
        default=None,
        help="Number of repeats to run. Only supported for certain evals.",
    )
    parser.add_argument(
        "--n-threads",
        type=int,
        default=120,
        help="Number of threads to run. Only supported for HealthBench and HealthBenchMeta.",
    )
    parser.add_argument("--debug", action="store_true", help="Run in debug mode")
    parser.add_argument(
        "--examples", type=int, help="Number of examples to use (overrides default)"
    )

    args = parser.parse_args()

    models = {
        # Reasoning Models
        "o3": ResponsesSampler(
            model="o3-2025-04-16",
            reasoning_model=True,
        ),
        "o3-temp-1": ResponsesSampler(
            model="o3-2025-04-16",
            reasoning_model=True,
            temperature=1.0,
        ),
        "o3_high": ResponsesSampler(
            model="o3-2025-04-16",
            reasoning_model=True,
            reasoning_effort="high",
        ),
        "o3_low": ResponsesSampler(
            model="o3-2025-04-16",
            reasoning_model=True,
            reasoning_effort="low",
        ),
        # Default == Medium
        "o4-mini": ResponsesSampler(
            model="o4-mini-2025-04-16",
            reasoning_model=True,
        ),
        "o4-mini_high": ResponsesSampler(
            model="o4-mini-2025-04-16",
            reasoning_model=True,
            reasoning_effort="high",
        ),
        "o4-mini_low": ResponsesSampler(
            model="o4-mini-2025-04-16",
            reasoning_model=True,
            reasoning_effort="low",
        ),
        "o1-pro": ResponsesSampler(
            model="o1-pro",
            reasoning_model=True,
        ),
        "o1": OChatCompletionSampler(
            model="o1",
        ),
        "o1_high": OChatCompletionSampler(
            model="o1",
            reasoning_effort="high",
        ),
        "o1_low": OChatCompletionSampler(
            model="o1",
            reasoning_effort="low",
        ),
        "o1-preview": OChatCompletionSampler(
            model="o1-preview",
        ),
        "o1-mini": OChatCompletionSampler(
            model="o1-mini",
        ),
        # Default == Medium
        "o3-mini": OChatCompletionSampler(
            model="o3-mini",
        ),
        "o3-mini_high": OChatCompletionSampler(
            model="o3-mini",
            reasoning_effort="high",
        ),
        "o3-mini_low": OChatCompletionSampler(
            model="o3-mini",
            reasoning_effort="low",
        ),
        # GPT-4.1 models
        "gpt-4.1": ChatCompletionSampler(
            model="gpt-4.1-2025-04-14",
            system_message=OPENAI_SYSTEM_MESSAGE_API,
            max_tokens=2048,
        ),
        "gpt-4.1-temp-1": ChatCompletionSampler(
            model="gpt-4.1-2025-04-14",
            system_message=OPENAI_SYSTEM_MESSAGE_API,
            max_tokens=2048,
            temperature=1.0,
        ),
        "gpt-4.1-mini": ChatCompletionSampler(
            model="gpt-4.1-mini-2025-04-14",
            system_message=OPENAI_SYSTEM_MESSAGE_API,
            max_tokens=2048,
        ),
        "gpt-4.1-nano": ChatCompletionSampler(
            model="gpt-4.1-nano-2025-04-14",
            system_message=OPENAI_SYSTEM_MESSAGE_API,
            max_tokens=2048,
        ),
        # GPT-4o models
        "gpt-4o": ChatCompletionSampler(
            model="gpt-4o",
            system_message=OPENAI_SYSTEM_MESSAGE_API,
            max_tokens=2048,
        ),
        "gpt-4o-2024-11-20": ChatCompletionSampler(
            model="gpt-4o-2024-11-20",
            system_message=OPENAI_SYSTEM_MESSAGE_API,
            max_tokens=2048,
        ),
        "gpt-4o-2024-08-06": ChatCompletionSampler(
            model="gpt-4o-2024-08-06",
            system_message=OPENAI_SYSTEM_MESSAGE_API,
            max_tokens=2048,
        ),
        "gpt-4o-2024-08-06-temp-1": ChatCompletionSampler(
            model="gpt-4o-2024-08-06",
            system_message=OPENAI_SYSTEM_MESSAGE_API,
            max_tokens=2048,
            temperature=1.0,
        ),
        "gpt-4o-2024-05-13": ChatCompletionSampler(
            model="gpt-4o-2024-05-13",
            system_message=OPENAI_SYSTEM_MESSAGE_API,
            max_tokens=2048,
        ),
        "gpt-4o-mini": ChatCompletionSampler(
            model="gpt-4o-mini-2024-07-18",
            system_message=OPENAI_SYSTEM_MESSAGE_API,
            max_tokens=2048,
        ),
        # GPT-4.5 model
        "gpt-4.5-preview": ChatCompletionSampler(
            model="gpt-4.5-preview-2025-02-27",
            system_message=OPENAI_SYSTEM_MESSAGE_API,
            max_tokens=2048,
        ),
        # GPT-4-turbo model
        "gpt-4-turbo-2024-04-09": ChatCompletionSampler(
            model="gpt-4-turbo-2024-04-09",
            system_message=OPENAI_SYSTEM_MESSAGE_API,
        ),
        # GPT-4 model
        "gpt-4-0613": ChatCompletionSampler(
            model="gpt-4-0613",
            system_message=OPENAI_SYSTEM_MESSAGE_API,
        ),
        # GPT-3.5 Turbo model
        "gpt-3.5-turbo-0125": ChatCompletionSampler(
            model="gpt-3.5-turbo-0125",
            system_message=OPENAI_SYSTEM_MESSAGE_API,
        ),
        "gpt-3.5-turbo-0125-temp-1": ChatCompletionSampler(
            model="gpt-3.5-turbo-0125",
            system_message=OPENAI_SYSTEM_MESSAGE_API,
            temperature=1.0,
        ),
        # Chatgpt models:
        "chatgpt-4o-latest": ChatCompletionSampler(
            model="chatgpt-4o-latest",
            system_message=OPENAI_SYSTEM_MESSAGE_CHATGPT,
            max_tokens=2048,
        ),
        "gpt-4-turbo-2024-04-09_chatgpt": ChatCompletionSampler(
            model="gpt-4-turbo-2024-04-09",
            system_message=OPENAI_SYSTEM_MESSAGE_CHATGPT,
        ),
        # Claude models:
        "claude-3-opus-20240229_empty": ClaudeCompletionSampler(
            model="claude-3-opus-20240229",
            system_message=CLAUDE_SYSTEM_MESSAGE_LMSYS,
        ),
        "claude-3-7-sonnet-20250219": ClaudeCompletionSampler(
            model="claude-3-7-sonnet-20250219",
            system_message=CLAUDE_SYSTEM_MESSAGE_LMSYS,
        ),
        "claude-3-haiku-20240307": ClaudeCompletionSampler(
            model="claude-3-haiku-20240307",
        ),
    }

    if args.list_models:
        print("Available models:")
        for model_name in models.keys():
            print(f" - {model_name}")
        return

    if args.model:
        models_chosen = args.model.split(",")
        for model_name in models_chosen:
            if model_name not in models:
                print(f"Error: Model '{model_name}' not found.")
                return
        models = {model_name: models[model_name] for model_name in models_chosen}

    print(f"Running with args {args}")

    grading_sampler = ChatCompletionSampler(
        model="gpt-4.1-2025-04-14",
        system_message=OPENAI_SYSTEM_MESSAGE_API,
        max_tokens=2048,
    )
    equality_checker = ChatCompletionSampler(model="gpt-4-turbo-preview")
    # ^^^ used for fuzzy matching, just for math

    def get_evals(eval_name, debug_mode):
        num_examples = (
            args.examples if args.examples is not None else (5 if debug_mode else None)
        )
        # Set num_examples = None to reproduce full evals
        match eval_name:
            case "mmlu":
                return MMLUEval(num_examples=1 if debug_mode else num_examples)
            case "math":
                return MathEval(
                    equality_checker=equality_checker,
                    num_examples=num_examples,
                    n_repeats=1 if debug_mode else args.n_repeats or 10,
                )
            case "gpqa":
                return GPQAEval(
                    n_repeats=1 if debug_mode else args.n_repeats or 10,
                    num_examples=num_examples,
                )
            case "mgsm":
                return MGSMEval(
                    num_examples_per_lang=10 if debug_mode else num_examples or 250
                )
            case "drop":
                return DropEval(
                    num_examples=10 if debug_mode else num_examples,
                    train_samples_per_prompt=3,
                )
            case "humaneval":
                return HumanEval(num_examples=10 if debug_mode else num_examples)
            case "simpleqa":
                return SimpleQAEval(
                    grader_model=grading_sampler,
                    num_examples=10 if debug_mode else num_examples,
                )
            case "browsecomp":
                return BrowseCompEval(
                    grader_model=grading_sampler,
                    num_examples=10 if debug_mode else num_examples,
                )
            case "healthbench":
                return HealthBenchEval(
                    grader_model=grading_sampler,
                    num_examples=10 if debug_mode else num_examples,
                    n_repeats=args.n_repeats or 1,
                    n_threads=args.n_threads or 1,
                    subset_name=None,
                )
            case "healthbench_hard":
                return HealthBenchEval(
                    grader_model=grading_sampler,
                    num_examples=10 if debug_mode else num_examples,
                    n_repeats=args.n_repeats or 1,
                    n_threads=args.n_threads or 1,
                    subset_name="hard",
                )
            case "healthbench_consensus":
                return HealthBenchEval(
                    grader_model=grading_sampler,
                    num_examples=10 if debug_mode else num_examples,
                    n_repeats=args.n_repeats or 1,
                    n_threads=args.n_threads or 1,
                    subset_name="consensus",
                )
            case "healthbench_meta":
                return HealthBenchMetaEval(
                    grader_model=grading_sampler,
                    num_examples=10 if debug_mode else num_examples,
                    n_repeats=args.n_repeats or 1,
                    n_threads=args.n_threads or 1,
                )
            case _:
                raise Exception(f"Unrecognized eval type: {eval_name}")

    if args.eval:
        evals_list = args.eval.split(",")
        evals = {}
        for eval_name in evals_list:
            try:
                evals[eval_name] = get_evals(eval_name, args.debug)
            except Exception:
                print(f"Error: eval '{eval_name}' not found.")
                return
    else:
        evals = {
            eval_name: get_evals(eval_name, args.debug)
            for eval_name in [
                "mmlu",
                "math",
                "gpqa",
                "mgsm",
                "drop",
                "humaneval",
                "simpleqa",
                "browsecomp",
                "healthbench",
                "healthbench_hard",
                "healthbench_consensus",
                "healthbench_meta",
            ]
        }

    print(evals)
    debug_suffix = "_DEBUG" if args.debug else ""
    print(debug_suffix)
    mergekey2resultpath = {}
    print(f"Running the following evals: {list(evals.keys())}")
    print(f"Running evals for the following models: {list(models.keys())}")

    now = datetime.now()
    date_str = now.strftime("%Y%m%d_%H%M%S")
    for model_name, sampler in models.items():
        for eval_name, eval_obj in evals.items():
            result = eval_obj(sampler)
            # ^^^ how to use a sampler
            file_stem = f"{eval_name}_{model_name}"
            # file stem should also include the year, month, day, and time in hours and minutes
            file_stem += f"_{date_str}"
            report_filename = f"/tmp/{file_stem}{debug_suffix}.html"
            print(f"Writing report to {report_filename}")
            with open(report_filename, "w") as fh:
                fh.write(common.make_report(result))
            assert result.metrics is not None
            metrics = result.metrics | {"score": result.score}
            # Sort metrics by key
            metrics = dict(sorted(metrics.items()))
            print(metrics)
            result_filename = f"/tmp/{file_stem}{debug_suffix}.json"
            with open(result_filename, "w") as f:
                f.write(json.dumps(metrics, indent=2))
            print(f"Writing results to {result_filename}")

            full_result_filename = f"/tmp/{file_stem}{debug_suffix}_allresults.json"
            with open(full_result_filename, "w") as f:
                result_dict = {
                    "score": result.score,
                    "metrics": result.metrics,
                    "htmls": result.htmls,
                    "convos": result.convos,
                    "metadata": result.metadata,
                }
                f.write(json.dumps(result_dict, indent=2))
                print(f"Writing all results to {full_result_filename}")

            mergekey2resultpath[f"{file_stem}"] = result_filename
    merge_metrics = []
    for eval_model_name, result_filename in mergekey2resultpath.items():
        try:
            result = json.load(open(result_filename, "r+"))
        except Exception as e:
            print(e, result_filename)
            continue
        result = result.get("f1_score", result.get("score", None))
        eval_name = eval_model_name[: eval_model_name.find("_")]
        model_name = eval_model_name[eval_model_name.find("_") + 1 :]
        merge_metrics.append(
            {"eval_name": eval_name, "model_name": model_name, "metric": result}
        )
    merge_metrics_df = pd.DataFrame(merge_metrics).pivot(
        index=["model_name"], columns="eval_name"
    )
    print("\nAll results: ")
    print(merge_metrics_df.to_markdown())
    return merge_metrics


if __name__ == "__main__":
    main()
