"""
Game-Changer #9: The Adversarial Collapse Lab.
Generates pathological, misleading, and non-canonical dynamical regimes specifically
crafted to evaluate the failure boundaries of early-warning systems.
"""

from typing import Dict, Any, List, Tuple
import numpy as np
import pandas as pd
from src.systems.base import DynamicalSystem
from src.simulation.integrator import SDEIntegrator, ObservationCorrupter
from src.evaluation.metrics import compute_false_alarm_rate, compute_lead_time_distribution


class AdversarialCollapseLab:
    """
    Stress-testing lab generating 5 distinct deceptive dynamical scenarios.
    """

    def __init__(self, dt_sim: float = 0.01, dt_obs: float = 0.05):
        self.dt_sim = dt_sim
        self.dt_obs = dt_obs

    def generate_scenario_1_false_csd_sinusoid(self, n_runs: int = 15, t_max: float = 100.0) -> List[Dict[str, np.ndarray]]:
        """
        Deceptive scenario: Parameter oscillates harmlessly mu(t) = 1.6 + 0.3 * sin(2*pi*t/40).
        Induces cyclic autocorrelation without any stability loss.
        """
        trajs = []
        n_steps = int(t_max / self.dt_sim)
        t_arr = np.linspace(0.0, t_max, n_steps + 1)
        
        for i in range(n_runs):
            np.random.seed(31000 + i)
            x = np.zeros(n_steps + 1)
            x[0] = 7.5
            for k in range(n_steps):
                t = t_arr[k]
                mu = 1.6 + 0.3 * np.sin(2.0 * np.pi * t / 40.0)
                # 1D May drift
                drift = 1.0 * x[k] * (1.0 - x[k] / 10.0) - mu * (x[k]**2) / (x[k]**2 + 1.0)
                dw = np.random.normal(0.0, np.sqrt(self.dt_sim))
                x[k + 1] = max(0.1, x[k] + drift * self.dt_sim + 0.03 * dw)
            # Downsample to dt_obs
            step_obs = int(self.dt_obs / self.dt_sim)
            trajs.append({'t': t_arr[::step_obs], 'x': x[::step_obs], 't_crit': np.nan, 'type': 'False_CSD_Sinusoid'})
        return trajs

    def generate_scenario_2_noise_spectrum_shift(self, n_runs: int = 15, t_max: float = 100.0) -> List[Dict[str, np.ndarray]]:
        """
        Deceptive scenario: Underlying system has constant mu=1.6, but observation noise shifts from white to red noise.
        """
        trajs = []
        n_steps = int(t_max / self.dt_sim)
        t_arr = np.linspace(0.0, t_max, n_steps + 1)
        
        for i in range(n_runs):
            np.random.seed(32000 + i)
            x = np.zeros(n_steps + 1)
            x[0] = 7.5
            eta = 0.0
            for k in range(n_steps):
                t = t_arr[k]
                drift = 1.0 * x[k] * (1.0 - x[k] / 10.0) - 1.6 * (x[k]**2) / (x[k]**2 + 1.0)
                dw = np.random.normal(0.0, np.sqrt(self.dt_sim))
                x[k + 1] = max(0.1, x[k] + drift * self.dt_sim + 0.02 * dw)
                
            step_obs = int(self.dt_obs / self.dt_sim)
            t_sub = t_arr[::step_obs]
            x_sub = x[::step_obs].copy()
            
            # Second half undergoes red noise coloring
            mid_idx = len(x_sub) // 2
            for j in range(mid_idx, len(x_sub)):
                eta = 0.7 * eta + np.random.normal(0.0, 0.08)
                x_sub[j] += eta
                
            trajs.append({'t': t_sub, 'x': x_sub, 't_crit': np.nan, 'type': 'Noise_Spectrum_Shift'})
        return trajs

    def generate_scenario_3_hidden_variable_crisis(self, n_runs: int = 15, t_max: float = 100.0) -> List[Dict[str, np.ndarray]]:
        """
        Deceptive scenario: 2D system where unobserved variable z destabilizes abruptly while observed x appears calm.
        """
        trajs = []
        n_steps = int(t_max / self.dt_sim)
        t_arr = np.linspace(0.0, t_max, n_steps + 1)
        
        for i in range(n_runs):
            np.random.seed(33000 + i)
            x = np.zeros(n_steps + 1)
            z = np.zeros(n_steps + 1)
            x[0], z[0] = 5.0, 0.0
            t_crit = np.nan
            
            for k in range(n_steps):
                t = t_arr[k]
                # z ramps toward crisis
                mu_z = -0.5 + (0.6 - (-0.5)) * (t / t_max)
                # x is weakly coupled until z crosses 0.2
                dx = -1.0 * (x[k] - 5.0) - (2.0 * max(0.0, z[k] - 0.2)**2)
                dz = mu_z * z[k] - z[k]**3
                
                dw1 = np.random.normal(0.0, np.sqrt(self.dt_sim))
                dw2 = np.random.normal(0.0, np.sqrt(self.dt_sim))
                
                x[k + 1] = x[k] + dx * self.dt_sim + 0.02 * dw1
                z[k + 1] = z[k] + dz * self.dt_sim + 0.02 * dw2
                
                if x[k + 1] < 2.0 and np.isnan(t_crit):
                    t_crit = t
                    
            step_obs = int(self.dt_obs / self.dt_sim)
            trajs.append({'t': t_arr[::step_obs], 'x': x[::step_obs], 't_crit': t_crit, 'type': 'Hidden_Variable_Crisis'})
        return trajs
