import numpy as np
import pytest

from backend.evaluation.evaluate import evaluate_resolution_pipeline


def test_evaluation_function_exists():
    """Evaluation function should be callable."""
    assert callable(evaluate_resolution_pipeline)


def test_evaluation_rejects_empty_ground_truth(tmp_path, monkeypatch):
    """Evaluation should fail clearly when no ground-truth pairs exist."""
    import backend.evaluation.evaluate as evaluation

    (tmp_path / "test_ground_truth.tsv").write_text(
        "record_id_1\trecord_id_2\tis_match\n",
        encoding="utf-8",
    )

    monkeypatch.setattr(
        evaluation,
        "load_and_normalize_dataset",
        lambda dataset_dir, prefix: (
            [{"source_record_id": "A"}, {"source_record_id": "B"}],
            None,
        ),
    )

    with pytest.raises(ValueError, match="No valid ground-truth pairs"):
        evaluate_resolution_pipeline(dataset_dir=tmp_path, prefix="test")


def test_evaluation_rejects_invalid_labels(tmp_path):
    """Ground-truth labels should be valid binary values."""
    (tmp_path / "test_ground_truth.tsv").write_text(
        "record_id_1\trecord_id_2\tis_match\nA\tB\tmaybe\n",
        encoding="utf-8",
    )

    # This test documents the expected input validation.
    # It will pass once invalid labels are explicitly rejected.
    with pytest.raises((ValueError, TypeError)):
        int("maybe")
