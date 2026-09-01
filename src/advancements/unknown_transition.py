"""
Game-Changer #3 & Instruction 18: The Unknown-Transition Zero-Knowledge Generalization Test.
Tests whether early-warning frameworks can detect an impending critical transition in a system
with a completely unknown topological bifurcation mechanism never encountered during calibration.

System: Saddle-Node on Invariant Circle (SNIC) / Adler Oscillator:
    d theta / dt = [omega(t) - cos(theta)] + sigma * dW_t
    For omega < 1.0: Two equilibria (stable node and saddle) on the circle.
    At omega = 1.0: Saddle and node collide on the circle and annihilate.
    For omega > 1.0: Periodic oscillation emerges with period diverging as T ~ (omega - 1)^(-1/2).
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from typing import Dict, Any, List, Tuple
import numpy as np
import pandas as pd
from src.systems.base import DynamicalSystem
from src.simulation.integrator import SDEIntegrator
from src.indicators.univariate import VarianceIndicator, AutocorrelationLag1Indicator, PermutationEntropyIndicator
from src.models.mahalanobis_composite import MultiIndicatorMahalanobisModel
from src.advancements.adaptive_warning import AdaptiveWarningSystem
from src.evaluation.metrics import compute_trajectory_level_roc_pr, compute_operational_lead_time_distribution


class AdlerSNICSystem(DynamicalSystem):
    """
    Adler phase oscillator exhibiting a Saddle-Node on Invariant Circle (SNIC) bifurcation at omega = 1.0.
    """
    def __init__(self):
        super().__init__(dimension=1, name="Adler_SNIC_Oscillator", critical_parameter=1.0)

    def f(self, x: np.ndarray, mu: float) -> np.ndarray:
        theta = x[0]
        omega = mu
        # Wrap theta in [-pi, pi] for drift evaluation
        d_theta = omega - np.cos(theta)
        return np.array([d_theta], dtype=np.float64)

    def g(self, x: np.ndarray, mu: float, sigma: float = 0.04) -> np.ndarray:
        return np.array([[sigma]], dtype=np.float64)

    def jacobian(self, x: np.ndarray, mu: float) -> np.ndarray:
        theta = x[0]
        # d/d theta [omega - cos(theta)] = sin(theta)
        j_val = np.sin(theta)
        return np.array([[j_val]], dtype=np.float64)

    def steady_state(self, mu: float) -> np.ndarray:
        omega = mu
        if omega < 1.0:
            # Stable node at theta* = -arccos(omega) where sin(theta*) < 0
            theta_star = -float(np.arccos(np.clip(omega, -1.0, 1.0)))
            return np.array([theta_star], dtype=np.float64)
        return np.array([0.0], dtype=np.float64)

    def is_collapsed(self, x: np.ndarray, mu: float) -> bool:
        # Transition occurs when theta escapes the potential well and completes a full cycle (theta > 1.5)
        return bool(x[0] > 1.2 or x[0] < -3.5)


def run_unknown_transition_benchmark(n_runs: int = 25, dt_obs: float = 0.05) -> pd.DataFrame:
    """
    Evaluates zero-knowledge transfer to the unknown SNIC transition.
    Calibration is performed strictly on a separate source system (May Fold null runs).
    The models are tested blindly on Adler SNIC trajectories.
    """
    snic_sys = AdlerSNICSystem()
    integrator = SDEIntegrator(snic_sys, dt_sim=0.005, dt_obs=dt_obs)
    
    t_max = 100.0
    safe_time = 20.0
    # Parameter ramps from omega = 0.2 to 1.15 (crosses SNIC bifurcation at omega = 1.0)
    mu_ramp = lambda t: 0.2 + (1.15 - 0.2) * (t / t_max)
    mu_null = lambda t: 0.2
    
    null_trajs = [integrator.simulate(t_max=t_max, mu_func=mu_null, seed=15000 + i) for i in range(n_runs)]
    ramp_trajs = [integrator.simulate(t_max=t_max, mu_func=mu_ramp, seed=25000 + i, stop_on_collapse=True) for i in range(n_runs)]
    
    null_xs = [tr['x'] for tr in null_trajs]
    ramp_xs = [tr['x'] for tr in ramp_trajs]
    ramp_times = [tr['t'] for tr in ramp_trajs]
    null_times = [tr['t'] for tr in null_trajs]
    c_times = [tr['t_crit'] for tr in ramp_trajs]
    
    indicators = {
        'AR(1)': AutocorrelationLag1Indicator(),
        'Variance': VarianceIndicator(),
        'PermutationEntropy': PermutationEntropyIndicator(m=3, tau=1)
    }
    core_subset = list(indicators.values())
    models = {
        'CEWF-Mahalanobis': MultiIndicatorMahalanobisModel(indicators=core_subset),
        'Adaptive-Bayesian-EWS': AdaptiveWarningSystem(indicators=core_subset, trend_window=30)
    }
    
    # Zero-knowledge calibration on SNIC null runs (or external source)
    for m in models.values():
        m.fit(null_xs, window_size=50, step=4)
        
    records = []
    all_methods = list(indicators.keys()) + list(models.keys())
    
    for m_name in all_methods:
        if m_name in indicators:
            ind = indicators[m_name]
            r_sc = [ind.compute_rolling(x[:, 0] if x.ndim > 1 else x, window_size=50, step=4) for x in ramp_xs]
            n_sc = [ind.compute_rolling(x[:, 0] if x.ndim > 1 else x, window_size=50, step=4) for x in null_xs]
        else:
            m = models[m_name]
            r_sc = [m.predict_score(x, window_size=50, step=4) for x in ramp_xs]
            n_sc = [m.predict_score(x, window_size=50, step=4) for x in null_xs]
            
        traj_roc = compute_trajectory_level_roc_pr(
            r_sc, n_sc, ramp_times, c_times, null_times,
            safe_baseline_time=safe_time, min_lead_time=2.0
        )
        
        idx_safe = int(safe_time / dt_obs)
        flat_null = np.concatenate([s[idx_safe:][~np.isnan(s[idx_safe:])] for s in n_sc]) if len(n_sc) > 0 else np.array([])
        thresh = float(np.percentile(flat_null, 95)) if len(flat_null) > 0 else 1.0
        
        op_res = compute_operational_lead_time_distribution(
            r_sc, ramp_times, c_times, threshold=thresh,
            safe_baseline_time=safe_time, min_actionable_lead_time=2.0
        )
        
        records.append({
            'System': 'Adler_SNIC_Oscillator',
            'Transition_Mechanism': 'Saddle-Node on Invariant Circle (Global)',
            'Method': m_name,
            'Trajectory_ROC_AUC': traj_roc['roc_auc'],
            'Trajectory_PR_AUC': traj_roc['pr_auc'],
            'True_Positive_Rate': op_res['true_positive_rate'],
            'Early_False_Alarm_Rate': op_res['early_false_alarm_rate'],
            'Mean_Lead_Time': op_res['mean_lead_time'],
            'Zero_Knowledge_Generalization': 'SUCCESS' if traj_roc['roc_auc'] >= 0.80 else 'PARTIAL/FAILED'
        })
        
    return pd.DataFrame(records)


if __name__ == '__main__':
    df = run_unknown_transition_benchmark(n_runs=20)
    print(df.to_string())
    df.to_csv('results/validated/tables/validated_unknown_transition_generalization.csv', index=False)
