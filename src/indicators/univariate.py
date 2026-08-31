"""
Univariate early-warning indicators (Statistical, Dynamical, and Information-Theoretic).
"""

import math
from itertools import permutations
from typing import Optional, Dict
import numpy as np
import scipy.stats as st
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
        super().__init__(name="Autocorrelation_AR1", is_multivariate=False)

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
        val = st.skew(y, bias=False)
        return float(val) if not np.isnan(val) else 0.0


class KurtosisIndicator(BaseIndicator):
    """Rolling sample excess kurtosis (tail fatness / flickering)."""
    
    def __init__(self):
        super().__init__(name="Kurtosis", is_multivariate=False)

    def compute_window(self, window: np.ndarray) -> float:
        y = window if window.ndim == 1 else window[:, 0]
        if len(y) < 5:
            return np.nan
        val = st.kurtosis(y, bias=False)
        return float(val) if not np.isnan(val) else 0.0


class PermutationEntropyIndicator(BaseIndicator):
    """
    Bandt-Pompe (2002) Permutation Entropy H_perm.
    Measures dynamical irregularity / loss of complexity.
    """
    
    def __init__(self, m: int = 3, tau: int = 1):
        super().__init__(name=f"PermutationEntropy_m{m}_t{tau}", is_multivariate=False)
        self.m = m
        self.tau = tau
        self.max_entropy = np.log(float(math.factorial(m)))

    def compute_window(self, window: np.ndarray) -> float:
        y = window if window.ndim == 1 else window[:, 0]
        n = len(y)
        n_patterns = n - (self.m - 1) * self.tau
        if n_patterns <= 0:
            return np.nan
            
        patterns = {}
        for i in range(n_patterns):
            sub = y[i : i + self.m * self.tau : self.tau]
            # Get ordinal permutation rank
            perm = tuple(np.argsort(sub))
            patterns[perm] = patterns.get(perm, 0) + 1
            
        probs = np.array(list(patterns.values()), dtype=np.float64) / n_patterns
        entropy = -np.sum(probs * np.log(probs + 1e-12))
        # Normalize to [0, 1]
        norm_entropy = float(entropy / self.max_entropy)
        return norm_entropy


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
        # Detrend window linearly to avoid low-frequency DC bias
        y_detrend = y - np.linspace(y[0], y[-1], n)
        # Power spectrum via FFT
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
        # Clip ar1 strictly inside (0, 0.999)
        ar1_clipped = np.clip(ar1, 1e-4, 0.999)
        rate = -np.log(ar1_clipped) / self.dt
        return float(rate)
