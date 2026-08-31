"""
Unit tests for evaluation metrics, lead-time distribution, and DeLong significance test.
"""

import pytest
import numpy as np
from src.evaluation.metrics import (
    compute_roc_pr,
    compute_lead_time_distribution,
    compute_false_alarm_rate,
    delong_paired_test
)


class TestEvaluationMetrics:
    def test_roc_pr_computation(self):
        # Perfect classifier
        y_true = np.array([0, 0, 0, 0, 0, 1, 1, 1, 1, 1])
        y_score_perf = np.array([0.1, 0.2, 0.1, 0.3, 0.2, 0.8, 0.9, 0.7, 0.95, 0.85])
        
        res = compute_roc_pr(y_true, y_score_perf)
        assert np.isclose(res['roc_auc'], 1.0)
        assert np.isclose(res['pr_auc'], 1.0)
        
        # Random classifier
        y_score_rand = np.array([0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5])
        res_rand = compute_roc_pr(y_true, y_score_rand)
        assert np.isclose(res_rand['roc_auc'], 0.5)

    def test_lead_time_and_false_alarms(self):
        times = [np.linspace(0, 100, 1000)]
        collapse_times = [80.0]
        
        # Score that crosses threshold at t = 60.0
        scores = np.zeros(1000)
        scores[600:] = 2.5
        
        res_lead = compute_lead_time_distribution([scores], times, collapse_times, threshold=2.0)
        assert res_lead['n_detected'] == 1
        # Lead time should be 80.0 - 60.0 = 20.0
        assert np.isclose(res_lead['median_lead_time'], 20.0, atol=0.2)
        
        # False alarm on null run
        null_scores = [np.full(500, 0.5), np.array([0.1]*400 + [2.5]*100)]
        far = compute_false_alarm_rate(null_scores, threshold=2.0)
        assert np.isclose(far, 0.5)

    def test_delong_significance_test(self):
        rng = np.random.default_rng(42)
        y_true = np.concatenate([np.zeros(50), np.ones(50)])
        score_a = np.concatenate([rng.normal(0, 1, 50), rng.normal(3, 1, 50)])
        score_b = np.concatenate([rng.normal(0, 1, 50), rng.normal(0.5, 1, 50)])
        
        res = delong_paired_test(y_true, score_a, score_b)
        assert res['auc_a'] > res['auc_b']
        assert res['p_value'] < 0.001
