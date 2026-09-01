"""
Deep Learning Early-Warning Baseline Benchmark (Bury et al. 2021 style).
Trains DeepEWS on independent training systems, evaluates on all 5 canonical systems,
and computes DeLong statistical significance tests against CEWF-Mahalanobis.
"""

import sys
from pathlib import Path
from typing import Dict, Any, List
import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from src.systems.may_harvesting import MayHarvestingSystem
from src.systems.fitzhugh_nagumo import FitzHughNagumoSystem
from src.systems.subcritical_pitchfork import SubcriticalPitchforkSystem
from src.systems.stommel_box import StommelBoxSystem
from src.systems.coupled_network import CoupledNetworkSystem
from src.simulation.integrator import SDEIntegrator
from src.indicators.univariate import (
    VarianceIndicator,
    AutocorrelationLag1Indicator,
    PermutationEntropyIndicator,
    SpectralReddeningIndicator
)
from src.models.mahalanobis_composite import MultiIndicatorMahalanobisModel
from src.models.deep_ews import DeepEWSModel
from src.evaluation.metrics import (
    compute_trajectory_level_roc_pr,
    delong_paired_test,
    clustered_bootstrap_auc_diff
)


def run_deep_ews_benchmark(n_runs: int = 25, dt_obs: float = 0.05) -> pd.DataFrame:
    print("=" * 70, flush=True)
    print("RUNNING DEEP LEARNING (BURY ET AL. 2021) BASELINE BENCHMARK", flush=True)
    print("=" * 70, flush=True)

    table_dir = Path("experiments/results/tables")
    table_dir.mkdir(parents=True, exist_ok=True)

    # 1. GENERATE TRAINING RUNS FOR DEEP EWS (SYS1 May Fold + SYS2 FHN Hopf)
    print("  Generating independent training runs on SYS1 and SYS2 ...", flush=True)
    int_train1 = SDEIntegrator(MayHarvestingSystem(), dt_sim=0.01, dt_obs=dt_obs)
    train_null1 = [int_train1.simulate(t_max=120.0, mu_func=lambda t: 1.5, seed=100 + r)['x'] for r in range(15)]
    train_ramp1 = [int_train1.simulate(t_max=120.0, mu_func=lambda t: 1.5 + (3.2 - 1.5)*(t/120.0), seed=200 + r, stop_on_collapse=True)['x'] for r in range(15)]

    int_train2 = SDEIntegrator(FitzHughNagumoSystem(), dt_sim=0.01, dt_obs=dt_obs)
    train_null2 = [int_train2.simulate(t_max=150.0, mu_func=lambda t: -0.5, seed=300 + r)['x'] for r in range(15)]
    train_ramp2 = [int_train2.simulate(t_max=150.0, mu_func=lambda t: -0.5 + (0.45 - (-0.5))*(t/150.0), seed=400 + r, stop_on_collapse=True)['x'] for r in range(15)]

    deep_model = DeepEWSModel(seed=42)
    print("  Training Bury et al. (2021) 1D-CNN on training trajectories ...", flush=True)
    deep_model.fit_supervised(
        train_null1 + train_null2,
        train_ramp1 + train_ramp2,
        window_size=50, step=4, epochs=15, lr=0.003
    )
    print("  DeepEWS model trained successfully.", flush=True)

    # 2. EVALUATE ON ALL 5 CANONICAL SYSTEMS
    systems = [
        ("SYS1_May_Fold", MayHarvestingSystem(), lambda t: 1.5 + (3.2 - 1.5)*(t/120.0), 120.0, lambda t: 1.5, 20.0),
        ("SYS2_FitzHughNagumo_Hopf", FitzHughNagumoSystem(), lambda t: -0.5 + (0.45 - (-0.5))*(t/150.0), 150.0, lambda t: -0.5, 20.0),
        ("SYS3_Subcritical_Pitchfork", SubcriticalPitchforkSystem(), lambda t: -0.6 + (0.1 - (-0.6))*(t/100.0), 100.0, lambda t: -0.6, 20.0),
        ("SYS4_Stommel_AMOC", StommelBoxSystem(), lambda t: 0.8 + (1.4 - 0.8)*(t/120.0), 120.0, lambda t: 0.8, 20.0),
        ("SYS5_Coupled_Network", CoupledNetworkSystem(n_nodes=10, network_type='erdos_renyi', seed=42), lambda t: 1.5 + (5.2 - 1.5)*(t/120.0), 120.0, lambda t: 1.5, 20.0)
    ]

    records = []

    for sys_name, sys_obj, ramp_fn, t_max, null_fn, safe_t in systems:
        print(f"\nEvaluating on {sys_name} ...", flush=True)
        integrator = SDEIntegrator(sys_obj, dt_sim=0.01, dt_obs=dt_obs)

        null_trajs = [integrator.simulate(t_max=t_max, mu_func=null_fn, seed=5000 + r) for r in range(n_runs)]
        ramp_trajs = [integrator.simulate(t_max=t_max, mu_func=ramp_fn, seed=6000 + r, stop_on_collapse=True) for r in range(n_runs)]

        r_times = [tr['t'] for tr in ramp_trajs]
        c_times = [tr['t_crit'] for tr in ramp_trajs]
        n_times = [tr['t'] for tr in null_trajs]

        r_xs = [tr['x'] for tr in ramp_trajs]
        n_xs = [tr['x'] for tr in null_trajs]
        r_1d = [tr['x'][:, 0] if tr['x'].ndim > 1 else tr['x'] for tr in ramp_trajs]
        n_1d = [tr['x'][:, 0] if tr['x'].ndim > 1 else tr['x'] for tr in null_trajs]

        # Evaluate DeepEWS
        deep_r = [deep_model.predict_score(x, window_size=50, step=4) for x in r_1d]
        deep_n = [deep_model.predict_score(x, window_size=50, step=4) for x in n_1d]

        m_deep = compute_trajectory_level_roc_pr(
            deep_r, deep_n, r_times, c_times, n_times, safe_baseline_time=safe_t, min_lead_time=2.0
        )

        # Evaluate CEWF-Mahalanobis for significance comparison
        core_subset = [
            VarianceIndicator(),
            AutocorrelationLag1Indicator(),
            PermutationEntropyIndicator(m=3, tau=1),
            SpectralReddeningIndicator(low_freq_fraction=0.15)
        ]
        mah_model = MultiIndicatorMahalanobisModel(indicators=core_subset, regularization=1e-3)
        mah_model.fit(n_xs, window_size=50, step=4)
        mah_r = [mah_model.predict_score(x, window_size=50, step=4) for x in r_xs]
        mah_n = [mah_model.predict_score(x, window_size=50, step=4) for x in n_xs]

        m_deep = compute_trajectory_level_roc_pr(
            deep_r, deep_n, r_times, c_times, n_times, safe_baseline_time=safe_t, min_lead_time=2.0
        )
        m_mah = compute_trajectory_level_roc_pr(
            mah_r, mah_n, r_times, c_times, n_times, safe_baseline_time=safe_t, min_lead_time=2.0
        )

        # Statistical significance tests
        boot_diff = clustered_bootstrap_auc_diff(
            deep_r, mah_r, deep_n, mah_n, r_times, c_times, n_times, n_boot=200, seed=42
        )

        # DeLong Paired Significance Test on robust trajectory peak scores
        def get_peaks(sc_list, t_list, c_list=None):
            pks = []
            for idx, (s_arr, t_arr) in enumerate(zip(sc_list, t_list)):
                if c_list is not None:
                    c_val = c_list[idx]
                    mask = (t_arr >= safe_t) & (t_arr <= c_val - 2.0) & (~np.isnan(s_arr))
                else:
                    mask = (t_arr >= safe_t) & (~np.isnan(s_arr))
                vals = s_arr[mask]
                pks.append(float(np.max(vals)) if len(vals) > 0 else 0.0)
            return pks

        deep_r_peaks = get_peaks(deep_r, r_times, c_times)
        deep_n_peaks = get_peaks(deep_n, n_times)
        mah_r_peaks = get_peaks(mah_r, r_times, c_times)
        mah_n_peaks = get_peaks(mah_n, n_times)

        y_true = np.array([1] * len(deep_r_peaks) + [0] * len(deep_n_peaks))
        y_deep = np.array(deep_r_peaks + deep_n_peaks)
        y_mah = np.array(mah_r_peaks + mah_n_peaks)
        delong_res = delong_paired_test(y_true, y_deep, y_mah)

        print(f"  DeepEWS ROC-AUC: {m_deep['roc_auc']:.4f} | PR-AUC: {m_deep['pr_auc']:.4f}", flush=True)
        print(f"  CEWF-Mahalanobis ROC-AUC: {m_mah['roc_auc']:.4f}", flush=True)
        print(f"  Delta AUC (DeepEWS - Mahalanobis): {boot_diff['diff_mean']:+.4f} | Bootstrap p-value: {boot_diff['p_value']:.4f} | DeLong p-value: {delong_res['p_value']:.4f}", flush=True)

        records.append({
            'System': sys_name,
            'DeepEWS_ROC_AUC': float(m_deep['roc_auc']),
            'DeepEWS_PR_AUC': float(m_deep['pr_auc']),
            'Mahalanobis_ROC_AUC': float(m_mah['roc_auc']),
            'Delta_AUC': float(boot_diff['diff_mean']),
            'CI_Lower': float(boot_diff['ci_lower']),
            'CI_Upper': float(boot_diff['ci_upper']),
            'Bootstrap_p_value': float(boot_diff['p_value']),
            'DeLong_p_value': float(delong_res['p_value']),
            'Significance': 'SIGNIFICANT' if delong_res['p_value'] < 0.05 else 'NOT_SIGNIFICANT'
        })

    df = pd.DataFrame(records)
    out_csv = table_dir / "deep_ews_benchmark.csv"
    df.to_csv(out_csv, index=False)
    print(f"\nSaved Deep EWS benchmark table to {out_csv}", flush=True)
    return df


if __name__ == '__main__':
    df_deep = run_deep_ews_benchmark(n_runs=25)
    print(df_deep.to_string())
