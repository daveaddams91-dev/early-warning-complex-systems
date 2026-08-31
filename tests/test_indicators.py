"""
Unit tests for univariate, multivariate, and Kendall trend indicators.
"""

import pytest
import numpy as np
from src.indicators.univariate import (
    VarianceIndicator,
    AutocorrelationLag1Indicator,
    SkewnessIndicator,
    KurtosisIndicator,
    PermutationEntropyIndicator,
    SpectralReddeningIndicator,
    RecoveryRateIndicator
)
from src.indicators.multivariate import (
    PCA1VarianceIndicator,
    GeneralizedVarianceIndicator,
    MahalanobisDistanceIndicator,
    DynamicalNetworkBiomarkerIndicator,
    AlgebraicConnectivityIndicator
)
from src.indicators.kendall_trend import RollingKendallTrend


class TestUnivariateIndicators:
    def test_variance_and_ar1(self):
        rng = np.random.default_rng(42)
        # Stationary white noise
        x_white = rng.standard_normal(200)
        
        var_ind = VarianceIndicator()
        ar1_ind = AutocorrelationLag1Indicator()
        
        var_roll = var_ind.compute_rolling(x_white, window_size=50)
        ar1_roll = ar1_ind.compute_rolling(x_white, window_size=50)
        
        assert np.isnan(var_roll[0])
        assert np.isnan(var_roll[48])
        assert not np.isnan(var_roll[49])
        assert 0.4 < var_roll[49] < 1.8
        # AR(1) for white noise should be near 0
        assert abs(ar1_roll[49]) < 0.3

    def test_permutation_entropy(self):
        # Highly ordered sinusoidal series vs random noise
        t = np.linspace(0, 10, 100)
        x_ordered = np.sin(t)
        rng = np.random.default_rng(42)
        x_random = rng.standard_normal(100)
        
        pe_ind = PermutationEntropyIndicator(m=3, tau=1)
        pe_ordered = pe_ind.compute_window(x_ordered)
        pe_random = pe_ind.compute_window(x_random)
        
        # Ordered series should have lower permutation entropy than random noise
        assert pe_ordered < pe_random
        assert 0.0 <= pe_ordered <= 1.0
        assert 0.0 <= pe_random <= 1.0


class TestMultivariateIndicators:
    def test_pca_and_generalized_variance(self):
        rng = np.random.default_rng(42)
        x_multi = rng.standard_normal((100, 4))
        
        pca_ind = PCA1VarianceIndicator()
        gen_ind = GeneralizedVarianceIndicator()
        
        pca_val = pca_ind.compute_window(x_multi)
        gen_val = gen_ind.compute_window(x_multi)
        
        assert not np.isnan(pca_val)
        assert pca_val > 0.0
        assert not np.isnan(gen_val)

    def test_mahalanobis_distance(self):
        rng = np.random.default_rng(42)
        baseline = rng.standard_normal((100, 3))
        # Anomaly shifted far from origin
        anomaly = rng.standard_normal((100, 3)) + 10.0
        
        mahal = MahalanobisDistanceIndicator()
        mahal.set_reference(baseline)
        
        dist_base = mahal.compute_window(baseline)
        dist_anom = mahal.compute_window(anomaly)
        
        assert dist_anom > dist_base * 3.0


class TestKendallTrend:
    def test_kendall_trend_detection(self):
        # Linearly increasing series should have Kendall tau = +1.0
        increasing = np.linspace(1.0, 10.0, 60)
        decreasing = np.linspace(10.0, 1.0, 60)
        
        kt = RollingKendallTrend(trend_window=30)
        tau_inc = kt.compute(increasing)
        tau_dec = kt.compute(decreasing)
        
        assert np.isclose(tau_inc[-1], 1.0, atol=1e-2)
        assert np.isclose(tau_dec[-1], -1.0, atol=1e-2)
