"""
Abstract base class for early-warning indicators.
Enforces strict causal, non-leaking rolling-window evaluation.
"""

from abc import ABC, abstractmethod
from typing import Optional, Dict, Any
import numpy as np


class BaseIndicator(ABC):
    """
    Abstract base class for statistical, dynamical, information-theoretic,
    and network-based early warning indicators.
    """
    
    def __init__(self, name: str, is_multivariate: bool = False):
        self.name = name
        self.is_multivariate = is_multivariate

    @abstractmethod
    def compute_window(self, window: np.ndarray) -> float:
        """
        Computes the indicator value on a single discrete window.
        
        Args:
            window: 1D array of shape (window_size,) for univariate indicators,
                    or 2D array of shape (window_size, n_channels) for multivariate.
                    
        Returns:
            Scalar indicator metric value.
        """
        pass

    def compute_rolling(
        self,
        x: np.ndarray,
        window_size: int,
        step: int = 1
    ) -> np.ndarray:
        """
        Computes the indicator causally across a continuous or discrete time series.
        Output at index k strictly uses only x[max(0, k - window_size + 1) : k + 1].
        
        Args:
            x: 1D array of shape (N,) or 2D array of shape (N, D)
            window_size: Number of past observation samples in rolling window
            step: Rolling stride (default: 1)
            
        Returns:
            1D array of length N, with np.nan for indices < window_size - 1.
        """
        n_obs = len(x)
        output = np.full(n_obs, np.nan, dtype=np.float64)
        
        if n_obs < window_size:
            return output
            
        for k in range(window_size - 1, n_obs, step):
            window_data = x[k - window_size + 1 : k + 1]
            # Handle possible NaNs in window
            if np.isnan(window_data).any():
                val = np.nan
            else:
                try:
                    val = self.compute_window(window_data)
                except Exception:
                    val = np.nan
            output[k] = val
            
        # If step > 1, forward-fill evaluated values for continuous alignment
        if step > 1:
            last_valid = np.nan
            for k in range(n_obs):
                if not np.isnan(output[k]):
                    last_valid = output[k]
                elif not np.isnan(last_valid):
                    output[k] = last_valid
                    
        return output
