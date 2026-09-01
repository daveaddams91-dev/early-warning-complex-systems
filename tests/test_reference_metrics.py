"""
Unit tests auditing production metrics against independent reference implementations.
"""

import pytest
import numpy as np
from sklearn.metrics import roc_auc_score, average_precision_score
from src.evaluation.metrics import compute_roc_pr, delong_paired_test
from src.evaluation.reference_metrics import (
    reference_roc_auc,
    reference_pr_auc,
    reference_confusion_metrics,
    reference_trajectory_roc_auc
)


class TestMetricVerification:
    def test_roc_auc_numerical_equality(self):
        np.random.seed(42)
        y_true = np.array([0, 0, 0, 1, 1, 1, 0, 1])
        y_score = np.array([0.1, 0.2, 0.4, 0.35, 0.8, 0.9, 0.5, 0.75])
        
        prod_res = compute_roc_pr(y_true, y_score)
        ref_auc = reference_roc_auc(y_true, y_score)
        skl_auc = float(roc_auc_score(y_true, y_score))
        
        assert abs(prod_res['roc_auc'] - ref_auc) < 1e-10
        assert abs(ref_auc - skl_auc) < 1e-10

    def test_pr_auc_numerical_equality(self):
        np.random.seed(42)
        y_true = np.array([0, 0, 1, 1, 0, 1])
        y_score = np.array([0.1, 0.4, 0.35, 0.8, 0.5, 0.75])
        
        prod_res = compute_roc_pr(y_true, y_score)
        ref_pr = reference_pr_auc(y_true, y_score)
        skl_pr = float(average_precision_score(y_true, y_score))
        
        # Differences between sklearn step interpolation and trapezoidal are within 1e-2
        assert abs(prod_res['pr_auc'] - skl_pr) < 1e-10
        assert abs(ref_pr - skl_pr) < 0.05

    def test_trajectory_level_roc_auc(self):
        # 5 ramp trajectories (higher warning scores)
        ramp_scores = [np.array([0.1, 0.2, 0.8, 1.2]) for _ in range(5)]
        # 5 null trajectories (lower stationary scores)
        null_scores = [np.array([0.1, 0.2, 0.15, 0.25]) for _ in range(5)]
        
        res = reference_trajectory_roc_auc(ramp_scores, null_scores, safe_skip_steps=1)
        assert res['trajectory_roc_auc'] == 1.0
        assert res['trajectory_pr_auc'] == 1.0
