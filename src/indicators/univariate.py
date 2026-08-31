"""
Univariate early-warning indicators (Statistical, Dynamical, and Information-Theoretic).
"""

import math
from typing import Optional, Dict
import numpy as np
from src.indicators.base_indicator import BaseIndicator


class VarianceIndicator(BaseIndicator):
    """Rolling sample variance sigma^2."""
    
    def __init__(self):
        super().__init__(name="Variance", is_multivariate=False)

    def compute_window(self, window: np.ndarray) -> float:
        y = window if window.ndim == 1 else window[:, 0]
        if len(y) < 2:
            return np.nan
        return float(np.var(y, ddof=1))


class AutocorrelationLag1Indicator(BaseIndicator):
    """Rolling lag-1 temporal autocorrelation AR(1)."""
    
    def __init__(self):
        super().__init__(name="AR(1)", is_multivariate=False)

    def compute_window(self, window: np.ndarray) -> float:
        y = window if window.ndim == 1 else window[:, 0]
        n = len(y)
        if n < 3:
            return np.nan
        mean = np.mean(y)
        dev = y - mean
        denom = np.sum(dev**2)
        if denom < 1e-12:
            return 0.0
        num = np.sum(dev[:-1] * dev[1:])
        return float(num / denom)


class SkewnessIndicator(BaseIndicator):
    """Rolling sample skewness (asymmetry)."""
    
    def __init__(self):
        super().__init__(name="Skewness", is_multivariate=False)

    def compute_window(self, window: np.ndarray) -> float:
        y = window if window.ndim == 1 else window[:, 0]
        if len(y) < 4:
            return np.nan
        dev = y - np.mean(y)
        s2 = np.mean(dev**2)
        if s2 < 1e-12:
            return 0.0
        m3 = np.mean(dev**3)
        return float(m3 / (s2**1.5))


class KurtosisIndicator(BaseIndicator):
    """Rolling sample excess kurtosis (tail fatness / flickering)."""
    
    def __init__(self):
        super().__init__(name="Kurtosis", is_multivariate=False)

    def compute_window(self, window: np.ndarray) -> float:
        y = window if window.ndim == 1 else window[:, 0]
        if len(y) < 5:
            return np.nan
        dev = y - np.mean(y)
        s2 = np.mean(dev**2)
        if s2 < 1e-12:
            return 0.0
        m4 = np.mean(dev**4)
        return float(m4 / (s2**2) - 3.0)


class PermutationEntropyIndicator(BaseIndicator):
    """
    Bandt-Pompe (2002) Permutation Entropy H_perm.
    Measures dynamical irregularity / loss of complexity.
    """
    
    def __init__(self, m: int = 3, tau: int = 1):
        super().__init__(name=f"PermutationEntropy", is_multivariate=False)
        self.m = m
        self.tau = tau
        self.max_entropy = np.log(float(math.factorial(m)))

    def compute_window(self, window: np.ndarray) -> float:
        y = window if window.ndim == 1 else window[:, 0]
        n = len(y)
        n_patterns = n - (self.m - 1) * self.tau
        if n_patterns <= 0:
            return np.nan
            
        # Fast vectorized path for default m=3, tau=1
        if self.m == 3 and self.tau == 1:
            y0, y1, y2 = y[:-2], y[1:-1], y[2:]
            c0 = (y0 < y1) & (y1 < y2)
            c1 = (y0 < y2) & (y2 <= y1)
            c2 = (y1 <= y0) & (y0 < y2)
            c3 = (y1 < y2) & (y2 <= y0)
            c4 = (y2 <= y0) & (y0 < y1)
            c5 = (y2 <= y1) & (y1 <= y0)
            counts = np.array([np.sum(c0), np.sum(c1), np.sum(c2), np.sum(c3), np.sum(c4), np.sum(c5)], dtype=np.float64)
            p = counts[counts > 0] / n_patterns
            entropy = -np.sum(p * np.log(p))
            return float(entropy / self.max_entropy)
            
        patterns = {}
        for i in range(n_patterns):
            sub = y[i : i + self.m * self.tau : self.tau]
            perm = tuple(np.argsort(sub))
            patterns[perm] = patterns.get(perm, 0) + 1
            
        probs = np.array(list(patterns.values()), dtype=np.float64) / n_patterns
        entropy = -np.sum(probs * np.log(probs + 1e-12))
        return float(entropy / self.max_entropy)


class SpectralReddeningIndicator(BaseIndicator):
    """
    Measures the concentration of power at low frequencies (spectral reddening).
    """
    
    def __init__(self, low_freq_fraction: float = 0.2):
        super().__init__(name="SpectralReddening", is_multivariate=False)
        self.low_freq_fraction = low_freq_fraction

    def compute_window(self, window: np.ndarray) -> float:
        y = window if window.ndim == 1 else window[:, 0]
        n = len(y)
        if n < 8:
            return np.nan
        y_detrend = y - np.linspace(y[0], y[-1], n)
        fft_vals = np.fft.rfft(y_detrend)
        psd = np.abs(fft_vals)**2
        if len(psd) <= 1 or np.sum(psd) < 1e-12:
            return 0.0
            
        k_cutoff = max(1, int(np.floor(len(psd) * self.low_freq_fraction)))
        low_power = np.sum(psd[:k_cutoff])
        total_power = np.sum(psd)
        return float(low_power / total_power)


class RecoveryRateIndicator(BaseIndicator):
    """
    Estimates empirical relaxation rate kappa = -ln(AR(1)) / dt.
    Approaches 0 as critical slowing down occurs.
    """
    
    def __init__(self, dt: float = 0.05):
        super().__init__(name="RecoveryRate", is_multivariate=False)
        self.dt = dt
        self.ar1_ind = AutocorrelationLag1Indicator()

    def compute_window(self, window: np.ndarray) -> float:
        ar1 = self.ar1_ind.compute_window(window)
        if np.isnan(ar1):
            return np.nan
        ar1_clipped = np.clip(ar1, 1e-4, 0.999)
        rate = -np.log(ar1_clipped) / self.dt
        return float(rate)
