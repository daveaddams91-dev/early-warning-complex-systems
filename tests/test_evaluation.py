"""
Unit tests for evaluation metrics, lead-time distribution, and DeLong significance test.
"""

import pytest
import numpy as np
from src.evaluation.metrics import (
    compute_roc_pr,
    compute_lead_time_distribution,
    compute_false_alarm_rate,
    delong_paired_test,
    compute_operational_lead_time_distribution,
    compute_trajectory_level_roc_pr,
    clustered_bootstrap_auc_diff
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

    def test_operational_early_warning_metrics(self):
        times = [np.linspace(0, 100, 1000)]
        collapse_times = [80.0]
        
        # 1. Early false alarm at t = 10.0 (safe_baseline_time = 20.0)
        early_score = np.zeros(1000)
        early_score[100:] = 3.0
        res_early = compute_operational_lead_time_distribution(
            [early_score], times, collapse_times, threshold=2.0, safe_baseline_time=20.0
        )
        assert res_early['early_false_alarm_rate'] == 1.0
        assert res_early['true_positive_rate'] == 0.0
        
        # 2. Actionable early warning at t = 60.0 (lead time = 20.0)
        valid_score = np.zeros(1000)
        valid_score[600:] = 3.0
        res_valid = compute_operational_lead_time_distribution(
            [valid_score], times, collapse_times, threshold=2.0, safe_baseline_time=20.0, min_actionable_lead_time=2.0
        )
        assert res_valid['true_positive_rate'] == 1.0
        assert res_valid['early_false_alarm_rate'] == 0.0
        assert np.isclose(res_valid['mean_lead_time'], 20.0, atol=0.2)
        
        # 3. Late alarm at t = 79.5 (min_actionable_lead_time = 2.0)
        late_score = np.zeros(1000)
        late_score[795:] = 3.0
        res_late = compute_operational_lead_time_distribution(
            [late_score], times, collapse_times, threshold=2.0, safe_baseline_time=20.0, min_actionable_lead_time=2.0
        )
        assert res_late['late_alarm_rate'] == 1.0
        assert res_late['true_positive_rate'] == 0.0

    def test_trajectory_level_roc_and_bootstrap(self):
        times = np.linspace(0, 100, 100)
        ramp_scores = [np.linspace(0, 5, 100) for _ in range(10)]
        null_scores = [np.linspace(0, 1, 100) for _ in range(10)]
        time_arrays_ramp = [times for _ in range(10)]
        collapse_times = [90.0 for _ in range(10)]
        time_arrays_null = [times for _ in range(10)]
        
        roc_res = compute_trajectory_level_roc_pr(
            ramp_scores, null_scores, time_arrays_ramp, collapse_times, time_arrays_null,
            safe_baseline_time=20.0, min_lead_time=2.0
        )
        assert roc_res['roc_auc'] == 1.0
        
        # Compare strong model vs weak model via clustered bootstrap
        weak_ramp = [np.linspace(0, 1, 100) for _ in range(10)]
        boot_res = clustered_bootstrap_auc_diff(
            ramp_scores, weak_ramp, null_scores, null_scores,
            time_arrays_ramp, collapse_times, time_arrays_null,
            n_boot=100, seed=42
        )
        assert boot_res['diff_mean'] >= 0.0
        assert not np.isnan(boot_res['ci_lower'])
