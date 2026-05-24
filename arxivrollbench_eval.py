"""
ArxivRollBench: a rolling arXiv benchmark for evaluating recent scientific text reasoning.
AAAI 2026 paper: https://ojs.aaai.org/index.php/AAAI/article/view/41098
"""

import re
from typing import Literal

from . import common
from .common import ANSWER_PATTERN_MULTICHOICE, HTML_JINJA, format_multichoice_question
from .types import Eval, EvalResult, SamplerBase, SingleEvalResult

DOMAINS = [
    ("cs", "cs"),
    ("q_fin", "q-fin"),
    ("math", "math"),
    ("physics", "physics"),
    ("stat", "stat"),
    ("q_bio", "q-bio"),
    ("econ", "econ"),
    ("eess", "eess"),
]
RELEASES = ["2024b", "2025a", "2026a"]
TASK_TYPES = ["s", "c", "p"]
TASK_TYPE_NAMES = {
    "s": "sequencing",
    "c": "cloze",
    "p": "prediction",
}


def _dataset_path(
    release: str,
    hf_domain: str,
    task_type: str,
    split: Literal["compact", "full"],
) -> str:
    suffix = "-50" if split == "compact" else ""
    if release == "2024b":
        return f"liangzid/robench2024b_all_set{hf_domain}SCP-{task_type}{suffix}"
    return (
        f"liangzid/robench{release}_test_all_category_set"
        f"{hf_domain}SCP-{task_type}{suffix}"
    )


def _selection_to_letter(label: str) -> str:
    match = re.search(r"\bselection\s*([1-4])\b", str(label), re.IGNORECASE)
    if match:
        return chr(ord("A") + int(match.group(1)) - 1)
    return str(label).strip().upper()


def _record_to_example(record: dict, release: str, domain: str, task_type: str) -> dict:
    if task_type == "p":
        question = (
            "Given the context, select the text that is the next sequence.\n\n"
            f"Context:\n{record['context']}"
        )
        answer = str(record["label"]).strip().upper()
    else:
        question = (
            "Select the option that correctly completes the sequencing or cloze task.\n\n"
            f"{record['shuffled_text']}"
        )
        answer = _selection_to_letter(record["label"])

    return {
        "Question": question,
        "A": record["A"],
        "B": record["B"],
        "C": record["C"],
        "D": record["D"],
        "Answer": answer,
        "release": release,
        "domain": domain,
        "task_type": task_type,
        "task_type_name": TASK_TYPE_NAMES[task_type],
        "source_label": record["label"],
    }


class ArxivRollBenchEval(Eval):
    def __init__(
        self,
        split: Literal["compact", "full"] = "compact",
        num_examples: int | None = None,
        subsets: list[str] | None = None,
    ):
        try:
            from datasets import load_dataset
        except ImportError as exc:
            raise ImportError(
                "ArxivRollBenchEval requires the optional `datasets` package. "
                "Install it with `pip install datasets`."
            ) from exc

        wanted_subsets = set(subsets) if subsets is not None else None
        examples = []
        for release in RELEASES:
            for domain, hf_domain in DOMAINS:
                for task_type in TASK_TYPES:
                    subset_name = f"{release}_{domain}_{task_type}"
                    if wanted_subsets is not None and subset_name not in wanted_subsets:
                        continue

                    remaining = (
                        None if num_examples is None else num_examples - len(examples)
                    )
                    if remaining is not None and remaining <= 0:
                        break

                    dataset_path = _dataset_path(release, hf_domain, task_type, split)
                    split_name = "train" if remaining is None else f"train[:{remaining}]"
                    dataset = load_dataset(dataset_path, split=split_name)
                    for record in dataset:
                        examples.append(
                            _record_to_example(record, release, domain, task_type)
                        )
            if num_examples is not None and len(examples) >= num_examples:
                break

        self.examples = examples
        self.split = split

    def __call__(self, sampler: SamplerBase) -> EvalResult:
        def fn(row: dict):
            prompt_messages = [
                sampler._pack_message(
                    content=format_multichoice_question(row),
                    role="user",
                )
            ]
            sampler_response = sampler(prompt_messages)
            response_text = sampler_response.response_text
            actual_queried_prompt_messages = sampler_response.actual_queried_message_list
            match = re.search(ANSWER_PATTERN_MULTICHOICE, response_text)
            extracted_answer = match.group(1).upper() if match else None
            score = 1.0 if extracted_answer == row["Answer"] else 0.0
            html = common.jinja_env.from_string(HTML_JINJA).render(
                prompt_messages=actual_queried_prompt_messages,
                next_message=dict(content=response_text, role="assistant"),
                score=score,
                correct_answer=row["Answer"],
                extracted_answer=extracted_answer,
            )
            convo = actual_queried_prompt_messages + [
                dict(content=response_text, role="assistant")
            ]
            return SingleEvalResult(
                html=html,
                score=score,
                convo=convo,
                metrics={
                    row["release"]: score,
                    row["domain"]: score,
                    row["task_type_name"]: score,
                    "chars": len(response_text),
                },
                example_level_metadata={
                    "release": row["release"],
                    "domain": row["domain"],
                    "task_type": row["task_type"],
                    "source_label": row["source_label"],
                },
            )

        results = common.map_with_progress(fn, self.examples)
        return common.aggregate_results(results)
