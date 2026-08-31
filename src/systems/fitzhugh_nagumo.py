"""
FitzHugh-Nagumo Oscillator Model (SYS-2).
Exhibits a canonical Supercritical Hopf bifurcation.

Governing Equations:
    dv/dt = v - v^3 / 3 - w + I(t) + sigma * dW_1
    dw/dt = epsilon * (v + a - b * w) + sigma * dW_2
"""

import numpy as np
from scipy.optimize import root_scalar
from src.systems.base import DynamicalSystem


class FitzHughNagumoSystem(DynamicalSystem):
    """
    FitzHugh-Nagumo 2D excitable / oscillatory system.
    
    Parameters:
        a: default 0.7
        b: default 0.8
        epsilon: time scale separation, default 0.08
        I: applied current (control parameter, I_crit approx 0.331)
    """
    
    def __init__(self, a: float = 0.7, b: float = 0.8, epsilon: float = 0.08):
        super().__init__(dimension=2, name="FitzHughNagumo", critical_parameter=0.3313)
        self.a = a
        self.b = b
        self.epsilon = epsilon
        self._cache = {}

    def f(self, x: np.ndarray, mu: float) -> np.ndarray:
        v, w = x[0], x[1]
        I_app = mu
        dv = v - (v**3) / 3.0 - w + I_app
        dw = self.epsilon * (v + self.a - self.b * w)
        return np.array([dv, dw], dtype=np.float64)

    def g(self, x: np.ndarray, mu: float, sigma: float = 0.03) -> np.ndarray:
        return np.diag([sigma, sigma]).astype(np.float64)

    def jacobian(self, x: np.ndarray, mu: float) -> np.ndarray:
        v, w = x[0], x[1]
        j00 = 1.0 - v**2
        j01 = -1.0
        j10 = self.epsilon
        j11 = -self.epsilon * self.b
        return np.array([[j00, j01], [j10, j11]], dtype=np.float64)

    def steady_state(self, mu: float) -> np.ndarray:
        I_app = mu
        if I_app in self._cache:
            return self._cache[I_app]
            
        def obj(v):
            w = (v + self.a) / self.b
            return v - (v**3) / 3.0 - w + I_app
            
        # Find root v in [-2.5, 0.5]
        sol = root_scalar(obj, bracket=[-2.5, 0.5], method='brentq')
        v_star = sol.root
        w_star = (v_star + self.a) / self.b
        res = np.array([v_star, w_star], dtype=np.float64)
        self._cache[I_app] = res
        return res

    def is_collapsed(self, x: np.ndarray, mu: float) -> bool:
        # For Hopf, transition is characterized by sustained large limit cycle oscillations (v > 1.2 or amplitude swing)
        v_star = self.steady_state(mu)[0]
        return bool(abs(x[0] - v_star) > 1.2)
