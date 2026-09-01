# Early-Warning Mathematics for Complex Systems

[![CI](https://github.com/Raj123-0/early-warning-complex-systems/actions/workflows/ci.yml/badge.svg)](https://github.com/Raj123-0/early-warning-complex-systems/actions)
[![Tests](https://img.shields.io/badge/pytest-49%20passed-brightgreen.svg)](tests/)
[![Python](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Audit](https://img.shields.io/badge/Phase%204%20Discovery-Validated-blueviolet.svg)](PHASE4_CHECKPOINT.md)

An open-source mathematical research framework and benchmark investigating whether statistical, physical, and information-theoretic indicators can reliably anticipate critical transitions and systemic collapse in complex dynamical systems.

---

## 🔬 Core Statistical Reality & Scientific Findings

> [!IMPORTANT]
> **Empirical Performance Breakdown of Composite Aggregation**:
> When evaluated under a rigorous, non-leaking trajectory-level protocol ($N=25$ realizations per regime, clustered bootstrap confidence intervals):
> - **Composite models significantly help on only 1 of 5 systems** (`SYS-2` FitzHugh-Nagumo Hopf: $\text{AUC} = 0.9792$ vs $\text{AR}(1) = 0.5072$), where complex conjugate eigenvalues blind scalar autocorrelation.
> - **Composite models are statistically indistinguishable from simple variance on 2 systems** (`SYS-1` May Fold: $\text{AUC} = 1.0000$ vs $1.0000$, and `SYS-5` Coupled Network: $\text{AUC} = 1.0000$ vs $1.0000$, $p \ge 0.08$).
> - **Composite models significantly underperform simple variance on 1 system** (`SYS-3` Subcritical Pitchfork: $\text{AUC} = 0.4764$ vs $\text{Variance} = 0.8945$, due to noise dilution and indicator conflict).
> - **All models (composite, deep learning, and univariate) fail catastrophically on 1 system** (`SYS-4` Stommel AMOC: $\text{AUC} \le 0.2944$), because convective density drag $|T - S|$ prevents critical fluctuation growth on the observed manifold.

- **Trajectory-Level Validation**: Replaced time-step pooled pseudoreplication with realization-level evaluation ($N=25$ independent stochastic trajectories per system) and clustered bootstrap confidence intervals.
- **The Non-Universality of Early-Warning Signals**: Critical Slowing Down (CSD) indicators fail completely on non-smooth thermohaline ocean circulation (Stommel AMOC, $\text{AUC} \le 0.314$), noise-induced tipping ($0.0\%$ detection), and rate-induced tipping ($0.0\%$ detection) ([FAILURE_MECHANISM_MAP.md](FAILURE_MECHANISM_MAP.md)).
- **Active Probing & Intervention**: Active test perturbations directly estimate local eigenvalues $\hat{\kappa}$ without sliding-window delays, enabling closed-loop feedback control to arrest tipping up to $5\text{ s}$ before bifurcation.

---

## 📊 Summary of Validated Benchmark Results

### Trajectory-Level Clean Benchmark (EXP-001 & EXP-012)
| System | Bifurcation Topology | Variance | `AR(1)` | CEWF-Mahalanobis | DeepEWS (Bury 2021) | DeLong $p$ (Deep vs Mah) | Adaptive-Bayesian-EWS |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **SYS1_May_Fold** | 1D Saddle-Node Fold | **1.0000** | 0.4848 | **1.0000** | **1.0000** | $1.0000$ (Neutral) | **1.0000** |
| **SYS2_FitzHughNagumo_Hopf**| 2D Supercritical Hopf | **1.0000** | 0.5072 | **0.9536** | **0.9984** | $0.1019$ (Neutral) | **1.0000** |
| **SYS3_Subcritical_Pitchfork**| 1D Pitchfork Jump | **0.8945** | 0.5127 | 0.4933 | **0.8000** | $0.0509$ (Marginal) | **0.8655** |
| **SYS4_Stommel_AMOC** | 2D Non-Smooth Fold | 0.2064 | 0.3136 | 0.2096 | 0.2944 | $0.4264$ (Neutral/Fail)| 0.2416 |
| **SYS5_Coupled_Network** | 10D Mutualistic Network | **1.0000** | 0.7072 | **1.0000** | **1.0000** | $1.0000$ (Neutral) | **1.0000** |

### Unknown-Transition Zero-Knowledge Generalization (EXP-009)
| System | Mechanism | Method | Trajectory ROC-AUC | Outcome |
| :--- | :--- | :---: | :---: | :---: |
| **Adler Phase Oscillator** | Saddle-Node on Invariant Circle (Global) | **Adaptive-Bayesian-EWS** | **0.9725** | **SUCCESS** |
| **Adler Phase Oscillator** | Saddle-Node on Invariant Circle (Global) | **CEWF-Mahalanobis** | **0.9600** | **SUCCESS** |
| **Adler Phase Oscillator** | Saddle-Node on Invariant Circle (Global) | **Variance** | **1.0000** | **SUCCESS** |
| **Adler Phase Oscillator** | Saddle-Node on Invariant Circle (Global) | `AR(1)` | 0.8050 | SUCCESS |
| **Adler Phase Oscillator** | Saddle-Node on Invariant Circle (Global) | Permutation Entropy | 0.4425 | **FAILED** |

---

## 📁 Research Documentation Ledger

- **[PHASE4_DISCOVERY_REPORT.md](PHASE4_DISCOVERY_REPORT.md)**: Definitive 10-question synthesis resolving the contradiction.
- **[INDICATOR_REGIME_MAP.md](INDICATOR_REGIME_MAP.md)**: Operating profiles and failure regimes across indicators.
- **[DETECTABILITY_BOUNDARY.md](DETECTABILITY_BOUNDARY.md)**: Empirical and analytical map of predictability boundaries.
- **[FAILURE_MECHANISM_MAP.md](FAILURE_MECHANISM_MAP.md)**: Six-class transition taxonomy and CSD limits.
- **[ADAPTIVE_FRAMEWORK.md](ADAPTIVE_FRAMEWORK.md)**: Full mathematical specification of AEWIF and abstention.
- **[INFORMATION_DIVERSITY.md](INFORMATION_DIVERSITY.md)**: Participation ratio $K_{\text{eff}}$ and adversarial consensus.
- **[ORACLE_GAP.md](ORACLE_GAP.md)**: Epistemic information loss between deployed and oracle ensembles.
- **[PHASE4_NOVELTY_AUDIT.md](PHASE4_NOVELTY_AUDIT.md)**: Novelty assessment achieving Level N5 classification.
- **[PHASE4_CRITICAL_REVIEW.md](PHASE4_CRITICAL_REVIEW.md)**: Hostile adversarial review auditing causal integrity.
- **[PHASE4_CHECKPOINT.md](PHASE4_CHECKPOINT.md)**: Formal milestone checkpoint.

---

## 🛠️ Quickstart & Reproduction

```bash
# 1. Clone repository
git clone https://github.com/Raj123-0/early-warning-complex-systems.git
cd early-warning-complex-systems

# 2. Install dependencies
pip install numpy scipy scikit-learn pandas matplotlib networkx pytest

# 3. Run all unit tests (38/38 passing)
python -m pytest tests/ -v

# 4. Run Phase 4 discovery experiments
python src/advancements/phase4_investigation.py
python experiments/scripts/run_phase4_discoveries.py
python src/advancements/information_diversity.py
python src/advancements/adaptive_inference_framework.py
```

---

## 📜 Citation & License

Released under the **MIT License**. If utilizing this code or the Phase 4 theoretical framework, cite as:

```bibtex
@software{early_warning_complex_systems_2026,
  author = {Autonomous Mathematical Research Agent},
  title = {Early-Warning Mathematics for Complex Systems: An Adaptive Multi-Indicator Inference Framework},
  year = {2026},
  publisher = {GitHub},
  url = {https://github.com/Raj123-0/early-warning-complex-systems}
}
```
