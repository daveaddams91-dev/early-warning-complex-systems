"""
Subcritical Pitchfork Model (SYS-3).
Exhibits subcritical pitchfork bifurcation with catastrophic discontinuous jump.

Governing Equation:
    dx/dt = mu * x + x^3 - x^5 + sigma * dW_t
"""

import numpy as np
from src.systems.base import DynamicalSystem


class SubcriticalPitchforkSystem(DynamicalSystem):
    """
    Subcritical Pitchfork normal form with 5th order saturation.
    
    Equilibrium x* = 0 is stable for mu < 0 with eigenvalue lambda = mu.
    At mu = 0, the origin loses stability, precipitating a catastrophic jump to |x| approx 1.
    """
    
    def __init__(self):
        super().__init__(dimension=1, name="SubcriticalPitchfork", critical_parameter=0.0)

    def f(self, x: np.ndarray, mu: float) -> np.ndarray:
        x_val = x[0]
        dx = mu * x_val + (x_val**3) - (x_val**5)
        return np.array([dx], dtype=np.float64)

    def g(self, x: np.ndarray, mu: float, sigma: float = 0.04) -> np.ndarray:
        return np.array([[sigma]], dtype=np.float64)

    def jacobian(self, x: np.ndarray, mu: float) -> np.ndarray:
        x_val = x[0]
        j_val = mu + 3.0 * (x_val**2) - 5.0 * (x_val**4)
        return np.array([[j_val]], dtype=np.float64)

    def steady_state(self, mu: float) -> np.ndarray:
        # Pre-transition stable origin
        return np.array([0.0], dtype=np.float64)

    def is_collapsed(self, x: np.ndarray, mu: float) -> bool:
        # Escaped the local potential well around x=0
        return bool(abs(x[0]) > 0.6)
