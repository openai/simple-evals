import types
from unittest import mock

import pandas

from .gpqa_eval import GPQAEval

ROW = {
    "Question": "Which is bigger?",
    "Correct Answer": "beta",
    "Incorrect Answer 1": "alpha",
    "Incorrect Answer 2": "gamma",
    "Incorrect Answer 3": "delta",
}


class StubSampler:
    """Minimal SamplerBase that always returns the given text."""

    def __init__(self, response_text: str):
        self.response_text = response_text

    def _pack_message(self, content, role):
        return {"content": content, "role": role}

    def __call__(self, message_list):
        return types.SimpleNamespace(
            response_text=self.response_text,
            actual_queried_message_list=message_list,
        )


def test_answer_letter_is_case_insensitive():
    # __init__ downloads the GPQA CSV, so feed it a local one-row frame instead.
    with mock.patch("pandas.read_csv", return_value=pandas.DataFrame([ROW])):
        eval_ = GPQAEval(n_repeats=1)

    row = eval_.examples[0]
    choices = [
        row["Correct Answer"],
        row["Incorrect Answer 1"],
        row["Incorrect Answer 2"],
        row["Incorrect Answer 3"],
    ]
    choices = [choices[i] for i in row["permutation"]]
    correct_letter = "ABCD"[choices.index(row["Correct Answer"])]

    for response_text in [
        f"Answer: {correct_letter}",
        f"Answer: {correct_letter.lower()}",
        f"answer: {correct_letter.lower()}",
    ]:
        result = eval_(StubSampler(response_text))
        assert result.score == 1.0, response_text
