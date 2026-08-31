"""
Abstract base class for dynamical systems exhibiting critical transitions.
All implementations provide exact drift vector fields, diffusion matrices,
analytical or numerical Jacobians, and theoretical steady-state metrics.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Tuple, Optional
import numpy as np
from scipy.linalg import solve_continuous_lyapunov


class DynamicalSystem(ABC):
    """
    Abstract base class for stochastic continuous-time dynamical systems.
    
    Governing SDE:
        dx(t) = f(x(t), mu(t)) dt + G(x(t), mu(t)) dW(t)
    """
    
    def __init__(self, dimension: int, name: str, critical_parameter: float):
        self.dimension = dimension
        self.name = name
        self.critical_parameter = critical_parameter

    @abstractmethod
    def f(self, x: np.ndarray, mu: float) -> np.ndarray:
        """
        Deterministic drift vector field f(x, mu).
        
        Args:
            x: State vector of shape (dimension,)
            mu: Scalar or vector control parameter
            
        Returns:
            Drift vector of shape (dimension,)
        """
        pass

    @abstractmethod
    def g(self, x: np.ndarray, mu: float, sigma: float = 0.05) -> np.ndarray:
        """
        Stochastic diffusion matrix G(x, mu).
        
        Args:
            x: State vector of shape (dimension,)
            mu: Control parameter
            sigma: Base noise intensity
            
        Returns:
            Dispersion matrix of shape (dimension, dimension)
        """
        pass

    @abstractmethod
    def jacobian(self, x: np.ndarray, mu: float) -> np.ndarray:
        """
        Analytical or high-order finite-difference Jacobian matrix J = df/dx at state x.
        
        Args:
            x: State vector of shape (dimension,)
            mu: Control parameter
            
        Returns:
            Jacobian matrix of shape (dimension, dimension)
        """
        pass

    @abstractmethod
    def steady_state(self, mu: float) -> np.ndarray:
        """
        Computes the stable equilibrium point x*(mu) for parameter mu prior to collapse.
        """
        pass

    @abstractmethod
    def is_collapsed(self, x: np.ndarray, mu: float) -> bool:
        """
        Evaluates whether state x has collapsed / exited the operational basin of attraction.
        """
        pass

    def eigenvalues(self, mu: float) -> np.ndarray:
        """
        Computes eigenvalues of the Jacobian at the stable equilibrium x*(mu).
        """
        x_star = self.steady_state(mu)
        j_mat = self.jacobian(x_star, mu)
        return np.linalg.eigvals(j_mat)

    def dominant_eigenvalue(self, mu: float) -> complex:
        """
        Returns the eigenvalue with the largest real part (closest to 0 from the left).
        """
        evals = self.eigenvalues(mu)
        idx = np.argmax(np.real(evals))
        return evals[idx]

    def theoretical_covariance(self, mu: float, sigma: float = 0.05) -> np.ndarray:
        """
        Computes the theoretical stationary covariance matrix C via continuous Lyapunov equation:
            J C + C J^T + G G^T = 0
            
        Valid for linearized Ornstein-Uhlenbeck process near stable steady state.
        """
        x_star = self.steady_state(mu)
        j_mat = self.jacobian(x_star, mu)
        g_mat = self.g(x_star, mu, sigma=sigma)
        q_mat = g_mat @ g_mat.T
        
        # Check stability: real parts of all eigenvalues must be negative
        evals = np.linalg.eigvals(j_mat)
        if np.any(np.real(evals) >= 0):
            return np.full((self.dimension, self.dimension), np.nan)
            
        try:
            c_mat = solve_continuous_lyapunov(j_mat, -q_mat)
            return c_mat
        except Exception:
            return np.full((self.dimension, self.dimension), np.nan)

    def theoretical_variance(self, mu: float, sigma: float = 0.05) -> float:
        """
        Returns theoretical variance of the leading variable or total trace variance.
        """
        cov = self.theoretical_covariance(mu, sigma=sigma)
        if np.isnan(cov).any():
            return np.nan
        return float(cov[0, 0])

    def theoretical_ar1(self, mu: float, dt: float) -> float:
        """
        Returns theoretical lag-1 autocorrelation AR(1) = exp(Re(lambda_max) * dt).
        """
        lam = self.dominant_eigenvalue(mu)
        if np.real(lam) >= 0:
            return 1.0
        return float(np.exp(np.real(lam) * dt))
