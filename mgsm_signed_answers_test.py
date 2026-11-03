import pytest

from . import mgsm_eval
from .types import SamplerBase, SamplerResponse


@pytest.mark.parametrize(
    "response, target, expected_prediction, expected_score",
    [
        ("Answer: -42", "42", "-42", False),
        ("Answer: -42", "-42", "-42", True),
        ("Answer: 42", "-42", "42", False),
        ("Answer: 42", "42", "42", True),
        ("Answer: +42", "42", "42", True),
        ("Answer: 43", "42", "43", False),
        ("Answer: -1,000", "1,000", "-1000", False),
        ("Answer: -1,000", "-1,000", "-1000", True),
        ("Answer: 1,000", "1000", "1000", True),
        ("Answer: -42.0", "42", "-42.0", False),
        ("Answer: -42.0", "-42", "-42.0", True),
        ("Answer: 42.0", "42", "42.0", True),
        ("Answer: -0", "0", "-0", True),
        ("Answer: -0.0", "0", "-0.0", True),
        ("Answer: -42.", "-42", "-42", True),
        ("Answer: 42 -43", "-43", "-43", True),
        ("Answer: 42 -43", "43", "-43", False),
        ("Answer: 42\nCorrection. Answer: -42", "42", "-42", False),
        ("No final answer", "42", "", False),
    ],
)
def test_signed_answer_scoring(response, target, expected_prediction, expected_score):
    prediction = mgsm_eval.parse_answer(response, "Answer")

    assert prediction == expected_prediction
    assert mgsm_eval.score_mgsm(target, prediction) is expected_score


@pytest.mark.parametrize(
    "answer, expected_prediction, target",
    [
        ("42-43", "43", "43"),
        ("4-2", "2", "2"),
        ("1,000-2,000", "2000", "2,000"),
        ("2-3", "3", "3"),
        ("42.0-43.0", "43.0", "43"),
        ("42-43.", "43", "43"),
    ],
)
def test_hyphen_delimited_answers_preserve_last_number(
    answer, expected_prediction, target
):
    prediction = mgsm_eval.parse_answer(f"Answer: {answer}", "Answer")

    assert prediction == expected_prediction
    assert mgsm_eval.score_mgsm(target, prediction)
    assert not mgsm_eval.score_mgsm(f"-{target}", prediction)


@pytest.mark.parametrize("language", mgsm_eval.ALL_LANGUAGES)
def test_negative_answer_is_not_credited_by_eval(language, monkeypatch):
    class NegativeAnswerSampler(SamplerBase):
        def _pack_message(self, role, content):
            return {"role": role, "content": content}

        def __call__(self, message_list):
            return SamplerResponse(
                response_text=f"{mgsm_eval.LANG_TO_ANSWER_PREFIX[language]}: -42",
                actual_queried_message_list=message_list,
                response_metadata={},
            )

    monkeypatch.setattr(
        mgsm_eval,
        "get_lang_examples",
        lambda lang: [{"inputs": "Synthetic question", "targets": "42", "lang": lang}],
    )
    evaluation = mgsm_eval.MGSMEval(num_examples_per_lang=1, languages=[language])

    result = evaluation(NegativeAnswerSampler())

    assert result.score == 0.0
    assert result.metrics[language] == 0.0
    assert "Extracted Answer: -42" in result.htmls[0]
