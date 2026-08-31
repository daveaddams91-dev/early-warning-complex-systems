"""
Non-Parametric Rank-Aggregation Composite Model (CEWF-Rank).
"""

from typing import List, Optional
import numpy as np
from src.indicators.base_indicator import BaseIndicator
from src.indicators.kendall_trend import RollingKendallTrend
from src.models.base_model import BaseEarlyWarningModel


class RankAggregationModel(BaseEarlyWarningModel):
    def __init__(
        self,
        indicators: List[BaseIndicator],
        trend_window: int = 30,
        aggregation_method: str = "mean",
        name: str = "CEWF-Rank"
    ):
        super().__init__(name=name, indicators=indicators)
        self.trend_window = trend_window
        self.aggregation_method = aggregation_method
        self.trend_estimator = RollingKendallTrend(trend_window=trend_window)

    def fit(self, baseline_trajectories: List[np.ndarray], window_size: int = 50, step: int = 1) -> 'RankAggregationModel':
        return self

    def predict_score(
        self,
        x: np.ndarray,
        window_size: int = 50,
        step: int = 1,
        features: Optional[np.ndarray] = None
    ) -> np.ndarray:
        if features is None:
            features = self.extract_indicator_features(x, window_size=window_size, step=step)
            
        n_obs, n_ind = features.shape
        taus = np.full((n_obs, n_ind), np.nan, dtype=np.float64)
        
        for idx in range(n_ind):
            series = features[:, idx]
            taus[:, idx] = self.trend_estimator.compute(series, step=step)
            
        scores = np.full(n_obs, np.nan, dtype=np.float64)
        
        for k in range(n_obs):
            row_tau = taus[k]
            if np.isnan(row_tau).any():
                continue
            pos_tau = np.maximum(row_tau, 0.0)
            if self.aggregation_method == "mean":
                scores[k] = float(np.mean(pos_tau))
            elif self.aggregation_method == "median":
                scores[k] = float(np.median(pos_tau))
            elif self.aggregation_method == "max":
                scores[k] = float(np.max(pos_tau))
            else:
                scores[k] = float(np.mean(pos_tau))
                
        return scores
