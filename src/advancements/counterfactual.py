"""
Game-Changer #4: Counterfactual Early Warning & Informational Distinguishability.
Investigates paired counterfactual scenarios:
  Case A: Perturbation -> Damped Return to Stability (Resilience Intact)
  Case B: Perturbation -> Basin Evacuation & Collapse (Loss of Resilience)
Measures the exact information-theoretic time t* at which the two futures become statistically distinguishable.
"""

from typing import Dict, Any, List, Tuple
import numpy as np
import scipy.stats as st
import pandas as pd
from src.systems.base import DynamicalSystem
from src.simulation.integrator import SDEIntegrator


class CounterfactualAnalysisEngine:
    """
    Evaluates informational distinguishability between paired recovery and collapse ensembles.
    """

    def __init__(self, system: DynamicalSystem, dt_sim: float = 0.01, dt_obs: float = 0.05):
        self.system = system
        self.dt_sim = dt_sim
        self.dt_obs = dt_obs

    def simulate_paired_counterfactuals(
        self,
        n_pairs: int = 30,
        t_max: float = 80.0,
        t_shock: float = 20.0,
        shock_magnitude: float = 1.8
    ) -> Tuple[List[Dict[str, np.ndarray]], List[Dict[str, np.ndarray]]]:
        """
        Simulates paired realizations with identical early shock:
          - Ensemble A (Recovery): Parameter mu remains subcritical (mu = 1.6). Damped recovery.
          - Ensemble B (Collapse): Parameter mu ramps into danger zone (mu -> 2.9). Escalating instability.
        """
        integrator = SDEIntegrator(self.system, dt_sim=self.dt_sim, dt_obs=self.dt_obs)
        
        recovery_ensemble = []
        collapse_ensemble = []
        
        idx_shock = int(t_shock / self.dt_obs)
        
        for i in range(n_pairs):
            # Case A: Stable Parameter
            res_a = integrator.simulate(t_max=t_max, mu_func=lambda t: 1.6, seed=10000 + i)
            x_a = res_a['x'].copy()
            if idx_shock < len(x_a):
                x_a[idx_shock : idx_shock + 10] -= shock_magnitude
            recovery_ensemble.append({'t': res_a['t'], 'x': x_a, 'mu': res_a['mu']})
            
            # Case B: Destabilizing Parameter
            mu_b = lambda t: 1.6 + (3.0 - 1.6) * (t / t_max)
            res_b = integrator.simulate(t_max=t_max, mu_func=mu_b, seed=20000 + i, stop_on_collapse=True)
            x_b = res_b['x'].copy()
            if idx_shock < len(x_b):
                x_b[idx_shock : idx_shock + 10] -= shock_magnitude
            collapse_ensemble.append({'t': res_b['t'], 'x': x_b, 'mu': res_b['mu'], 't_crit': res_b['t_crit']})
            
        return recovery_ensemble, collapse_ensemble

    def compute_distinguishability_profile(
        self,
        recovery_ensemble: List[Dict[str, np.ndarray]],
        collapse_ensemble: List[Dict[str, np.ndarray]],
        t_shock: float = 20.0
    ) -> pd.DataFrame:
        """
        Computes rolling empirical KL-divergence, Wasserstein-1 distance, and Kolmogorov-Smirnov p-values
        between the state distributions of Case A and Case B across time.
        """
        min_len = min(min(len(r['x']) for r in recovery_ensemble), min(len(c['x']) for c in collapse_ensemble))
        t_arr = recovery_ensemble[0]['t'][:min_len]
        
        records = []
        
        for k in range(0, min_len, 4):
            t_curr = t_arr[k]
            
            # Extract state cross-sections across ensembles
            vals_a = np.array([r['x'][k, 0] if r['x'].ndim > 1 else r['x'][k] for r in recovery_ensemble])
            vals_b = np.array([c['x'][k, 0] if c['x'].ndim > 1 else c['x'][k] for c in collapse_ensemble])
            
            # 1. Kolmogorov-Smirnov 2-sample test
            ks_stat, ks_pval = st.ks_2samp(vals_a, vals_b)
            
            # 2. Wasserstein-1 Distance (Earth Mover's Distance)
            w1_dist = float(st.wasserstein_distance(vals_a, vals_b))
            
            # 3. Gaussian-Approximated KL Divergence: D_KL(N_a || N_b)
            mu_a, std_a = np.mean(vals_a), np.std(vals_a) + 1e-6
            mu_b, std_b = np.mean(vals_b), np.std(vals_b) + 1e-6
            kl_div = np.log(std_b / std_a) + (std_a**2 + (mu_a - mu_b)**2) / (2.0 * std_b**2) - 0.5
            
            is_distinguishable = bool(ks_pval < 0.01 and w1_dist > 0.5)
            
            records.append({
                'Time': t_curr,
                'Post_Shock_Delta_T': max(0.0, t_curr - t_shock),
                'Wasserstein1_Dist': w1_dist,
                'Gaussian_KL_Div': max(0.0, float(kl_div)),
                'KS_Statistic': ks_stat,
                'KS_pvalue': ks_pval,
                'Is_Distinguishable': is_distinguishable,
                'Informational_Regime': 'Distinguishable' if is_distinguishable else 'Ambiguous/Indistinguishable'
            })
            
        return pd.DataFrame(records)
