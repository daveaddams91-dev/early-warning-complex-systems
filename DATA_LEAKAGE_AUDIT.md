# COMPREHENSIVE DATA-LEAKAGE & CAUSALITY AUDIT (PHASE 3)

**Project**: Early-Warning Mathematics for Complex Systems  
**Stage**: Phase 3 Line-by-Line Causality Verification  
**Standard**: Strict Causal Filtering ($\partial \hat{S}_k / \partial x_{k+j} \equiv 0, \forall j \ge 1$), No Future Window Contamination, No Test-Time Calibration Leakage  
**Date**: September 2026  

---

## 1. Line-by-Line Causality Audit Across Pipeline Components

### 1.1 Sliding Window Indicators (`src/indicators/`)
- **Inspection**:
  - `compute_rolling(x, window_size, step)`: At step $k$, slices are formed via `x[k - window_size + 1 : k + 1]`.
  - Slice upper bound `k + 1` in Python corresponds to observations $x_0, x_1, \dots, x_k$.
  - Future observations $x_{k+1}, x_{k+2}, \dots$ are strictly excluded.
- **Mathematical Proof**:
  $$\frac{\partial \hat{S}_k}{\partial x_{k+j}} \equiv 0, \quad \forall j \ge 1$$
- **Finding**: **STRICTLY CAUSAL (NO LEAKAGE)**.

### 1.2 Kendall Rank Correlation Trend (`src/indicators/kendall_trend.py`)
- **Inspection**:
  - Sub-slice is `indicator_series[k - trend_window + 1 : k + 1]`.
  - Pairs are evaluated with $i < j$ between time and metric values strictly within the trailing window.
- **Finding**: **STRICTLY CAUSAL (NO LEAKAGE)**.

### 1.3 Composite Model Calibration & Baseline Normalization (`src/models/`)
- **Inspection of `CEWF-Mahalanobis`**:
  - Reference mean $\boldsymbol{\mu}_0$ and inverse covariance $\mathbf{\Sigma}_0^{-1}$ are fitted strictly on independent null baseline trajectories (`seed=1000..1024`).
  - Prediction on test trajectories applies:
    $$D_M(x_k) = \sqrt{(\mathbf{f}(x_k) - \boldsymbol{\mu}_0)^T \mathbf{\Sigma}_0^{-1} (\mathbf{f}(x_k) - \boldsymbol{\mu}_0)}$$
  - Test trajectories never enter covariance estimation.
  - **Finding**: **STRICTLY CAUSAL (NO LEAKAGE)**.

- **Inspection of `CEWF-BOCPD` (Issue ISSUE-003)**:
  - `fit()` was a no-op (`return self`).
  - `predict_score()` computed:
    `mean_base = np.mean(feats_valid[:min(len(feats_valid), 50)], axis=0)`
  - **Audit Verdict**: **PARTIAL LEAKAGE / UNCALIBRATED COVARIANCE SHIFT**. Normalizing a test trajectory with its own initial 50 time steps can introduce calibration bias if the test trajectory experiences early transient fluctuations.
  - **Fix**: Update `BayesianChangepointModel.fit()` to record empirical baseline means and standard deviations from independent null trajectories, and use those fixed parameters during `predict_score()`.

- **Inspection of `CEWF-ElasticNet` (Issue ISSUE-002)**:
  - `fit()` assigned synthetic label $y=1$ to the last 30% of null baseline series.
  - **Audit Verdict**: **PSEUDO-LABELING ON STATIONARY NULL DATA**. While not looking into the future of test trajectories, it trains on pure noise artifacts.
  - **Fix**: Replace synthetic labeling with an out-of-system trained linear classifier or unsupervised density anomaly score.

---

## 2. Evaluation & Metric Leakage Audit (`src/evaluation/metrics.py`)

### 2.1 Critical Transition Timestamp $T_c$
- **Inspection**:
  - Is $T_c$ passed into the models during warning score generation?
  - **Code Check**: `m.predict_score(x, window_size, step)` receives only the raw time series $x(t)$. It receives neither $T_c$ nor the parameter ramp function $\mu(t)$.
  - **Finding**: **NO LEAKAGE TO MODEL**.
  
### 2.2 Operational Alarm Definition & Safe Baseline Window (Issue ISSUE-005)
- **Inspection**:
  - Does the metric allow premature alarms during the safe baseline period to count as successful early warnings?
  - **Code Check**: In historical `compute_lead_time_distribution`:
    `if first_alarm_time <= t_crit - min_lead_time: lead_time = t_crit - first_alarm_time; detected_count += 1`
  - **Audit Verdict**: **EVALUATION ARTIFACT (Premature Alarm Crediting)**. If a threshold is set so low that it triggers at $t=1.0\text{ s}$ during the calm baseline, it was credited as a True Positive with $L = 119\text{ s}$.
  - **Fix**: Partition the timeline into:
    1. **Safe Baseline Window $[0, T_{\text{baseline}}]$**: Any trigger here is classified as an Early False Alarm ($FA_{\text{early}}$).
    2. **Actionable Early Warning Window $[T_{\text{baseline}}, T_c - \delta_{\min}]$**: Triggers here count as valid True Positive warnings with actionable lead time $L = T_c - T_w$.
    3. **Late Alarm Window $(T_c - \delta_{\min}, T_c]$**: Triggers here are counted as Late Alarms (unactionable).
    4. **Post-Collapse $(> T_c)$**: Missed detection (False Negative).

---

## 3. Data Leakage Checklist Summary

| Potential Leakage Vector | Evaluated Component | Line / File | Status | Remediation Required |
| :--- | :--- | :--- | :---: | :--- |
| **Future Observations in Features** | `Variance`, `AR(1)`, etc. | `src/indicators/univariate.py` | **PASS** | None. Strict backward slicing verified. |
| **Collapse Time in Feature Extraction**| `BaseEarlyWarningModel` | `src/models/base_model.py` | **PASS** | None. $T_c$ never passed to models. |
| **Self-Normalization on Test Data** | `CEWF-BOCPD` | `src/models/bocpd_composite.py:47`| **FAIL** | Standardize via stored baseline parameters. |
| **Supervised Labels on Null Data** | `CEWF-ElasticNet` | `src/models/elastic_net_composite.py:57`| **FAIL** | Eliminate ad-hoc pseudo-labels. |
| **Premature Alarm Crediting** | `compute_lead_time` | `src/evaluation/metrics.py:76` | **FAIL** | Enforce safe baseline window exclusion. |
| **Temporal Data Shuffling** | Train/Test splitters | Benchmark scripts | **PASS** | Chronological ordering strictly preserved. |
