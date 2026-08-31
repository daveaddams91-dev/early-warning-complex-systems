"""
Unit tests for SDE numerical integration and observation corruption pipeline.
"""

import pytest
import numpy as np
from src.systems.may_harvesting import MayHarvestingSystem
from src.simulation.integrator import SDEIntegrator, ObservationCorrupter


class TestSDEIntegrator:
    def test_reproducibility(self):
        sys = MayHarvestingSystem()
        integrator = SDEIntegrator(sys, dt_sim=0.01, dt_obs=0.05)
        
        # Fixed parameter
        mu_fn = lambda t: 1.5
        
        res1 = integrator.simulate(t_max=10.0, mu_func=mu_fn, seed=42)
        res2 = integrator.simulate(t_max=10.0, mu_func=mu_fn, seed=42)
        res3 = integrator.simulate(t_max=10.0, mu_func=mu_fn, seed=99)
        
        np.testing.assert_array_equal(res1['t'], res2['t'])
        np.testing.assert_array_equal(res1['x'], res2['x'])
        # Different seed should produce different stochastic trajectory
        assert not np.array_equal(res1['x'], res3['x'])

    def test_collapse_under_parameter_ramp(self):
        sys = MayHarvestingSystem()
        integrator = SDEIntegrator(sys, dt_sim=0.005, dt_obs=0.05)
        
        # Ramp c from 1.5 to 3.2 over t = [0, 120]
        mu_fn = lambda t: 1.5 + (3.2 - 1.5) * (t / 120.0)
        
        res = integrator.simulate(t_max=120.0, mu_func=mu_fn, seed=42, stop_on_collapse=True)
        assert res['collapsed'] is True
        assert not np.isnan(res['t_crit'])
        # Critical value should be reached near t where c ~ 2.6
        mu_at_collapse = mu_fn(res['t_crit'])
        assert 2.50 <= mu_at_collapse <= 3.20

    def test_observation_corrupter(self):
        sys = MayHarvestingSystem()
        integrator = SDEIntegrator(sys, dt_sim=0.01, dt_obs=0.05)
        res = integrator.simulate(t_max=20.0, mu_func=lambda t: 1.5, seed=42)
        x_clean = res['x']
        
        # Test Gaussian noise
        x_noisy = ObservationCorrupter.add_gaussian_noise(x_clean, snr_db=10.0, seed=123)
        assert x_noisy.shape == x_clean.shape
        assert np.var(x_noisy - x_clean) > 0.0
        
        # Test Student-t noise
        x_t = ObservationCorrupter.add_student_t_noise(x_clean, scale=0.05, df=3.0, seed=123)
        assert x_t.shape == x_clean.shape
        
        # Test Red noise
        x_red = ObservationCorrupter.add_colored_red_noise(x_clean, dt=0.05, gamma=0.5, seed=123)
        assert x_red.shape == x_clean.shape
        
        # Test Distractors
        x_dist = ObservationCorrupter.append_distractors(x_clean, n_distractors=4, dt=0.05, seed=123)
        assert x_dist.shape == (x_clean.shape[0], x_clean.shape[1] + 4)
