"""
Coupled Multi-Node Network System (SYS-5).
Simulates N interacting nodes with mutualistic / synergistic coupling and harvesting stress,
exhibiting localized or cascading critical transitions.

Governing Equations for node i:
    dx_i/dt = x_i * (alpha_i - beta_i * x_i + sum_j [A_ij * x_j / (1 + h * sum_k A_ik * x_k)]) 
              - c(t) * x_i^2 / (x_i^2 + d^2) + sigma * dW_i
"""

import numpy as np
import networkx as nx
from scipy.optimize import root
from src.systems.base import DynamicalSystem


class CoupledNetworkSystem(DynamicalSystem):
    """
    Coupled Multi-Node Network System.
    
    Parameters:
        n_nodes: Number of nodes N (default: 10)
        network_type: 'erdos_renyi', 'scale_free', or 'ring'
        seed: Random seed for topology generation
        h: Handling time / saturation parameter
        d: Half-saturation constant for harvesting loss
    """
    
    def __init__(self, n_nodes: int = 10, network_type: str = 'erdos_renyi', seed: int = 42,
                 h: float = 0.1, d: float = 1.0):
        super().__init__(dimension=n_nodes, name=f"CoupledNetwork_{network_type}_N{n_nodes}", critical_parameter=2.85)
        self.n_nodes = n_nodes
        self.h = h
        self.d = d
        self.rng = np.random.default_rng(seed)
        
        # Base biological parameters
        self.alpha = 0.5 + 0.1 * self.rng.standard_normal(n_nodes)
        self.beta = np.full(n_nodes, 0.5)
        
        # Build network topology
        if network_type == 'erdos_renyi':
            g = nx.erdos_renyi_graph(n_nodes, p=0.35, seed=seed)
            # Ensure connected
            while not nx.is_connected(g):
                g = nx.erdos_renyi_graph(n_nodes, p=0.45, seed=seed + 1)
        elif network_type == 'scale_free':
            g = nx.barabasi_albert_graph(n_nodes, m=2, seed=seed)
        else:
            g = nx.cycle_graph(n_nodes)
            
        self.adj = nx.to_numpy_array(g, dtype=np.float64)
        # Normalize adjacency coupling weights
        degrees = np.sum(self.adj, axis=1)
        degrees[degrees == 0] = 1.0
        self.denom_factor = 1.0 + self.h * degrees
        self._cache = {}

    def f(self, x: np.ndarray, mu: float) -> np.ndarray:
        x_pos = np.maximum(x, 0.0)
        c = mu
        d2 = self.d**2
        
        # Mutualistic interaction term: (A @ x) / denom_factor
        interaction = (self.adj @ x_pos) / self.denom_factor
        
        # Intrinsic growth + mutualism: x_i * (alpha_i - beta_i * x_i + interaction_i)
        growth = x_pos * (self.alpha - self.beta * x_pos + interaction)
        
        # Harvesting loss term
        loss = c * (x_pos**2) / (x_pos**2 + d2)
        
        return growth - loss

    def g(self, x: np.ndarray, mu: float, sigma: float = 0.03) -> np.ndarray:
        return np.diag(np.full(self.n_nodes, sigma)).astype(np.float64)

    def jacobian(self, x: np.ndarray, mu: float) -> np.ndarray:
        x_pos = np.maximum(x, 1e-5)
        c = mu
        d2 = self.d**2
        
        # Compute vector of mutualistic inputs
        interaction = (self.adj @ x_pos) / self.denom_factor
        
        # Diagonal elements:
        # d/dx_i [ x_i*(alpha_i - beta_i*x_i + interaction_i) - c*x_i^2/(x_i^2 + d^2) ]
        diag_growth = self.alpha - 2.0 * self.beta * x_pos + interaction
        diag_loss = (2.0 * c * d2 * x_pos) / ((x_pos**2 + d2)**2)
        diag = diag_growth - diag_loss
        
        # Off-diagonal elements: d/dx_j = x_i * A_ij / denom_factor_i
        off_diag = (x_pos[:, np.newaxis] * self.adj) / self.denom_factor[:, np.newaxis]
        
        j_mat = off_diag.copy()
        np.fill_diagonal(j_mat, diag)
        return j_mat

    def steady_state(self, mu: float) -> np.ndarray:
        if mu in self._cache:
            return self._cache[mu]
            
        def obj(v):
            return self.f(v, mu)
            
        sol = root(obj, x0=np.full(self.n_nodes, 2.5), method='hybr')
        if sol.success:
            res = np.maximum(sol.x, 0.1).astype(np.float64)
            self._cache[mu] = res
            return res
        return np.full(self.n_nodes, 2.0, dtype=np.float64)

    def is_collapsed(self, x: np.ndarray, mu: float) -> bool:
        # Network cascade defined as >= 50% of nodes dropping below x_i < 1.0
        collapsed_nodes = np.sum(x < 1.0)
        return bool(collapsed_nodes >= self.n_nodes / 2)
