"""
Multivariate and Network-based early-warning indicators.
"""

from typing import Optional, Dict
import numpy as np
from scipy.linalg import eigh
from src.indicators.base_indicator import BaseIndicator


class PCA1VarianceIndicator(BaseIndicator):
    """
    Leading eigenvalue (PC1 variance) of the rolling covariance matrix.
    Captures variance along the dominant collective fluctuation axis.
    """
    
    def __init__(self):
        super().__init__(name="PCA1_Variance", is_multivariate=True)

    def compute_window(self, window: np.ndarray) -> float:
        w = np.atleast_2d(window)
        if w.shape[0] < 3 or w.shape[1] < 1:
            return np.nan
        if w.shape[1] == 1:
            return float(np.var(w[:, 0], ddof=1))
            
        cov = np.cov(w, rowvar=False)
        if np.isnan(cov).any():
            return np.nan
        # Eigenvalues of symmetric covariance matrix
        evals = np.linalg.eigvalsh(cov)
        return float(np.max(evals))


class GeneralizedVarianceIndicator(BaseIndicator):
    """
    Log-determinant of regularized sample covariance matrix.
    Measures the volume of multidimensional phase-space dispersion.
    """
    
    def __init__(self, regularization: float = 1e-4):
        super().__init__(name="GeneralizedVariance", is_multivariate=True)
        self.reg = regularization

    def compute_window(self, window: np.ndarray) -> float:
        w = np.atleast_2d(window)
        if w.shape[0] < 3:
            return np.nan
        if w.shape[1] == 1:
            return float(np.log(np.var(w[:, 0], ddof=1) + self.reg))
            
        cov = np.cov(w, rowvar=False)
        # Add regularization to diagonal for numerical stability
        cov_reg = cov + np.eye(cov.shape[0]) * self.reg
        sign, logdet = np.linalg.slogdet(cov_reg)
        if sign <= 0:
            return np.nan
        return float(logdet)


class MahalanobisDistanceIndicator(BaseIndicator):
    """
    Mean Mahalanobis statistical distance of window samples from a baseline reference distribution.
    """
    
    def __init__(self, ref_mean: Optional[np.ndarray] = None, ref_cov: Optional[np.ndarray] = None, reg: float = 1e-3):
        super().__init__(name="MahalanobisDistance", is_multivariate=True)
        self.ref_mean = ref_mean
        self.ref_cov = ref_cov
        self.reg = reg
        self._inv_cov = None
        if ref_cov is not None:
            cov_reg = ref_cov + np.eye(ref_cov.shape[0]) * reg
            self._inv_cov = np.linalg.pinv(cov_reg)

    def set_reference(self, baseline_data: np.ndarray):
        """Sets reference mean and covariance from initial stable baseline window."""
        b = np.atleast_2d(baseline_data)
        self.ref_mean = np.mean(b, axis=0)
        self.ref_cov = np.cov(b, rowvar=False)
        if self.ref_cov.ndim == 0:
            self.ref_cov = np.array([[self.ref_cov]])
        cov_reg = self.ref_cov + np.eye(self.ref_cov.shape[0]) * self.reg
        self._inv_cov = np.linalg.pinv(cov_reg)

    def compute_window(self, window: np.ndarray) -> float:
        w = np.atleast_2d(window)
        if self.ref_mean is None or self._inv_cov is None:
            # Self-reference to first half of window if not explicitly initialized
            mid = max(2, len(w) // 2)
            self.set_reference(w[:mid])
            
        diff = w - self.ref_mean
        # Compute Mahalanobis distance for each row: d_i = sqrt(diff_i @ inv_cov @ diff_i^T)
        dist_sq = np.sum((diff @ self._inv_cov) * diff, axis=1)
        mean_dist = np.mean(np.sqrt(np.maximum(dist_sq, 0.0)))
        return float(mean_dist)


class DynamicalNetworkBiomarkerIndicator(BaseIndicator):
    """
    Chen et al. (2012) Dynamical Network Biomarker (DNB) Index.
    Identifies coordinated subnetwork fluctuations before systemic collapse.
    """
    
    def __init__(self):
        super().__init__(name="DNB_Index", is_multivariate=True)

    def compute_window(self, window: np.ndarray) -> float:
        w = np.atleast_2d(window)
        n_samples, n_nodes = w.shape
        if n_samples < 5 or n_nodes < 2:
            return np.nan
            
        std_nodes = np.std(w, axis=0, ddof=1)
        mean_std = np.mean(std_nodes)
        
        corr_mat = np.corrcoef(w, rowvar=False)
        if np.isnan(corr_mat).any():
            return np.nan
            
        # Upper triangle correlations
        upper_idx = np.triu_indices(n_nodes, k=1)
        mean_abs_corr = np.mean(np.abs(corr_mat[upper_idx]))
        
        # DNB score = mean_std * mean_internal_correlation
        dnb_score = mean_std * mean_abs_corr
        return float(dnb_score)


class AlgebraicConnectivityIndicator(BaseIndicator):
    """
    Fiedler eigenvalue lambda_2 of the correlation graph Laplacian.
    Measures collective synchronization and algebraic connectivity across nodes.
    """
    
    def __init__(self, corr_threshold: float = 0.3):
        super().__init__(name="AlgebraicConnectivity", is_multivariate=True)
        self.corr_threshold = corr_threshold

    def compute_window(self, window: np.ndarray) -> float:
        w = np.atleast_2d(window)
        n_samples, n_nodes = w.shape
        if n_samples < 5 or n_nodes < 3:
            return np.nan
            
        corr_mat = np.corrcoef(w, rowvar=False)
        if np.isnan(corr_mat).any():
            return np.nan
            
        # Adjacency from thresholded absolute correlation
        adj = (np.abs(corr_mat) > self.corr_threshold).astype(np.float64)
        np.fill_diagonal(adj, 0.0)
        
        # Laplacian L = D - A
        degrees = np.sum(adj, axis=1)
        laplacian = np.diag(degrees) - adj
        
        evals = np.linalg.eigvalsh(laplacian)
        # Second smallest eigenvalue (Fiedler eigenvalue)
        fiedler = evals[1] if len(evals) > 1 else 0.0
        return float(max(0.0, fiedler))
