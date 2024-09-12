import json

import pandas as pd

from . import common
from .mmlu_eval import MMLUEval
from .sampler.chat_completion_sampler import (
    OPENAI_SYSTEM_MESSAGE_API,
    OPENAI_SYSTEM_MESSAGE_CHATGPT,
    ChatCompletionSampler,
)
from .sampler.o1_chat_completion_sampler import O1ChatCompletionSampler


def main():
    debug = True
    samplers = {
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
        "o1-preview": O1ChatCompletionSampler(
            model="o1-preview",
        ),
        "o1-mini": O1ChatCompletionSampler(
            model="o1-mini",
        ),
    }

    def get_evals(eval_name):
        match eval_name:
            case "mmlu_EN-US":
                return MMLUEval(num_examples=10 if debug else None, language="EN-US")
            case "mmlu_AR-XY":
                return MMLUEval(num_examples=10 if debug else None, language="AR-XY")
            case "mmlu_BN-BD":
                return MMLUEval(num_examples=10 if debug else None, language="BN-BD")
            case "mmlu_DE-DE":
                return MMLUEval(num_examples=10 if debug else None, language="DE-DE")
            case "mmlu_ES-LA":
                return MMLUEval(num_examples=10 if debug else None, language="ES-LA")
            case "mmlu_FR-FR":
                return MMLUEval(num_examples=10 if debug else None, language="FR-FR")
            case "mmlu_HI-IN":
                return MMLUEval(num_examples=10 if debug else None, language="HI-IN")
            case "mmlu_ID-ID":
                return MMLUEval(num_examples=10 if debug else None, language="ID-ID")
            case "mmlu_IT-IT":
                return MMLUEval(num_examples=10 if debug else None, language="IT-IT")
            case "mmlu_JA-JP":
                return MMLUEval(num_examples=10 if debug else None, language="JA-JP")
            case "mmlu_KO-KR":
                return MMLUEval(num_examples=10 if debug else None, language="KO-KR")
            case "mmlu_PT-BR":
                return MMLUEval(num_examples=10 if debug else None, language="PT-BR")
            case "mmlu_ZH-CN":
                return MMLUEval(num_examples=10 if debug else None, language="ZH-CN")
            case "mmlu_SW-KE":
                return MMLUEval(num_examples=10 if debug else None, language="SW-KE")
            case "mmlu_YO-NG":
                return MMLUEval(num_examples=10 if debug else None, language="YO-NG")
            case _:
                raise Exception(f"Unrecoginized eval type: {eval_name}")

    evals = {
        eval_name: get_evals(eval_name)
        for eval_name in [
            "mmlu_AR-XY",
            "mmlu_BN-BD",
            "mmlu_DE-DE",
            "mmlu_EN-US",
            "mmlu_ES-LA",
            "mmlu_FR-FR",
            "mmlu_HI-IN",
            "mmlu_ID-ID",
            "mmlu_IT-IT",
            "mmlu_JA-JP",
            "mmlu_KO-KR",
            "mmlu_PT-BR",
            "mmlu_ZH-CN",
            "mmlu_SW-KE",
            "mmlu_YO-NG",
        ]
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
