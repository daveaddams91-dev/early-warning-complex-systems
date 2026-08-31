"""
Multi-Indicator Mahalanobis Anomaly Distance Model (CEWF-Mahalanobis).
"""

from typing import List, Optional
import numpy as np
from src.indicators.base_indicator import BaseIndicator
from src.models.base_model import BaseEarlyWarningModel


class MultiIndicatorMahalanobisModel(BaseEarlyWarningModel):
    def __init__(
        self,
        indicators: List[BaseIndicator],
        regularization: float = 1e-3,
        name: str = "CEWF-Mahalanobis"
    ):
        super().__init__(name=name, indicators=indicators)
        self.regularization = regularization
        self.ref_mean = None
        self.inv_cov = None

    def fit(self, baseline_trajectories: List[np.ndarray], window_size: int = 50, step: int = 1) -> 'MultiIndicatorMahalanobisModel':
        all_feats = []
        for traj in baseline_trajectories:
            feat = self.extract_indicator_features(traj, window_size=window_size, step=step)
            valid_rows = feat[~np.isnan(feat).any(axis=1)]
            if len(valid_rows) > 0:
                all_feats.append(valid_rows)
                
        if len(all_feats) > 0:
            concat_feats = np.vstack(all_feats)
            self.ref_mean = np.nanmean(concat_feats, axis=0)
            cov = np.cov(concat_feats, rowvar=False)
            if cov.ndim == 0:
                cov = np.array([[cov]])
            cov_reg = cov + np.eye(cov.shape[0]) * self.regularization
            self.inv_cov = np.linalg.pinv(cov_reg)
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
            
        if self.ref_mean is None or self.inv_cov is None:
            valid_idx = np.where(valid_mask)[0]
            calib_end = valid_idx[min(len(valid_idx) // 4, 100)]
            calib_data = features[valid_idx[0] : calib_end + 1]
            self.ref_mean = np.nanmean(calib_data, axis=0)
            cov = np.cov(calib_data, rowvar=False)
            if cov.ndim == 0:
                cov = np.array([[cov]])
            cov_reg = cov + np.eye(cov.shape[0]) * self.regularization
            self.inv_cov = np.linalg.pinv(cov_reg)
            
        diff = features[valid_mask] - self.ref_mean
        dist_sq = np.sum((diff @ self.inv_cov) * diff, axis=1)
        scores[valid_mask] = np.sqrt(np.maximum(dist_sq, 0.0))
        return scores
