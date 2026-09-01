"""
High-Performance Stochastic Differential Equation (SDE) Integrator and Observation Pipeline.

Provides:
- Euler-Maruyama numerical SDE integration with seed reproducibility.
- Parameter ramp profiles (Quasi-static, Constant Null, Fast R-tipping, Transient Shock).
- Ground-truth collapse detection with exact timestamps.
- Observation corruption operators (Gaussian, Student-t, Colored Red Noise, Dropouts, Distractors).
"""

from typing import Callable, Dict, Any, Tuple, Optional, List
import numpy as np
from src.systems.base import DynamicalSystem


class SDEIntegrator:
    """
    Euler-Maruyama stochastic numerical integrator for continuous-time SDEs.
    """
    
    def __init__(self, system: DynamicalSystem, dt_sim: float = 0.005, dt_obs: float = 0.05):
        self.system = system
        self.dt_sim = dt_sim
        self.dt_obs = dt_obs
        self.subsample_rate = max(1, int(round(dt_obs / dt_sim)))

    def simulate(
        self,
        t_max: float,
        mu_func: Callable[[float], float],
        x0: Optional[np.ndarray] = None,
        sigma: float = 0.03,
        seed: Optional[int] = None,
        stop_on_collapse: bool = False,
        collapse_grace_period: float = 5.0
    ) -> Dict[str, Any]:
        """
        Simulates an SDE trajectory from t = 0 to t = t_max.
        
        Returns a dictionary containing:
            - t: array of observation timestamps
            - x: array of observed state vectors of shape (N_obs, dimension)
            - mu: array of parameter values at observation timestamps
            - collapsed: boolean indicating whether transition occurred
            - t_crit: timestamp of collapse (or np.nan if no collapse)
            - collapse_index: observation index of collapse (or -1)
        """
        rng = np.random.default_rng(seed)
        n_steps = int(np.ceil(t_max / self.dt_sim))
        dim = self.system.dimension
        
        # Initial state: steady state at mu(0) if not provided
        mu_0 = mu_func(0.0)
        if x0 is None:
            x_curr = self.system.steady_state(mu_0).copy()
        else:
            x_curr = np.array(x0, dtype=np.float64).copy()
            
        t_arr = []
        x_arr = []
        mu_arr = []
        
        t_curr = 0.0
        collapsed = False
        t_crit = np.nan
        collapse_step = -1
        
        sqrt_dt = np.sqrt(self.dt_sim)
        
        for step in range(n_steps + 1):
            mu_val = mu_func(t_curr)
            
            # Record observation at sub-sampled intervals
            if step % self.subsample_rate == 0:
                t_arr.append(t_curr)
                x_arr.append(x_curr.copy())
                mu_arr.append(mu_val)
                
            # Check collapse criterion
            if not collapsed and self.system.is_collapsed(x_curr, mu_val):
                collapsed = True
                t_crit = t_curr
                # If current time is not already in t_arr, append it so t_arr reflects the collapse instant
                if len(t_arr) == 0 or t_arr[-1] != t_curr:
                    t_arr.append(t_curr)
                    x_arr.append(x_curr.copy())
                    mu_arr.append(mu_val)
                collapse_step = len(t_arr) - 1
                if stop_on_collapse:
                    break
                    
            if step == n_steps:
                break
                
            # Euler-Maruyama step:
            # x_{t+dt} = x_t + f(x_t, mu_t) * dt + G(x_t, mu_t) * dW
            f_val = self.system.f(x_curr, mu_val)
            g_val = self.system.g(x_curr, mu_val, sigma=sigma)
            dw = rng.standard_normal(dim) * sqrt_dt
            
            dx = f_val * self.dt_sim + g_val @ dw
            x_curr = x_curr + dx
            t_curr += self.dt_sim
            
            # Numerical safeguard against NaN / Inf explosion
            if np.isnan(x_curr).any() or np.isinf(x_curr).any():
                collapsed = True
                if np.isnan(t_crit):
                    t_crit = t_curr
                    collapse_step = len(t_arr) - 1
                break

        return {
            't': np.array(t_arr, dtype=np.float64),
            'x': np.array(x_arr, dtype=np.float64),
            'mu': np.array(mu_arr, dtype=np.float64),
            'collapsed': collapsed,
            't_crit': t_crit,
            'collapse_index': collapse_step,
            'dt_obs': self.dt_obs,
            'dimension': dim,
            'system_name': self.system.name
        }


class ObservationCorrupter:
    """
    Applies realistic observation distortions (measurement noise, heavy tails,
    colored red noise, downsampling, dropouts, and distractor variables).
    """
    
    @staticmethod
    def add_gaussian_noise(x: np.ndarray, snr_db: float, seed: Optional[int] = None) -> np.ndarray:
        """
        Adds additive Gaussian white noise matching a specified Signal-to-Noise Ratio (SNR in dB).
        """
        rng = np.random.default_rng(seed)
        signal_power = np.var(x, axis=0, keepdims=True)
        signal_power[signal_power == 0] = 1e-6
        # SNR_dB = 10 * log10(P_signal / P_noise) => P_noise = P_signal / 10^(SNR_dB / 10)
        noise_power = signal_power / (10.0 ** (snr_db / 10.0))
        noise_std = np.sqrt(noise_power)
        noise = rng.standard_normal(x.shape) * noise_std
        return x + noise

    @staticmethod
    def add_student_t_noise(x: np.ndarray, scale: float = 0.05, df: float = 3.0, seed: Optional[int] = None) -> np.ndarray:
        """
        Adds heavy-tailed Student-t measurement noise with degrees of freedom df.
        """
        rng = np.random.default_rng(seed)
        noise = rng.standard_t(df=df, size=x.shape) * scale
        return x + noise

    @staticmethod
    def add_colored_red_noise(x: np.ndarray, dt: float, gamma: float = 0.5, sigma_eta: float = 0.05, seed: Optional[int] = None) -> np.ndarray:
        """
        Adds colored (red/autoregressive) measurement noise via an Ornstein-Uhlenbeck process:
            d_eta = -gamma * eta * dt + sigma_eta * dW
        """
        rng = np.random.default_rng(seed)
        n_obs, dim = x.shape
        eta = np.zeros((n_obs, dim))
        eta_curr = np.zeros(dim)
        sqrt_dt = np.sqrt(dt)
        decay = np.exp(-gamma * dt)
        std_inc = sigma_eta * np.sqrt((1.0 - np.exp(-2.0 * gamma * dt)) / (2.0 * gamma))
        
        for k in range(n_obs):
            eta[k] = eta_curr
            eta_curr = decay * eta_curr + rng.standard_normal(dim) * std_inc
            
        return x + eta

    @staticmethod
    def apply_random_dropout(x: np.ndarray, drop_prob: float = 0.2, seed: Optional[int] = None) -> Tuple[np.ndarray, np.ndarray]:
        """
        Simulates missing sensor dropouts. Returns (corrupted_x, mask_valid).
        """
        rng = np.random.default_rng(seed)
        mask_valid = rng.uniform(0.0, 1.0, size=x.shape) > drop_prob
        # Forward fill or NaN fill
        x_corrupted = x.copy()
        x_corrupted[~mask_valid] = np.nan
        return x_corrupted, mask_valid

    @staticmethod
    def append_distractors(x: np.ndarray, n_distractors: int, dt: float, seed: Optional[int] = None) -> np.ndarray:
        """
        Appends D uncoupled irrelevant distractor time series (random walks / AR(1) processes).
        """
        if n_distractors <= 0:
            return x
        rng = np.random.default_rng(seed)
        n_obs = x.shape[0]
        distractors = np.zeros((n_obs, n_distractors))
        
        # Generate mixed AR(1) and Wiener processes
        decay = 0.95
        curr = rng.standard_normal(n_distractors)
        for k in range(n_obs):
            distractors[k] = curr
            curr = decay * curr + rng.standard_normal(n_distractors) * 0.1
            
        return np.hstack([x, distractors])
