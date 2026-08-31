"""
Abstract base class for early-warning composite models.
Enforces strictly causal rolling scoring without look-ahead bias.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional, Union
import numpy as np
from src.indicators.base_indicator import BaseIndicator


class BaseEarlyWarningModel(ABC):
    """
    Abstract base class for composite early-warning frameworks.
    """
    
    def __init__(self, name: str, indicators: List[BaseIndicator]):
        self.name = name
        self.indicators = indicators
        self.feature_names = [ind.name for ind in indicators]

    def extract_indicator_features(
        self,
        x: np.ndarray,
        window_size: int = 50,
        step: int = 1
    ) -> np.ndarray:
        """
        Computes all constituent indicators causally along time series x.
        
        Args:
            x: 1D or 2D array of shape (N,) or (N, D)
            window_size: Rolling window length
            step: Subsampling stride
            
        Returns:
            2D feature matrix of shape (N, n_indicators)
        """
        n_obs = len(x)
        n_ind = len(self.indicators)
        features = np.full((n_obs, n_ind), np.nan, dtype=np.float64)
        
        for idx, ind in enumerate(self.indicators):
            if ind.is_multivariate:
                feat = ind.compute_rolling(x, window_size=window_size, step=step)
            else:
                x_1d = x[:, 0] if x.ndim > 1 else x
                feat = ind.compute_rolling(x_1d, window_size=window_size, step=step)
            features[:, idx] = feat
            
        return features

    @abstractmethod
    def fit(self, baseline_trajectories: List[np.ndarray], window_size: int = 50) -> 'BaseEarlyWarningModel':
        """
        Calibrates model parameters using only baseline safe trajectories.
        """
        pass

    @abstractmethod
    def predict_score(
        self,
        x: np.ndarray,
        window_size: int = 50,
        features: Optional[np.ndarray] = None
    ) -> np.ndarray:
        """
        Computes the continuous composite early-warning score W(t) causally.
        
        Args:
            x: Observation trajectory
            window_size: Rolling window length
            features: Precomputed feature matrix (optional)
            
        Returns:
            1D array of shape (N,) containing warning scores.
        """
        pass

    def predict_alarm(
        self,
        x: np.ndarray,
        threshold: float,
        window_size: int = 50,
        features: Optional[np.ndarray] = None
    ) -> np.ndarray:
        """
        Computes binary alarms where W(t) >= threshold.
        """
        scores = self.predict_score(x, window_size=window_size, features=features)
        alarms = (scores >= threshold).astype(int)
        alarms[np.isnan(scores)] = 0
        return alarms
