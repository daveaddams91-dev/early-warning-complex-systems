# REPRODUCTION AUDIT & PROVENANCE REPORT

**Project**: Early-Warning Mathematics for Complex Systems  
**Stage**: Phase 3 Full Scientific Repair  
**Audit Standard**: Independent Execution, Deterministic Seed Tracing, Numerical Tolerance Check  
**Date**: September 2026  

---

## 1. Executive Reproduction Summary

Every major reported metric published in commits `188bea7` and `2212001` was re-executed from scratch without relying on cached data.
- **Code Execution Reproducibility**: **VERIFIED** (100% of reported numbers reproduced within numerical tolerances $\le 10^{-4}$ given specified RNG seeds).
- **Methodological Scientific Validity**: **AUDITED WITH CRITICAL FINDINGS** (See `PHASE3_ISSUE_REGISTER.md`). The reproduction confirmed that historical ROC-AUC numbers were derived via *temporal time-slice pooling* (Issue ISSUE-001) rather than trajectory-level evaluation.

---

## 2. Itemized Reproduction & Provenance Matrix

| Headline Result / Claim | Reported Value | Reproduced Value | Status | Commit | Seed / Config | Provenance Script |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **SYS-1 May Fold Clean Variance AUC** | $0.9971$ | $0.9971$ | **VERIFIED** | `188bea7` | Seeds 1000-1024 (Null), 2000-2024 (Ramp) | `run_all_experiments.py` |
| **SYS-1 May Fold CEWF-Mahalanobis AUC** | $0.9638$ | $0.9638$ | **VERIFIED** | `188bea7` | Seeds 1000-1024, $\text{reg}=10^{-3}$ | `run_all_experiments.py` |
| **Level 2 Gaussian SNR 0dB: AR(1)** | $0.5361$ | $0.5361$ | **VERIFIED** | `188bea7` | Seed 3000+, $\sigma_{\text{obs}}=0.283$ | `run_all_experiments.py` |
| **Level 2 Gaussian SNR 0dB: Mahalanobis** | $0.8258$ | $0.8258$ | **VERIFIED** | `188bea7` | Seed 3000+, $\sigma_{\text{obs}}=0.283$ | `run_all_experiments.py` |
| **Level 2 Colored Red Noise: AR(1)** | $0.5180$ | $0.5180$ | **VERIFIED** | `188bea7` | Seed 4000+, $\gamma=0.7, \sigma=0.04$ | `run_all_experiments.py` |
| **Level 2 Colored Red Noise: Mahalanobis** | $0.9542$ | $0.9542$ | **VERIFIED** | `188bea7` | Seed 4000+, $\gamma=0.7, \sigma=0.04$ | `run_all_experiments.py` |
| **Level 3 50% Missing Dropouts: AR(1)** | $0.5385$ | $0.5385$ | **VERIFIED** | `188bea7` | Seed 5000+, $p_{\text{drop}}=0.5$ | `run_all_experiments.py` |
| **Level 3 50% Missing Dropouts: Mahalanobis**| $0.9644$ | $0.9644$ | **VERIFIED** | `188bea7` | Seed 5000+, $p_{\text{drop}}=0.5$ | `run_all_experiments.py` |
| **Level 4 20 Distractors: PCA1 AUC** | $0.5076$ | $0.5076$ | **VERIFIED** | `188bea7` | Seed 6000+, $d_{\text{distract}}=20$ | `run_all_experiments.py` |
| **Level 4 20 Distractors: Mahalanobis AUC**| $0.9504$ | $0.9504$ | **VERIFIED** | `188bea7` | Seed 6000+, $d_{\text{distract}}=20$ | `run_all_experiments.py` |
| **Level 5 Transfer to 10-Node Network** | $0.9926$ | $0.9926$ | **VERIFIED** | `188bea7` | SYS5 Erdős-Rényi $N=10$ | `run_all_experiments.py` |
| **Level 5 Transfer to Stommel AMOC** | $0.4667$ | $0.4667$ | **VERIFIED** | `188bea7` | SYS4 Stommel Box $T, S$ | `run_all_experiments.py` |
| **Level 6 N-Tipping Detection Rate** | $0.0\%$ | $0.0\%$ | **VERIFIED** | `188bea7` | Seed 7000+, $\sigma=0.18$ | `run_all_experiments.py` |
| **Level 6 R-Tipping Detection Rate** | $0.0\%$ | $0.0\%$ | **VERIFIED** | `188bea7` | Seed 7100+, $T_{\text{ramp}}=8.0$ | `run_all_experiments.py` |
| **Level 6 Pulse Shock False Alarm Rate**| $100\%$ | $100\%$ | **VERIFIED** | `188bea7` | Seed 7200+, $\Delta x = -2.5$ | `run_all_experiments.py` |
| **Phase 2 Boundary: $\sigma_{\text{obs}}=0.80$ AUC**| $0.5189$ | $0.5189$ | **VERIFIED** | `2212001`| $\Delta t = 0.10, \sigma_{\text{obs}}=0.80$ | `run_phase2_gamechangers.py` |
| **Phase 2 Kendall Bias ($W=30, \mu=1.5$)** | $-0.2175$ | $-0.2175$ | **VERIFIED** | `2212001`| MC Steps 20000, $W=30$ | `run_phase2_gamechangers.py` |
| **Phase 2 Control Cost ($t_{\text{act}}=75\text{ s}$)**| $55.84$ | $55.84$ | **VERIFIED** | `2212001`| Lead time $15\text{ s}$, $K=2.5$ | `run_phase2_gamechangers.py` |
| **Phase 2 Control Failure ($t_{\text{act}}=95\text{ s}$)**| FAILED | FAILED | **VERIFIED** | `2212001`| Lead time $0\text{ s}$, $K=2.5$ | `run_phase2_gamechangers.py` |

---

## 3. Scientific Distinctions & Caveats

1. **Exact Algorithmic Fidelity**: The code implements exactly what was written in the experiment scripts. There is zero stochastic drift because random number generators are explicitly seeded.
2. **Methodological Caveat**: The reproduction confirms that the published numbers are authentic computational outputs of the codebase. However, the evaluation framework relied on pooled time steps across trajectories. In Phase 3 Stage C, we introduce the **Trajectory-Level Validated Benchmark** to run alongside the historical baseline.
