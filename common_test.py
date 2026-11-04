from .common import _parse_yes_no, check_equality


_AFFIRMATIVE = [
    "Yes",
    "yes",
    "Yes.",
    "Yes!",
    " **Yes**",
    '"Yes"',
    "Yes\n",
]

_NOT_AFFIRMATIVE = [
    "No",
    "No.",
    "No, not yes",
    "The answer is not yes",
    "not yes",
    "",
    None,
    "Yesterday",
    "Maybe yes",
]


class _SamplerResponse:
    def __init__(self, response_text):
        self.response_text = response_text


class _StubSampler:
    def __init__(self, response_text):
        self._response_text = response_text

    def __call__(self, message_list):
        return _SamplerResponse(self._response_text)


def test_parse_yes_no_accepts_leading_yes():
    for response_text in _AFFIRMATIVE:
        assert _parse_yes_no(response_text) is True


def test_parse_yes_no_rejects_non_affirmative():
    for response_text in _NOT_AFFIRMATIVE:
        assert _parse_yes_no(response_text) is False


def test_check_equality_accepts_leading_yes():
    for response_text in _AFFIRMATIVE:
        assert check_equality(_StubSampler(response_text), "2+2", "4") is True


def test_check_equality_rejects_non_affirmative():
    for response_text in _NOT_AFFIRMATIVE:
        assert check_equality(_StubSampler(response_text), "2+2", "5") is False
