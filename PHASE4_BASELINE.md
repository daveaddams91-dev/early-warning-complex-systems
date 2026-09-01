# PHASE 4 — RESEARCH BASELINE & AUDIT FREEZE

**Repository**: `early-warning-complex-systems`  
**Git Baseline Tag**: `v3.0.0-phase3-validated`  
**Baseline Commit**: `932cae9`  
**Stage**: Phase 4 Initiation  
**Date**: September 2026  

---

## 1. Frozen Baseline Benchmark State

The Phase 3 validated benchmark established rigorous, realization-level evaluation ($N=25$ independent stochastic trajectories per system) and eliminated time-slice pseudoreplication. All raw data and summary tables are preserved in:
- `results/historical/` (Initial uncalibrated benchmark outputs)
- `results/validated/tables/` (Repaired realization-level benchmark outputs)

### 1.1 Summary of Baseline Metrics (Trajectory-Level ROC-AUC)

| System | Topology | Variance | AR(1) | PermutationEntropy | CEWF-Rank | CEWF-Mahalanobis | Adaptive-Bayesian-EWS |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **SYS1_May_Fold** | 1D Saddle-Node Fold | **1.0000** | 0.4848 | 0.0888 | 0.3224 | **1.0000** | **1.0000** |
| **SYS2_FitzHughNagumo_Hopf** | 2D Supercritical Hopf | **1.0000** | 0.5072 | 0.2600 | 0.2832 | **0.9792** | **1.0000** |
| **SYS3_Subcritical_Pitchfork** | 1D Pitchfork Jump | **0.8945** | 0.5127 | 0.2873 | 0.5891 | 0.4764 | **0.8655** |
| **SYS4_Stommel_AMOC** | 2D Non-Smooth Fold | 0.2064 | 0.3136 | 0.1824 | 0.2784 | 0.2736 | 0.2416 |
| **SYS5_Coupled_Network** | 10D Mutualistic Network | **1.0000** | 0.7072 | 0.0064 | 0.3088 | **1.0000** | **1.0000** |
| **Adler SNIC Oscillator** | 1D Out-of-Distribution SNIC | **1.0000** | 0.8050 | 0.4425 | — | **0.9600** | **0.9725** |

### 1.2 Summary of Stress & Corruption Metrics on May Fold (Trajectory-Level ROC-AUC)

| Scenario | Variance | AR(1) | PermutationEntropy | CEWF-Rank | CEWF-Mahalanobis | Adaptive-Bayesian-EWS |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **Clean Reference** | **1.0000** | 0.4848 | 0.0888 | 0.3224 | **1.0000** | **1.0000** |
| **Severe Gaussian Noise (0 dB SNR)** | **1.0000** | 0.0000 | 0.4120 | 0.1240 | **1.0000** | **1.0000** |
| **Colored Red Noise ($\gamma=0.7$)** | **1.0000** | 0.3840 | 0.0864 | 0.4392 | **1.0000** | **1.0000** |
| **Sparse Downsampling ($\Delta t = 0.25$)** | **1.0000** | 0.6800 | 0.0616 | 0.2072 | **1.0000** | **1.0000** |
| **20 Distractor Channels** | **1.0000** | 0.4848 | 0.0888 | 0.3224 | **1.0000** | **1.0000** |

---

## 2. The Core Scientific Contradiction

The empirical evidence reveals four fundamental contradictions that challenge conventional wisdom in the early-warning systems literature:

1. **Noise Robustness vs. Clean-Regime Degradation**:
   - Under $0\text{ dB}$ SNR noise, multivariate Mahalanobis distance maintains perfect trajectory discrimination ($\text{AUC} = 1.000$) while scalar $AR(1)$ collapses to zero ($\text{AUC} = 0.000$).
   - However, on clean data, composite models like `CEWF-Rank` severely degrade performance ($\text{AUC} = 0.322$ on May fold and $0.308$ on network) compared to univariate `Variance` ($\text{AUC} = 1.000$).
2. **Selective Cross-System Transferability**:
   - Models transfer cleanly across smooth bifurcations (May fold $\to$ Coupled network $\to$ Adler SNIC), but collapse completely on piecewise-smooth density flows (Stommel AMOC $\text{AUC} \le 0.314$).
3. **Transition-Mechanism Fragility**:
   - CSD indicators excel on B-tipping (smooth parameter ramps crossing bifurcations) but exhibit $0.0\%$ detection on N-tipping (stochastic escape) and R-tipping (fast rate drift).
4. **False Consensus & Operational Point Alarms**:
   - Pointwise $95\text{th}$ percentile thresholding yields an $80\% - 100\%$ early false alarm rate during benign baseline windows due to cumulative probability accretion $1 - (1-\alpha)^M \to 1$.

---

## 3. The New Central Research Question

Rather than attempting to force a single composite model to "win" everywhere, Phase 4 asks:

> **«What deeper mathematical principles govern when early-warning indicators should be combined, rejected, or considered fundamentally unreliable?»**

---

## 4. Exact Experimental Configurations for Phase 4 Reproduction

- **Software Environment**: Python 3.14.6, NumPy 2.x, SciPy 1.15+, scikit-learn 1.6+, Pandas 2.2+, Matplotlib 3.10+.
- **Numerical Solvers**: Euler-Maruyama SDE integrator with $dt_{\text{sim}} = 0.01\text{ s}$ and observation subsampling $dt_{\text{obs}} = 0.05\text{ s}$.
- **Evaluation Protocols**:
  - Realization ensemble: $N=25$ null trajectories, $N=25$ transition trajectories per regime.
  - Causal sliding windows: Backward-looking only ($x[k-W+1:k+1]$) with window $W=50$ steps ($2.5\text{ s}$), step size $S=4$ steps ($0.2\text{ s}$).
  - Operational partitioning: Safe baseline window $[0, T_{\text{safe}}]$, actionable early warning window $[T_{\text{safe}}, T_c - \delta_{\min}]$ with $\delta_{\min} = 2.0\text{ s}$.
  - Significance testing: Clustered realization bootstrap ($B=500$ resamples with replacement).
