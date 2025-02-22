# add current folder to python path
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent))

import json
from typing import Dict, Optional

import logfire
import pandas as pd
import typer
from dotenv import load_dotenv

import common
from drop_eval import DropEval
from gpqa_eval import GPQAEval
from humaneval_eval import HumanEval
from math_eval import MathEval
from mgsm_eval import MGSMEval
from mmlu_eval import MMLUEval
from sampler.chat_completion_sampler import (
    OPENAI_SYSTEM_MESSAGE_API,
    OPENAI_SYSTEM_MESSAGE_CHATGPT,
    ChatCompletionSampler,
)
from sampler.claude_sampler import CLAUDE_SYSTEM_MESSAGE_LMSYS, ClaudeCompletionSampler
from sampler.o_chat_completion_sampler import OChatCompletionSampler
from simpleqa_eval import SimpleQAEval

# Load environment variables
load_dotenv()

# Configure logfire
logfire.configure()
logfire.instrument_openai()

# Initialize Typer app
app = typer.Typer()


def get_available_models() -> Dict[str, ChatCompletionSampler]:
    """Return dictionary of available models and their samplers."""
    return {
        # chatgpt models:
        "gpt-4o-2024-11-20_assistant": ChatCompletionSampler(
            model="gpt-4o-2024-11-20",
            system_message=OPENAI_SYSTEM_MESSAGE_API,
            max_tokens=2048,
        ),
        "gpt-4o-2024-11-20_chatgpt": ChatCompletionSampler(
            model="gpt-4o-2024-11-20",
            system_message=OPENAI_SYSTEM_MESSAGE_CHATGPT,
            max_tokens=2048,
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
        "gpt-4-turbo-2024-04-09_assistant": ChatCompletionSampler(
            model="gpt-4-turbo-2024-04-09",
            system_message=OPENAI_SYSTEM_MESSAGE_API,
        ),
        "gpt-4-turbo-2024-04-09_chatgpt": ChatCompletionSampler(
            model="gpt-4-turbo-2024-04-09",
            system_message=OPENAI_SYSTEM_MESSAGE_CHATGPT,
        ),
        "gpt-4o_assistant": ChatCompletionSampler(
            model="gpt-4o",
            system_message=OPENAI_SYSTEM_MESSAGE_API,
            max_tokens=2048,
        ),
        "gpt-4o_chatgpt": ChatCompletionSampler(
            model="gpt-4o",
            system_message=OPENAI_SYSTEM_MESSAGE_CHATGPT,
            max_tokens=2048,
        ),
        "gpt-4o-mini-2024-07-18": ChatCompletionSampler(
            model="gpt-4o-mini-2024-07-18",
            system_message=OPENAI_SYSTEM_MESSAGE_API,
            max_tokens=2048,
        ),
        # claude models:
        "claude-3-opus-20240229_empty": ClaudeCompletionSampler(
            model="claude-3-opus-20240229",
            system_message=CLAUDE_SYSTEM_MESSAGE_LMSYS,
        ),
        # Llama 3 models
        "llama-3-8b": ChatCompletionSampler(
            model="llama-3-8b",
            system_message=OPENAI_SYSTEM_MESSAGE_API,
            max_tokens=2048,
        ),
        "llama-3.3-70b": ChatCompletionSampler(
            model="llama-3.3-70b",
            system_message=OPENAI_SYSTEM_MESSAGE_API,
            max_tokens=2048,
        ),
        # Qwen 2.5 models
        "qwen-2.5-32b": ChatCompletionSampler(
            model="qwen-2.5-32b",
            system_message=OPENAI_SYSTEM_MESSAGE_API,
            max_tokens=2048,
        ),
        # DeepSeek R1 models
        "deepseek-r1-llama-8b": OChatCompletionSampler(
            model="deepseek-r1-llama-8b",
        ),
        "deepseek-r1-llama-70b": OChatCompletionSampler(
            model="deepseek-r1-llama-70b",
        ),
        "deepseek-r1-qwen-32b": OChatCompletionSampler(
            model="deepseek-r1-qwen-32b",
        ),
    }


def get_available_evals() -> list[str]:
    return [
        "simpleqa",
        "mmlu",
        "math",
        "gpqa",
        "mgsm",
        "drop",
        "humaneval",
    ]


def get_eval_instance(eval_name: str, debug_mode: bool, num_examples: Optional[int] = None) -> any:
    """Get evaluation instance based on name and parameters."""
    grading_sampler = ChatCompletionSampler(model="llama-3.3-70b")
    equality_checker = ChatCompletionSampler(model="llama-3.3-70b")

    examples = num_examples if num_examples is not None else (5 if debug_mode else None)

    eval_configs = {
        "mmlu": lambda: MMLUEval(num_examples=1 if debug_mode else examples),
        "math": lambda: MathEval(
            equality_checker=equality_checker,
            num_examples=examples,
            n_repeats=1 if debug_mode else 10,
        ),
        "gpqa": lambda: GPQAEval(n_repeats=1 if debug_mode else 10, num_examples=examples),
        "mgsm": lambda: MGSMEval(num_examples_per_lang=10 if debug_mode else 250),
        "drop": lambda: DropEval(
            num_examples=10 if debug_mode else examples,
            train_samples_per_prompt=3,
        ),
        "humaneval": lambda: HumanEval(num_examples=10 if debug_mode else examples),
        "simpleqa": lambda: SimpleQAEval(
            grader_model=grading_sampler,
            num_examples=10 if debug_mode else examples,
        ),
    }

    if eval_name not in eval_configs:
        raise ValueError(f"Unrecognized eval type: {eval_name}")

    return eval_configs[eval_name]()


def write_results(result: any, eval_name: str, model_name: str, output_dir: Path) -> str:
    """Write evaluation results to files and return result filename."""
    output_dir.mkdir(exist_ok=True)

    file_stem = f"{eval_name}_{model_name}"

    # Write HTML report
    report_filename = output_dir / f"{file_stem}-report.html"
    report_filename.write_text(common.make_report(result))
    typer.echo(f"Writing report to {report_filename}")

    # Write metrics
    metrics_filename = output_dir / f"{file_stem}-metrics.json"
    metrics = result.metrics | {"score": result.score}
    metrics_filename.write_text(json.dumps(metrics, indent=2))
    typer.echo(f"Writing results to {metrics_filename}")

    # Write results
    results_filename = output_dir / f"{file_stem}-results.json"
    results_filename.write_text(json.dumps(result.results, indent=2))
    typer.echo(f"Writing results to {results_filename}")
    return str(metrics_filename)


def create_results_dataframe(mergekey2resultpath: Dict[str, str]) -> pd.DataFrame:
    """Create and return a DataFrame from evaluation results."""
    merge_metrics = []

    for eval_model_name, result_filename in mergekey2resultpath.items():
        try:
            with open(result_filename) as f:
                result = json.load(f)
        except Exception as e:
            typer.echo(f"Error loading {result_filename}: {e}")
            continue

        result = result.get("f1_score", result.get("score", None))
        eval_name, model_name = eval_model_name.split("_", 1)

        merge_metrics.append({"eval_name": eval_name, "model_name": model_name, "metric": result})

    return pd.DataFrame(merge_metrics).pivot(index=["model_name"], columns="eval_name")


@app.command()
def list_models():
    """List all available models."""
    models = get_available_models()
    typer.echo("Available models:")
    for model_name in models:
        typer.echo(f" - {model_name}")


@app.command()
def run(
    eval_name: str = typer.Argument(..., help="Specify an eval by name or 'all'"),
    model: Optional[str] = typer.Option(None, help="Specify a model by name"),
    n_examples: Optional[int] = typer.Option(None, "-n", help="Number of examples to use (overrides default)"),
    out: Path = typer.Option(default=Path("tmp/"), help="Output directory"),
    debug: bool = typer.Option(False, help="Run in debug mode"),
):
    """Run sampling and evaluations using different samplers and evaluations."""
    models = get_available_models()

    if model:
        if model not in models:
            typer.echo(f"Error: Model '{model}' not found.")
            raise typer.Exit(1)
        models = {model: models[model]}

    if eval_name == "all":
        eval_map = {eval_name: get_eval_instance(eval_name, debug, n_examples) for eval_name in get_available_evals()}
    else:
        eval_map = {eval_name: get_eval_instance(eval_name, debug, n_examples)}

    mergekey2resultpath = {}

    # Run evaluations
    for model_name, sampler in models.items():
        for eval_name, eval_obj in eval_map.items():
            result = eval_obj(sampler)
            result_filename = write_results(result, eval_name, model_name, out)
            mergekey2resultpath[f"{eval_name}_{model_name}"] = result_filename

    # Create and display results table
    merge_metrics_df = create_results_dataframe(mergekey2resultpath)
    typer.echo("\nAll results:")
    typer.echo(merge_metrics_df.to_markdown())

    return merge_metrics_df


if __name__ == "__main__":
    app()
