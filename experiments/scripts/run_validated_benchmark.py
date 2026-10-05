"""
Phase 3 Validated Benchmark Suite.
Implements rigorous Trajectory-Level Evaluation, Operational Early-Warning Metrics,
and Clustered Realization Bootstrap to produce verified, reproducible scientific outputs.
All outputs saved to results/validated/.
"""

import sys
from pathlib import Path
import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from src.systems.may_harvesting import MayHarvestingSystem
from src.systems.fitzhugh_nagumo import FitzHughNagumoSystem
from src.systems.subcritical_pitchfork import SubcriticalPitchforkSystem
from src.systems.stommel_box import StommelBoxSystem
from src.systems.coupled_network import CoupledNetworkSystem
from src.simulation.integrator import SDEIntegrator, ObservationCorrupter
from src.indicators.univariate import (
    VarianceIndicator,
    AutocorrelationLag1Indicator,
    SkewnessIndicator,
    KurtosisIndicator,
    PermutationEntropyIndicator,
    SpectralReddeningIndicator
)
from src.indicators.multivariate import (
    PCA1VarianceIndicator,
    MahalanobisDistanceIndicator,
    DynamicalNetworkBiomarkerIndicator
)
from src.models.linear_composite import LinearCompositeModel
from src.models.rank_composite import RankAggregationModel
from src.models.mahalanobis_composite import MultiIndicatorMahalanobisModel
from src.models.bocpd_composite import BayesianChangepointModel
from src.advancements.adaptive_warning import AdaptiveWarningSystem
from src.evaluation.metrics import (
    compute_roc_pr,
    compute_trajectory_level_roc_pr,
    compute_operational_lead_time_distribution,
    compute_false_alarm_rate,
    clustered_bootstrap_auc_diff
)


def get_core_methods(dt_obs: float = 0.05):
    """Retrieve core methods.
    
    Args:
        dt_obs (float):
    
    Returns:
        tuple: Result of type tuple
    
    """
    indicators = {
        'Variance': VarianceIndicator(),
        'AR(1)': AutocorrelationLag1Indicator(),
        'PermutationEntropy': PermutationEntropyIndicator(m=3, tau=1),
        'SpectralReddening': SpectralReddeningIndicator(low_freq_fraction=0.15),
        'PCA1-Variance': PCA1VarianceIndicator()
    }
    core_subset = [indicators['Variance'], indicators['AR(1)'], indicators['PermutationEntropy'], indicators['SpectralReddening']]
    
    models = {
        'CEWF-Linear': LinearCompositeModel(indicators=core_subset),
        'CEWF-Rank': RankAggregationModel(indicators=core_subset, trend_window=30),
        'CEWF-Mahalanobis': MultiIndicatorMahalanobisModel(indicators=core_subset, regularization=1e-3),
        'CEWF-BOCPD': BayesianChangepointModel(indicators=core_subset, hazard_rate=150.0),
        'Adaptive-Bayesian-EWS': AdaptiveWarningSystem(indicators=core_subset, trend_window=30)
    }
    return indicators, models, core_subset


def evaluate_trajectory(x: np.ndarray, indicators: dict, models: dict, core_subset: list, window_size: int = 50, step: int = 4):
    """Evaluate trajectory.
    
    Args:
        x:
        indicators:
        models:
        core_subset:
        window_size (int):
        step (int):
    
    Returns:
        The computed result
    
    """
    scores = {}
    x_1d = x[:, 0] if x.ndim > 1 else x
    for name, ind in indicators.items():
        if ind.is_multivariate:
            sc = ind.compute_rolling(x, window_size=window_size, step=step)
        else:
            sc = ind.compute_rolling(x_1d, window_size=window_size, step=step)
        scores[name] = sc
        
    for name, m in models.items():
        sc = m.predict_score(x, window_size=window_size, step=step)
        scores[name] = sc
    return scores


def run_validated_experiments(n_runs: int = 25, eval_step: int = 4):
    """Worker function for validated experiments.
    
    Args:
        n_runs (int):
        eval_step (int):
    
    """
    print("=" * 70, flush=True)
    print(f"STARTING PHASE 3 VALIDATED BENCHMARK SUITE (N_runs={n_runs}, Trajectory-Level)", flush=True)
    print("=" * 70, flush=True)

    out_dir = Path("results/validated")
    tables_dir = out_dir / "tables"
    figs_dir = out_dir / "figures"
    tables_dir.mkdir(parents=True, exist_ok=True)
    figs_dir.mkdir(parents=True, exist_ok=True)

    dt_obs = 0.05
    window_size = 50

    systems = [
        (MayHarvestingSystem(), lambda t: 1.5 + (3.2 - 1.5) * (t / 120.0), 120.0, lambda t: 1.5, "SYS1_May_Fold", 20.0),
        (FitzHughNagumoSystem(), lambda t: -0.5 + (0.45 - (-0.5)) * (t / 150.0), 150.0, lambda t: -0.5, "SYS2_FitzHughNagumo_Hopf", 25.0),
        (SubcriticalPitchforkSystem(), lambda t: -0.6 + (0.1 - (-0.6)) * (t / 100.0), 100.0, lambda t: -0.6, "SYS3_Subcritical_Pitchfork", 20.0),
        (StommelBoxSystem(), lambda t: 0.8 + (1.4 - 0.8) * (t / 120.0), 120.0, lambda t: 0.8, "SYS4_Stommel_AMOC", 20.0),
        (CoupledNetworkSystem(n_nodes=10, network_type='erdos_renyi', seed=42), lambda t: 1.5 + (5.2 - 1.5) * (t / 120.0), 120.0, lambda t: 1.5, "SYS5_Coupled_Network", 20.0)
    ]

    # -------------------------------------------------------------------------
    # BENCHMARK 1: Multi-System Trajectory-Level Clean Benchmark
    # -------------------------------------------------------------------------
    print("\n>>> 1. Running Clean Multi-System Trajectory-Level Benchmark...", flush=True)
    clean_results = []
    bootstrap_results = []

    for system, ramp_fn, t_max, null_fn, sys_tag, safe_time in systems:
        print(f"  Evaluating {sys_tag} ...", flush=True)
        integrator = SDEIntegrator(system, dt_sim=0.01, dt_obs=dt_obs)
        indicators, models, core_subset = get_core_methods(dt_obs=dt_obs)

        # Generate Null Baseline Runs
        null_trajs = [integrator.simulate(t_max=t_max, mu_func=null_fn, seed=1000 + r) for r in range(n_runs)]
        null_xs = [tr['x'] for tr in null_trajs]
        null_times = [tr['t'] for tr in null_trajs]

        # Fit models on null runs strictly
        for m in models.values():
            m.fit(null_xs, window_size=window_size, step=eval_step)

        # Generate Transition Ramp Runs
        ramp_trajs = [integrator.simulate(t_max=t_max, mu_func=ramp_fn, seed=2000 + r, stop_on_collapse=True) for r in range(n_runs)]
        ramp_xs = [tr['x'] for tr in ramp_trajs]
        ramp_times = [tr['t'] for tr in ramp_trajs]
        collapse_times = [tr['t_crit'] for tr in ramp_trajs]

        # Evaluate signals
        ramp_signals = [evaluate_trajectory(x, indicators, models, core_subset, window_size, eval_step) for x in ramp_xs]
        null_signals = [evaluate_trajectory(x, indicators, models, core_subset, window_size, eval_step) for x in null_xs]

        all_methods = list(indicators.keys()) + list(models.keys())
        method_scores_ramp = {}
        method_scores_null = {}

        for m_name in all_methods:
            r_sc = [s[m_name] for s in ramp_signals]
            n_sc = [s[m_name] for s in null_signals]
            method_scores_ramp[m_name] = r_sc
            method_scores_null[m_name] = n_sc

            # Trajectory-Level ROC-AUC
            traj_roc = compute_trajectory_level_roc_pr(
                r_sc, n_sc, ramp_times, collapse_times, null_times,
                safe_baseline_time=safe_time, min_lead_time=2.0
            )

            # Determine 95th percentile threshold on null runs
            idx_safe = int(safe_time / dt_obs)
            flat_null = np.concatenate([s[idx_safe:][~np.isnan(s[idx_safe:])] for s in n_sc]) if bool(n_sc) else np.array([])
            thresh = float(np.percentile(flat_null, 95)) if bool(flat_null) else 1.0

            # Operational early warning distribution
            op_res = compute_operational_lead_time_distribution(
                r_sc, ramp_times, collapse_times, threshold=thresh,
                safe_baseline_time=safe_time, min_actionable_lead_time=2.0
            )
            far_null = compute_false_alarm_rate(n_sc, threshold=thresh)

            clean_results.append({
                'System': sys_tag,
                'Method': m_name,
                'Category': 'Composite' if m_name.startswith('CEWF') or 'Adaptive' in m_name else 'Univariate/Multivariate',
                'Trajectory_ROC_AUC': traj_roc['roc_auc'],
                'Trajectory_PR_AUC': traj_roc['pr_auc'],
                'True_Positive_Rate': op_res['true_positive_rate'],
                'Early_False_Alarm_Rate': op_res['early_false_alarm_rate'],
                'Late_Alarm_Rate': op_res['late_alarm_rate'],
                'Missed_Detection_Rate': op_res['missed_detection_rate'],
                'Mean_Actionable_Lead_Time': op_res['mean_lead_time'],
                'Median_Lead_Time': op_res['median_lead_time'],
                'Null_False_Alarm_Rate': far_null
            })

        # Clustered Bootstrap comparison vs AR(1) baseline
        base_r_sc = method_scores_ramp['AR(1)']
        base_n_sc = method_scores_null['AR(1)']
        for comp_name in ['Variance', 'CEWF-Mahalanobis', 'CEWF-Rank', 'Adaptive-Bayesian-EWS']:
            comp_r_sc = method_scores_ramp[comp_name]
            comp_n_sc = method_scores_null[comp_name]
            boot_diff = clustered_bootstrap_auc_diff(
                comp_r_sc, base_r_sc, comp_n_sc, base_n_sc,
                ramp_times, collapse_times, null_times,
                n_boot=500, seed=42
            )
            bootstrap_results.append({
                'System': sys_tag,
                'Comparison': f"{comp_name} vs AR(1)",
                'Delta_AUC_Mean': boot_diff['diff_mean'],
                'CI_Lower_95': boot_diff['ci_lower'],
                'CI_Upper_95': boot_diff['ci_upper'],
                'Bootstrap_p_value': boot_diff['p_value'],
                'Significant_at_005': bool(boot_diff['p_value'] < 0.05) if not np.isnan(boot_diff['p_value']) else False
            })

    df_clean = pd.DataFrame(clean_results)
    df_clean.to_csv(tables_dir / "validated_clean_benchmark.csv", index=False)
    df_boot = pd.DataFrame(bootstrap_results)
    df_boot.to_csv(tables_dir / "validated_clustered_bootstrap_significance.csv", index=False)
    print("  Clean benchmark and clustered bootstrap significance recorded.", flush=True)

    # -------------------------------------------------------------------------
    # BENCHMARK 2: Noise, Distortion, and Distractor Robustness
    # -------------------------------------------------------------------------
    print("\n>>> 2. Running Noise, Red Noise & Distractor Robustness...", flush=True)
    corrupt_results = []
    sys_may = MayHarvestingSystem()
    integrator_may = SDEIntegrator(sys_may, dt_sim=0.01, dt_obs=dt_obs)
    indicators, models, core_subset = get_core_methods(dt_obs=dt_obs)

    null_may = [integrator_may.simulate(t_max=120.0, mu_func=lambda t: 1.5, seed=1000 + r) for r in range(n_runs)]
    for m in models.values():
        m.fit([tr['x'] for tr in null_may], window_size=window_size, step=eval_step)

    ramp_may = [integrator_may.simulate(t_max=120.0, mu_func=lambda t: 1.5 + (3.2 - 1.5)*(t/120.0), seed=2000 + r, stop_on_collapse=True) for r in range(n_runs)]
    c_times = [tr['t_crit'] for tr in ramp_may]
    r_times = [tr['t'] for tr in ramp_may]
    n_times = [tr['t'] for tr in null_may]

    corruption_scenarios = [
        ('Clean_Reference', lambda x, s: x),
        ('Severe_Gaussian_Noise_SNR_0dB', lambda x, s: ObservationCorrupter.add_gaussian_noise(x, snr_db=0.0, seed=s)),
        ('Colored_Red_Noise_Gamma_0.7', lambda x, s: ObservationCorrupter.add_colored_red_noise(x, dt=dt_obs, gamma=0.7, sigma_eta=0.04, seed=s)),
        ('Missing_Data_Dropouts_50pct', lambda x, s: ObservationCorrupter.apply_random_dropout(x, drop_prob=0.5, seed=s)[0]),
        ('Sparse_Sampling_Dt_0.25', None),
        ('High_Dimensional_Distractors_D20', lambda x, s: ObservationCorrupter.append_distractors(x, n_distractors=20, dt=dt_obs, seed=s))
    ]

    for scen_name, corrupter_fn in corruption_scenarios:
        if scen_name == 'Sparse_Sampling_Dt_0.25':
            int_sparse = SDEIntegrator(sys_may, dt_sim=0.01, dt_obs=0.25)
            r_tr = [int_sparse.simulate(t_max=120.0, mu_func=lambda t: 1.5 + (3.2 - 1.5)*(t/120.0), seed=2000 + r, stop_on_collapse=True) for r in range(n_runs)]
            n_tr = [int_sparse.simulate(t_max=120.0, mu_func=lambda t: 1.5, seed=1000 + r) for r in range(n_runs)]
            r_c_times = [tr['t_crit'] for tr in r_tr]
            r_t_arr = [tr['t'] for tr in r_tr]
            n_t_arr = [tr['t'] for tr in n_tr]
            r_corrupt = [tr['x'] for tr in r_tr]
            n_corrupt = [tr['x'] for tr in n_tr]
            w_size = 15
        else:
            r_c_times = c_times
            r_t_arr = r_times
            n_t_arr = n_times
            w_size = window_size
            r_corrupt = [corrupter_fn(tr['x'], 3000 + i) for i, tr in enumerate(ramp_may)]
            n_corrupt = [corrupter_fn(tr['x'], 4000 + i) for i, tr in enumerate(null_may)]

        for m_name in ['AR(1)', 'Variance', 'PermutationEntropy', 'CEWF-Rank', 'CEWF-Mahalanobis', 'Adaptive-Bayesian-EWS']:
            if m_name in indicators:
                ind = indicators[m_name]
                r_sc = [ind.compute_rolling(x[:, 0] if x.ndim > 1 else x, window_size=w_size, step=eval_step) for x in r_corrupt]
                n_sc = [ind.compute_rolling(x[:, 0] if x.ndim > 1 else x, window_size=w_size, step=eval_step) for x in n_corrupt]
            else:
                m = models[m_name]
                r_sc = [m.predict_score(x, window_size=w_size, step=eval_step) for x in r_corrupt]
                n_sc = [m.predict_score(x, window_size=w_size, step=eval_step) for x in n_corrupt]

            traj_roc = compute_trajectory_level_roc_pr(
                r_sc, n_sc, r_t_arr, r_c_times, n_t_arr,
                safe_baseline_time=20.0, min_lead_time=2.0
            )

            corrupt_results.append({
                'Scenario': scen_name,
                'Method': m_name,
                'Trajectory_ROC_AUC': traj_roc['roc_auc'],
                'Trajectory_PR_AUC': traj_roc['pr_auc']
            })

    df_corrupt = pd.DataFrame(corrupt_results)
    df_corrupt.to_csv(tables_dir / "validated_stress_and_corruption_benchmark.csv", index=False)
    print("  Stress and corruption benchmark recorded.", flush=True)

    print("\n" + "=" * 70, flush=True)
    print("PHASE 3 VALIDATED BENCHMARK COMPLETE!", flush=True)
    print("=" * 70, flush=True)


if __name__ == "__main__":
    run_validated_experiments()
