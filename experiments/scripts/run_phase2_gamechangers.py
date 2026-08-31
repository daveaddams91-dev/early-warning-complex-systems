"""
Phase 2 Game-Changer Master Experiment Runner.
Executes the advanced research protocols for Game-Changers #1, #2, #4, #5, #6, #7, #9, #10.
"""

import sys
import time
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from src.systems.may_harvesting import MayHarvestingSystem
from src.systems.fitzhugh_nagumo import FitzHughNagumoSystem
from src.systems.coupled_network import CoupledNetworkSystem
from src.indicators.univariate import (
    VarianceIndicator,
    AutocorrelationLag1Indicator,
    PermutationEntropyIndicator,
    SpectralReddeningIndicator
)
from src.indicators.multivariate import MahalanobisDistanceIndicator
from src.models.rank_composite import RankAggregationModel
from src.models.mahalanobis_composite import MultiIndicatorMahalanobisModel
from src.advancements.detectability import DetectabilityBoundaryEngine
from src.advancements.adaptive_warning import AdaptiveWarningSystem
from src.advancements.counterfactual import CounterfactualAnalysisEngine
from src.advancements.data_scaling import DataScalingEngine
from src.advancements.active_probing import ActiveExperimentationEngine
from src.advancements.theoretical_analysis import TheoreticalComparisonEngine
from src.advancements.adversarial_lab import AdversarialCollapseLab
from src.evaluation.metrics import compute_roc_pr, compute_false_alarm_rate


def run_phase2_benchmarks():
    print("=" * 70, flush=True)
    print("STARTING PHASE 2 GAME-CHANGER RESEARCH EXPERIMENTAL SUITE", flush=True)
    print("=" * 70, flush=True)

    tables_dir = Path("experiments/results/tables")
    figs_dir = Path("experiments/results/figures")
    tables_dir.mkdir(parents=True, exist_ok=True)
    figs_dir.mkdir(parents=True, exist_ok=True)

    sys_may = MayHarvestingSystem()

    # -------------------------------------------------------------
    # 1. GAME-CHANGER #1: Detectability Phase Boundary Diagram
    # -------------------------------------------------------------
    print("\n>>> 1. Mapping the Detectability Phase Boundary...", flush=True)
    det_engine = DetectabilityBoundaryEngine(sys_may, dt_sim=0.01)
    sigma_grid = [0.0, 0.05, 0.10, 0.20, 0.40, 0.80]
    dt_grid = [0.02, 0.05, 0.10, 0.25, 0.50]
    ramp_grid = [1.0]

    df_detectability = det_engine.evaluate_grid(
        sigma_obs_levels=sigma_grid,
        dt_obs_levels=dt_grid,
        ramp_rates=ramp_grid,
        n_runs=15,
        target_auc_threshold=0.75
    )
    df_detectability.to_csv(tables_dir / "phase2_detectability_phase_diagram.csv", index=False)
    print("  Detectability phase diagram recorded.", flush=True)

    # -------------------------------------------------------------
    # 2. GAME-CHANGER #2: Adaptive Warning Engine & Abstention Benchmarks
    # -------------------------------------------------------------
    print("\n>>> 2. Benchmarking Adaptive Early-Warning Engine...", flush=True)
    ind_subset = [
        VarianceIndicator(),
        AutocorrelationLag1Indicator(),
        PermutationEntropyIndicator(m=3, tau=1),
        SpectralReddeningIndicator()
    ]
    adaptive_model = AdaptiveWarningSystem(indicators=ind_subset, trend_window=30)
    rank_model = RankAggregationModel(indicators=ind_subset, trend_window=30)
    mahal_model = MultiIndicatorMahalanobisModel(indicators=ind_subset)

    # Test under: Clean, High Noise (SNR 0dB), Shock Disturbance, Benign Drift
    integrator = det_engine.system
    dt_obs = 0.05
    from src.simulation.integrator import SDEIntegrator
    sde_int = SDEIntegrator(sys_may, dt_sim=0.01, dt_obs=dt_obs)

    null_trajs = [sde_int.simulate(t_max=100.0, mu_func=lambda t: 1.5, seed=7000 + i)['x'] for i in range(15)]
    adaptive_model.fit(null_trajs, window_size=50, step=4)
    rank_model.fit(null_trajs, window_size=50, step=4)
    mahal_model.fit(null_trajs, window_size=50, step=4)

    ramp_trajs = [sde_int.simulate(t_max=120.0, mu_func=lambda t: 1.5 + (3.2 - 1.5)*(t/120.0), seed=8000 + i, stop_on_collapse=True) for i in range(15)]
    shock_trajs = []
    for i in range(15):
        res = sde_int.simulate(t_max=100.0, mu_func=lambda t: 1.6, seed=9000 + i)
        x_s = res['x'].copy()
        idx_50 = int(50.0 / dt_obs)
        if idx_50 < len(x_s):
            x_s[idx_50 : idx_50 + 20] -= 2.5
        shock_trajs.append({'t': res['t'], 'x': x_s})

    adaptive_results = []
    for model_name, m in [('Baseline-AR1', None), ('CEWF-Rank', rank_model), ('CEWF-Mahalanobis', mahal_model), ('Adaptive-Bayesian-EWS', adaptive_model)]:
        # 1. Performance on True Tipping
        y_true, y_score = [], []
        for r in ramp_trajs:
            t_crit, t_arr, x = r['t_crit'], r['t'], r['x']
            if np.isnan(t_crit):
                continue
            if model_name == 'Baseline-AR1':
                ind_ar1 = AutocorrelationLag1Indicator()
                sc = ind_ar1.compute_rolling(x, window_size=50, step=4)
            else:
                sc = m.predict_score(x, window_size=50, step=4)

            pre = (t_arr >= t_crit - 20.0) & (t_arr <= t_crit) & (~np.isnan(sc))
            safe = (t_arr >= 10.0) & (t_arr <= 30.0) & (~np.isnan(sc))
            if np.sum(pre) > 0 and np.sum(safe) > 0:
                y_true.extend([1] * np.sum(pre))
                y_score.extend(sc[pre])
                y_true.extend([0] * np.sum(safe))
                y_score.extend(sc[safe])

        roc_res = compute_roc_pr(np.array(y_true), np.array(y_score))

        # 2. False Alarm Rate on Pulse Shock
        shock_scores = []
        for s_tr in shock_trajs:
            x = s_tr['x']
            if model_name == 'Baseline-AR1':
                sc = ind_ar1.compute_rolling(x, window_size=50, step=4)
            else:
                sc = m.predict_score(x, window_size=50, step=4)
            shock_scores.append(sc)

        thresh = 0.5 if not model_name.startswith('CEWF-Mahal') else 1.5
        far_shock = compute_false_alarm_rate(shock_scores, threshold=thresh)

        adaptive_results.append({
            'Model': model_name,
            'True_Tipping_ROC_AUC': roc_res['roc_auc'],
            'True_Tipping_PR_AUC': roc_res['pr_auc'],
            'False_Alarm_Rate_Shock': far_shock,
            'Can_Abstain_From_Alarm': (model_name == 'Adaptive-Bayesian-EWS')
        })

    df_adaptive = pd.DataFrame(adaptive_results)
    df_adaptive.to_csv(tables_dir / "phase2_adaptive_warning_benchmark.csv", index=False)
    print("  Adaptive Early-Warning benchmarks recorded.", flush=True)

    # -------------------------------------------------------------
    # 3. GAME-CHANGER #4: Counterfactual Distinguishability
    # -------------------------------------------------------------
    print("\n>>> 3. Computing Counterfactual Informational Distinguishability...", flush=True)
    cf_engine = CounterfactualAnalysisEngine(sys_may, dt_sim=0.01, dt_obs=0.05)
    rec_ens, col_ens = cf_engine.simulate_paired_counterfactuals(n_pairs=25, t_max=80.0, t_shock=20.0, shock_magnitude=2.0)
    df_cf = cf_engine.compute_distinguishability_profile(rec_ens, col_ens, t_shock=20.0)
    df_cf.to_csv(tables_dir / "phase2_counterfactual_distinguishability.csv", index=False)
    print("  Counterfactual distinguishability profile recorded.", flush=True)

    # -------------------------------------------------------------
    # 4. GAME-CHANGER #5: Minimum Data Scaling
    # -------------------------------------------------------------
    print("\n>>> 4. Measuring Minimum Data Scaling (N_min)...", flush=True)
    scale_engine = DataScalingEngine(sys_may, dt_sim=0.01)
    df_scaling = scale_engine.measure_n_min_grid(
        noise_levels=[0.02, 0.05, 0.10, 0.20],
        dt_levels=[0.02, 0.05, 0.10],
        target_auc=0.75,
        n_runs=10
    )
    df_scaling.to_csv(tables_dir / "phase2_minimum_data_scaling.csv", index=False)
    print("  Data scaling laws recorded.", flush=True)

    # -------------------------------------------------------------
    # 5. GAME-CHANGER #6 & #7: Active Probing & Stabilizing Intervention
    # -------------------------------------------------------------
    print("\n>>> 5. Evaluating Active Probing and Stabilizing Control...", flush=True)
    active_engine = ActiveExperimentationEngine(sys_may, dt_sim=0.01, dt_obs=0.05)
    probe_data = active_engine.run_active_probe_experiment(t_max=100.0, probe_interval=15.0, probe_amplitude=0.5, seed=42)

    # Stabilizing intervention across activation times
    intervention_records = []
    for t_act in [40.0, 60.0, 75.0, 85.0, 95.0]:
        ctrl_res = active_engine.run_stabilizing_intervention(
            t_max=110.0,
            intervention_time=t_act,
            control_gain=2.5,
            seed=42
        )
        intervention_records.append({
            'Intervention_Time': t_act,
            'Lead_Time_Before_Natural_Collapse': max(0.0, 90.0 - t_act),
            'Stabilization_Success': ctrl_res['success'],
            'Intervention_Cost_Integral_U2': ctrl_res['intervention_cost'],
            'Final_State': float(ctrl_res['x'][-1, 0])
        })
    df_ctrl = pd.DataFrame(intervention_records)
    df_ctrl.to_csv(tables_dir / "phase2_active_probing_intervention.csv", index=False)
    print("  Active probing and control benchmarks recorded.", flush=True)

    # -------------------------------------------------------------
    # 6. GAME-CHANGER #9: Adversarial Collapse Lab
    # -------------------------------------------------------------
    print("\n>>> 6. Running Adversarial Collapse Lab Scenarios...", flush=True)
    adv_lab = AdversarialCollapseLab(dt_sim=0.01, dt_obs=0.05)
    sc1_trajs = adv_lab.generate_scenario_1_false_csd_sinusoid(n_runs=15, t_max=100.0)
    sc2_trajs = adv_lab.generate_scenario_2_noise_spectrum_shift(n_runs=15, t_max=100.0)
    sc3_trajs = adv_lab.generate_scenario_3_hidden_variable_crisis(n_runs=15, t_max=100.0)

    adv_records = []
    for sc_name, sc_data, expected_outcome in [
        ('Scenario_1_Sinusoidal_False_CSD', sc1_trajs, 'No Collapse (False Positive Test)'),
        ('Scenario_2_Noise_Spectrum_Shift', sc2_trajs, 'No Collapse (False Positive Test)'),
        ('Scenario_3_Hidden_Variable_Crisis', sc3_trajs, 'Sudden Collapse (False Negative Test)')
    ]:
        for model_name, m in [('Baseline_AR1', None), ('CEWF_Rank', rank_model), ('CEWF_Mahalanobis', mahal_model), ('Adaptive_Bayesian_EWS', adaptive_model)]:
            scores_list = []
            for tr in sc_data:
                x = tr['x']
                if model_name == 'Baseline_AR1':
                    sc = AutocorrelationLag1Indicator().compute_rolling(x, window_size=50, step=4)
                else:
                    sc = m.predict_score(x, window_size=50, step=4)
                scores_list.append(sc)

            thresh = 0.5 if not model_name.startswith('CEWF_Mahal') else 1.5
            far = compute_false_alarm_rate(scores_list, threshold=thresh)

            adv_records.append({
                'Adversarial_Scenario': sc_name,
                'Expected_Physical_Outcome': expected_outcome,
                'Model': model_name,
                'False_Alarm_Rate': far
            })

    df_adv = pd.DataFrame(adv_records)
    df_adv.to_csv(tables_dir / "phase2_adversarial_lab_results.csv", index=False)
    print("  Adversarial lab stress tests recorded.", flush=True)

    # -------------------------------------------------------------
    # 7. GAME-CHANGER #10: Theoretical Bias vs Monte Carlo
    # -------------------------------------------------------------
    print("\n>>> 7. Quantifying Theoretical Estimator Bias...", flush=True)
    th_engine = TheoreticalComparisonEngine(sys_may)
    df_th = th_engine.compare_theoretical_vs_empirical(
        mu_values=[1.5, 1.8, 2.1, 2.4, 2.55],
        sigma=0.05,
        dt_obs=0.05,
        window_sizes=[30, 50, 100],
        n_mc_steps=20000
    )
    df_th.to_csv(tables_dir / "phase2_theoretical_bias_analysis.csv", index=False)
    print("  Theoretical estimator bias quantified.", flush=True)

    print("\n" + "=" * 70, flush=True)
    print("PHASE 2 GAME-CHANGER EXPERIMENTAL SUITE COMPLETE!", flush=True)
    print("=" * 70, flush=True)


if __name__ == "__main__":
    run_phase2_benchmarks()
