# SCIENTIFIC CLAIM AUDIT & FALSIFICATION REGISTER

**Project**: Early-Warning Mathematics for Complex Systems  
**Stage**: Phase 3 Independent Verification  
**Audit Standard**: Strict Empirical Traceability & Claim Classification  
**Date**: September 2026  

---

## 1. Classification Standard

Every major claim is evaluated against experimental evidence and classified into one of seven formal truth statuses:
- **PROVEN**: Mathematically proved or confirmed down to machine precision.
- **STRONGLY SUPPORTED**: Backed by statistically significant ($p < 0.001$), replicated empirical experiments across multiple systems.
- **EMPIRICALLY OBSERVED**: Observed in specific numerical simulations, but with acknowledged domain boundaries.
- **PLAUSIBLE**: Consistent with dynamical systems theory, but subject to observational caveats.
- **SPECULATIVE**: Theoretical conjecture lacking sufficient empirical proof.
- **UNSUPPORTED**: Lacks experimental verification or mathematical proof.
- **FALSE**: Contradicted by experimental evidence or mathematical counter-example.

---

## 2. Itemized Claim Audit

### Claim 1: "Critical slowing down indicators can detect impending transitions across complex systems."
- **Status**: **EMPIRICALLY OBSERVED (DOMAIN-BOUNDED)**
- **Evidence**: Verified on 1D Fold (May), 1D Pitchfork, 10D Mutualistic Network, and 1D SNIC Oscillator ($\text{ROC-AUC} \ge 0.89 - 1.000$, EXP-001, EXP-009).
- **Contradiction**: Fails completely on Stommel AMOC ($\text{AUC} = 0.380 - 0.490$) and on all N-tipping and R-tipping transitions ($0.0\%$ detection rate).
- **Strength**: Moderate. Valid only for B-tipping on smooth manifolds where the unstable mode projects onto the observed variable.

---

### Claim 2: "Multi-indicator Mahalanobis distance outperforms classical scalar AR(1) under noise and distortion."
- **Status**: **STRONGLY SUPPORTED**
- **Evidence**: On May Fold under $0\text{ dB}$ SNR, `CEWF-Mahalanobis` achieves trajectory $\text{ROC-AUC} = 1.000$ while `AR(1)` collapses to $\text{AUC} = 0.000$ (EXP-003). Under colored red noise, `CEWF-Mahalanobis` achieves $\text{AUC} = 1.000$ vs `AR(1)` $\text{AUC} = 0.384$. Clustered bootstrap confirms statistical significance ($\Delta \text{AUC} = +0.516, p = 0.000$, EXP-002).
- **Strength**: Very Strong.

---

### Claim 3: "Naive rank aggregation across all indicators improves detection reliability."
- **Status**: **FALSE (REFUTED)**
- **Evidence**: In EXP-001 and EXP-003, `CEWF-Rank` consistently degraded performance relative to scalar variance (May Fold: $\text{AUC} = 0.322$ vs $1.000$ for Variance; Network: $\text{AUC} = 0.449$ vs $1.000$). Higher-order symbolic and skewness moments inject uncorrelated noise into the rank ensemble.
- **Action**: Published as a negative finding; practitioners are cautioned against unweighted rank averaging.

---

### Claim 4: "There exists an empirical detectability boundary in parameter space $(\sigma_{\text{obs}}, \Delta t)$."
- **Status**: **STRONGLY SUPPORTED**
- **Evidence**: EXP-004 demonstrated that for $\sigma_{\text{obs}} \ge 0.40$, $\text{ROC-AUC} \le 0.60$ across all sampling rates. When dynamical $\text{SNR} = \frac{\sigma_{\text{dyn}}^2}{2 |\lambda| \sigma_{\text{obs}}^2} < 1.0$, observation noise drowns out critical slowing down fluctuations.
- **Strength**: Strong.

---

### Claim 5: "Passive early warning can instantaneously distinguish a harmless pulse shock from an impending collapse."
- **Status**: **FALSE (REFUTED)**
- **Evidence**: EXP-005 proved that for $t \in [0, 15]\text{ s}$ post-shock, the Wasserstein distance between resilient recovery and impending collapse trajectories is negligible ($W_1 < 0.05, D_{\text{KL}} < 1.0$). Both futures are statistically indistinguishable during the initial relaxation window.
- **Strength**: Formally Falsified.

---

### Claim 6: "Active perturbation probing directly measures the return rate without window latency."
- **Status**: **PROVEN / STRONGLY SUPPORTED**
- **Evidence**: EXP-006 showed that active pulse displacement ($a = 0.5$) allows direct calculation of $\hat{\kappa} = -\frac{1}{\Delta t} \ln(|\Delta x| / |a|)$, matching the theoretical Jacobian eigenvalue $|J(x^*, \mu)|$ without sliding window delays.
- **Strength**: Very Strong.

---

### Claim 7: "Stabilizing feedback control can prevent collapse if initiated prior to the bifurcation crossing."
- **Status**: **STRONGLY SUPPORTED**
- **Evidence**: In EXP-006, closed-loop feedback control $u(t) = -K (x - x_{\text{target}})$ stabilized the system when initiated at lead times of $50\text{ s}, 30\text{ s}, 15\text{ s},$ and $5\text{ s}$ ($\int u^2 dt \approx 55 - 65$). When initiated at $0\text{ s}$ (post-bifurcation), the equilibrium vanished and stabilization failed.
- **Strength**: Strong.

---

### Claim 8: "Empirical AR(1) estimators are unbiased estimators of continuous physical autocorrelation."
- **Status**: **FALSE (MATHEMATICALLY DISPROVEN)**
- **Evidence**: Kendall's 1954 small-sample bias derivation and EXP-008 prove that sliding window estimators exhibit an analytical downward bias $\mathbb{E}[\hat{\rho}] \approx \rho - \frac{1+3\rho}{W}$. For window $W=30$, empirical $\hat{\rho} = 0.751$ severely underestimates true theoretical $\rho = 0.968$ ($\Delta \rho = -0.218$).
- **Strength**: Formally Falsified.
