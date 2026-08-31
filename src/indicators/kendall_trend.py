"""
Rolling causal Kendall tau non-parametric trend estimator.
Computes Kendall rank correlation tau between time and metric values over a rolling window.
"""

from typing import Optional
import numpy as np
import scipy.stats as st


class RollingKendallTrend:
    """
    Computes causal rolling Kendall tau trend statistic on any indicator series.
    Strictly non-leaking: at index k, uses only S[k - trend_window + 1 : k + 1].
    """
    
    def __init__(self, trend_window: int = 50):
        self.trend_window = trend_window

    def compute(self, indicator_series: np.ndarray) -> np.ndarray:
        """
        Computes rolling Kendall tau for a 1D indicator series.
        
        Returns:
            1D array of same length as indicator_series, with np.nan where window is incomplete.
        """
        n_obs = len(indicator_series)
        output = np.full(n_obs, np.nan, dtype=np.float64)
        
        if n_obs < self.trend_window:
            return output
            
        time_index = np.arange(self.trend_window, dtype=np.float64)
        
        for k in range(self.trend_window - 1, n_obs):
            sub = indicator_series[k - self.trend_window + 1 : k + 1]
            if np.isnan(sub).any() or np.all(sub == sub[0]):
                output[k] = 0.0
                continue
                
            res = st.kendalltau(time_index, sub)
            tau_val = res.correlation if not np.isnan(res.correlation) else 0.0
            output[k] = float(tau_val)
            
        return output
