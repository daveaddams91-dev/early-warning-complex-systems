"""
Phase 4: Information Diversity, False Consensus, and Indicator Ecology.
Implements:
1. Effective Dimensionality / Diversity Ratio K_eff of early-warning indicator suites.
2. Adversarial False Consensus Experiment: Non-collapsing shock exciting all energy moments.
3. Redundant Ensemble vs Complementary Diversity Ensemble Benchmark.
"""

import sys
from pathlib import Path
from typing import Dict, Any, List, Tuple
import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from src.systems.may_harvesting import MayHarvestingSystem
from src.simulation.integrator import SDEIntegrator
from src.indicators.univariate import (
    VarianceIndicator,
    AutocorrelationLag1Indicator,
    SkewnessIndicator,
    KurtosisIndicator,
    PermutationEntropyIndicator,
    SpectralReddeningIndicator
)
from src.evaluation.metrics import compute_trajectory_level_roc_pr, compute_operational_lead_time_distribution


def calculate_effective_diversity(indicator_matrix: np.ndarray) -> Tuple[float, np.ndarray]:
    """
    Computes the effective number of independent indicator dimensions K_eff
    via the participation ratio of the indicator correlation matrix:
        K_eff = (Tr(R))^2 / Tr(R^2) = (sum lambda_i)^2 / sum(lambda_i^2)
    """
    # Remove NaNs
    valid = indicator_matrix[~np.isnan(indicator_matrix).any(axis=1)]
    if len(valid) < 10:
        return 1.0, np.eye(indicator_matrix.shape[1])
        
    corr = np.corrcoef(valid, rowvar=False)
    evals = np.linalg.eigvalsh(corr)
    evals = np.maximum(evals, 0.0)
    sum_e = np.sum(evals)
    sum_sq_e = np.sum(evals**2)
    k_eff = float((sum_e**2) / (sum_sq_e + 1e-8))
    return k_eff, corr


def run_false_consensus_and_diversity_experiment(n_runs: int = 20, dt_obs: float = 0.05) -> pd.DataFrame:
    """
    EXP-014: Information Diversity & Adversarial False Consensus.
    1. Simulates an adversarial non-collapsing transient pulse shock that inflates all energy moments.
    2. Compares a Redundant Ensemble (5 energy-related indicators) vs a Diverse Ensemble (3 orthogonal indicators).
    3. Measures False Alarm Rate under the shock and True Warning Rate under genuine fold collapse.
    """
    print("=" * 70, flush=True)
    print("RUNNING EXP-014: INFORMATION DIVERSITY & FALSE CONSENSUS", flush=True)
    print("=" * 70, flush=True)

    out_dir = Path("results/validated/tables")
    out_dir.mkdir(parents=True, exist_ok=True)

    sys_may = MayHarvestingSystem()
    integrator = SDEIntegrator(sys_may, dt_sim=0.01, dt_obs=dt_obs)

    # 1. Null Baseline
    null_trajs = [integrator.simulate(t_max=120.0, mu_func=lambda t: 1.5, seed=1000 + r) for r in range(n_runs)]
    # 2. Genuine Bifurcation Ramp (True Positive Case)
    ramp_trajs = [integrator.simulate(t_max=120.0, mu_func=lambda t: 1.5 + (3.2 - 1.5)*(t/120.0), seed=2000 + r, stop_on_collapse=True) for r in range(n_runs)]
    # 3. Adversarial False Consensus: Sharp transient pulse shock at t in [30, 35]s, but system is stable
    shock_fn = lambda t: 1.5 + (1.2 if 30.0 <= t <= 35.0 else 0.0)
    shock_trajs = [integrator.simulate(t_max=120.0, mu_func=shock_fn, seed=3000 + r) for r in range(n_runs)]

    c_times = [tr['t_crit'] for tr in ramp_trajs]
    r_times = [tr['t'] for tr in ramp_trajs]
    n_times = [tr['t'] for tr in null_trajs]
    s_times = [tr['t'] for tr in shock_trajs]

    # Indicators
    ind_var = VarianceIndicator()
    ind_skew = SkewnessIndicator()
    ind_kurt = KurtosisIndicator()
    ind_ar1 = AutocorrelationLag1Indicator()
    ind_spec = SpectralReddeningIndicator(low_freq_fraction=0.15)
    ind_pe = PermutationEntropyIndicator(m=3, tau=1)

    # Compute rolling indicators on null data to assess baseline diversity
    null_feats = []
    for tr in null_trajs:
        x_1d = tr['x'][:, 0]
        v = ind_var.compute_rolling(x_1d, window_size=50, step=4)
        sk = ind_skew.compute_rolling(x_1d, window_size=50, step=4)
        kt = ind_kurt.compute_rolling(x_1d, window_size=50, step=4)
        ar = ind_ar1.compute_rolling(x_1d, window_size=50, step=4)
        sp = ind_spec.compute_rolling(x_1d, window_size=50, step=4)
        null_feats.append(np.column_stack([v, sk, kt, ar, sp]))

    flat_null = np.concatenate(null_feats, axis=0)

    # Redundant set: Variance, Skewness, Kurtosis (all 3 are higher-order moments of the same distribution)
    k_eff_redundant, corr_red = calculate_effective_diversity(flat_null[:, :3])
    # Diverse set: Variance (energy), AR(1) (temporal memory), SpectralReddening (frequency spectrum)
    k_eff_diverse, corr_div = calculate_effective_diversity(flat_null[:, [0, 3, 4]])

    print(f"  Redundant Suite Effective Dimensions K_eff: {k_eff_redundant:.3f} / 3.0")
    print(f"  Diverse Suite Effective Dimensions K_eff:     {k_eff_diverse:.3f} / 3.0")

    # Evaluate Ensembles:
    # Suite A: Redundant Ensemble (Averages Variance, Skewness, Kurtosis)
    # Suite B: Diverse Complementary Ensemble (Requires concordant agreement between Variance, AR1, and Spectral Reddening)
    results = []

    for name, suite_idx, is_diverse in [('Redundant_Moment_Ensemble', [0, 1, 2], False), ('Diverse_Complementary_Ensemble', [0, 3, 4], True)]:
        # Evaluate on Genuine Ramp
        ramp_scores = []
        null_scores = []
        shock_scores = []

        for tr_r, tr_n, tr_s in zip(ramp_trajs, null_trajs, shock_trajs):
            # Ramp
            xr = tr_r['x'][:, 0]
            vr = ind_var.compute_rolling(xr, window_size=50, step=4)
            skr = ind_skew.compute_rolling(xr, window_size=50, step=4)
            ktr = ind_kurt.compute_rolling(xr, window_size=50, step=4)
            arr = ind_ar1.compute_rolling(xr, window_size=50, step=4)
            spr = ind_spec.compute_rolling(xr, window_size=50, step=4)
            all_r = [vr, skr, ktr, arr, spr]

            # Null
            xn = tr_n['x'][:, 0]
            vn = ind_var.compute_rolling(xn, window_size=50, step=4)
            skn = ind_skew.compute_rolling(xn, window_size=50, step=4)
            ktn = ind_kurt.compute_rolling(xn, window_size=50, step=4)
            arn = ind_ar1.compute_rolling(xn, window_size=50, step=4)
            spn = ind_spec.compute_rolling(xn, window_size=50, step=4)
            all_n = [vn, skn, ktn, arn, spn]

            # Shock
            xs = tr_s['x'][:, 0]
            vs = ind_var.compute_rolling(xs, window_size=50, step=4)
            sks = ind_skew.compute_rolling(xs, window_size=50, step=4)
            kts = ind_kurt.compute_rolling(xs, window_size=50, step=4)
            ars = ind_ar1.compute_rolling(xs, window_size=50, step=4)
            sps = ind_spec.compute_rolling(xs, window_size=50, step=4)
            all_s = [vs, sks, kts, ars, sps]

            # Normalize against null
            norm_r = []
            norm_n = []
            norm_s = []
            for k in suite_idx:
                mu_k = np.nanmean(all_n[k])
                sig_k = np.nanstd(all_n[k]) + 1e-6
                norm_r.append(np.maximum(0.0, (all_r[k] - mu_k) / sig_k))
                norm_n.append(np.maximum(0.0, (all_n[k] - mu_k) / sig_k))
                norm_s.append(np.maximum(0.0, (all_s[k] - mu_k) / sig_k))

            if not is_diverse:
                # Naive unweighted sum: vulnerable to false consensus when all moments spike together
                sc_r = np.mean(norm_r, axis=0)
                sc_n = np.mean(norm_n, axis=0)
                sc_s = np.mean(norm_s, axis=0)
            else:
                # Geometric concordance: requires all orthogonal channels to exhibit elevation
                # Geometric mean = (prod x_i)^(1/K): drops to 0 if AR(1) or Spectral Reddening does NOT confirm
                sc_r = (norm_r[0] * norm_r[1] * norm_r[2]) ** (1.0 / 3.0)
                sc_n = (norm_n[0] * norm_n[1] * norm_n[2]) ** (1.0 / 3.0)
                sc_s = (norm_s[0] * norm_s[1] * norm_s[2]) ** (1.0 / 3.0)

            ramp_scores.append(sc_r)
            null_scores.append(sc_n)
            shock_scores.append(sc_s)

        # Genuine Ramp Trajectory ROC
        roc_ramp = compute_trajectory_level_roc_pr(ramp_scores, null_scores, r_times, c_times, n_times, safe_baseline_time=20.0, min_lead_time=2.0)['roc_auc']

        # Threshold at null 95th percentile
        flat_n = np.concatenate([s[400:][~np.isnan(s[400:])] for s in null_scores])
        th = float(np.percentile(flat_n, 95))

        # False alarm rate under adversarial shock (system does NOT collapse, yet shock occurs)
        shock_alarms = sum([np.nanmax(s[400:]) >= th for s in shock_scores]) / n_runs
        true_alarms = sum([np.nanmax(s[400:]) >= th for s in ramp_scores]) / n_runs

        results.append({
            'Ensemble_Type': name,
            'Effective_Diversity_K_eff': k_eff_diverse if is_diverse else k_eff_redundant,
            'Genuine_Ramp_ROC_AUC': roc_ramp,
            'True_Alarm_Rate_Ramp': true_alarms,
            'Adversarial_Shock_False_Alarm_Rate': shock_alarms,
            'Resistance_to_False_Consensus': 'HIGH (Immune)' if shock_alarms <= 0.20 else 'LOW (Vulnerable to False Consensus)'
        })

    df_div = pd.DataFrame(results)
    df_div.to_csv(out_dir / "phase4_information_diversity_results.csv", index=False)
    print("  Information diversity results saved to results/validated/tables/phase4_information_diversity_results.csv", flush=True)
    return df_div


if __name__ == '__main__':
    df = run_false_consensus_and_diversity_experiment(n_runs=15)
    print(df.to_string())
