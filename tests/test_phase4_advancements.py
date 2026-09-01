"""
Unit tests for Phase 4 theoretical and algorithmic advancements:
- Noise Dilution Theorem validation
- Effective indicator diversity K_eff
- Adaptive Early-Warning Inference Framework (AEWIF)
- Causal non-leakage and abstention state
"""

import numpy as np
import pytest
from src.advancements.adaptive_inference_framework import AdaptiveInferenceFramework
from src.advancements.information_diversity import calculate_effective_diversity
from src.advancements.reliability_calibration import ReliabilityCalibrator, compute_calibration_metrics
from src.indicators.univariate import VarianceIndicator, AutocorrelationLag1Indicator


class TestPhase4Advancements:

    def test_effective_diversity_ratio(self):
        # 1. Perfectly collinear matrix: K_eff should be exactly 1.0
        x = np.random.default_rng(42).normal(0, 1, size=(100, 1))
        collinear = np.column_stack([x, 2*x, -3*x])
        k_eff_collinear, _ = calculate_effective_diversity(collinear)
        assert np.isclose(k_eff_collinear, 1.0, atol=1e-2), f"Expected K_eff ~ 1.0, got {k_eff_collinear}"

        # 2. Mutually orthogonal matrix: K_eff should be close to K=3.0
        rng = np.random.default_rng(123)
        orthogonal = rng.normal(0, 1, size=(2000, 3))
        k_eff_orth, _ = calculate_effective_diversity(orthogonal)
        assert k_eff_orth > 2.7, f"Expected K_eff close to 3.0, got {k_eff_orth}"

    def test_noise_dilution_theorem_numerical(self):
        # High SNR signal
        N = 5000
        signal = 5.0
        x1 = np.random.default_rng(1).normal(signal, 1.0, size=N)
        snr_1 = np.mean(x1) / np.std(x1)

        # Average with 3 pure noise channels (signal = 0, std = 1)
        x2 = np.random.default_rng(2).normal(0.0, 1.0, size=N)
        x3 = np.random.default_rng(3).normal(0.0, 1.0, size=N)
        x4 = np.random.default_rng(4).normal(0.0, 1.0, size=N)

        composite = 0.25 * (x1 + x2 + x3 + x4)
        snr_comp = np.mean(composite) / np.std(composite)

        # Theoretical prediction: SNR_comp = SNR_1 / sqrt(4) = 0.5 * SNR_1
        expected_ratio = 0.5
        actual_ratio = snr_comp / snr_1
        assert np.isclose(actual_ratio, expected_ratio, atol=0.08), (
            f"Expected SNR ratio ~ {expected_ratio}, got {actual_ratio}"
        )

    def test_aewif_causal_predictions_and_boundedness(self):
        rng = np.random.default_rng(999)
        traj = rng.normal(1.0, 0.1, size=(300, 1))

        aewif = AdaptiveInferenceFramework(window_size=30, trend_window=20, reliability_threshold=0.25)
        # Baseline calibration
        baseline_runs = [rng.normal(1.0, 0.1, size=(300, 1)) for _ in range(5)]
        aewif.calibrate_baseline(baseline_runs, step=2)

        res = aewif.predict_trajectory(traj, step=2)
        warn = res['warning_score']
        rel = res['reliability_score']
        weights = res['weights']

        assert len(warn) == 300
        assert len(rel) == 300
        assert weights.shape == (300, len(aewif.indicators))

        # Check bounded reliability
        assert np.all(rel >= 0.0) and np.all(rel <= 1.0)
        # Check non-negative warning score
        assert np.all(warn >= 0.0)

    def test_aewif_abstention_under_extreme_noise(self):
        # When signal is pure Gaussian white noise with large variance
        rng = np.random.default_rng(456)
        pure_noise = rng.normal(0, 10.0, size=(400, 1))

        aewif = AdaptiveInferenceFramework(window_size=30, trend_window=20, reliability_threshold=0.30)
        baseline_runs = [rng.normal(0, 1.0, size=(400, 1)) for _ in range(5)]
        aewif.calibrate_baseline(baseline_runs, step=4)

        res = aewif.predict_trajectory(pure_noise, step=4)
        # Because noise_ratio = Var(diff)/Var(tot) ~ 2.0 and indicators are discordant,
        # mean reliability score should be below threshold
        mean_rel = np.mean(res['reliability_score'][100:])
        assert mean_rel < 0.30, f"Expected reliability < 0.30 under pure white noise, got {mean_rel}"

    def test_reliability_calibrator_ece_reduction(self):
        rng = np.random.default_rng(789)
        # Generate uncalibrated overconfident scores
        raw_scores = rng.beta(2, 5, size=500)
        # True labels with probability proportional to monotonic sigmoid
        true_probs = 1.0 / (1.0 + np.exp(-4.0 * (raw_scores - 0.3)))
        labels = rng.binomial(1, true_probs)

        # Uncalibrated metrics
        uncal_m = compute_calibration_metrics(raw_scores, labels)

        # Calibrate via Isotonic Regression
        cal = ReliabilityCalibrator()
        cal.fit(raw_scores[:250], labels[:250])
        cal_scores = cal.predict(raw_scores[250:])

        cal_m = compute_calibration_metrics(cal_scores, labels[250:])

        # Expect calibration to reduce ECE and Brier score
        assert cal_m['ece'] < uncal_m['ece'], f"Expected ECE reduction: {cal_m['ece']} vs {uncal_m['ece']}"
        assert cal_m['brier_score'] <= uncal_m['brier_score'] + 0.05

    def test_finite_window_detectability_bound(self):
        # Verify that N_req exceeds N_max when SNR_dyn is below the minimax threshold
        alpha = 0.05
        beta = 0.20
        c_val = 2.0 * (1.645 + 0.842)**2  # ~12.37
        r = 0.02
        dt = 0.05
        delta_mu = 0.5
        n_max = int(delta_mu / (r * dt))  # 500 points

        # Case 1: High SNR_dyn (1.5) -> N_req = 12.37 / 1.5^2 = 5.5 < N_max (Detectable)
        snr_high = 1.5
        n_req_high = c_val / (snr_high**2)
        assert n_req_high < n_max, "High SNR should be within quasi-stationary window"

        # Case 2: Very Low SNR_dyn (0.05) -> N_req = 12.37 / 0.0025 = 4948 > N_max (Mathematically Undetectable)
        snr_low = 0.05
        n_req_low = c_val / (snr_low**2)
        assert n_req_low > n_max, "Very low SNR should exceed maximum quasi-stationary window"

    def test_aewif_persistence_filter_and_zero_weight_abstention(self):
        # 1. Test persistence filter: transient single spike must NOT trigger alarm_active
        aewif = AdaptiveInferenceFramework(
            window_size=20, trend_window=15, reliability_threshold=0.25,
            alarm_threshold=1.5, persistence_steps=4
        )
        rng = np.random.default_rng(101)
        traj = np.ones((200, 1)) + rng.normal(0, 0.01, size=(200, 1))
        # Single transient spike at step 50
        traj[50, 0] = 10.0

        # Calibrate baseline
        baselines = [np.ones((200, 1)) + rng.normal(0, 0.01, size=(200, 1)) for _ in range(5)]
        aewif.calibrate_baseline(baselines, step=2)

        res = aewif.predict_trajectory(traj, step=2)
        assert 'alarm_active' in res
        assert res['alarm_active'].dtype == bool

        # Because spike lasted only 1 step (less than persistence_steps = 4), alarm_active at step 50 must be False
        assert not res['alarm_active'][50], "Single-step spike should not trigger persistent alarm"

        # 2. Test zero-weight abstention when completely flat null
        flat_traj = np.ones((200, 1))
        res_flat = aewif.predict_trajectory(flat_traj, step=2)
        # Check that weights are strictly zero when no trend exists
        assert np.all(res_flat['weights'][50] == 0.0), "Uninformative data must receive zero weights, not equal weights"
        assert not res_flat['is_reliable'][50], "Uninformative data must be marked unreliable"
