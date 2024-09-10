import json
import time

import pandas as pd

from openai import OpenAI

from . import common
from .gpqa_eval import GPQAEval
from .humaneval_eval import HumanEval
from .math_eval import MathEval
from .mmlu_eval import MMLUEval
from .sampler.reflection_sampler import (
    REFLECTION_SYSTEM_MESSAGE,
    ChatCompletionSampler,
)

from .sampler.chat_completion_sampler import ChatCompletionSampler as CheckerSampler


def main():
    debug = True
  # init your client
    client = OpenAI(
        base_url="http://0.0.0.0:8000/v1/",
        api_key= "test"
        )
    
    # real_openai = OpenAI()

    samplers = {
        # chatgpt models:
        "reflection_70b": ChatCompletionSampler(
            model="reflection_70b",
            system_message=REFLECTION_SYSTEM_MESSAGE,
            client=client
        ),
    }

    equality_checker = CheckerSampler(model="gpt-4-turbo-preview")
    # ^^^ used for fuzzy matching, just for math

    def get_evals(eval_name):
        # Set num_examples = None to reproduce full evals
        match eval_name:
            case "mmlu":
                return MMLUEval()
            case "math":
                return MathEval(
                    equality_checker=equality_checker,
                )
            case "gpqa":
                return GPQAEval(n_repeats= 10)
            case "humaneval":
                return HumanEval()
            case _:
                raise Exception(f"Unrecoginized eval type: {eval_name}")

    evals = {
        eval_name: get_evals(eval_name) for eval_name in ["mmlu", "math", "gpqa","humaneval"]
    }
    print(evals)
    debug_suffix = "_DEBUG" if debug else ""
    mergekey2resultpath = {}
    for sampler_name, sampler in samplers.items():
        for eval_name, eval_obj in evals.items():
            result = eval_obj(sampler)
            # ^^^ how to use a sampler
            file_stem = f"{eval_name}_{sampler_name}"
            report_filename = f"/tmp/{file_stem}{debug_suffix}.html"
            print(f"Writing report to {report_filename}")
            with open(report_filename, "w") as fh:
                fh.write(common.make_report(result))
            metrics = result.metrics | {"score": result.score}
            print(metrics)
            result_filename = f"/tmp/{file_stem}{debug_suffix}.json"
            with open(result_filename, "w") as f:
                f.write(json.dumps(metrics, indent=2))
            print(f"Writing results to {result_filename}")
            mergekey2resultpath[f"{file_stem}"] = result_filename
    merge_metrics = []
    for eval_sampler_name, result_filename in mergekey2resultpath.items():
        try:
            result = json.load(open(result_filename, "r+"))
        except Exception as e:
            print(e, result_filename)
            continue
        result = result.get("f1_score", result.get("score", None))
        eval_name = eval_sampler_name[: eval_sampler_name.find("_")]
        sampler_name = eval_sampler_name[eval_sampler_name.find("_") + 1 :]
        merge_metrics.append(
            {"eval_name": eval_name, "sampler_name": sampler_name, "metric": result}
        )
    merge_metrics_df = pd.DataFrame(merge_metrics).pivot(
        index=["sampler_name"], columns="eval_name"
    )
    print("\nAll results: ")
    print(merge_metrics_df.to_markdown())
    return merge_metrics


if __name__ == "__main__":
    main()
