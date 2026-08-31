"""
Unit tests for composite early-warning model architectures.
"""

import pytest
import numpy as np
from src.systems.may_harvesting import MayHarvestingSystem
from src.simulation.integrator import SDEIntegrator
from src.indicators.univariate import VarianceIndicator, AutocorrelationLag1Indicator, PermutationEntropyIndicator
from src.models.linear_composite import LinearCompositeModel
from src.models.rank_composite import RankAggregationModel
from src.models.mahalanobis_composite import MultiIndicatorMahalanobisModel
from src.models.elastic_net_composite import ElasticNetWarningModel
from src.models.bocpd_composite import BayesianChangepointModel


@pytest.fixture
def sample_trajectory():
    sys = MayHarvestingSystem()
    integrator = SDEIntegrator(sys, dt_sim=0.01, dt_obs=0.05)
    # Ramp c from 1.5 to 3.2
    mu_fn = lambda t: 1.5 + (3.2 - 1.5) * (t / 120.0)
    res = integrator.simulate(t_max=120.0, mu_func=mu_fn, seed=42)
    return res


class TestCompositeModels:
    def test_linear_and_rank_models(self, sample_trajectory):
        inds = [VarianceIndicator(), AutocorrelationLag1Indicator(), PermutationEntropyIndicator()]
        lin_model = LinearCompositeModel(inds)
        rank_model = RankAggregationModel(inds, trend_window=30)
        
        x = sample_trajectory['x']
        lin_scores = lin_model.predict_score(x, window_size=50)
        rank_scores = rank_model.predict_score(x, window_size=50)
        
        assert len(lin_scores) == len(x)
        assert len(rank_scores) == len(x)
        
        # Valid non-NaN scores after window fills
        valid_lin = lin_scores[~np.isnan(lin_scores)]
        valid_rank = rank_scores[~np.isnan(rank_scores)]
        assert len(valid_lin) > 0
        assert len(valid_rank) > 0
        
        # Warning score at the end of the ramping regime should be higher than at the beginning
        assert np.nanmean(lin_scores[-100:]) > np.nanmean(lin_scores[50:150])

    def test_mahalanobis_model(self, sample_trajectory):
        inds = [VarianceIndicator(), AutocorrelationLag1Indicator()]
        mahal_model = MultiIndicatorMahalanobisModel(inds)
        
        x = sample_trajectory['x']
        scores = mahal_model.predict_score(x, window_size=50)
        
        valid = scores[~np.isnan(scores)]
        assert len(valid) > 0
        assert np.all(valid >= 0.0)
        assert np.nanmean(scores[-100:]) > np.nanmean(scores[50:150])

    def test_bocpd_model(self, sample_trajectory):
        inds = [VarianceIndicator(), AutocorrelationLag1Indicator()]
        bocpd = BayesianChangepointModel(inds, hazard_rate=100.0)
        
        x = sample_trajectory['x']
        scores = bocpd.predict_score(x, window_size=50)
        valid = scores[~np.isnan(scores)]
        assert len(valid) > 0
        assert np.all(valid >= 0.0)
        assert np.all(valid <= 1.0)
