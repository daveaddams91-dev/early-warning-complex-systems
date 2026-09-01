# PHASE 3 — CHECKPOINT A: REPOSITORY AUDIT & REPRODUCTION GATE

**STAGE**: STAGE A (Full Repository Audit, Provenance Tracing & Metric Verification)  
**Date**: September 2026  

---

## 1. Core Evaluation Matrix

- **Research Question**: Are the reported early-warning results scientifically valid, causal, and statistically sound, or are they inflated by pseudoreplication, sample pooling, or calibration artifacts?
- **Current Hypothesis**: The raw dynamical models and SDE simulations are physically sound, but the historical time-slice pooling evaluation creates massive pseudoreplication, inflating statistical significance. Composite models require rigorous trajectory-level validation and unsupervised calibration.

### What was completed:
1. Conducted line-by-line inspection across the entire codebase (`src/`, `tests/`, `experiments/`, `docs/`).
2. Created **`PHASE3_ISSUE_REGISTER.md`** classifying 8 critical, high, medium, and low issues.
3. Created **`results/historical/`** freezing the original outputs, and **`results/validated/`** for corrected outputs.
4. Executed clean reproduction audit in **`REPRODUCTION_AUDIT.md`**, verifying all published numbers down to 4 decimal places given historical code and seeds.
5. Performed comprehensive line-by-line data-leakage and causality audit in **`DATA_LEAKAGE_AUDIT.md`**.
6. Implemented independent reference metric suite in `src/evaluation/reference_metrics.py` and validated numerical equality in `tests/test_reference_metrics.py`.

### What changed:
- Established formal separation between historical published artifacts (`results/historical/`) and new rigorously validated outputs (`results/validated/`).
- Identified and isolated 2 CRITICAL issues: (1) Pseudoreplication / temporal pooling in ROC-AUC & DeLong tests, and (2) Spurious pseudo-labeling on null data in `CEWF-ElasticNet`.

### What was disproven:
- **Disproven**: The claim that the DeLong test with pooled time steps ($p < 0.0001$) proves statistically significant dominance of composite models. Because points within each trajectory are heavily autocorrelated, treating $N \approx 15,000$ points as independent degrees of freedom severely underestimates the variance of $\Delta \text{AUC}$.

### What was confirmed:
- SDE simulations, Lyapunov solvers, Euler-Maruyama integrators, cubic steady-state solvers, and backward-sliding window causality are mathematically verified.
- 100% of historical numbers are deterministically reproducible under the original code and seed configurations.

### Strongest evidence:
- Independent reference implementation of Mann-Whitney U confirms exact numerical match with production ROC-AUC (`diff < 1e-10`).
- Slices $x[k - W + 1 : k + 1]$ strictly guarantee $\partial \hat{S}_k / \partial x_{k+j} = 0, \forall j \ge 1$.

### Strongest contradiction:
- `CEWF-ElasticNet.fit()` assigns arbitrary $y=1$ labels to the last 30% of stationary null runs, learning pure noise.
- Premature alarms during the safe baseline period were historically credited as valid early warnings with inflated lead times.

### Remaining bugs:
- ISSUE-001 (Pseudoreplication / temporal pooling in benchmark scripts).
- ISSUE-002 (Null pseudo-labeling in `CEWF-ElasticNet`).
- ISSUE-003 (Self-normalization in `CEWF-BOCPD`).
- ISSUE-004 (Empty-slice RuntimeWarnings in `AdaptiveWarningSystem`).
- ISSUE-005 (Safe baseline window exclusion in `metrics.py`).
- ISSUE-006 (Collapse index timestamp misalignment in `SDEIntegrator`).

### Remaining scientific weaknesses:
- Lack of hierarchical/trajectory-level ROC-AUC and clustered bootstrap confidence intervals.
- Lack of out-of-distribution / unknown transition benchmark.

- **Novelty assessment**: N3 (Solid empirical and method development; requires rigorous trajectory-level statistical repair to reach N4/N5).
- **Reproducibility status**: **VERIFIED (100% historical match)**.
- **Statistical validity**: **REVISION REQUIRED (Pseudoreplication must be corrected)**.
- **Mathematical validity**: **PASS**.
- **Biggest remaining risk**: Trajectory-level ROC-AUC will show lower nominal AUC values than pooled time-slice AUC, requiring honest reporting of the true operational performance.

- **Decision**: **CONTINUE TO STAGE C (Leakage, Statistical, and Metric Correction)**.

### Next experiment:
Execute Stage C:
1. Fix `src/evaluation/metrics.py` (trajectory-level evaluation, safe baseline window exclusion, clustered bootstrap).
2. Fix `src/models/bocpd_composite.py` (store baseline calibration parameters).
3. Fix `src/models/elastic_net_composite.py` (replace pseudo-labels with unsupervised anomaly detection or cross-system calibration).
4. Fix `src/advancements/adaptive_warning.py` (eliminate empty slice NaNs).
5. Fix `src/simulation/integrator.py` (align collapse timestamp).
