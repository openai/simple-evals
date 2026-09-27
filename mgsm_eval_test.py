import pytest

from . import mgsm_eval
from .types import SamplerResponse


@pytest.mark.parametrize("fails", [False, True])
def test_sampler_error_preserves_prompt_in_report(monkeypatch, fails):
    monkeypatch.setattr(
        mgsm_eval,
        "get_lang_examples",
        lambda lang: [{"inputs": "What is 1 + 1?", "targets": "2", "lang": lang}] * 2,
    )

    class Sampler:
        def _pack_message(self, content, role):
            return {"content": content, "role": role}

        def __call__(self, messages):
            if fails:
                raise RuntimeError("sampling failed")
            return SamplerResponse(
                response_text="Answer: 2",
                actual_queried_message_list=[
                    {"role": "system", "content": "Answer the question."},
                    *messages,
                ],
                response_metadata={},
            )

    result = mgsm_eval.MGSMEval(languages=["en"])(Sampler())

    assert result.score == (0 if fails else 1)
    assert len(result.convos) == 2
    for convo, html in zip(result.convos, result.htmls):
        assert convo[-2]["role"] == "user"
        assert "What is 1 + 1?" in convo[-2]["content"]
        assert convo[-1] == {
            "role": "assistant",
            "content": "" if fails else "Answer: 2",
        }
        assert "What is 1 + 1?" in html
        if not fails:
            assert convo[0] == {"role": "system", "content": "Answer the question."}
