# Experimental Design & Evaluation Suite

This document describes the hierarchical 6-level experimental benchmark designed to rigorously evaluate early-warning indicators under controlled stochastic conditions.

---

## 1. Experimental Hierarchy

```
Level 1: Clean Synthetic Data (Quasistatic B-Tipping across 5 Systems)
   │
Level 2: Measurement Noise & Corruption (Gaussian SNR 20dB to 0dB, Student-t, Red Noise)
   │
Level 3: Sparse & Irregular Sampling (Downsampling up to 10x)
   │
Level 4: Distractor & High-Dimensional Scaling (Adding 0-20 uncoupled noise channels)
   │
Level 5: Cross-System Zero-Shot Generalization (Transfer from 1D Fold to Hopf/Pitchfork/AMOC/Network)
   │
Level 6: Adversarial & Deceiver Test Suite (Shocks, Drift, N-Tipping, Fast R-Tipping)
```

---

## 2. Strict Non-Leakage Axioms

1. **Causal Rolling Processing**: At time step $t_k$, all indicator calculations and trend statistics only access indices $\{t_0, t_1, \dots, t_k\}$. No centered filters or whole-series lookahead.
2. **Independent Calibration**: All baseline means $\bar{\mathbf{S}}_0$ and covariance matrices $\mathbf{\Sigma}_0$ are estimated strictly on null (non-tipping) trajectories or early calibration windows $[0, t_{\text{calib}}]$.
3. **Paired Statistical Significance**: Comparisons between composite models and baselines are conducted using paired DeLong tests on identical test realization splits.
