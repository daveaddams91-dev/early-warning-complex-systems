"""
Game-Changer #10: Exact Theoretical Analysis & Estimator Bias Quantification.
Compares:
  1. Exact continuous Lyapunov stationary predictions: Var_th = sigma^2 / (2 |lambda|), AR1_th = exp(lambda * dt)
  2. Stationary Monte Carlo SDE simulation
  3. Finite-sliding-window empirical estimators (quantifying Kendall 1954 small-sample bias: E[rho] ~ rho - (1+3rho)/W)
"""

from typing import Dict, Any, List, Tuple
import numpy as np
import pandas as pd
from src.systems.base import DynamicalSystem
from src.simulation.integrator import SDEIntegrator


class TheoreticalComparisonEngine:
    """
    Evaluates analytical Lyapunov formulas vs Monte Carlo truth vs finite-window empirical estimators.
    """

    def __init__(self, system: DynamicalSystem):
        self.system = system

    def compare_theoretical_vs_empirical(
        self,
        mu_values: List[float],
        sigma: float = 0.05,
        dt_obs: float = 0.05,
        window_sizes: List[int] = [30, 50, 100],
        n_mc_steps: int = 50000
    ) -> pd.DataFrame:
        """
        Computes analytical, stationary Monte Carlo, and finite-window empirical estimates across mu.
        """
        records = []
        
        for mu in mu_values:
            x_star = self.system.steady_state(mu)[0]
            j_val = float(self.system.jacobian(np.array([x_star]), mu)[0, 0])
            lambda_val = j_val
            abs_lambda = max(1e-5, abs(lambda_val))
            
            # 1. Exact Analytical Theory
            var_th = (sigma**2) / (2.0 * abs_lambda)
            ar1_th = float(np.exp(lambda_val * dt_obs))
            
            # 2. Long Stationary Monte Carlo Simulation
            integrator = SDEIntegrator(self.system, dt_sim=0.005, dt_obs=dt_obs)
            t_max_mc = n_mc_steps * dt_obs
            res = integrator.simulate(t_max=t_max_mc, mu_func=lambda t, m=mu: m, sigma=sigma, seed=42)
            x_mc = res['x'][:, 0] if res['x'].ndim > 1 else res['x']
            
            var_mc = float(np.var(x_mc[1000:], ddof=1))
            dev = x_mc[1000:] - np.mean(x_mc[1000:])
            ar1_mc = float(np.sum(dev[:-1] * dev[1:]) / (np.sum(dev**2) + 1e-12))
            
            # 3. Finite Sliding Window Empirical Estimators
            for w in window_sizes:
                # Finite sample Kendall bias formula: E[rho_hat] ~ rho - (1 + 3*rho)/W
                ar1_expected_biased = ar1_th - (1.0 + 3.0 * ar1_th) / w
                
                # Empirical distribution across sliding windows
                n_eval = 200
                stride = max(1, (len(x_mc) - w) // n_eval)
                w_vars, w_ar1s = [], []
                for k in range(w, len(x_mc), stride):
                    sub = x_mc[k - w : k]
                    w_vars.append(np.var(sub, ddof=1))
                    d = sub - np.mean(sub)
                    w_ar1s.append(np.sum(d[:-1] * d[1:]) / (np.sum(d**2) + 1e-12))
                    
                records.append({
                    'Mu': mu,
                    'Eigenvalue_Lambda': lambda_val,
                    'Window_W': w,
                    'Var_Theoretical': var_th,
                    'Var_MC_Truth': var_mc,
                    'Var_Empirical_Mean': float(np.mean(w_vars)),
                    'AR1_Theoretical': ar1_th,
                    'AR1_MC_Truth': ar1_mc,
                    'AR1_Expected_Biased': ar1_expected_biased,
                    'AR1_Empirical_Mean': float(np.mean(w_ar1s)),
                    'AR1_Bias_Observed': float(np.mean(w_ar1s) - ar1_th),
                    'Theoretical_Bias_Match': bool(abs(np.mean(w_ar1s) - ar1_expected_biased) < 0.10)
                })
                
        return pd.DataFrame(records)
