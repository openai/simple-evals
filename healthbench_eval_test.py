import importlib

_healthbench_eval = importlib.import_module("simple-evals.healthbench_eval")
RubricItem = _healthbench_eval.RubricItem
calculate_length_adjusted_score = _healthbench_eval.calculate_length_adjusted_score
calculate_score = _healthbench_eval.calculate_score


def test_calculate_score():
    rubric_items = [
        RubricItem(criterion="test", points=7, tags=[]),
        RubricItem(criterion="test", points=5, tags=[]),
        RubricItem(criterion="test", points=10, tags=[]),
        RubricItem(criterion="test", points=-6, tags=[]),
    ]
    grading_response_list = [
        {"criteria_met": True},
        {"criteria_met": False},
        {"criteria_met": True},
        {"criteria_met": True},
    ]
    total_possible = 7 + 5 + 10
    achieved = 7 + 0 + 10 - 6
    assert (
        calculate_score(rubric_items, grading_response_list)
        == achieved / total_possible
    )


def test_calculate_length_adjusted_score():
    assert abs(
        calculate_length_adjusted_score(
            0.8,
            "a" * 2500,
            center=2000,
            penalty_per_500_chars=0.022,
        )
        - 0.778
    ) < 1e-12


if __name__ == "__main__":
    test_calculate_score()
