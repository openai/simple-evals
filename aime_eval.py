"""
"""

import random
import re

import pandas

from . import common
from .common import (
    HTML_JINJA
)
from .types import Eval, EvalResult, SamplerBase, SingleEvalResult


import random
import re
from typing import Literal

import pandas

from . import common
from .common import ANSWER_PATTERN, HTML_JINJA, check_equality
from .types import Eval, EvalResult, SamplerBase, SingleEvalResult

QUERY_TEMPLATE = """
Solve the following math problem step by step. The last line of your response should be of the form Answer: $ANSWER (without quotes) where $ANSWER is the answer to the problem.

{problem}

Remember to put your answer on its own line after "Answer:", and you do not need to use a \\boxed command.
""".strip()


class AiMEEval(Eval):
    def __init__(
        self,
        equality_checker: SamplerBase,
        num_examples: int | None = None,
        n_repeats: int = 16,
        split: Literal["aime25-1", 'aime25-2', "aime24"] = "aime25-1",
    ):
        split_map = {
            "aime25-1": "test2025-I",
            "aime25-2": "test2025-II",
            "aime24": "test2024",
        }
        df = pandas.read_json(
            f"https://raw.githubusercontent.com/GAIR-NLP/AIME-Preview/refs/heads/main/eval/data/aime/{split_map[split]}.jsonl",
            lines=True
        )
        examples = [row.to_dict() for _, row in df.iterrows()]
        if num_examples:
            assert n_repeats == 1, "n_repeats only supported for num_examples = None"
            rng = random.Random(0)
            examples = rng.sample(examples, num_examples)
        self.examples = examples * n_repeats
        self.equality_checker = equality_checker

    def __call__(self, sampler: SamplerBase) -> EvalResult:
        def fn(row: dict):
            prompt_messages = [
                sampler._pack_message(content=QUERY_TEMPLATE.format(**row), role="user")
            ]
            response_text = sampler(prompt_messages)
            match = re.search(ANSWER_PATTERN, response_text)
            extracted_answer = match.group(1) if match else None
            score = float(check_equality(self.equality_checker, row["answer"], extracted_answer))
            html = common.jinja_env.from_string(HTML_JINJA).render(
                prompt_messages=prompt_messages,
                next_message=dict(content=response_text, role="assistant"),
                score=score,
                correct_answer=row["answer"],
                extracted_answer=extracted_answer,
            )
            convo = prompt_messages + [dict(content=response_text, role="assistant")]
            return SingleEvalResult(html=html, score=score, convo=convo)

        results = common.map_with_progress(fn, self.examples)
        return common.aggregate_results(results)