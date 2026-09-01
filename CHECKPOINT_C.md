# PHASE 3 — CHECKPOINT C: LEAKAGE, STATISTICAL & METRIC CORRECTION GATE

**STAGE**: STAGE C (Leakage Elimination, Statistical Repair & Metric Correction)  
**Date**: September 2026  

---

## 1. Core Evaluation Matrix

- **Research Question**: Have all identified data leakages, self-normalization artifacts, and pseudoreplications been mathematically and computationally eliminated?
- **Current Hypothesis**: Replacing time-slice sample pooling with realization-level evaluation will produce honest, uninflated trajectory-level performance metrics, providing a rock-solid scientific foundation for downstream baselines.

### What was completed:
1. Implemented **`compute_trajectory_level_roc_pr`** in `src/evaluation/metrics.py` to evaluate each stochastic realization as exactly 1 independent sample.
2. Implemented **`clustered_bootstrap_auc_diff`** to compute valid, realization-level confidence intervals and bootstrap $p$-values for $\Delta \text{AUC}$.
3. Implemented **`compute_operational_lead_time_distribution`** with explicit safe baseline window exclusion $[0, T_{\text{baseline}}]$, preventing premature baseline false alarms from masquerading as early warnings.
4. Corrected `CEWF-BOCPD` (`src/models/bocpd_composite.py`) to store and use empirical baseline calibration from independent null runs.
5. Eliminated arbitrary pseudo-labeling on null trajectories in `CEWF-ElasticNet` (`src/models/elastic_net_composite.py`).
6. Fixed empty-slice NaN RuntimeWarnings in `AdaptiveWarningSystem` (`src/advancements/adaptive_warning.py`).
7. Aligned collapse state and timestamp in `SDEIntegrator` (`src/simulation/integrator.py`).
8. Added regression tests in `tests/test_leakage_regression.py` and operational metric tests in `tests/test_evaluation.py`. All 34 tests passing cleanly.

### What changed:
- Metrics now distinguish between **Early False Alarms** (before transition process begins), **Actionable Warnings** (prior to collapse with lead time $L \ge \delta_{\min}$), **Late Alarms** (unactionable), and **Misses**.
- Models no longer perform self-normalization on test sequences.

### What was disproven:
- The assumption that high time-slice pooled ROC-AUC implies high trajectory-level warning capability. Under trajectory-level evaluation, models must cleanly elevate their peak score above the maximum score observed across the entire duration of null trajectories.

### What was confirmed:
- Backward sliding windows $x[k - W + 1 : k + 1]$ are strictly causal ($\partial \hat{S}_k / \partial x_{k+j} = 0, \forall j \ge 1$).
- Independent reference implementation of Mann-Whitney U matches production ROC-AUC to within machine precision.

### Remaining bugs:
- None identified in core simulation, indicators, models, or evaluation metrics.

### Remaining scientific weaknesses:
- Need to re-execute benchmark suite with trajectory-level evaluation and populate `results/validated/`.
- Need to conduct formal failure analysis (`FAILURE_ANALYSIS.md`) on Stommel AMOC and FitzHugh-Nagumo.

- **Novelty assessment**: N3 (Solid statistical and algorithmic repair).
- **Reproducibility status**: **VERIFIED (All tests passing, zero warnings)**.
- **Statistical validity**: **PASS (Pseudoreplication eliminated; clustered bootstrap active)**.
- **Mathematical validity**: **PASS**.
- **Biggest remaining risk**: Trajectory-level ROC-AUC on difficult regimes (e.g. noise-induced tipping) will show lower nominal scores, requiring clear documentation that this reflects true physical unpredictability.

- **Decision**: **CONTINUE TO STAGE D & E (Baseline Reconstruction & Failure Analysis)**.

### Next experiment:
Re-run the validated experimental benchmark using the corrected trajectory-level evaluation framework and output validated tables to `results/validated/`.
