"""
Unit tests for Game-Changer Advancements (Phase 2).
"""

import pytest
import numpy as np
from src.systems.may_harvesting import MayHarvestingSystem
from src.indicators.univariate import VarianceIndicator, AutocorrelationLag1Indicator, PermutationEntropyIndicator
from src.advancements.detectability import DetectabilityBoundaryEngine
from src.advancements.adaptive_warning import AdaptiveWarningSystem
from src.advancements.counterfactual import CounterfactualAnalysisEngine
from src.advancements.data_scaling import DataScalingEngine
from src.advancements.active_probing import ActiveExperimentationEngine
from src.advancements.theoretical_analysis import TheoreticalComparisonEngine
from src.advancements.adversarial_lab import AdversarialCollapseLab


class TestAdvancements:
    def setup_method(self):
        self.system = MayHarvestingSystem()

    def test_detectability_boundary_engine(self):
        engine = DetectabilityBoundaryEngine(self.system, dt_sim=0.01)
        snr_clean = engine.compute_snr_analytical(x_star=7.5, mu=1.6, sigma=0.05, sigma_obs=0.01)
        snr_noisy = engine.compute_snr_analytical(x_star=7.5, mu=1.6, sigma=0.05, sigma_obs=0.50)
        assert snr_clean > snr_noisy
        assert snr_clean > 1.0

    def test_adaptive_warning_system(self):
        indicators = [VarianceIndicator(), AutocorrelationLag1Indicator(), PermutationEntropyIndicator(m=3, tau=1)]
        model = AdaptiveWarningSystem(indicators=indicators, trend_window=20)
        
        # Test on clean ramp series
        x_clean = np.linspace(10.0, 1.0, 100) + np.random.normal(0, 0.05, 100)
        scores = model.predict_score(x_clean, window_size=30, step=2)
        assert len(scores) == 100
        assert not np.isnan(scores[-1])

    def test_counterfactual_distinguishability(self):
        engine = CounterfactualAnalysisEngine(self.system, dt_sim=0.01, dt_obs=0.05)
        rec, col = engine.simulate_paired_counterfactuals(n_pairs=4, t_max=30.0, t_shock=10.0)
        assert len(rec) == 4
        assert len(col) == 4
        
        df_dist = engine.compute_distinguishability_profile(rec, col, t_shock=10.0)
        assert len(df_dist) > 0
        assert 'Wasserstein1_Dist' in df_dist.columns

    def test_data_scaling_engine(self):
        engine = DataScalingEngine(self.system, dt_sim=0.01)
        df_scale = engine.measure_n_min_grid(noise_levels=[0.03], dt_levels=[0.05], target_auc=0.75, n_runs=3)
        assert len(df_scale) == 1
        assert 'N_min_samples' in df_scale.columns

    def test_active_probing_and_intervention(self):
        engine = ActiveExperimentationEngine(self.system, dt_sim=0.01, dt_obs=0.05)
        probe_res = engine.run_active_probe_experiment(t_max=30.0, probe_interval=10.0, probe_amplitude=0.3)
        assert len(probe_res['probe_times']) >= 2
        assert len(probe_res['estimated_kappas']) == len(probe_res['probe_times'])
        
        ctrl_res = engine.run_stabilizing_intervention(t_max=40.0, intervention_time=20.0, control_gain=1.5)
        assert 'intervention_cost' in ctrl_res
        assert ctrl_res['intervention_cost'] >= 0.0

    def test_theoretical_comparison_engine(self):
        engine = TheoreticalComparisonEngine(self.system)
        df_comp = engine.compare_theoretical_vs_empirical(mu_values=[1.6], sigma=0.05, dt_obs=0.05, window_sizes=[30], n_mc_steps=1000)
        assert len(df_comp) == 1
        assert 'AR1_Theoretical' in df_comp.columns
        assert 'AR1_Expected_Biased' in df_comp.columns

    def test_adversarial_collapse_lab(self):
        lab = AdversarialCollapseLab(dt_sim=0.01, dt_obs=0.05)
        s1 = lab.generate_scenario_1_false_csd_sinusoid(n_runs=2, t_max=20.0)
        s2 = lab.generate_scenario_2_noise_spectrum_shift(n_runs=2, t_max=20.0)
        s3 = lab.generate_scenario_3_hidden_variable_crisis(n_runs=2, t_max=20.0)
        assert len(s1) == 2
        assert len(s2) == 2
        assert len(s3) == 2
