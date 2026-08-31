"""
Game-Changer #2: The Adaptive Bayesian Early-Warning System (ABEWS).
Dynamically estimates P(indicator_i is informative | X_1:t) online and has the explicit
capability to abstain from false alarms when indicators conflict or noise dominates.
"""

from typing import List, Dict, Any, Optional, Tuple
import numpy as np
from src.indicators.base_indicator import BaseIndicator
from src.indicators.kendall_trend import RollingKendallTrend
from src.models.base_model import BaseEarlyWarningModel


class AdaptiveWarningSystem(BaseEarlyWarningModel):
    """
    Adaptive warning framework with dynamic indicator selection, consensus auditing,
    and explicit abstention ("None of these indicators are trustworthy").
    """

    def __init__(
        self,
        indicators: List[BaseIndicator],
        trend_window: int = 30,
        consensus_threshold: float = 0.35,
        min_snr_threshold: float = 1.2,
        name: str = "Adaptive-Bayesian-EWS"
    ):
        super().__init__(name=name, indicators=indicators)
        self.trend_window = trend_window
        self.consensus_threshold = consensus_threshold
        self.min_snr_threshold = min_snr_threshold
        self.trend_estimator = RollingKendallTrend(trend_window=trend_window)
        self.baseline_means = None
        self.baseline_stds = None

    def fit(self, baseline_trajectories: List[np.ndarray], window_size: int = 50, step: int = 1) -> 'AdaptiveWarningSystem':
        all_feats = []
        for traj in baseline_trajectories:
            feat = self.extract_indicator_features(traj, window_size=window_size, step=step)
            valid = feat[~np.isnan(feat).any(axis=1)]
            if len(valid) > 0:
                all_feats.append(valid)
        if len(all_feats) > 0:
            concat = np.vstack(all_feats)
            self.baseline_means = np.nanmean(concat, axis=0)
            self.baseline_stds = np.nanstd(concat, axis=0)
            self.baseline_stds[self.baseline_stds < 1e-6] = 1.0
        return self

    def estimate_indicator_weights(
        self,
        features: np.ndarray,
        tau_matrix: np.ndarray
    ) -> Tuple[np.ndarray, np.ndarray]:
        """
        Estimates online probability/weight vector w_i(t) and trustworthiness mask T(t).
        """
        n_obs, n_ind = features.shape
        weights = np.zeros((n_obs, n_ind), dtype=np.float64)
        trustworthy = np.zeros(n_obs, dtype=bool)

        for k in range(n_obs):
            row_tau = tau_matrix[k]
            if np.isnan(row_tau).any():
                continue

            # 1. Indicator Concordance Matrix C_ij = tau_i * tau_j
            # When C_ij > 0, indicators agree on direction
            signs = np.sign(row_tau)
            concordance = np.mean([signs[i] == signs[j] for i in range(n_ind) for j in range(i + 1, n_ind)]) if n_ind > 1 else 1.0

            # 2. Local Signal-to-Noise Ratio (SNR) in indicator space
            if k >= self.trend_window:
                sub_feats = features[k - self.trend_window + 1 : k + 1]
                mean_diff = np.abs(np.nanmean(sub_feats[-5:], axis=0) - np.nanmean(sub_feats[:5], axis=0))
                noise_std = np.nanstd(sub_feats, axis=0) + 1e-6
                snr = mean_diff / noise_std
            else:
                snr = np.ones(n_ind)

            # 3. Dynamic Bayesian Weighting P(ind_i informative | X_1:t)
            # Indicators with positive Kendall tau and high SNR receive exponentially higher posterior belief
            pos_tau = np.maximum(row_tau, 0.0)
            unnorm_weights = pos_tau * np.log1p(snr)
            total_w = np.sum(unnorm_weights)

            # 4. Abstention Criterion:
            # If concordance is too low (conflicting signals) or overall SNR is weak, ABSTAIN.
            is_trust = bool((concordance >= self.consensus_threshold) and (np.max(snr) >= self.min_snr_threshold) and (total_w > 0.1))
            trustworthy[k] = is_trust

            if is_trust and total_w > 1e-12:
                weights[k] = unnorm_weights / total_w
            else:
                weights[k] = np.zeros(n_ind)

        return weights, trustworthy

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

        # Compute rolling Kendall tau for each indicator
        tau_mat = np.full((n_obs, n_ind), np.nan, dtype=np.float64)
        for idx in range(n_ind):
            tau_mat[:, idx] = self.trend_estimator.compute(features[:, idx], step=step)

        # Estimate dynamic weights and trustworthiness online
        weights, trustworthy = self.estimate_indicator_weights(features, tau_mat)

        # Baseline normalized feature z-scores
        if self.baseline_means is None:
            means = np.nanmean(features[:min(n_obs, 50)], axis=0)
            stds = np.nanstd(features[:min(n_obs, 50)], axis=0) + 1e-6
        else:
            means = self.baseline_means
            stds = self.baseline_stds

        z_feats = np.maximum((features - means) / stds, 0.0)

        for k in range(n_obs):
            if np.isnan(features[k]).any():
                continue
            if not trustworthy[k]:
                # Explicitly Abstain from Alarm (Output 0 score)
                scores[k] = 0.0
            else:
                # Weighted consensus score
                scores[k] = float(np.dot(weights[k], z_feats[k]))

        return scores
