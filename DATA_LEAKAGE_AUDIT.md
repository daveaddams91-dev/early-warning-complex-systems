# DATA LEAKAGE & CAUSALITY AUDIT

**Audit Date**: September 2026  
**Auditor**: Principal Investigator & Hostile Software Auditor  
**Audit Standard**: Zero look-ahead bias, strict train/test separation, causal sliding windows.

---

## 1. Potential Leakage Pathways & Systematic Inspection

| Leakage Pathway | Potential Mechanism | Code Inspection Location | Verdict | Audit Demonstration / Evidence |
| :--- | :--- | :--- | :---: | :--- |
| **1. Look-Ahead Windowing** | Using centered rolling windows (e.g. `pd.Series.rolling(center=True)`) or future observations. | `src/indicators/base_indicator.py:L26-38` | **PASS (No Leakage)** | Slice indexing is strictly backward-looking: `window = x[k - window_size + 1 : k + 1]`. For any step $k$, indices $> k$ are never read. |
| **2. Whole-Series Normalization** | Z-scoring features using mean and standard deviation computed over the full test trajectory ($t \in [0, T]$). | `src/models/linear_composite.py:L40-58`, `src/models/mahalanobis_composite.py:L40-60` | **PASS (No Leakage)** | Means $\boldsymbol{\mu}_0$ and covariance $\mathbf{\Sigma}_0$ are computed exclusively on independent null calibration trajectories during `.fit()` or from initial calibration segments ($t \le 10\text{ s}$). |
| **3. Metric & Threshold Leakage** | Optimizing alarm thresholds using receiver operating characteristics on the test evaluation set. | `experiments/scripts/run_all_experiments.py:L148-154` | **PASS (No Leakage)** | The operational alarm threshold is determined solely as the 95th percentile of null (non-tipping) baseline trajectory scores: `thresh = np.percentile(valid_flat_null, 95)`. |
| **4. Collapse Time Leakage** | Passing ground-truth collapse time $t_{\text{crit}}$ to indicator or model calculation functions. | `src/models/base_model.py:L20-55` | **PASS (No Leakage)** | Feature extraction and model scoring functions `predict_score(x, window_size, step)` receive only raw state observations $\mathbf{x}_{1:t}$. $t_{\text{crit}}$ is referenced strictly in post-hoc metric evaluation (`metrics.py`). |
| **5. Model Fitting Contamination** | Fitting ML weights (e.g. ElasticNet logistic weights) on test ramp simulations. | `experiments/scripts/run_all_experiments.py:L114-118` | **PASS (No Leakage)** | Models are fitted on independent null trajectories (seeds 1000..1024). Test ramp trajectories use non-overlapping seeds (2000..2024). |
| **6. Trend Filter Leakage** | Running two-sided low-pass filters (e.g. `scipy.signal.filtfilt`) on time series before computing indicators. | `src/indicators/kendall_trend.py:L25-45` | **PASS (No Leakage)** | No forward-backward filtering is performed. The Kendall $\tau$ trend filter uses causal sliding slices of past indicator values: `series[k - w + 1 : k + 1]`. |

---

## 2. Code Verification Check: Causal Windowing

```python
# From src/indicators/base_indicator.py
def compute_rolling(self, x: np.ndarray, window_size: int = 50, step: int = 1) -> np.ndarray:
    n_obs = len(x)
    output = np.full(n_obs, np.nan, dtype=np.float64)
    # Starts at window_size - 1, reading ONLY [k - window_size + 1 : k + 1]
    for k in range(window_size - 1, n_obs, step):
        window = x[k - window_size + 1 : k + 1]
        output[k] = self.compute_window(window)
    return output
```

**Formal Mathematical Statement**:
$$\forall k \ge W-1, \quad \hat{S}_k = g(x_{k-W+1}, x_{k-W+2}, \dots, x_k)$$
$$\frac{\partial \hat{S}_k}{\partial x_{k+j}} \equiv 0, \quad \forall j \ge 1$$

---

## 3. Conclusion

The codebase is free of look-ahead bias, train/test contamination, threshold cheating, and data leakage. All reported metrics represent valid out-of-sample causal predictions.
