"""
Linear Composite Early-Warning Model (CEWF-Linear).
"""

from typing import List, Optional
import numpy as np
from src.indicators.base_indicator import BaseIndicator
from src.models.base_model import BaseEarlyWarningModel


class LinearCompositeModel(BaseEarlyWarningModel):
    def __init__(
        self,
        indicators: List[BaseIndicator],
        weights: Optional[np.ndarray] = None,
        name: str = "CEWF-Linear"
    ):
        super().__init__(name=name, indicators=indicators)
        n_ind = len(indicators)
        if weights is None:
            self.weights = np.full(n_ind, 1.0 / n_ind, dtype=np.float64)
        else:
            self.weights = np.array(weights, dtype=np.float64) / np.sum(weights)
        self.baseline_means = None
        self.baseline_stds = None

    def fit(self, baseline_trajectories: List[np.ndarray], window_size: int = 50, step: int = 1) -> 'LinearCompositeModel':
        all_feats = []
        for traj in baseline_trajectories:
            feat = self.extract_indicator_features(traj, window_size=window_size, step=step)
            valid_rows = feat[~np.isnan(feat).any(axis=1)]
            if len(valid_rows) > 0:
                all_feats.append(valid_rows)
        if len(all_feats) > 0:
            concat_feats = np.vstack(all_feats)
            self.baseline_means = np.nanmean(concat_feats, axis=0)
            self.baseline_stds = np.nanstd(concat_feats, axis=0)
            self.baseline_stds[self.baseline_stds < 1e-6] = 1.0
        else:
            n_ind = len(self.indicators)
            self.baseline_means = np.zeros(n_ind)
            self.baseline_stds = np.ones(n_ind)
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
        scores = np.full(n_obs, np.nan, dtype=np.float64)
        
        valid_mask = ~np.isnan(features).any(axis=1)
        if np.sum(valid_mask) == 0:
            return scores
            
        if self.baseline_means is None:
            valid_idx = np.where(valid_mask)[0]
            calib_end = valid_idx[min(len(valid_idx) // 4, 100)]
            calib_data = features[valid_idx[0] : calib_end + 1]
            means = np.nanmean(calib_data, axis=0)
            stds = np.nanstd(calib_data, axis=0)
            stds[stds < 1e-6] = 1.0
        else:
            means = self.baseline_means
            stds = self.baseline_stds
            
        norm_feats = (features[valid_mask] - means) / stds
        pos_norm = np.maximum(norm_feats, 0.0)
        scores[valid_mask] = pos_norm @ self.weights
        return scores
