import json
import re

import pytest

from . import healthbench_meta_eval
from .types import SamplerBase, SamplerResponse


def test_compute_agreement_for_rater_by_class():
    self_pred_list = [True, False, True]
    other_preds_list = [[True, True, False], [True, False], [False]]
    cluster_list = ["a", "a", "b"]
    model_or_physician = "model"
    metrics = healthbench_meta_eval.compute_metrics_for_rater_by_class(
        self_pred_list, other_preds_list, cluster_list, model_or_physician
    )

    # precision overall
    index_str_pos_precision = healthbench_meta_eval.INDEX_STR_TEMPLATE.format(
        model_or_physician=model_or_physician, metric="precision", pred_str="pos"
    )
    index_str_neg_precision = healthbench_meta_eval.INDEX_STR_TEMPLATE.format(
        model_or_physician=model_or_physician, metric="precision", pred_str="neg"
    )
    overall_pos_precision = metrics[index_str_pos_precision]
    overall_neg_precision = metrics[index_str_neg_precision]
    expected_overall_pos_precision = (2 + 0 + 0) / (3 + 0 + 1)
    expected_overall_neg_precision = (0 + 1 + 0) / (0 + 2 + 0)
    assert overall_pos_precision["value"] == expected_overall_pos_precision
    assert overall_neg_precision["value"] == expected_overall_neg_precision
    assert overall_pos_precision["n"] == 4
    assert overall_neg_precision["n"] == 2

    # recall overall
    index_str_pos_recall = healthbench_meta_eval.INDEX_STR_TEMPLATE.format(
        model_or_physician=model_or_physician, metric="recall", pred_str="pos"
    )
    index_str_neg_recall = healthbench_meta_eval.INDEX_STR_TEMPLATE.format(
        model_or_physician=model_or_physician, metric="recall", pred_str="neg"
    )
    overall_pos_recall = metrics[index_str_pos_recall]
    overall_neg_recall = metrics[index_str_neg_recall]
    expected_overall_pos_recall = (2 + 0 + 0) / (2 + 1 + 0)
    expected_overall_neg_recall = (0 + 1 + 0) / (1 + 1 + 1)
    assert overall_pos_recall["value"] == expected_overall_pos_recall
    assert overall_neg_recall["value"] == expected_overall_neg_recall
    assert overall_pos_recall["n"] == 3
    assert overall_neg_recall["n"] == 3

    # f1 overall
    index_str_pos_f1 = healthbench_meta_eval.INDEX_STR_TEMPLATE.format(
        model_or_physician=model_or_physician, metric="f1", pred_str="pos"
    )
    index_str_neg_f1 = healthbench_meta_eval.INDEX_STR_TEMPLATE.format(
        model_or_physician=model_or_physician, metric="f1", pred_str="neg"
    )
    overall_pos_f1 = metrics[index_str_pos_f1]
    overall_neg_f1 = metrics[index_str_neg_f1]
    expected_overall_pos_f1 = (
        2
        * expected_overall_pos_precision
        * expected_overall_pos_recall
        / (expected_overall_pos_precision + expected_overall_pos_recall)
    )
    expected_overall_neg_f1 = (
        2
        * expected_overall_neg_precision
        * expected_overall_neg_recall
        / (expected_overall_neg_precision + expected_overall_neg_recall)
    )
    assert overall_pos_f1["value"] == expected_overall_pos_f1
    assert overall_neg_f1["value"] == expected_overall_neg_f1

    # balanced f1
    index_str_balanced_f1 = healthbench_meta_eval.INDEX_STR_TEMPLATE.format(
        model_or_physician=model_or_physician, metric="f1", pred_str="balanced"
    )
    balanced_f1 = metrics[index_str_balanced_f1]
    expected_balanced_f1 = (expected_overall_pos_f1 + expected_overall_neg_f1) / 2
    assert balanced_f1["value"] == expected_balanced_f1

    # by cluster
    # precision
    cluster_a_str_pos_precision = healthbench_meta_eval.CLUSTER_STR_TEMPLATE.format(
        cluster="a", index_str=index_str_pos_precision
    )
    cluster_a_str_neg_precision = healthbench_meta_eval.CLUSTER_STR_TEMPLATE.format(
        cluster="a", index_str=index_str_neg_precision
    )
    cluster_a_pos_precision = metrics[cluster_a_str_pos_precision]
    cluster_a_neg_precision = metrics[cluster_a_str_neg_precision]
    assert cluster_a_pos_precision["value"] == (
        # example 1, 2 in order
        (2 + 0) / (3 + 0)
    )
    assert cluster_a_neg_precision["value"] == (
        # example 1, 2 in order
        (0 + 1) / (0 + 2)
    )
    assert cluster_a_pos_precision["n"] == 3
    assert cluster_a_neg_precision["n"] == 2

    # recall
    cluster_a_str_pos_recall = healthbench_meta_eval.CLUSTER_STR_TEMPLATE.format(
        cluster="a", index_str=index_str_pos_recall
    )
    cluster_a_str_neg_recall = healthbench_meta_eval.CLUSTER_STR_TEMPLATE.format(
        cluster="a", index_str=index_str_neg_recall
    )
    cluster_a_pos_recall = metrics[cluster_a_str_pos_recall]
    cluster_a_neg_recall = metrics[cluster_a_str_neg_recall]
    assert cluster_a_pos_recall["value"] == (
        # example 1, 2 in order
        (2 + 0) / (2 + 1)
    )
    assert cluster_a_neg_recall["value"] == (
        # example 1, 2 in order
        (0 + 1) / (1 + 1)
    )
    assert cluster_a_pos_recall["n"] == 3
    assert cluster_a_neg_recall["n"] == 2

    # cluster B
    # precision
    cluster_b_str_pos_precision = healthbench_meta_eval.CLUSTER_STR_TEMPLATE.format(
        cluster="b", index_str=index_str_pos_precision
    )
    cluster_b_str_neg_precision = healthbench_meta_eval.CLUSTER_STR_TEMPLATE.format(
        cluster="b", index_str=index_str_neg_precision
    )
    cluster_b_str_pos_precision = metrics[cluster_b_str_pos_precision]
    assert cluster_b_str_neg_precision not in metrics
    assert cluster_b_str_pos_precision["value"] == (
        # example 3 only
        0 / 1
    )
    assert cluster_b_str_pos_precision["n"] == 1

    # recall
    cluster_b_str_pos_recall = healthbench_meta_eval.CLUSTER_STR_TEMPLATE.format(
        cluster="b", index_str=index_str_pos_recall
    )
    cluster_b_str_neg_recall = healthbench_meta_eval.CLUSTER_STR_TEMPLATE.format(
        cluster="b", index_str=index_str_neg_recall
    )
    assert cluster_b_str_pos_recall not in metrics
    cluster_b_neg_recall = metrics[cluster_b_str_neg_recall]
    assert cluster_b_neg_recall["value"] == (
        # example 3 only
        0 / 1
    )
    assert cluster_b_neg_recall["n"] == 1

    # f1
    index_str_pos_f1 = healthbench_meta_eval.CLUSTER_STR_TEMPLATE.format(
        cluster="b", index_str=index_str_pos_f1
    )
    index_str_neg_f1 = healthbench_meta_eval.CLUSTER_STR_TEMPLATE.format(
        cluster="b", index_str=index_str_neg_f1
    )
    index_str_balanced_f1 = healthbench_meta_eval.CLUSTER_STR_TEMPLATE.format(
        cluster="b", index_str=index_str_balanced_f1
    )
    assert index_str_pos_f1 not in metrics
    assert index_str_neg_f1 not in metrics
    assert index_str_balanced_f1 not in metrics


@pytest.mark.parametrize(
    "predictions, physician_labels, expected_score",
    [
        ([True, True], [[True, True], [False, False]], None),
        ([False, False], [[True, True], [False, False]], None),
        ([True, False], [[True, True], [False, False]], 1.0),
        ([False, True], [[True, True], [False, False]], 0.0),
        ([True, False], [[True, True], [True, True]], None),
        ([True, False], [[False, False], [False, False]], None),
    ],
    ids=[
        "all-positive",
        "all-negative",
        "perfect",
        "inverted",
        "positive-references",
        "negative-references",
    ],
)
def test_meta_eval_handles_undefined_balanced_f1(
    predictions, physician_labels, expected_score, tmp_path, monkeypatch
):
    class BooleanSampler(SamplerBase):
        def __call__(self, message_list):
            # Identify the row without relying on worker execution order.
            label = predictions[int("sample-1" in message_list[0]["content"])]
            return SamplerResponse(
                response_text=json.dumps({"criteria_met": label}),
                actual_queried_message_list=message_list,
                response_metadata={},
            )

    examples = [
        {
            "prompt": [{"role": "user", "content": f"sample-{i}"}],
            "completion": "Synthetic response",
            "rubric": "Synthetic criterion",
            "binary_labels": labels,
            "anonymized_physician_ids": ["rater-a", "rater-b"],
            "category": "test",
        }
        for i, labels in enumerate(physician_labels)
    ]
    input_path = tmp_path / "meta_eval.jsonl"
    input_path.write_text(
        "\n".join(json.dumps(row) for row in examples), encoding="utf-8"
    )
    monkeypatch.setattr(healthbench_meta_eval, "INPUT_PATH", str(input_path))
    monkeypatch.setattr(healthbench_meta_eval.bf, "BlobFile", open)
    sampler = BooleanSampler()
    evaluation = healthbench_meta_eval.HealthBenchMetaEval(sampler, n_threads=1)

    result = evaluation(sampler)

    assert result.score == expected_score
    assert len(result.htmls) == len(examples)
    assert len(result.convos) == len(examples)
    assert result.metrics["model_predicted_positive"] == sum(predictions) / len(
        predictions
    )
    assert result.metadata["physician_agreement_metric_lists"]
    score_key = "pairwise_model_f1_balanced"
    if expected_score is None:
        assert score_key not in result.metrics
    else:
        assert result.metrics[score_key] == expected_score

    report = healthbench_meta_eval.common.make_report(result)
    score_cell = re.search(r"<td><b>Score</b></td>\s*<td>(.*?)</td>", report)
    assert score_cell is not None
    assert score_cell.group(1) == (
        "N/A" if expected_score is None else str(expected_score)
    )


if __name__ == "__main__":
    test_compute_agreement_for_rater_by_class()
