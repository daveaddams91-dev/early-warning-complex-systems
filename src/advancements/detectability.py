"""
Game-Changer #1: The Detectability Boundary Engine.
Constructs empirical and analytical phase diagrams mapping the boundary between
detectable and impossible regimes across (Noise, Sampling Frequency, Ramp Velocity, Observation Window).
"""

from typing import Dict, Any, List, Tuple
import numpy as np
import pandas as pd
from src.systems.base import DynamicalSystem
from src.simulation.integrator import SDEIntegrator, ObservationCorrupter
from src.evaluation.metrics import compute_roc_pr


class DetectabilityBoundaryEngine:
    """
    Evaluates early-warning detectability across a multi-dimensional parameter grid.
    Identifies the critical boundary where ROC-AUC drops below a detectable threshold (e.g. AUC = 0.75).
    """

    def __init__(self, system: DynamicalSystem, dt_sim: float = 0.01):
        self.system = system
        self.dt_sim = dt_sim

    def compute_snr_analytical(self, x_star: float, mu: float, sigma: float, sigma_obs: float) -> float:
        """
        Computes analytical dynamical Signal-to-Measurement-Noise Ratio:
        Var_dyn = sigma^2 / (2 * |J(x_star, mu)|)
        SNR_dyn = Var_dyn / sigma_obs^2
        """
        j_val = float(self.system.jacobian(np.array([x_star]), mu)[0, 0])
        recovery_rate = max(1e-5, abs(j_val))
        var_dyn = (sigma**2) / (2.0 * recovery_rate)
        snr = var_dyn / (sigma_obs**2 + 1e-12)
        return snr

    def evaluate_grid(
        self,
        sigma_obs_levels: List[float],
        dt_obs_levels: List[float],
        ramp_rates: List[float],
        n_runs: int = 15,
        target_auc_threshold: float = 0.75
    ) -> pd.DataFrame:
        """
        Sweeps across noise levels sigma_obs and sampling intervals dt_obs to map the detectability phase boundary.
        """
        results = []
        
        for sigma_obs in sigma_obs_levels:
            for dt_obs in dt_obs_levels:
                for ramp_rate in ramp_rates:
                    t_max = 120.0 / ramp_rate
                    integrator = SDEIntegrator(self.system, dt_sim=self.dt_sim, dt_obs=dt_obs)
                    
                    mu_ramp = lambda t, r_rate=ramp_rate, tm=t_max: 1.5 + (3.2 - 1.5) * (t / tm)
                    mu_null = lambda t: 1.5
                    
                    # Generate test ramp trajectories
                    ramp_trajs = [integrator.simulate(t_max=t_max, mu_func=mu_ramp, seed=5000 + i, stop_on_collapse=True) for i in range(n_runs)]
                    null_trajs = [integrator.simulate(t_max=t_max, mu_func=mu_null, seed=6000 + i) for i in range(n_runs)]
                    
                    # Apply measurement noise
                    for r in ramp_trajs:
                        r['x_noisy'] = r['x'] + np.random.normal(0.0, sigma_obs, size=r['x'].shape)
                    for n_t in null_trajs:
                        n_t['x_noisy'] = n_t['x'] + np.random.normal(0.0, sigma_obs, size=n_t['x'].shape)
                        
                    w_size = max(10, int(2.5 / dt_obs))
                    
                    y_true, y_score = [], []
                    for r in ramp_trajs:
                        t_crit, t_arr, x_n = r['t_crit'], r['t'], r['x_noisy']
                        if np.isnan(t_crit) or len(x_n) < w_size + 10:
                            continue
                        n_pts = len(x_n)
                        scores = np.full(n_pts, np.nan)
                        step_k = max(1, n_pts // 200)
                        for k in range(w_size - 1, n_pts, step_k):
                            scores[k] = np.var(x_n[k - w_size + 1 : k + 1], ddof=1)
                            
                        pre_mask = (t_arr >= t_crit - 0.2 * t_max) & (t_arr <= t_crit) & (~np.isnan(scores))
                        safe_mask = (t_arr >= 0.1 * t_max) & (t_arr <= 0.3 * t_max) & (~np.isnan(scores))
                        
                        if np.sum(pre_mask) > 0 and np.sum(safe_mask) > 0:
                            y_true.extend([1] * np.sum(pre_mask))
                            y_score.extend(scores[pre_mask])
                            y_true.extend([0] * np.sum(safe_mask))
                            y_score.extend(scores[safe_mask])
                            
                    for n_t in null_trajs:
                        t_arr, x_n = n_t['t'], n_t['x_noisy']
                        n_pts = len(x_n)
                        if n_pts < w_size + 10:
                            continue
                        scores = np.full(n_pts, np.nan)
                        step_k = max(1, n_pts // 200)
                        for k in range(w_size - 1, n_pts, step_k):
                            scores[k] = np.var(x_n[k - w_size + 1 : k + 1], ddof=1)
                        valid_sc = scores[~np.isnan(scores)]
                        if len(valid_sc) > 20:
                            y_true.extend([0] * len(valid_sc[10:]))
                            y_score.extend(valid_sc[10:])
                            
                    roc_res = compute_roc_pr(np.array(y_true), np.array(y_score))
                    auc = roc_res['roc_auc']
                    is_detectable = bool(auc >= target_auc_threshold) if not np.isnan(auc) else False
                    
                    results.append({
                        'Sigma_Obs': sigma_obs,
                        'Dt_Obs': dt_obs,
                        'Sampling_Freq': 1.0 / dt_obs,
                        'Ramp_Rate_Multiplier': ramp_rate,
                        'ROC_AUC': auc,
                        'Is_Detectable': is_detectable,
                        'Regime': 'Detectable' if is_detectable else 'Undetectable/Noise-Dominated'
                    })
                    
        return pd.DataFrame(results)
