"""
Coupled Multi-Node Network System (SYS-5).
Dakos & Bascompte (2014) mutualistic network model with logistic self-regulation and harvesting stress.

Governing Equations for node i:
    dx_i/dt = r_i * x_i * (1 - x_i / K_i) + sum_j [gamma * A_ij * x_j / (1 + h * sum_k A_ik * x_k)]
              - c(t) * x_i^2 / (x_i^2 + d^2) + sigma * dW_i
"""

import numpy as np
import networkx as nx
from scipy.optimize import root
from src.systems.base import DynamicalSystem


class CoupledNetworkSystem(DynamicalSystem):
    def __init__(self, n_nodes: int = 10, network_type: str = 'erdos_renyi', seed: int = 42,
                 r: float = 1.0, K: float = 10.0, gamma: float = 0.2, h: float = 0.1, d: float = 1.0):
        super().__init__(dimension=n_nodes, name=f"CoupledNetwork_{network_type}_N{n_nodes}", critical_parameter=4.8)
        self.n_nodes = n_nodes
        self.r = r
        self.K = K
        self.gamma = gamma
        self.h = h
        self.d = d
        
        # Build network topology
        if network_type == 'erdos_renyi':
            g = nx.erdos_renyi_graph(n_nodes, p=0.4, seed=seed)
            while not nx.is_connected(g):
                g = nx.erdos_renyi_graph(n_nodes, p=0.5, seed=seed + 1)
        elif network_type == 'scale_free':
            g = nx.barabasi_albert_graph(n_nodes, m=2, seed=seed)
        else:
            g = nx.cycle_graph(n_nodes)
            
        self.adj = nx.to_numpy_array(g, dtype=np.float64)
        self._cache = {}

    def f(self, x: np.ndarray, mu: float) -> np.ndarray:
        x_pos = np.maximum(x, 0.0)
        c = mu
        d2 = self.d**2
        
        # Mutualism input
        inter_in = self.adj @ x_pos
        mutualism = self.gamma * inter_in / (1.0 + self.h * inter_in)
        
        logistic = self.r * x_pos * (1.0 - x_pos / self.K)
        loss = c * (x_pos**2) / (x_pos**2 + d2)
        
        return logistic + mutualism - loss

    def g(self, x: np.ndarray, mu: float, sigma: float = 0.03) -> np.ndarray:
        return np.diag(np.full(self.n_nodes, sigma)).astype(np.float64)

    def jacobian(self, x: np.ndarray, mu: float) -> np.ndarray:
        x_pos = np.maximum(x, 1e-4)
        c = mu
        d2 = self.d**2
        
        inter_in = self.adj @ x_pos
        denom = (1.0 + self.h * inter_in)**2
        
        # d(mutualism_i)/dx_j = gamma * A_ij / denom_i
        j_mat = (self.gamma * self.adj) / denom[:, np.newaxis]
        
        # Diagonal elements: d(logistic_i)/dx_i - d(loss_i)/dx_i
        diag_logistic = self.r * (1.0 - 2.0 * x_pos / self.K)
        diag_loss = (2.0 * c * d2 * x_pos) / ((x_pos**2 + d2)**2)
        
        for i in range(self.n_nodes):
            j_mat[i, i] += diag_logistic[i] - diag_loss[i]
            
        return j_mat

    def steady_state(self, mu: float) -> np.ndarray:
        if mu in self._cache:
            return self._cache[mu]
            
        def obj(v):
            return self.f(v, mu)
            
        sol = root(obj, x0=np.full(self.n_nodes, 8.0), method='hybr')
        if sol.success and np.all(sol.x > 1.0):
            res = sol.x.astype(np.float64)
            self._cache[mu] = res
            return res
        return np.full(self.n_nodes, 8.0, dtype=np.float64)

    def is_collapsed(self, x: np.ndarray, mu: float) -> bool:
        # Collapse when average biomass drops below 2.5
        return bool(np.mean(x) < 2.5)
