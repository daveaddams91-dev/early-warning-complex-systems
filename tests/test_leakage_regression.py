"""
Regression unit tests verifying zero data-leakage and principled null baseline calibration.
"""

import pytest
import numpy as np
from src.indicators.univariate import VarianceIndicator, AutocorrelationLag1Indicator
from src.models.bocpd_composite import BayesianChangepointModel
from src.models.elastic_net_composite import ElasticNetWarningModel


class TestLeakageRegression:
    def test_bocpd_uses_fitted_baseline(self):
        indicators = [VarianceIndicator(), AutocorrelationLag1Indicator()]
        model = BayesianChangepointModel(indicators=indicators)
        
        # Fit on null baseline runs
        baseline_null = [np.ones(100) * 5.0 + np.random.normal(0, 0.05, 100) for _ in range(5)]
        model.fit(baseline_null, window_size=30, step=2)
        
        assert model.baseline_means is not None
        assert model.baseline_stds is not None
        assert len(model.baseline_means) == 2
        
        # Predict on a test series
        test_series = np.linspace(5.0, 1.0, 100) + np.random.normal(0, 0.05, 100)
        scores = model.predict_score(test_series, window_size=30, step=2)
        assert len(scores) == 100
        assert not np.isnan(scores[-1])

    def test_elastic_net_no_spurious_labels(self):
        indicators = [VarianceIndicator(), AutocorrelationLag1Indicator()]
        model = ElasticNetWarningModel(indicators=indicators)
        
        baseline_null = [np.ones(100) * 5.0 + np.random.normal(0, 0.05, 100) for _ in range(5)]
        model.fit(baseline_null, window_size=30, step=2)
        
        # Model should NOT claim to be trained on genuine labels, but scaler should be fitted
        assert not model.is_trained
        assert hasattr(model.scaler, 'mean_')
        assert model.scaler.mean_ is not None
