from .arxivrollbench_eval import (
    _dataset_path,
    _record_to_example,
    _selection_to_letter,
)


def test_dataset_path_compact_and_full():
    assert (
        _dataset_path("2026a", "cs", "s", "compact")
        == "liangzid/robench2026a_test_all_category_setcsSCP-s-50"
    )
    assert (
        _dataset_path("2024b", "q-fin", "p", "full")
        == "liangzid/robench2024b_all_setq-finSCP-p"
    )


def test_selection_to_letter():
    assert _selection_to_letter("Selection 1") == "A"
    assert _selection_to_letter("selection 4") == "D"
    assert _selection_to_letter("A") == "A"
    assert _selection_to_letter("1") == "1"


def test_record_to_example_prediction():
    record = {
        "context": "The introduction describes a new method.",
        "A": "A candidate",
        "B": "B candidate",
        "C": "C candidate",
        "D": "D candidate",
        "label": "C",
    }

    example = _record_to_example(record, "2026a", "cs", "p")

    assert example["Answer"] == "C"
    assert "Context:\nThe introduction describes a new method." in example["Question"]
    assert example["task_type_name"] == "prediction"


def test_record_to_example_selection():
    record = {
        "shuffled_text": "Paragraph with a blank.",
        "A": "A candidate",
        "B": "B candidate",
        "C": "C candidate",
        "D": "D candidate",
        "label": "Selection 2",
    }

    example = _record_to_example(record, "2026a", "math", "s")

    assert example["Answer"] == "B"
    assert example["task_type_name"] == "sequencing"
