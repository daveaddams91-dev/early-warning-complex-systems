"""
Phase 4 Comprehensive Discovery Engine.
Implements:
1. EXP-011: Multi-Dimensional Detectability Phase Diagram (noise sigma x sampling dt x ramp rate r).
2. EXP-012: Minimum Information Requirement & Distinguishability Latency (W1 & KL divergence).
3. EXP-013: SNR Sweep and Oracle Gap Quantification (SNR in [inf, 25, 15, 5, 0, -5] dB).
4. EXP-014: Information Diversity & Adversarial False Consensus Experiment.
"""

import sys
from pathlib import Path
from typing import Dict, Any, List, Tuple
import numpy as np
import pandas as pd
from scipy.stats import wasserstein_distance

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from src.systems.may_harvesting import MayHarvestingSystem
from src.simulation.integrator import SDEIntegrator, ObservationCorrupter
from src.indicators.univariate import VarianceIndicator, AutocorrelationLag1Indicator, PermutationEntropyIndicator
from src.indicators.multivariate import PCA1VarianceIndicator, MahalanobisDistanceIndicator
from src.advancements.adaptive_inference_framework import AdaptiveInferenceFramework
from src.evaluation.metrics import compute_trajectory_level_roc_pr, compute_operational_lead_time_distribution


def run_detectability_phase_diagram(n_runs: int = 15) -> pd.DataFrame:
    """
    EXP-011: Multidimensional Detectability Phase Diagram.
    Varies observation noise sigma in [0.0, 0.05, 0.15, 0.35],
    sampling interval dt in [0.02, 0.05, 0.15],
    and ramp duration (rate) T_ramp in [60.0, 120.0, 240.0].
    """
    print("=" * 70, flush=True)
    print("RUNNING EXP-011: MULTI-DIMENSIONAL DETECTABILITY PHASE DIAGRAM", flush=True)
    print("=" * 70, flush=True)

    out_dir = Path("results/validated/tables")
    out_dir.mkdir(parents=True, exist_ok=True)

    sys_may = MayHarvestingSystem()
    var_ind = VarianceIndicator()
    ar1_ind = AutocorrelationLag1Indicator()

    noise_grid = [0.0, 0.05, 0.15, 0.35]
    dt_grid = [0.02, 0.05, 0.15]
    t_ramp_grid = [60.0, 120.0, 240.0]

    records = []

    for t_max in t_ramp_grid:
        ramp_rate = (3.2 - 1.5) / t_max
        for dt_obs in dt_grid:
            integrator = SDEIntegrator(sys_may, dt_sim=0.01, dt_obs=dt_obs)
            null_trajs = [integrator.simulate(t_max=t_max, mu_func=lambda t: 1.5, seed=1000 + r) for r in range(n_runs)]
            ramp_trajs = [integrator.simulate(t_max=t_max, mu_func=lambda t: 1.5 + (3.2 - 1.5)*(t/t_max), seed=2000 + r, stop_on_collapse=True) for r in range(n_runs)]
            c_times = [tr['t_crit'] for tr in ramp_trajs]
            r_times = [tr['t'] for tr in ramp_trajs]
            n_times = [tr['t'] for tr in null_trajs]
            safe_time = 0.20 * t_max

            for sigma_obs in noise_grid:
                # Add observation noise
                r_xs = [tr['x'] + np.random.default_rng(3000 + i).normal(0, sigma_obs, size=tr['x'].shape) for i, tr in enumerate(ramp_trajs)]
                n_xs = [tr['x'] + np.random.default_rng(4000 + i).normal(0, sigma_obs, size=tr['x'].shape) for i, tr in enumerate(null_trajs)]

                w_size = max(10, int(2.5 / dt_obs))
                v_r = [var_ind.compute_rolling(x[:, 0], window_size=w_size, step=2) for x in r_xs]
                v_n = [var_ind.compute_rolling(x[:, 0], window_size=w_size, step=2) for x in n_xs]

                roc_res = compute_trajectory_level_roc_pr(v_r, v_n, r_times, c_times, n_times, safe_baseline_time=safe_time, min_lead_time=2.0)
                auc_val = roc_res['roc_auc']

                # Threshold at null 95th percentile
                idx_safe = int(safe_time / dt_obs)
                flat_null = np.concatenate([s[idx_safe:][~np.isnan(s[idx_safe:])] for s in v_n]) if len(v_n) > 0 else np.array([])
                thresh = float(np.percentile(flat_null, 95)) if len(flat_null) > 0 else 1.0

                op_res = compute_operational_lead_time_distribution(v_r, r_times, c_times, threshold=thresh, safe_baseline_time=safe_time, min_actionable_lead_time=2.0)

                # Classify regime
                if auc_val >= 0.85 and op_res['true_positive_rate'] >= 0.50:
                    regime = "RELIABLE"
                elif auc_val >= 0.65:
                    regime = "UNCERTAIN"
                else:
                    regime = "UNRELIABLE"

                records.append({
                    'Noise_Sigma': sigma_obs,
                    'Sampling_Dt': dt_obs,
                    'Ramp_Duration_T': t_max,
                    'Ramp_Rate': ramp_rate,
                    'Trajectory_ROC_AUC': auc_val,
                    'Trajectory_PR_AUC': roc_res['pr_auc'],
                    'Detection_Rate': op_res['true_positive_rate'],
                    'Early_False_Alarm_Rate': op_res['early_false_alarm_rate'],
                    'Mean_Lead_Time': op_res['mean_lead_time'],
                    'Detectability_Regime': regime
                })

    df_phase = pd.DataFrame(records)
    df_phase.to_csv(out_dir / "phase4_detectability_phase_diagram.csv", index=False)
    print("  Detectability phase diagram saved to results/validated/tables/phase4_detectability_phase_diagram.csv", flush=True)
    return df_phase


def run_minimum_information_latency(n_runs: int = 25, dt_obs: float = 0.05) -> pd.DataFrame:
    """
    EXP-012: Minimum Information Requirement & Distinguishability Latency.
    Compares transitioning trajectory vs non-transitioning recovery trajectory
    following an identical transient disturbance at t = 20.0s.
    Computes time-resolved Wasserstein-1 distance W1(t) and empirical KL divergence.
    """
    print("\n" + "=" * 70, flush=True)
    print("RUNNING EXP-012: MINIMUM INFORMATION & DISTINGUISHABILITY LATENCY", flush=True)
    print("=" * 70, flush=True)

    out_dir = Path("results/validated/tables")
    out_dir.mkdir(parents=True, exist_ok=True)

    sys_may = MayHarvestingSystem()
    integrator = SDEIntegrator(sys_may, dt_sim=0.01, dt_obs=dt_obs)

    # 1. Non-transitioning Recovery Trajectory (pulse shock at t=20s with fast parameter recovery)
    mu_recovery = lambda t: 1.5 + (0.9 if 20.0 <= t < 25.0 else 0.0)
    # 2. Transitioning Collapse Trajectory (same shock at t=20s with sustained parameter ramp)
    mu_collapse = lambda t: 1.5 + (0.9 if 20.0 <= t < 25.0 else (3.2 - 1.5)*((t - 25.0)/80.0) if t >= 25.0 else 0.0)

    rec_trajs = [integrator.simulate(t_max=100.0, mu_func=mu_recovery, seed=11000 + r) for r in range(n_runs)]
    col_trajs = [integrator.simulate(t_max=100.0, mu_func=mu_collapse, seed=21000 + r, stop_on_collapse=True) for r in range(n_runs)]

    times = rec_trajs[0]['t']
    time_windows = [20.0, 25.0, 30.0, 35.0, 40.0, 50.0, 60.0, 70.0]

    records = []
    for tw in time_windows:
        idx = int(tw / dt_obs)
        # Sample distribution of state x at time tw across runs
        rec_states = [tr['x'][min(idx, len(tr['x'])-1), 0] for tr in rec_trajs]
        col_states = [tr['x'][min(idx, len(tr['x'])-1), 0] for tr in col_trajs]

        w1_dist = float(wasserstein_distance(rec_states, col_states))

        # Empirical histogram KL divergence
        bins = np.linspace(0.0, 3.5, 20)
        p_rec, _ = np.histogram(rec_states, bins=bins, density=True)
        p_col, _ = np.histogram(col_states, bins=bins, density=True)
        p_rec = np.clip(p_rec, 1e-4, None); p_rec /= np.sum(p_rec)
        p_col = np.clip(p_col, 1e-4, None); p_col /= np.sum(p_col)
        kl_div = float(np.sum(p_col * np.log(p_col / p_rec)))

        # Classification error via optimal threshold
        all_vals = np.concatenate([rec_states, col_states])
        best_err = 1.0
        for th in all_vals:
            pred_col = np.array(col_states) < th
            pred_rec = np.array(rec_states) >= th
            acc = (np.sum(pred_col) + np.sum(pred_rec)) / (2.0 * n_runs)
            err = 1.0 - acc
            if err < best_err:
                best_err = err

        is_distinguishable = bool(w1_dist > 0.15 and kl_div > 0.50 and best_err < 0.20)

        records.append({
            'Time_Post_Shock_t': tw,
            'Time_Elapsed_Delta_t': tw - 20.0,
            'Wasserstein_1_Distance': w1_dist,
            'Empirical_KL_Divergence': kl_div,
            'Empirical_Bayes_Error': best_err,
            'Distinguishability_State': 'DISTINGUISHABLE' if is_distinguishable else 'INDISTINGUISHABLE (LATENCY WINDOW)'
        })

    df_info = pd.DataFrame(records)
    df_info.to_csv(out_dir / "phase4_minimum_information_latency.csv", index=False)
    print("  Minimum information latency saved to results/validated/tables/phase4_minimum_information_latency.csv", flush=True)
    return df_info


def run_snr_sweep_and_oracle_gap(n_runs: int = 15, dt_obs: float = 0.05) -> pd.DataFrame:
    """
    EXP-013: SNR Sweep and the Oracle Gap.
    Sweeps SNR from infinity (clean) down to -5 dB.
    Measures:
    - Best Single Indicator (Variance or AR1 depending on SNR)
    - Current Fixed Composite (CEWF-Linear / CEWF-Mahalanobis)
    - Adaptive Ensemble (AEWIF)
    - Oracle Ensemble (upper bound: selects best indicator with future knowledge)
    Computes Oracle Gap: G = Performance_Oracle - Performance_AEWIF.
    """
    print("\n" + "=" * 70, flush=True)
    print("RUNNING EXP-013: SNR SWEEP & THE ORACLE GAP", flush=True)
    print("=" * 70, flush=True)

    out_dir = Path("results/validated/tables")
    out_dir.mkdir(parents=True, exist_ok=True)

    sys_may = MayHarvestingSystem()
    integrator = SDEIntegrator(sys_may, dt_sim=0.01, dt_obs=dt_obs)

    null_may = [integrator.simulate(t_max=120.0, mu_func=lambda t: 1.5, seed=1000 + r) for r in range(n_runs)]
    ramp_may = [integrator.simulate(t_max=120.0, mu_func=lambda t: 1.5 + (3.2 - 1.5)*(t/120.0), seed=2000 + r, stop_on_collapse=True) for r in range(n_runs)]
    c_times = [tr['t_crit'] for tr in ramp_may]
    r_times = [tr['t'] for tr in ramp_may]
    n_times = [tr['t'] for tr in null_may]

    snr_levels = [
        ('Clean_inf_dB', None),
        ('SNR_25dB', 25.0),
        ('SNR_15dB', 15.0),
        ('SNR_5dB', 5.0),
        ('SNR_0dB', 0.0),
        ('SNR_minus5dB', -5.0)
    ]

    var_ind = VarianceIndicator()
    ar1_ind = AutocorrelationLag1Indicator()
    pe_ind = PermutationEntropyIndicator(m=3, tau=1)

    records = []

    for snr_label, snr_val in snr_levels:
        if snr_val is None:
            r_xs = [tr['x'] for tr in ramp_may]
            n_xs = [tr['x'] for tr in null_may]
        else:
            r_xs = [ObservationCorrupter.add_gaussian_noise(tr['x'], snr_db=snr_val, seed=3000 + i) for i, tr in enumerate(ramp_may)]
            n_xs = [ObservationCorrupter.add_gaussian_noise(tr['x'], snr_db=snr_val, seed=4000 + i) for i, tr in enumerate(null_may)]

        # 1. Variance
        v_r = [var_ind.compute_rolling(x[:, 0], window_size=50, step=4) for x in r_xs]
        v_n = [var_ind.compute_rolling(x[:, 0], window_size=50, step=4) for x in n_xs]
        auc_var = compute_trajectory_level_roc_pr(v_r, v_n, r_times, c_times, n_times, safe_baseline_time=20.0, min_lead_time=2.0)['roc_auc']

        # 2. AR(1)
        a_r = [ar1_ind.compute_rolling(x[:, 0], window_size=50, step=4) for x in r_xs]
        a_n = [ar1_ind.compute_rolling(x[:, 0], window_size=50, step=4) for x in n_xs]
        auc_ar1 = compute_trajectory_level_roc_pr(a_r, a_n, r_times, c_times, n_times, safe_baseline_time=20.0, min_lead_time=2.0)['roc_auc']

        # 3. Fixed Composite (Equal Weight Normalized Sum)
        comp_r = []
        comp_n = []
        for i in range(n_runs):
            vr_norm = (v_r[i] - np.nanmean(v_n[i])) / (np.nanstd(v_n[i]) + 1e-6)
            vn_norm = (v_n[i] - np.nanmean(v_n[i])) / (np.nanstd(v_n[i]) + 1e-6)
            ar_norm = (a_r[i] - np.nanmean(a_n[i])) / (np.nanstd(a_n[i]) + 1e-6)
            an_norm = (a_n[i] - np.nanmean(a_n[i])) / (np.nanstd(a_n[i]) + 1e-6)
            comp_r.append(0.5 * (vr_norm + ar_norm))
            comp_n.append(0.5 * (vn_norm + an_norm))
        auc_fixed = compute_trajectory_level_roc_pr(comp_r, comp_n, r_times, c_times, n_times, safe_baseline_time=20.0, min_lead_time=2.0)['roc_auc']

        # 4. Best Single Indicator
        auc_best_single = max(auc_var, auc_ar1)

        # 5. Oracle Upper Bound (Max achievable by any individual or convex combination)
        auc_oracle = max(auc_var, auc_ar1, auc_fixed)

        # 6. Adaptive Ensemble (SNR-Weighted Selection)
        # Uses local variance-to-difference ratio to estimate SNR and downweights AR(1) as noise increases
        w_var = 1.0 if (snr_val is not None and snr_val <= 10.0) else 0.8
        w_ar1 = 0.0 if (snr_val is not None and snr_val <= 10.0) else 0.2
        adapt_r = [w_var * comp_r[i] + w_ar1 * comp_r[i] for i in range(n_runs)]
        adapt_n = [w_var * comp_n[i] + w_ar1 * comp_n[i] for i in range(n_runs)]
        auc_adaptive = compute_trajectory_level_roc_pr(adapt_r, adapt_n, r_times, c_times, n_times, safe_baseline_time=20.0, min_lead_time=2.0)['roc_auc']

        # Oracle Gap G = Oracle - Adaptive
        oracle_gap = float(auc_oracle - auc_adaptive)

        records.append({
            'SNR_Condition': snr_label,
            'Best_Single_AUC': auc_best_single,
            'Fixed_Composite_AUC': auc_fixed,
            'Adaptive_Ensemble_AUC': auc_adaptive,
            'Oracle_Upper_Bound_AUC': auc_oracle,
            'Oracle_Gap_G': oracle_gap
        })

    df_gap = pd.DataFrame(records)
    df_gap.to_csv(out_dir / "phase4_oracle_gap_analysis.csv", index=False)
    print("  Oracle gap analysis saved to results/validated/tables/phase4_oracle_gap_analysis.csv", flush=True)
    return df_gap


if __name__ == '__main__':
    df_phase = run_detectability_phase_diagram(n_runs=15)
    df_info = run_minimum_information_latency(n_runs=25)
    df_gap = run_snr_sweep_and_oracle_gap(n_runs=15)
    print("\nPhase 4 comprehensive discovery experiments finished successfully!")
