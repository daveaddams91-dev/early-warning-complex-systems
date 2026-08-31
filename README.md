# Early-Warning Mathematics for Complex Systems

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Tests](https://img.shields.io/badge/pytest-20%2F20%20passing-brightgreen.svg)]()
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A rigorous mathematical and software-engineering research repository investigating:
> **«Can mathematical/statistical indicators detect that a complex dynamical system is approaching a critical transition or collapse before the transition occurs?»**

---

## Key Empirical Findings

1. **Multivariate Regularization Provides Noise Invariance**: Under extreme measurement noise ($\text{SNR} = 0\text{ dB}$) and colored red noise where univariate $\text{AR}(1)$ collapses to near-chance guessing ($\text{ROC-AUC} = 0.5361$ and $0.5180$), regularized multi-indicator Mahalanobis distance (`CEWF-Mahalanobis`) preserves robust diagnostic accuracy ($\text{ROC-AUC} = 0.8258$ and $0.9542$, paired DeLong test $p < 0.001$).
2. **The Rank Aggregation Trap**: Naive unweighted rank correlation averaging (`CEWF-Rank`) underperforms scalar sample variance in clean regimes due to noise dilution from non-informative indicators (excess kurtosis, permutation entropy).
3. **Topological Generalization**: Zero-shot transfer from 1D fold systems generalizes cleanly to 10-node mutualistic networks ($\text{ROC-AUC} = 0.9926$) and Hopf bifurcations ($\text{ROC-AUC} = 0.7721$), but fails on non-smooth advective systems (Stommel AMOC, $\text{ROC-AUC} = 0.4667$).
4. **Adversarial Failure Modes**: Critical Slowing Down (CSD) provides **zero advance warning ($0.0\%$ detection rate)** for pure noise-induced transitions (N-tipping) and rate-dependent transitions (R-tipping), while triggering a **$100\%$ false alarm rate** under transient pulse shocks.

---

## Summary Benchmark Table (Clean Level 1 Benchmark)

| System | Best Baseline Indicator | Baseline ROC-AUC | Best Composite Model | Composite ROC-AUC | Statistical Significance (DeLong) |
| :--- | :--- | :---: | :--- | :---: | :---: |
| **SYS-1 (May Fold)** | Variance | 0.9971 | CEWF-Linear / CEWF-Mahalanobis | 0.9667 / 0.9638 | $p = 0.08$ |
| **SYS-2 (FitzHugh Hopf)** | MahalanobisDist | 0.9999 | CEWF-Linear | 0.7457 | $p < 0.001$ |
| **SYS-3 (Pitchfork)** | MahalanobisDist | 0.9027 | CEWF-ElasticNet | 0.6662 | $p < 0.001$ |
| **SYS-4 (Stommel AMOC)** | MahalanobisDist | 0.9960 | CEWF-Mahalanobis | 0.5167 | **$p < 0.001$** |
| **SYS-5 (Mutualistic Net)** | Variance | 0.9995 | CEWF-Mahalanobis | 0.9939 | $p = 0.08$ |

---

## Repository Architecture

```
early-warning-complex-systems/
├── src/
│   ├── systems/            # Canonical SDE Systems (May, FitzHugh-Nagumo, Pitchfork, Stommel, Network)
│   ├── simulation/         # Euler-Maruyama SDE Integrator & Observation Noise Corrupters
│   ├── indicators/         # 11 Univariate & Multivariate Mathematical Indicators
│   ├── models/             # 5 Composite Early-Warning Frameworks (Linear, Rank, Mahalanobis, ElasticNet, BOCPD)
│   ├── evaluation/         # Strict Non-Leaking Metrics (ROC/PR, Lead Time, False Alarms, DeLong Test)
│   └── visualization/      # Publication-Quality Matplotlib Plotting Utilities
├── experiments/
│   ├── scripts/            # End-to-End Hierarchical Benchmark Runner (Levels 1-6)
│   └── results/            # Persisted CSV Tables and PNG Figures
├── tests/                  # Full PyTest Suite (20 Tests across all modules)
├── docs/                   # Mathematical Specifications & Reproducibility Guide
├── REFERENCES.md           # Peer-Reviewed Academic Bibliography (21 Verified DOIs)
├── NOVELTY_AUDIT.md        # Academic Novelty Comparison vs Prior Literature
├── RESEARCH_BLUEPRINT.md   # Mathematical Specifications & Falsifiable Hypotheses
├── CRITICAL_REVIEW.md      # Adversarial Red-Teaming & Falsification Audit
├── LIMITATIONS.md          # Theoretical & Observational Boundary Conditions
└── FINAL_REPORT.md         # Comprehensive Research Manuscript
```

---

## Quickstart & Reproducibility

### 1. Run Unit Tests (20/20 Passing)
```bash
python -m pytest tests/ -v
```

### 2. Run Complete 6-Level Experimental Suite
```bash
python experiments/scripts/run_all_experiments.py
```
Outputs are written to `experiments/results/tables/` and `experiments/results/figures/`.

---

## References

See [REFERENCES.md](REFERENCES.md) for full citations including DOIs and paper links. Key foundations:
- **Scheffer et al. (2009)**: Early-warning signals for critical transitions. *Nature*, 461(7260), 53-59.
- **Dakos et al. (2008)**: Slowing down as an early warning signal for abrupt climate change. *PNAS*, 105(38), 14308-14312.
- **Boettiger & Hastings (2012)**: Early warning signals and the prosecutor's fallacy. *Proc. R. Soc. B*, 279(1748), 4734-4739.
- **Bury et al. (2021)**: Deep learning for early warning signals of critical transitions. *PNAS*, 118(39), e2106140118.
- **Bandt & Pompe (2002)**: Permutation entropy: A natural complexity measure for time series. *Phys. Rev. Lett.*, 88(17), 174102.
