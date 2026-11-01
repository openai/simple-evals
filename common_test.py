import pytest

from . import common


@pytest.mark.parametrize("debug", [False, True])
@pytest.mark.parametrize("pbar", [False, True])
def test_map_with_progress_empty_input(monkeypatch, debug, pbar):
    if debug:
        monkeypatch.setenv("debug", "1")
    else:
        monkeypatch.delenv("debug", raising=False)

    def unexpected_call(value):
        pytest.fail("The callback must not be called for empty input")

    assert common.map_with_progress(unexpected_call, [], pbar=pbar) == []


@pytest.mark.parametrize("debug", [False, True])
@pytest.mark.parametrize("num_threads", [1, 4])
def test_map_with_progress_preserves_order(monkeypatch, debug, num_threads):
    if debug:
        monkeypatch.setenv("debug", "1")
    else:
        monkeypatch.delenv("debug", raising=False)

    assert common.map_with_progress(
        lambda value: value * 2, [3, 1, 2], num_threads=num_threads, pbar=False
    ) == [6, 2, 4]


@pytest.mark.parametrize("debug", [False, True])
def test_map_with_progress_propagates_callback_error(monkeypatch, debug):
    if debug:
        monkeypatch.setenv("debug", "1")
    else:
        monkeypatch.delenv("debug", raising=False)

    def fail(value):
        raise ValueError("callback failed")

    with pytest.raises(ValueError, match="callback failed"):
        common.map_with_progress(fail, [1], pbar=False)
