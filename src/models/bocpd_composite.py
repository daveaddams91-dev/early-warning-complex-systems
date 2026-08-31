"""
Bayesian Online Changepoint Detection Composite Model (CEWF-BOCPD).
"""

from typing import List, Optional
import numpy as np
from src.indicators.base_indicator import BaseIndicator
from src.models.base_model import BaseEarlyWarningModel


class BayesianChangepointModel(BaseEarlyWarningModel):
    def __init__(
        self,
        indicators: List[BaseIndicator],
        hazard_rate: float = 200.0,
        prior_mean: float = 0.0,
        prior_var: float = 1.0,
        name: str = "CEWF-BOCPD"
    ):
        super().__init__(name=name, indicators=indicators)
        self.hazard_rate = hazard_rate
        self.prior_mean = prior_mean
        self.prior_var = prior_var

    def fit(self, baseline_trajectories: List[np.ndarray], window_size: int = 50, step: int = 1) -> 'BayesianChangepointModel':
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
        valid_indices = np.where(valid_mask)[0]
        if len(valid_indices) < 5:
            return scores
            
        feats_valid = features[valid_indices]
        mean_base = np.mean(feats_valid[:min(len(feats_valid), 50)], axis=0)
        std_base = np.std(feats_valid[:min(len(feats_valid), 50)], axis=0) + 1e-6
        norm_series = np.mean(np.maximum((feats_valid - mean_base) / std_base, 0.0), axis=1)
        
        T = len(norm_series)
        R = np.zeros((T + 1, T + 1))
        R[0, 0] = 1.0
        H = 1.0 / self.hazard_rate
        obs_var = 1.0
        inv_sqrt_2pi = 0.3989422804014327
        
        for t in range(T):
            obs = norm_series[t]
            r_lengths = np.arange(t + 1)
            post_var = 1.0 / (1.0 / self.prior_var + r_lengths / obs_var)
            pred_var = obs_var + post_var
            pred_std = np.sqrt(pred_var)
            
            # Fast vectorized Gaussian density evaluation
            inv_std = 1.0 / pred_std
            z = (obs - self.prior_mean) * inv_std
            pred_prob = (inv_sqrt_2pi * inv_std) * np.exp(-0.5 * z**2) + 1e-12
            
            growth_probs = R[r_lengths, t] * pred_prob * (1.0 - H)
            cp_prob = np.sum(R[r_lengths, t] * pred_prob * H)
            
            R[0, t + 1] = cp_prob
            R[1 : t + 2, t + 1] = growth_probs
            
            total = np.sum(R[:, t + 1])
            if total > 0:
                R[:, t + 1] /= total
                
            score_t = np.clip(np.sum(R[:10, t + 1]), 0.0, 1.0)
            orig_idx = valid_indices[t]
            scores[orig_idx] = float(score_t)
            
        return scores
