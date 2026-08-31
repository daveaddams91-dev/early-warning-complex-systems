"""
Rolling causal Kendall tau non-parametric trend estimator.
Computes Kendall rank correlation tau between time and metric values over a rolling window.
"""

from typing import Optional
import numpy as np


class RollingKendallTrend:
    """
    Computes causal rolling Kendall tau trend statistic on any indicator series.
    Strictly non-leaking: at index k, uses only S[k - trend_window + 1 : k + 1].
    """
    
    def __init__(self, trend_window: int = 30):
        self.trend_window = trend_window
        w = trend_window
        self.denom = w * (w - 1) / 2.0
        self.i_idx, self.j_idx = np.triu_indices(w, k=1)

    def compute(self, indicator_series: np.ndarray, step: int = 1) -> np.ndarray:
        """
        Computes rolling Kendall tau for a 1D indicator series using fast vectorized pairwise signs.
        """
        n_obs = len(indicator_series)
        output = np.full(n_obs, np.nan, dtype=np.float64)
        
        if n_obs < self.trend_window:
            return output
            
        w = self.trend_window
        denom = self.denom
        i_idx = self.i_idx
        j_idx = self.j_idx
        
        for k in range(w - 1, n_obs, step):
            sub = indicator_series[k - w + 1 : k + 1]
            if np.isnan(sub).any():
                output[k] = 0.0
                continue
            # For i < j, concordant pair has sub[j] > sub[i]
            s = np.sign(sub[j_idx] - sub[i_idx])
            output[k] = float(np.sum(s) / denom)
            
        if step > 1:
            last_valid = np.nan
            for k in range(n_obs):
                if not np.isnan(output[k]):
                    last_valid = output[k]
                elif not np.isnan(last_valid):
                    output[k] = last_valid
                    
        return output
