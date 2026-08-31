"""
May's Ecological Harvesting Model (SYS-1).
Exhibits a canonical Fold (Saddle-Node) bifurcation and catastrophic collapse.

Governing Equation:
    dx/dt = r * x * (1 - x / K) - c * x^2 / (x^2 + d^2) + sigma * dW_t
"""

import numpy as np
from src.systems.base import DynamicalSystem


class MayHarvestingSystem(DynamicalSystem):
    """
    May (1977) Grazing / Harvesting Model.
    
    Parameters:
        r: Intrinsic growth rate (default: 1.0)
        K: Carrying capacity (default: 10.0)
        d: Half-saturation constant (default: 1.0)
        c: Grazing / harvesting capacity (control parameter, c_crit approx 2.6044)
    """
    
    def __init__(self, r: float = 1.0, K: float = 10.0, d: float = 1.0):
        super().__init__(dimension=1, name="MayHarvesting", critical_parameter=2.6044)
        self.r = r
        self.K = K
        self.d = d
        self._cache = {}

    def f(self, x: np.ndarray, mu: float) -> np.ndarray:
        x_val = np.maximum(x[0], 0.0)
        c = mu
        growth = self.r * x_val * (1.0 - x_val / self.K)
        grazing = c * (x_val**2) / (x_val**2 + self.d**2)
        return np.array([growth - grazing], dtype=np.float64)

    def g(self, x: np.ndarray, mu: float, sigma: float = 0.05) -> np.ndarray:
        return np.array([[sigma]], dtype=np.float64)

    def jacobian(self, x: np.ndarray, mu: float) -> np.ndarray:
        x_val = max(x[0], 1e-6)
        c = mu
        d2 = self.d**2
        x2 = x_val**2
        
        # d/dx [ r x (1 - x/K) ] = r (1 - 2x/K)
        d_growth = self.r * (1.0 - 2.0 * x_val / self.K)
        # d/dx [ c x^2 / (x^2 + d^2) ] = 2 c d^2 x / (x^2 + d^2)^2
        d_grazing = (2.0 * c * d2 * x_val) / ((x2 + d2)**2)
        
        j_val = d_growth - d_grazing
        return np.array([[j_val]], dtype=np.float64)

    def steady_state(self, mu: float) -> np.ndarray:
        """
        Finds the high-biomass stable fixed point x*(mu) for c = mu.
        Analytical solution via roots of the cubic polynomial:
            x^3 - K x^2 + (c*K/r + d^2) x - K*d^2 = 0
        """
        c = mu
        if c in self._cache:
            return self._cache[c]
            
        coeffs = [1.0, -self.K, (c * self.K / self.r) + (self.d**2), -self.K * (self.d**2)]
        roots = np.roots(coeffs)
        real_roots = np.sort([np.real(r) for r in roots if np.isreal(r) and np.real(r) > 0])
        
        # If 3 positive roots exist, the largest is the high stable state, middle is saddle, smallest is low stable
        if len(real_roots) == 3:
            res = np.array([real_roots[2]], dtype=np.float64)
        elif len(real_roots) >= 1:
            res = np.array([real_roots[-1]], dtype=np.float64)
        else:
            res = np.array([self.K], dtype=np.float64)
            
        self._cache[c] = res
        return res

    def is_collapsed(self, x: np.ndarray, mu: float) -> bool:
        # Collapse is defined as biomass dropping below threshold x_crit = 2.0 (falling into low attractor)
        return bool(x[0] < 2.0)
