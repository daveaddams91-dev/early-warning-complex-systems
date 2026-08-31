"""
Multi-Indicator Mahalanobis Anomaly Distance Model (CEWF-Mahalanobis).
Measures joint statistical distance of the heterogeneous indicator vector from the baseline stable distribution.
"""

from typing import List, Optional
import numpy as np
from src.indicators.base_indicator import BaseIndicator
from src.models.base_model import BaseEarlyWarningModel


class MultiIndicatorMahalanobisModel(BaseEarlyWarningModel):
    """
    Mahalanobis distance anomaly detector over multi-indicator feature space.
    """
    
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

    def fit(self, baseline_trajectories: List[np.ndarray], window_size: int = 50) -> 'MultiIndicatorMahalanobisModel':
        all_feats = []
        for traj in baseline_trajectories:
            feat = self.extract_indicator_features(traj, window_size=window_size)
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
        features: Optional[np.ndarray] = None
    ) -> np.ndarray:
        if features is None:
            features = self.extract_indicator_features(x, window_size=window_size)
            
        n_obs, n_ind = features.shape
        scores = np.full(n_obs, np.nan, dtype=np.float64)
        
        # If not fit externally, calibrate on first valid window segment
        if self.ref_mean is None or self.inv_cov is None:
            valid_idx = np.where(~np.isnan(features).any(axis=1))[0]
            if len(valid_idx) > 15:
                calib_end = valid_idx[min(len(valid_idx) // 4, 100)]
                calib_data = features[valid_idx[0] : calib_end + 1]
                self.ref_mean = np.nanmean(calib_data, axis=0)
                cov = np.cov(calib_data, rowvar=False)
                if cov.ndim == 0:
                    cov = np.array([[cov]])
                cov_reg = cov + np.eye(cov.shape[0]) * self.regularization
                self.inv_cov = np.linalg.pinv(cov_reg)
            else:
                self.ref_mean = np.zeros(n_ind)
                self.inv_cov = np.eye(n_ind)
                
        for k in range(n_obs):
            row = features[k]
            if np.isnan(row).any():
                continue
            diff = row - self.ref_mean
            dist_sq = float(diff @ self.inv_cov @ diff.T)
            scores[k] = np.sqrt(max(0.0, dist_sq))
            
        return scores
