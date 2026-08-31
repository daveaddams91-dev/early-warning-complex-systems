"""
Regularized Elastic-Net Logistic Early-Warning Model (CEWF-ElasticNet).
Learns an optimal sparse linear combination of multi-indicator features with L1/L2 penalties.
"""

from typing import List, Optional, Tuple
import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from src.indicators.base_indicator import BaseIndicator
from src.models.base_model import BaseEarlyWarningModel


class ElasticNetWarningModel(BaseEarlyWarningModel):
    """
    Elastic-Net regularized logistic regression classifier.
    Predicts the calibrated posterior probability of an impending transition.
    """
    
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
            penalty='elasticnet',
            solver='saga',
            l1_ratio=l1_ratio,
            C=C,
            max_iter=1000,
            random_state=42
        )
        self.is_trained = False

    def train_on_labeled_data(
        self,
        X_train: np.ndarray,
        y_train: np.ndarray
    ) -> 'ElasticNetWarningModel':
        """
        Trains the classifier on labeled indicator feature matrices.
        X_train: (N_samples, n_indicators)
        y_train: (N_samples,) binary labels (0 = safe baseline, 1 = pre-transition)
        """
        valid_mask = ~np.isnan(X_train).any(axis=1)
        X_clean = X_train[valid_mask]
        y_clean = y_train[valid_mask]
        
        if len(np.unique(y_clean)) < 2:
            # Fallback if only one class
            self.is_trained = False
            return self
            
        X_scaled = self.scaler.fit_transform(X_clean)
        self.classifier.fit(X_scaled, y_clean)
        self.is_trained = True
        return self

    def fit(self, baseline_trajectories: List[np.ndarray], window_size: int = 50) -> 'ElasticNetWarningModel':
        # Default baseline fit: create pseudo-labels using Kendall trend consensus if no transition labels
        all_feats = []
        for traj in baseline_trajectories:
            feat = self.extract_indicator_features(traj, window_size=window_size)
            valid = feat[~np.isnan(feat).any(axis=1)]
            if len(valid) > 0:
                all_feats.append(valid)
                
        if len(all_feats) > 0:
            X = np.vstack(all_feats)
            # Label earlier portion as 0, later portion as 1 for demonstration if parameter ramped
            n = len(X)
            y = np.zeros(n)
            y[int(0.7 * n) :] = 1
            self.train_on_labeled_data(X, y)
        return self

    def predict_score(
        self,
        x: np.ndarray,
        window_size: int = 50,
        features: Optional[np.ndarray] = None
    ) -> np.ndarray:
        if features is None:
            features = self.extract_indicator_features(x, window_size=window_size)
            
        n_obs = len(features)
        scores = np.full(n_obs, np.nan, dtype=np.float64)
        
        if not self.is_trained:
            # If not trained, fall back to simple mean normalized score
            valid = ~np.isnan(features).any(axis=1)
            if np.sum(valid) > 0:
                mean_f = np.nanmean(features[valid], axis=0)
                std_f = np.nanstd(features[valid], axis=0) + 1e-6
                scores[valid] = np.mean(np.maximum((features[valid] - mean_f) / std_f, 0.0), axis=1)
            return scores
            
        for k in range(n_obs):
            row = features[k]
            if np.isnan(row).any():
                continue
            row_scaled = self.scaler.transform(row.reshape(1, -1))
            prob = self.classifier.predict_proba(row_scaled)[0, 1]
            scores[k] = float(prob)
            
        return scores
