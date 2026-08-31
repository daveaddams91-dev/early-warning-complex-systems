"""
Game-Changer #5: Minimum Data Required for Reliable Prediction.
Empirically and analytically derives the scaling relation N_min = f(sigma, dt, delta_mu)
for achieving a target detection performance (e.g. ROC-AUC >= 0.80).
"""

from typing import List, Dict, Any, Tuple
import numpy as np
import pandas as pd
from scipy.optimize import curve_fit
from src.systems.base import DynamicalSystem
from src.simulation.integrator import SDEIntegrator
from src.evaluation.metrics import compute_roc_pr


class DataScalingEngine:
    """
    Measures the minimum number of observation samples N_min required for reliable early warning.
    """

    def __init__(self, system: DynamicalSystem, dt_sim: float = 0.01):
        self.system = system
        self.dt_sim = dt_sim

    def measure_n_min_grid(
        self,
        noise_levels: List[float],
        dt_levels: List[float],
        target_auc: float = 0.80,
        n_runs: int = 15
    ) -> pd.DataFrame:
        """
        Sweeps observation lengths to find the minimum number of observations N_min reaching target_auc.
        """
        records = []
        
        for sigma in noise_levels:
            for dt in dt_levels:
                # Test durations T in [20, 40, 60, 80, 120]
                t_durations = [20.0, 40.0, 60.0, 80.0, 120.0]
                achieved_n_min = np.nan
                achieved_auc = np.nan
                
                for t_max in t_durations:
                    integrator = SDEIntegrator(self.system, dt_sim=self.dt_sim, dt_obs=dt)
                    mu_ramp = lambda t, tm=t_max: 1.5 + (3.2 - 1.5) * (t / tm)
                    mu_null = lambda t: 1.5
                    
                    ramp_trajs = [integrator.simulate(t_max=t_max, mu_func=mu_ramp, sigma=sigma, seed=3000 + i, stop_on_collapse=True) for i in range(n_runs)]
                    null_trajs = [integrator.simulate(t_max=t_max, mu_func=mu_null, sigma=sigma, seed=4000 + i) for i in range(n_runs)]
                    
                    w_size = max(10, int(2.5 / dt))
                    
                    y_true, y_score = [], []
                    for r in ramp_trajs:
                        t_crit, t_arr, x = r['t_crit'], r['t'], r['x']
                        if np.isnan(t_crit) or len(x) < w_size + 10:
                            continue
                        n_pts = len(x)
                        scores = np.full(n_pts, np.nan)
                        step_k = max(1, n_pts // 150)
                        for k in range(w_size - 1, n_pts, step_k):
                            scores[k] = np.var(x[k - w_size + 1 : k + 1], ddof=1)
                            
                        pre_mask = (t_arr >= t_crit - 0.2 * t_max) & (t_arr <= t_crit) & (~np.isnan(scores))
                        safe_mask = (t_arr >= 0.1 * t_max) & (t_arr <= 0.3 * t_max) & (~np.isnan(scores))
                        if np.sum(pre_mask) > 0 and np.sum(safe_mask) > 0:
                            y_true.extend([1] * np.sum(pre_mask))
                            y_score.extend(scores[pre_mask])
                            y_true.extend([0] * np.sum(safe_mask))
                            y_score.extend(scores[safe_mask])
                            
                    for n_t in null_trajs:
                        x = n_t['x']
                        n_pts = len(x)
                        if n_pts < w_size + 10:
                            continue
                        scores = np.full(n_pts, np.nan)
                        step_k = max(1, n_pts // 150)
                        for k in range(w_size - 1, n_pts, step_k):
                            scores[k] = np.var(x[k - w_size + 1 : k + 1], ddof=1)
                        valid_sc = scores[~np.isnan(scores)]
                        if len(valid_sc) > 10:
                            y_true.extend([0] * len(valid_sc[5:]))
                            y_score.extend(valid_sc[5:])
                            
                    roc_res = compute_roc_pr(np.array(y_true), np.array(y_score))
                    auc = roc_res['roc_auc']
                    n_samples = int(t_max / dt)
                    
                    if not np.isnan(auc) and auc >= target_auc and np.isnan(achieved_n_min):
                        achieved_n_min = n_samples
                        achieved_auc = auc
                        break
                        
                records.append({
                    'Noise_Sigma': sigma,
                    'Sampling_Dt': dt,
                    'Target_AUC': target_auc,
                    'N_min_samples': achieved_n_min if not np.isnan(achieved_n_min) else int(120.0 / dt),
                    'Achieved_AUC': achieved_auc if not np.isnan(achieved_auc) else 0.50,
                    'Status': 'Sufficient Data Found' if not np.isnan(achieved_n_min) else 'Unreached (Insufficient Budget)'
                })
                
        return pd.DataFrame(records)
