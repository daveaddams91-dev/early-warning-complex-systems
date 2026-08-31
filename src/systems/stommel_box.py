"""
Stommel 2-Box Ocean Circulation Model (SYS-4).
Exhibits bistability and a saddle-node tipping point of the thermohaline circulation (AMOC).

Governing Equations:
    dT/dt = eta_1 * (T_0 - T) - |T - S| * T + sigma_T * dW_1
    dS/dt = eta_2 * (mu - S) - |T - S| * S + sigma_S * dW_2
"""

import numpy as np
from scipy.optimize import root
from src.systems.base import DynamicalSystem


class StommelBoxSystem(DynamicalSystem):
    """
    Stommel (1961) two-box ocean model.
    
    T: Temperature difference between low and high latitudes
    S: Salinity difference between low and high latitudes
    mu: Freshwater forcing / atmospheric freshwater flux (control parameter, mu_crit approx 1.25)
    """
    
    def __init__(self, eta1: float = 1.0, eta2: float = 0.3, T0: float = 1.0):
        super().__init__(dimension=2, name="StommelBox", critical_parameter=1.25)
        self.eta1 = eta1
        self.eta2 = eta2
        self.T0 = T0
        self._cache = {}

    def f(self, x: np.ndarray, mu: float) -> np.ndarray:
        T, S = x[0], x[1]
        q = T - S
        flow = abs(q)
        dT = self.eta1 * (self.T0 - T) - flow * T
        dS = self.eta2 * (mu - S) - flow * S
        return np.array([dT, dS], dtype=np.float64)

    def g(self, x: np.ndarray, mu: float, sigma: float = 0.02) -> np.ndarray:
        return np.diag([sigma, sigma]).astype(np.float64)

    def jacobian(self, x: np.ndarray, mu: float) -> np.ndarray:
        T, S = x[0], x[1]
        q = T - S
        # For the thermally driven state (T > S > 0, q > 0):
        if q >= 0:
            # dT/dt = eta1(T0 - T) - (T - S)T = eta1 T0 - eta1 T - T^2 + TS
            j00 = -self.eta1 - 2.0 * T + S
            j01 = T
            # dS/dt = eta2(mu - S) - (T - S)S = eta2 mu - eta2 S - TS + S^2
            j10 = -S
            j11 = -self.eta2 - T + 2.0 * S
        else:
            # Reverse circulation
            j00 = -self.eta1 + 2.0 * T - S
            j01 = -T
            j10 = S
            j11 = -self.eta2 + T - 2.0 * S
        return np.array([[j00, j01], [j10, j11]], dtype=np.float64)

    def steady_state(self, mu: float) -> np.ndarray:
        if mu in self._cache:
            return self._cache[mu]
            
        def obj(v):
            return self.f(v, mu)
            
        # Prior to collapse, T is near 0.8, S is near 0.5
        sol = root(obj, x0=[0.8, 0.5], method='hybr')
        if sol.success:
            res = sol.x.astype(np.float64)
            self._cache[mu] = res
            return res
        return np.array([0.8, 0.5], dtype=np.float64)

    def is_collapsed(self, x: np.ndarray, mu: float) -> bool:
        # Collapse when overturning circulation q = T - S drops below 0.15 (flow shutdown)
        q = x[0] - x[1]
        return bool(q < 0.15)
