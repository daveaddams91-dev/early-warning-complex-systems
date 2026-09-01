"""
Ablation Study: Mechanistic Investigation of the AMOC (SYS-4) Failure.
Tests individual indicators and transforms on the Stommel 2-Box model to isolate
why CSD collapses and whether mathematical reparametrizations recover signal.
"""

import sys
from pathlib import Path
from typing import Dict, Any, List, Tuple
import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from src.systems.stommel_box import StommelBoxSystem
from src.simulation.integrator import SDEIntegrator
from src.indicators.univariate import (
    VarianceIndicator,
    AutocorrelationLag1Indicator,
    PermutationEntropyIndicator,
    SpectralReddeningIndicator
)
from src.indicators.multivariate import (
    MahalanobisDistanceIndicator,
    PCA1VarianceIndicator
)
from src.evaluation.metrics import compute_trajectory_level_roc_pr


def apply_transform(x: np.ndarray, transform_name: str) -> np.ndarray:
    """
    Applies the specified signal transform prior to indicator computation.
    Supports 1D (scalar) and 2D arrays.
    """
    x_arr = np.asarray(x, dtype=np.float64)
    
    if transform_name == "raw":
        return x_arr

    elif transform_name == "log_transform":
        # Shift to positive domain if necessary
        min_val = np.min(x_arr, axis=0, keepdims=True)
        shifted = x_arr - min_val + 1e-2
        return np.log(shifted)

    elif transform_name == "first_difference":
        diff = np.diff(x_arr, axis=0)
        # Pad first row with zero to maintain length
        first_row = np.zeros((1, x_arr.shape[1])) if x_arr.ndim > 1 else np.zeros(1)
        return np.vstack([first_row, diff]) if x_arr.ndim > 1 else np.concatenate([first_row, diff])

    elif transform_name == "local_detrend":
        # Rolling local detrending with small window (e.g. 20 steps)
        w = 20
        n = len(x_arr)
        detrended = np.zeros_like(x_arr)
        for i in range(n):
            start = max(0, i - w + 1)
            mean_val = np.mean(x_arr[start : i + 1], axis=0)
            detrended[i] = x_arr[i] - mean_val
        return detrended

    elif transform_name == "linearizing_reparam":
        # Monotonic quadratic reparametrization:
        # In Stommel box model, the advective drag is -|T - S|T = -q T = -T^2 + TS.
        # For scalar T, the dominant non-linear drag is quadratic (-T^2).
        # Transform y = T^2 linearizes the effective potential gradient dV/dT ~ T^2.
        # For 2D (T, S), the physical overturning flow is q = T - S.
        if x_arr.ndim > 1 and x_arr.shape[1] >= 2:
            q = x_arr[:, 0] - x_arr[:, 1]  # Overturning circulation flux
            # Return reconstructed 2D space: [q, T]
            return np.column_stack([q, x_arr[:, 0]])
        else:
            # For scalar T alone, apply quadratic power reparametrization T^2
            return x_arr ** 2

    else:
        raise ValueError(f"Unknown transform: {transform_name}")


def run_amoc_ablation(n_runs: int = 25, dt_obs: float = 0.05) -> pd.DataFrame:
    """
    Executes full (indicator x transform) ablation on SYS-4 Stommel AMOC.
    """
    print("=" * 70, flush=True)
    print("RUNNING MECHANISTIC AMOC (SYS-4) FAILURE ABLATION EXPERIMENT", flush=True)
    print("=" * 70, flush=True)

    out_dir_tables = Path("experiments/results/tables")
    out_dir_tables.mkdir(parents=True, exist_ok=True)

    sys_stommel = StommelBoxSystem()
    integrator = SDEIntegrator(sys_stommel, dt_sim=0.01, dt_obs=dt_obs)

    # 1. Simulate paired trajectories
    print(f"  Simulating {n_runs} null and {n_runs} ramp trajectories on Stommel AMOC ...", flush=True)
    null_trajs = [
        integrator.simulate(t_max=120.0, mu_func=lambda t: 0.8, seed=1000 + r)
        for r in range(n_runs)
    ]
    ramp_trajs = [
        integrator.simulate(
            t_max=120.0,
            mu_func=lambda t: 0.8 + (1.4 - 0.8) * (t / 120.0),
            seed=2000 + r,
            stop_on_collapse=True
        )
        for r in range(n_runs)
    ]

    c_times = [tr['t_crit'] for tr in ramp_trajs]
    r_times = [tr['t'] for tr in ramp_trajs]
    n_times = [tr['t'] for tr in null_trajs]

    transforms = [
        "raw",
        "log_transform",
        "first_difference",
        "local_detrend",
        "linearizing_reparam"
    ]

    indicators = [
        ("Variance", VarianceIndicator(), False),
        ("AR(1)", AutocorrelationLag1Indicator(), False),
        ("PermutationEntropy", PermutationEntropyIndicator(m=3, tau=1), False),
        ("SpectralReddening", SpectralReddeningIndicator(low_freq_fraction=0.15), False),
        ("MahalanobisDist_2D", MahalanobisDistanceIndicator(), True),
        ("PCA1_Variance_2D", PCA1VarianceIndicator(), True),
    ]

    results = []

    for t_name in transforms:
        print(f"\n--- Testing Transform: {t_name} ---", flush=True)
        # Apply transform to trajectories
        null_trans_2d = [apply_transform(tr['x'], t_name) for tr in null_trajs]
        ramp_trans_2d = [apply_transform(tr['x'], t_name) for tr in ramp_trajs]
        null_trans_1d = [apply_transform(tr['x'][:, 0], t_name) for tr in null_trajs]
        ramp_trans_1d = [apply_transform(tr['x'][:, 0], t_name) for tr in ramp_trajs]

        for ind_name, ind_obj, is_multi in indicators:
            r_data = ramp_trans_2d if is_multi else ramp_trans_1d
            n_data = null_trans_2d if is_multi else null_trans_1d

            # Compute rolling indicator on each trajectory
            ramp_scores = [ind_obj.compute_rolling(x, window_size=50, step=4) for x in r_data]
            null_scores = [ind_obj.compute_rolling(x, window_size=50, step=4) for x in n_data]

            # Evaluate trajectory-level ROC-AUC & PR-AUC
            metrics = compute_trajectory_level_roc_pr(
                ramp_scores, null_scores, r_times, c_times, n_times,
                safe_baseline_time=20.0, min_lead_time=2.0
            )

            auc = metrics['roc_auc']
            pr_auc = metrics['pr_auc']
            print(f"  {ind_name:<22} | Transform: {t_name:<20} | ROC-AUC: {auc:.4f} | PR-AUC: {pr_auc:.4f}", flush=True)

            results.append({
                'System': 'SYS4_Stommel_AMOC',
                'Indicator': ind_name,
                'Transform': t_name,
                'ROC_AUC': float(auc),
                'PR_AUC': float(pr_auc),
                'Is_Multivariate': is_multi
            })

    # Diagnostic benchmark: What if the observer directly monitors overturning circulation q = T - S?
    print("\n--- Diagnostic Physical Coordinate: Overturning Circulation q = T - S ---", flush=True)
    null_q = [tr['x'][:, 0] - tr['x'][:, 1] for tr in null_trajs]
    ramp_q = [tr['x'][:, 0] - tr['x'][:, 1] for tr in ramp_trajs]

    q_var = VarianceIndicator().compute_rolling
    ramp_q_var = [VarianceIndicator().compute_rolling(q, window_size=50, step=4) for q in ramp_q]
    null_q_var = [VarianceIndicator().compute_rolling(q, window_size=50, step=4) for q in null_q]
    m_q = compute_trajectory_level_roc_pr(
        ramp_q_var, null_q_var, r_times, c_times, n_times,
        safe_baseline_time=20.0, min_lead_time=2.0
    )
    print(f"  Variance on Overturning Circulation q(t) | ROC-AUC: {m_q['roc_auc']:.4f} | PR-AUC: {m_q['pr_auc']:.4f}", flush=True)

    results.append({
        'System': 'SYS4_Stommel_AMOC',
        'Indicator': 'Variance(q=T-S)',
        'Transform': 'physical_circulation_coordinate',
        'ROC_AUC': float(m_q['roc_auc']),
        'PR_AUC': float(m_q['pr_auc']),
        'Is_Multivariate': False
    })

    df = pd.DataFrame(results)
    out_csv = out_dir_tables / "amoc_failure_ablation.csv"
    df.to_csv(out_csv, index=False)
    print(f"\nSaved ablation table to {out_csv}", flush=True)
    return df


if __name__ == '__main__':
    df_res = run_amoc_ablation(n_runs=25)
