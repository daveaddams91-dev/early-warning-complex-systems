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
