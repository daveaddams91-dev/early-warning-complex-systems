# Early-Warning Mathematics for Complex Systems

[![Tests](https://img.shields.io/badge/pytest-34%20passed-brightgreen.svg)](tests/)
[![Python](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Audit](https://img.shields.io/badge/Phase%203%20Audit-Validated-blueviolet.svg)](CHECKPOINT_C.md)

An open-source mathematical research framework and benchmark investigating whether statistical and information-theoretic indicators can reliably anticipate critical transitions and systemic collapse in complex dynamical systems.

---

## 🔬 Core Scientific Findings (Phase 3 Validated Benchmark)

- **Trajectory-Level Validation**: Replaced time-step pooled pseudoreplication with realization-level evaluation ($N=25$ independent stochastic trajectories per system) and clustered bootstrap confidence intervals.
- **Composite Model Superiority**: Tikhonov-regularized multi-indicator Mahalanobis distance (`CEWF-Mahalanobis`) and Adaptive Bayesian Warning Engine (`Adaptive-Bayesian-EWS`) achieve trajectory-level $\text{ROC-AUC} = 1.000$ under $0\text{ dB}$ SNR Gaussian noise and colored red noise, where classical scalar `AR(1)` collapses to $\text{AUC} \le 0.384$ ($p = 0.0000$, EXP-002, EXP-003).
- **The Non-Universality of Early-Warning Signals**: Critical Slowing Down (CSD) indicators fail completely on non-smooth thermohaline ocean circulation (Stommel AMOC, $\text{AUC} \le 0.314$), noise-induced tipping ($0.0\%$ detection), and rate-induced tipping ($0.0\%$ detection).
- **The Detectability Phase Boundary**: Mapped the parameter space boundary where dynamical $\text{SNR} < 1.0$ ($\sigma_{\text{obs}} \ge 0.40$), rendering statistical warning fundamentally impossible regardless of sliding-window length (EXP-004).
- **Active Probing & Control**: Active test perturbations directly estimate local eigenvalues $\hat{\kappa}$ without sliding-window delays, enabling closed-loop feedback control to arrest tipping up to $5\text{ s}$ before bifurcation (EXP-006).

---

## 📊 Summary of Validated Benchmark Results

### Trajectory-Level Clean Benchmark (EXP-001)
| System | Bifurcation Topology | Variance | AR(1) | CEWF-Mahalanobis | Adaptive-Bayesian-EWS |
| :--- | :--- | :---: | :---: | :---: | :---: |
| **SYS1_May_Fold** | 1D Saddle-Node Fold | **1.0000** | 0.4848 | **1.0000** | **1.0000** |
| **SYS2_FitzHughNagumo_Hopf**| 2D Supercritical Hopf | **1.0000** | 0.5072 | **0.9792** | **1.0000** |
| **SYS3_Subcritical_Pitchfork**| 1D Pitchfork Jump | **0.8945** | 0.5127 | 0.4764 | **0.8655** |
| **SYS4_Stommel_AMOC** | 2D Non-Smooth Fold | 0.2064 | 0.3136 | 0.2736 | 0.2416 |
| **SYS5_Coupled_Network** | 10D Mutualistic Network | **1.0000** | 0.7072 | **1.0000** | **1.0000** |

### Unknown-Transition Zero-Knowledge Generalization (EXP-009)
| System | Mechanism | Method | Trajectory ROC-AUC | Outcome |
| :--- | :--- | :---: | :---: | :---: |
| **Adler Phase Oscillator** | Saddle-Node on Invariant Circle (Global) | **Adaptive-Bayesian-EWS** | **0.9725** | **SUCCESS** |
| **Adler Phase Oscillator** | Saddle-Node on Invariant Circle (Global) | **CEWF-Mahalanobis** | **0.9600** | **SUCCESS** |
| **Adler Phase Oscillator** | Saddle-Node on Invariant Circle (Global) | **Variance** | **1.0000** | **SUCCESS** |
| **Adler Phase Oscillator** | Saddle-Node on Invariant Circle (Global) | **AR(1)** | 0.8050 | SUCCESS |
| **Adler Phase Oscillator** | Saddle-Node on Invariant Circle (Global) | Permutation Entropy | 0.4425 | **FAILED** |

---

## 🛠️ Quickstart & Reproduction

```bash
# 1. Clone repository
git clone https://github.com/Raj123-0/early-warning-complex-systems.git
cd early-warning-complex-systems

# 2. Install dependencies
pip install numpy scipy scikit-learn pandas matplotlib networkx pytest

# 3. Run all unit tests (34/34 passing)
pytest tests/ -v

# 4. Run full validated benchmark suite
python experiments/scripts/run_validated_benchmark.py

# 5. Generate automated summary reports
python experiments/scripts/generate_reports.py
```

---

## 📁 Repository Architecture

- `src/systems/`: 5 canonical dynamical systems + Adler SNIC oscillator.
- `src/simulation/`: SDE Euler-Maruyama numerical integrator and distortion operators.
- `src/indicators/`: Univariate and multivariate statistical indicators.
- `src/models/`: Multi-indicator composite frameworks (`CEWF-Linear`, `CEWF-Rank`, `CEWF-Mahalanobis`, `CEWF-BOCPD`).
- `src/advancements/`: Phase 2 & 3 research advancements (Detectability, Adaptive Warning, Counterfactuals, Active Probing, Control, Unknown Transition).
- `src/evaluation/`: Production and reference metric implementations (Trajectory-level ROC, Operational lead times, Clustered bootstrap).
- `results/historical/`: Frozen original published artifacts (commits `188bea7`, `2212001`).
- `results/validated/`: Repaired, realization-level validated experimental outputs.
- `FINAL_REPORT.md`: Comprehensive academic research manuscript.
- `FAILURE_ANALYSIS.md`: Systematic investigation of failure cases (AMOC, Hopf, N-tipping, R-tipping).
- `LIMITATIONS.md`: Formal theoretical and observational boundary conditions.
- `CLAIM_AUDIT.md`: Itemized claim verification register.
- `experiments/REGISTRY.md`: Structured experiment ledger (`EXP-001` - `EXP-009`).
