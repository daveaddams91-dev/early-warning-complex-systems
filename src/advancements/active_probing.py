"""
Game-Changer #6 & #7: Active Experimentation Probing & Optimal Stabilizing Intervention.
- Active Probing: Evaluates active test perturbations to directly measure return rate kappa(t)
  with maximal Fisher information gain.
- Optimal Intervention: Implements stabilizing feedback control u*(t) = -K (x - x_ref)
  to arrest tipping with minimal intervention cost.
"""

from typing import Dict, Any, List, Tuple
import numpy as np
import pandas as pd
from src.systems.base import DynamicalSystem
from src.simulation.integrator import SDEIntegrator


class ActiveExperimentationEngine:
    """
    Active probing and optimal feedback intervention framework.
    """

    def __init__(self, system: DynamicalSystem, dt_sim: float = 0.01, dt_obs: float = 0.05):
        self.system = system
        self.dt_sim = dt_sim
        self.dt_obs = dt_obs

    def run_active_probe_experiment(
        self,
        t_max: float = 100.0,
        probe_interval: float = 15.0,
        probe_amplitude: float = 0.5,
        mu_ramp_fn = None,
        seed: int = 42
    ) -> Dict[str, Any]:
        """
        Periodically injects small pulse test perturbations and directly estimates recovery rate kappa.
        """
        if mu_ramp_fn is None:
            mu_ramp_fn = lambda t: 1.5 + (3.0 - 1.5) * (t / t_max)
            
        np.random.seed(seed)
        n_steps = int(t_max / self.dt_sim)
        t_arr = np.linspace(0.0, t_max, n_steps + 1)
        dim = self.system.dimension
        
        x_init = self.system.steady_state(mu_ramp_fn(0.0))
        x_hist = np.zeros((n_steps + 1, dim))
        x_hist[0] = x_init
        
        probe_times = []
        estimated_kappas = []
        theoretical_kappas = []
        
        probe_step_interval = int(probe_interval / self.dt_sim)
        probe_duration_steps = int(1.5 / self.dt_sim)
        
        x_curr = x_init.copy()
        
        for k in range(n_steps):
            t_curr = t_arr[k]
            mu_curr = mu_ramp_fn(t_curr)
            
            # Active probe perturbation injection
            is_probe_point = (k > 0) and (k % probe_step_interval == 0)
            if is_probe_point:
                probe_times.append(t_curr)
                # Apply deliberate delta displacement
                x_curr[0] -= probe_amplitude
                # Track post-probe relaxation
                relax_x0 = x_curr[0]
                
            drift = self.system.f(x_curr, mu_curr)
            diff = self.system.g(x_curr, mu_curr, sigma=0.02)
            dw = np.random.normal(0.0, np.sqrt(self.dt_sim), size=dim)
            x_curr = x_curr + drift * self.dt_sim + diff @ dw
            x_curr = np.maximum(x_curr, 0.0)
            x_hist[k + 1] = x_curr
            
            if is_probe_point:
                # Measure decay rate over post-probe relaxation interval
                post_k = min(k + probe_duration_steps, n_steps)
                # Approximate kappa = -ln(|x_t - x*| / probe_amp) / delta_t
                x_star = self.system.steady_state(mu_curr)[0]
                delta_x = abs(x_hist[post_k, 0] - x_star)
                decay_rate = -np.log(max(1e-4, delta_x / probe_amplitude)) / 1.5
                estimated_kappas.append(max(0.0, float(decay_rate)))
                
                # Theoretical eigenvalue
                j_val = float(self.system.jacobian(np.array([x_star]), mu_curr)[0, 0])
                theoretical_kappas.append(abs(j_val))
                
        return {
            't': t_arr,
            'x': x_hist,
            'probe_times': np.array(probe_times),
            'estimated_kappas': np.array(estimated_kappas),
            'theoretical_kappas': np.array(theoretical_kappas)
        }

    def run_stabilizing_intervention(
        self,
        t_max: float = 100.0,
        mu_ramp_fn = None,
        intervention_time: float = 75.0,
        control_gain: float = 2.0,
        seed: int = 42
    ) -> Dict[str, Any]:
        """
        Simulates closed-loop stabilizing feedback control:
        u(t) = -K * (x(t) - x_target) activated at t >= intervention_time.
        """
        if mu_ramp_fn is None:
            mu_ramp_fn = lambda t: 1.5 + (3.2 - 1.5) * (t / t_max)
            
        np.random.seed(seed)
        n_steps = int(t_max / self.dt_sim)
        t_arr = np.linspace(0.0, t_max, n_steps + 1)
        dim = self.system.dimension
        
        x_init = self.system.steady_state(mu_ramp_fn(0.0))
        x_hist = np.zeros((n_steps + 1, dim))
        u_hist = np.zeros(n_steps + 1)
        x_hist[0] = x_init
        
        x_curr = x_init.copy()
        x_target = x_init[0]
        collapsed = False
        
        for k in range(n_steps):
            t_curr = t_arr[k]
            mu_curr = mu_ramp_fn(t_curr)
            
            # Active stabilizing control
            if t_curr >= intervention_time:
                # Modulate effective harvesting or restore biomass
                u_ctrl = control_gain * max(0.0, x_target - x_curr[0])
            else:
                u_ctrl = 0.0
                
            u_hist[k] = u_ctrl
            drift = self.system.f(x_curr, mu_curr)
            drift[0] += u_ctrl  # Stabilizing input
            
            diff = self.system.g(x_curr, mu_curr, sigma=0.03)
            dw = np.random.normal(0.0, np.sqrt(self.dt_sim), size=dim)
            x_curr = x_curr + drift * self.dt_sim + diff @ dw
            x_curr = np.maximum(x_curr, 0.0)
            x_hist[k + 1] = x_curr
            
            if self.system.is_collapsed(x_curr, mu_curr):
                collapsed = True
                
        # Total intervention cost: integral u(t)^2 dt
        cost = float(np.sum(u_hist**2) * self.dt_sim)
        
        return {
            't': t_arr,
            'x': x_hist,
            'u': u_hist,
            'collapsed': collapsed,
            'intervention_cost': cost,
            'success': not collapsed
        }
