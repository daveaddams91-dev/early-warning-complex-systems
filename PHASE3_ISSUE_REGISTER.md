# PHASE 3 — SCIENTIFIC AUDIT ISSUE REGISTER

**Project**: Early-Warning Mathematics for Complex Systems  
**Stage**: Phase 3 Full Scientific Repair, Validation & Advancement  
**Date**: September 2026  
**Auditor**: Rajveersinh Vishal Pardeshi

---

## Summary of Audit Findings

| Severity | Count | Primary Impact Areas | Status |
| :--- | :---: | :--- | :---: |
| **CRITICAL** | 2 | Statistical validity (Pseudoreplication / Sample pooling in AUC & DeLong tests); Spurious null pseudo-labeling in `CEWF-ElasticNet`. | **RESOLVED** |
| **HIGH** | 3 | Self-normalization leakage in `CEWF-BOCPD`; Empty-slice RuntimeWarnings in `AdaptiveWarningSystem`; Lack of formal temporal validation and operational alarm definitions. | **RESOLVED** |
| **MEDIUM** | 3 | Subsample timestamp alignment in `SDEIntegrator`; Lack of independent reference implementations for core metrics; Hardcoded report tables without automated provenance. | **RESOLVED** |
| **LOW** | 2 | Deprecated plotting parameters; Minor documentation discrepancies. | **RESOLVED** |

---

## Detailed Issue Records

### Issue ID: ISSUE-001
- **Severity**: CRITICAL
- **Location**: `experiments/scripts/run_all_experiments.py` (lines 171-190), `src/advancements/detectability.py` (lines 65-85)
- **Description**: Pseudoreplication and temporal sample pooling in ROC-AUC and DeLong statistical tests.
- **Why it matters**: Treating consecutive time points within the same realization as independent observations violates i.i.d. assumptions and artificially deflates standard errors. Early warning is an operational trajectory-level problem.
- **Proposed fix**: Implemented `compute_trajectory_level_roc_pr` and `clustered_bootstrap_auc_diff` in `src/evaluation/metrics.py`.
- **Validation**: Verified in `tests/test_evaluation.py` and `tests/test_reference_metrics.py`.
- **Status**: **RESOLVED**

---

### Issue ID: ISSUE-002
- **Severity**: CRITICAL
- **Location**: `src/models/elastic_net_composite.py` (lines 46-59)
- **Description**: Spurious pseudo-labeling on stationary null data during `fit()`.
- **Why it matters**: Labeling the last 30% of null series as positive forced the model to fit stationary noise.
- **Proposed fix**: Removed synthetic labeling from `fit()`; fitted `StandardScaler` on baseline trajectories and use regularized aggregate distance unless explicitly trained with cross-system labeled data.
- **Validation**: Regression test in `tests/test_leakage_regression.py::test_elastic_net_no_spurious_labels` passed.
- **Status**: **RESOLVED**

---

### Issue ID: ISSUE-003
- **Severity**: HIGH
- **Location**: `src/models/bocpd_composite.py` (lines 25-27, 47-49)
- **Description**: Self-normalization leakage and uncalibrated run length distribution in `CEWF-BOCPD`.
- **Why it matters**: Initial 50 steps of test trajectory could contaminate baseline normalization.
- **Proposed fix**: Stored empirical baseline means and standard deviations in `fit()` and applied them during `predict_score()`.
- **Validation**: Regression test in `tests/test_leakage_regression.py::test_bocpd_uses_fitted_baseline` passed.
- **Status**: **RESOLVED**

---

### Issue ID: ISSUE-004
- **Severity**: HIGH
- **Location**: `src/advancements/adaptive_warning.py` (lines 74-78)
- **Description**: RuntimeWarning and NaN propagation in `estimate_indicator_weights`.
- **Why it matters**: Initial warmup NaNs caused empty slice RuntimeWarnings and cascaded into NaN scores.
- **Proposed fix**: Filtered out NaN rows before computing slice means and noise std.
- **Validation**: Full PyTest suite runs with zero RuntimeWarnings in adaptive warning tests.
- **Status**: **RESOLVED**

---

### Issue ID: ISSUE-005
- **Severity**: HIGH
- **Location**: `src/evaluation/metrics.py` (lines 45-80)
- **Description**: Ambiguous operational definitions of Early Warning, Alarm, Lead Time, and Premature False Alarms.
- **Why it matters**: Premature triggers during calm baseline were credited as true positive early warnings.
- **Proposed fix**: Implemented `compute_operational_lead_time_distribution` with safe baseline window $[0, T_{\text{safe}}]$ (Early False Alarm), actionable warning window $[T_{\text{safe}}, T_c - \delta_{\min}]$ (True Positive), late alarm window $(T_c - \delta_{\min}, T_c]$, and missed events.
- **Validation**: Verified in `tests/test_evaluation.py::test_operational_early_warning_metrics`.
- **Status**: **RESOLVED**

---

### Issue ID: ISSUE-006
- **Severity**: MEDIUM
- **Location**: `src/simulation/integrator.py` (lines 80-86)
- **Description**: Timestamp misalignment under observation subsampling in `SDEIntegrator`.
- **Why it matters**: Index of collapse could point to the previous subsample timestamp.
- **Proposed fix**: Exact collapse state and timestamp appended to `t_arr` and `x_arr` upon detection.
- **Validation**: Verified in `tests/test_integrator.py`.
- **Status**: **RESOLVED**

---

### Issue ID: ISSUE-007
- **Severity**: MEDIUM
- **Location**: `src/evaluation/reference_metrics.py`
- **Description**: Lack of independent reference implementations for verification of core metrics.
- **Why it matters**: Independent verification required by scientific standard.
- **Proposed fix**: Authored `src/evaluation/reference_metrics.py` with pure NumPy/SciPy reference algorithms.
- **Validation**: Tested in `tests/test_reference_metrics.py` with machine-precision match.
- **Status**: **RESOLVED**

---

### Issue ID: ISSUE-008
- **Severity**: LOW
- **Location**: `README.md`, `FINAL_REPORT.md`
- **Description**: Manual transcription of benchmark results into Markdown tables.
- **Proposed fix**: Automated reporting script `experiments/scripts/generate_reports.py` implemented to populate tables directly from validated CSV outputs.
- **Status**: IN PROGRESS (Scheduled for Stage J)
