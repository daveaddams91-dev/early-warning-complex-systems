"""
Bayesian Online Changepoint Detection Composite Model (CEWF-BOCPD).
Recursive online inference of posterior run-length probability without future leakage (Adams & MacKay, 2007).
"""

from typing import List, Optional
import numpy as np
import scipy.stats as st
from src.indicators.base_indicator import BaseIndicator
from src.models.base_model import BaseEarlyWarningModel


class BayesianChangepointModel(BaseEarlyWarningModel):
    """
    Bayesian Online Changepoint Detection (BOCPD) for multi-indicator feature streams.
    """
    
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

    def fit(self, baseline_trajectories: List[np.ndarray], window_size: int = 50) -> 'BayesianChangepointModel':
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
        
        # Summary 1D feature: mean normalized indicator
        valid_mask = ~np.isnan(features).any(axis=1)
        valid_indices = np.where(valid_mask)[0]
        if len(valid_indices) < 5:
            return scores
            
        feats_valid = features[valid_indices]
        mean_base = np.mean(feats_valid[:min(len(feats_valid), 50)], axis=0)
        std_base = np.std(feats_valid[:min(len(feats_valid), 50)], axis=0) + 1e-6
        norm_series = np.mean(np.maximum((feats_valid - mean_base) / std_base, 0.0), axis=1)
        
        # Online BOCPD recursion
        T = len(norm_series)
        R = np.zeros((T + 1, T + 1))
        R[0, 0] = 1.0
        
        # Constant hazard function
        H = 1.0 / self.hazard_rate
        
        # Sufficient statistics for Gaussian with known observation variance
        obs_var = 1.0
        
        for t in range(T):
            obs = norm_series[t]
            
            # Predictive distribution for each possible run length
            # Posterior parameters given run length r
            r_lengths = np.arange(t + 1)
            # Prior variance for run length r
            post_var = 1.0 / (1.0 / self.prior_var + r_lengths / obs_var)
            pred_var = obs_var + post_var
            pred_std = np.sqrt(pred_var)
            
            # Predictive probability under Gaussian: N(prior_mean, pred_var)
            pred_prob = st.norm.pdf(obs, loc=self.prior_mean, scale=pred_std) + 1e-12
            
            # Growth probabilities
            growth_probs = R[r_lengths, t] * pred_prob * (1.0 - H)
            
            # Changepoint probability
            cp_prob = np.sum(R[r_lengths, t] * pred_prob * H)
            
            # Update run length distribution
            R[0, t + 1] = cp_prob
            R[1 : t + 2, t + 1] = growth_probs
            
            # Normalize
            total = np.sum(R[:, t + 1])
            if total > 0:
                R[:, t + 1] /= total
                
            # Score: Probability that a changepoint occurred recently (run length <= 10)
            score_t = np.clip(np.sum(R[:10, t + 1]), 0.0, 1.0)
            orig_idx = valid_indices[t]
            scores[orig_idx] = float(score_t)
            
        return scores
