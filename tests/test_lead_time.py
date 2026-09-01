import numpy as np
import pytest
from src.evaluation.lead_time import find_threshold_at_far, compute_lead_time_distribution


class TestLeadTimeEvaluation:
    def test_find_threshold_at_far(self):
        rng = np.random.default_rng(42)
        # 50 null trajectories of length 200
        null_scores = [rng.normal(0.0, 1.0, size=200) for _ in range(50)]
        times = [np.linspace(0, 100, 200) for _ in range(50)]

        th_10 = find_threshold_at_far(null_scores, times, safe_baseline_time=20.0, target_far=0.10, persistence_steps=4)
        th_01 = find_threshold_at_far(null_scores, times, safe_baseline_time=20.0, target_far=0.01, persistence_steps=4)

        # 1% FAR threshold should be strictly higher than 10% FAR threshold
        assert th_01 >= th_10

    def test_compute_lead_time_distribution(self):
        rng = np.random.default_rng(123)
        n_trajs = 20
        times = [np.linspace(0, 100, 200) for _ in range(n_trajs)]
        c_times = [80.0] * n_trajs

        # Null: flat low scores
        null_scores = [rng.normal(0.0, 0.1, size=200) for _ in range(n_trajs)]

        # Ramp: scores rise sharply at t = 50.0 (lead time = 80 - 50 = 30s)
        ramp_scores = []
        for _ in range(n_trajs):
            s = rng.normal(0.0, 0.1, size=200)
            s[100:] += 5.0  # t=50 corresponds to index 100
            ramp_scores.append(s)

        dist = compute_lead_time_distribution(
            ramp_scores, null_scores, times, c_times, times,
            safe_baseline_time=10.0, min_lead_time=2.0, far_points=(0.05,), persistence_steps=4
        )

        assert 0.05 in dist
        res_05 = dist[0.05]
        assert res_05['detection_rate'] == 1.0
        # Expected lead time should be close to 80 - 50 = 30s
        assert np.isclose(res_05['lead_time_mean'], 30.0, atol=3.0)
        assert res_05['lead_time_median'] > 25.0
