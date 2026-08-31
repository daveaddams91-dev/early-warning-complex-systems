"""
Regularized Elastic-Net Logistic Early-Warning Model (CEWF-ElasticNet).
"""

from typing import List, Optional
import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from src.indicators.base_indicator import BaseIndicator
from src.models.base_model import BaseEarlyWarningModel


class ElasticNetWarningModel(BaseEarlyWarningModel):
    def __init__(
        self,
        indicators: List[BaseIndicator],
        l1_ratio: float = 0.5,
        C: float = 1.0,
        name: str = "CEWF-ElasticNet"
    ):
        super().__init__(name=name, indicators=indicators)
        self.l1_ratio = l1_ratio
        self.C = C
        self.scaler = StandardScaler()
        self.classifier = LogisticRegression(
            solver='saga',
            l1_ratio=l1_ratio,
            C=C,
            max_iter=500,
            random_state=42
        )
        self.is_trained = False

    def train_on_labeled_data(self, X_train: np.ndarray, y_train: np.ndarray) -> 'ElasticNetWarningModel':
        valid_mask = ~np.isnan(X_train).any(axis=1)
        X_clean = X_train[valid_mask]
        y_clean = y_train[valid_mask]
        if len(np.unique(y_clean)) < 2:
            self.is_trained = False
            return self
        X_scaled = self.scaler.fit_transform(X_clean)
        self.classifier.fit(X_scaled, y_clean)
        self.is_trained = True
        return self

    def fit(self, baseline_trajectories: List[np.ndarray], window_size: int = 50, step: int = 1) -> 'ElasticNetWarningModel':
        all_feats = []
        for traj in baseline_trajectories:
            feat = self.extract_indicator_features(traj, window_size=window_size, step=step)
            valid = feat[~np.isnan(feat).any(axis=1)]
            if len(valid) > 0:
                all_feats.append(valid)
        if len(all_feats) > 0:
            X = np.vstack(all_feats)
            n = len(X)
            y = np.zeros(n)
            y[int(0.7 * n) :] = 1
            self.train_on_labeled_data(X, y)
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
            
        n_obs = len(features)
        scores = np.full(n_obs, np.nan, dtype=np.float64)
        valid_mask = ~np.isnan(features).any(axis=1)
        if np.sum(valid_mask) == 0:
            return scores
            
        if not self.is_trained:
            mean_f = np.nanmean(features[valid_mask], axis=0)
            std_f = np.nanstd(features[valid_mask], axis=0) + 1e-6
            scores[valid_mask] = np.mean(np.maximum((features[valid_mask] - mean_f) / std_f, 0.0), axis=1)
            return scores
            
        # Fast batch evaluation
        rows_scaled = self.scaler.transform(features[valid_mask])
        probs = self.classifier.predict_proba(rows_scaled)[:, 1]
        scores[valid_mask] = probs
        return scores
