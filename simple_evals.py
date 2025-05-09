import json
import argparse
import pandas as pd
import os
import common
from browsecomp_eval import BrowseCompEval
from drop_eval import DropEval
from gpqa_eval import GPQAEval
from humaneval_eval import HumanEval
from math_eval import MathEval
from mgsm_eval import MGSMEval
from mmlu_eval import MMLUEval
from simpleqa_eval import SimpleQAEval
from sampler.chat_completion_sampler import (
    OPENAI_SYSTEM_MESSAGE_API,
    OPENAI_SYSTEM_MESSAGE_CHATGPT,
    ChatCompletionSampler,
)
from sampler.o_chat_completion_sampler import OChatCompletionSampler
from sampler.responses_sampler import ResponsesSampler
from sampler.claude_sampler import ClaudeCompletionSampler, CLAUDE_SYSTEM_MESSAGE_LMSYS
from sampler.gemini_sampler import GeminiSampler
from sampler.claude_vertex_sampler import ClaudeVertexCompletionSampler


def main():
    parser = argparse.ArgumentParser(
        description="Run sampling and evaluations using different samplers and evaluations."
    )
    parser.add_argument(
        "--list-models", action="store_true", help="List available models"
    )
    parser.add_argument("--model", type=str, help="Select a model by name")
    parser.add_argument("--debug", action="store_true", help="Run in debug mode")
    parser.add_argument(
        "--examples", type=int, help="Number of examples to use (overrides default)"
    )
    parser.add_argument(
        "--evals",
        type=str,
        nargs="+",
        help="Specify one or more evaluation suites to run (e.g., mmlu math)",
        default=["simpleqa", "mmlu", "math", "gpqa", "mgsm", "drop", "humaneval", "browsecomp"],
    )
    parser.add_argument(
        "--checkpoint_dir",
        type=str,
        help="Directory to store and load checkpoint files for each eval. If not provided, checkpointing is disabled.",
        default=None,
    )
    parser.add_argument(
        "--use-gemini-grounding",
        action="store_true",
        help="Enable Gemini grounding API for Gemini models."
    )

    args = parser.parse_args()

    models = {
        # Reasoning Models
        "o3": ResponsesSampler(
            model="o3-2025-04-16",
            reasoning_model=True,
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
        "o1": OChatCompletionSampler(
            model="o1",
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
        # Llama models:
        "llama-4-maverick-17b-128e-instruct-maas": ChatCompletionSampler(
            model="meta/llama-4-maverick-17b-128e-instruct-maas",
            system_message=OPENAI_SYSTEM_MESSAGE_API,
            base_url="https://us-east5-aiplatform.googleapis.com/v1/projects/{your-project-id}/locations/us-east5/endpoints/openapi"
        ),
        "gemini-2.5-pro-preview-05-06": GeminiSampler(
            model="gemini-2.5-pro-preview-05-06",
            project_id="{your-project-id}",
            location="us-central1",
            use_gemini_grounding=args.use_gemini_grounding,
        ),
        "gemini-2.0-flash-001": GeminiSampler(
            model="gemini-2.0-flash-001",
            project_id="{your-project-id}",
            location="us-central1",
            use_gemini_grounding=args.use_gemini_grounding,
        ),
        # "claude-3-7-sonnet": ClaudeVertexCompletionSampler(
        #     model="claude-3-7-sonnet@20250219",
        #     project_id="{your-project-id}",
        #     location="us-east5",
        # ),
    }

    if args.list_models:
        print("Available models:")
        for model_name in models.keys():
            print(f" - {model_name}")
        return

    if args.model:
        if args.model not in models:
            print(f"Error: Model '{args.model}' not found.")
            return
        models = {args.model: models[args.model]}

    # grading_sampler = ChatCompletionSampler(model="gpt-4o")
    grading_sampler = ChatCompletionSampler(
        model="meta/llama-4-maverick-17b-128e-instruct-maas",
        system_message=OPENAI_SYSTEM_MESSAGE_API,
        base_url="https://us-east5-aiplatform.googleapis.com/v1/projects/{your-project-id}/locations/us-east5/endpoints/openapi"
    )
    # equality_checker = ChatCompletionSampler(model="gpt-4-turbo-preview")
    equality_checker = ChatCompletionSampler(
        model="meta/llama-4-maverick-17b-128e-instruct-maas",
        system_message=OPENAI_SYSTEM_MESSAGE_API,
        base_url="https://us-east5-aiplatform.googleapis.com/v1/projects/{your-project-id}/locations/us-east5/endpoints/openapi"
    )
    # ^^^ used for fuzzy matching, just for math

    def get_evals(eval_name, debug_mode, checkpoint_dir, model_name_for_checkpoint):
        num_examples = (
            args.examples if args.examples is not None else (5 if debug_mode else None)
        )

        checkpoint_file_path = None
        if checkpoint_dir and model_name_for_checkpoint:
            # Construct a debug suffix consistent with the one used for report filenames
            debug_suffix_for_file = "_DEBUG" if debug_mode else ""
            # Sanitize model_name_for_checkpoint by replacing slashes with underscores for valid filenames
            sanitized_model_name = model_name_for_checkpoint.replace("/", "_")
            checkpoint_filename = f"{eval_name}_{sanitized_model_name}{debug_suffix_for_file}.jsonl"
            checkpoint_file_path = os.path.join(checkpoint_dir, checkpoint_filename)
            os.makedirs(checkpoint_dir, exist_ok=True) # Ensure directory exists

        # Set num_examples = None to reproduce full evals
        match eval_name:
            case "mmlu":
                return MMLUEval(num_examples=1 if debug_mode else num_examples, checkpoint_file=checkpoint_file_path)
            case "math":
                return MathEval(
                    equality_checker=equality_checker,
                    num_examples=num_examples,
                    n_repeats=1 if debug_mode else 10,
                    checkpoint_file=checkpoint_file_path
                )
            case "gpqa":
                return GPQAEval(
                    n_repeats=1 if debug_mode else 10, num_examples=num_examples, checkpoint_file=checkpoint_file_path
                )
            case "mgsm": # MGSMEval might need specific handling for num_examples_per_lang with checkpointing
                return MGSMEval(num_examples_per_lang=10 if debug_mode else 250, checkpoint_file=checkpoint_file_path)
            case "drop":
                return DropEval(
                    num_examples=10 if debug_mode else num_examples,
                    train_samples_per_prompt=3,
                    checkpoint_file=checkpoint_file_path
                )
            case "humaneval": # HumanEval might process problems, checkpointing logic might differ
                return HumanEval(num_examples=10 if debug_mode else num_examples, checkpoint_file=checkpoint_file_path)
            case "simpleqa":
                return SimpleQAEval(
                    grader_model=grading_sampler,
                    num_examples=10 if debug_mode else num_examples,
                    checkpoint_file=checkpoint_file_path
                )
            case "browsecomp":
                return BrowseCompEval(
                    grader_model=grading_sampler,
                    num_examples=10 if debug_mode else num_examples,
                    checkpoint_file=checkpoint_file_path
                )
            case _:
                raise Exception(f"Unrecognized eval type: {eval_name}")

    evals_dict = {} # Changed from evals to evals_dict to avoid conflict
    for model_name, sampler in models.items():
        current_model_evals = {
            eval_name: get_evals(eval_name, args.debug, args.checkpoint_dir, model_name) # Pass checkpoint_dir and model_name
            for eval_name in args.evals
        }
        evals_dict[model_name] = current_model_evals

    debug_suffix = "_DEBUG" if args.debug else ""

    mergekey2resultpath = {}
    for model_name, sampler in models.items():
        for eval_name, eval_obj in evals_dict[model_name].items(): # Iterate through the new structure
            result = eval_obj(sampler)
            # ^^^ how to use a sampler
            file_stem = f"{eval_name}_{model_name}"
            report_filename = f"./tmp/{file_stem}{debug_suffix}.html"
            print(f"Writing report to {report_filename}")
            with open(report_filename, "w", encoding="utf-8") as fh:
                fh.write(common.make_report(result))
            metrics = result.metrics | {"score": result.score}
            print(metrics)
            result_filename = f"./tmp/{file_stem}{debug_suffix}.json"
            with open(result_filename, "w", encoding="utf-8") as f:
                f.write(json.dumps(metrics, indent=2))
            print(f"Writing results to {result_filename}")
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
