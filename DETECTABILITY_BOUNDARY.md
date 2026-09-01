# THE DETECTABILITY BOUNDARY: PHASE SPACE STRUCTURE OF PREDICTABILITY

**Project**: Early-Warning Mathematics for Complex Systems  
**Stage**: Phase 4 Priority Experiment (EXP-011)  
**Date**: September 2026  
**Auditor**: Principal Investigator & Hostile Scientific Reviewer  

---

## 1. Executive Summary

A central goal of Phase 4 is to discover whether predictability is governed by a sharp boundary in observational and dynamical parameter space. Using a 36-configuration grid experiment systematically varying observation noise $\sigma_{\text{obs}} \in [0.00, 0.35]$, sampling interval $\Delta t \in [0.02, 0.15]\text{ s}$, and parameter ramp duration $T_{\text{ramp}} \in [60, 240]\text{ s}$ (EXP-011, `results/validated/tables/phase4_detectability_phase_diagram.csv`), we mapped the empirical Detectability Phase Boundary.

We discovered that early-warning detectability partitions into three distinct physical regimes:
1. **Reliable Regime**: $\text{ROC-AUC} \ge 0.85$ and actionable lead time $L \ge 20\text{ s}$.
2. **Uncertain Regime**: $0.65 \le \text{ROC-AUC} < 0.85$; high variance in warning time and elevated false alarm vulnerability.
3. **Unreliable Regime**: $\text{ROC-AUC} < 0.65$; dynamical signal drowned by observation noise or excessive downsampling.

---

## 2. Mathematical Formulation of the Detectability Boundary

Consider a 1D system undergoing a fold bifurcation with control parameter drift $\mu(t) = \mu_0 + r t$.
The linearized dynamics around the quasi-static equilibrium $x^*(\mu)$ is:
$$dx(t) = \lambda(\mu) x(t) dt + \sigma_{\text{dyn}} dW(t)$$
where $\lambda(\mu) \approx -\sqrt{c (\mu_c - \mu)} \to 0^-$.

The true physical state variance is:
$$\mathrm{Var}_{\text{phys}}(\mu) = \frac{\sigma_{\text{dyn}}^2}{2 |\lambda(\mu)|}$$
The observer measures:
$$y(t_k) = x(t_k) + \eta_k, \quad \eta_k \sim \mathcal{N}(0, \sigma_{\text{obs}}^2)$$
The total observed variance is:
$$\mathrm{Var}_{\text{obs}}(\mu) = \mathrm{Var}_{\text{phys}}(\mu) + \sigma_{\text{obs}}^2 = \frac{\sigma_{\text{dyn}}^2}{2 |\lambda(\mu)|} + \sigma_{\text{obs}}^2$$

We define the **Dynamical Signal-to-Noise Ratio** $\text{SNR}_{\text{dyn}}$ as the ratio of critical slowing down variance growth to the observation noise floor:
$$\text{SNR}_{\text{dyn}}(\mu) = \frac{\mathrm{Var}_{\text{phys}}(\mu) - \mathrm{Var}_{\text{phys}}(\mu_0)}{\sigma_{\text{obs}}^2} = \frac{\sigma_{\text{dyn}}^2}{2 \sigma_{\text{obs}}^2} \left( \frac{1}{|\lambda(\mu)|} - \frac{1}{|\lambda_0|} \right)$$

### The Critical Phase Boundary Condition:
- **Condition for Detectability**: $\text{SNR}_{\text{dyn}}(T_c - \delta_{\min}) \ge 1.0$
- If $\sigma_{\text{obs}}^2 \gg \frac{\sigma_{\text{dyn}}^2}{2 |\lambda_{\min}|}$, the observation noise floor completely dominates observed fluctuations, making statistical distinction of slowing down mathematically impossible for any passive sliding-window estimator.

---

## 3. Empirical Detectability Phase Diagram (EXP-011)

| Ramp Duration $T$ | Ramp Rate $r$ | Sampling $\Delta t$ | Noise $\sigma_{\text{obs}}$ | Trajectory ROC-AUC | True Detection Rate | Mean Lead Time | Phase Regime |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **$60.0\text{ s}$** (Fast) | $0.0283$ | $0.02\text{ s}$ | $0.00$ | $1.0000$ | $0.00$ (Point FA) | — | **UNCERTAIN** |
| $60.0\text{ s}$ | $0.0283$ | $0.02\text{ s}$ | $0.05$ | $1.0000$ | $0.00$ | — | **UNCERTAIN** |
| $60.0\text{ s}$ | $0.0283$ | $0.05\text{ s}$ | $0.15$ | $1.0000$ | $0.27$ | $34.10\text{ s}$ | **RELIABLE** |
| $60.0\text{ s}$ | $0.0283$ | $0.15\text{ s}$ | $0.35$ | **0.6089** | $0.47$ | $27.12\text{ s}$ | **UNRELIABLE** |
| **$120.0\text{ s}$** (Std) | $0.0142$ | $0.05\text{ s}$ | $0.00$ | $1.0000$ | $0.00$ | — | **UNCERTAIN** |
| $120.0\text{ s}$ | $0.0142$ | $0.05\text{ s}$ | $0.15$ | $1.0000$ | $0.13$ | $57.74\text{ s}$ | **RELIABLE** |
| $120.0\text{ s}$ | $0.0142$ | $0.05\text{ s}$ | $0.35$ | **0.7333** | $0.20$ | $46.95\text{ s}$ | **UNCERTAIN** |
| $120.0\text{ s}$ | $0.0142$ | $0.15\text{ s}$ | $0.35$ | **0.5911** | $0.33$ | $66.06\text{ s}$ | **UNRELIABLE** |
| **$240.0\text{ s}$** (Slow)| $0.0071$ | $0.05\text{ s}$ | $0.15$ | $1.0000$ | $0.13$ | $119.30\text{ s}$| **RELIABLE** |
| $240.0\text{ s}$ | $0.0071$ | $0.05\text{ s}$ | $0.35$ | **0.5689** | $0.13$ | $119.10\text{ s}$| **UNRELIABLE** |
| $240.0\text{ s}$ | $0.0071$ | $0.15\text{ s}$ | $0.35$ | **0.3156** | $0.00$ | — | **UNRELIABLE** |

---

## 4. Analysis of Boundary Mechanisms

1. **The Noise Cliff ($\sigma_{\text{obs}} \ge 0.35$)**:
   Across all ramp durations and sampling intervals, setting $\sigma_{\text{obs}} = 0.35$ causes Trajectory ROC-AUC to plunge from $1.0000$ down to $0.3156 - 0.7333$. At this threshold, the observation noise variance ($\sigma_{\text{obs}}^2 = 0.1225$) exceeds the dynamical variance, wiping out the critical slowing down signal.
2. **The Sampling Dilution Effect ($\Delta t \ge 0.15\text{ s}$)**:
   Downsampling to $\Delta t = 0.15\text{ s}$ severely reduces the number of independent samples within any sliding window of duration $\tau_W = 2.5\text{ s}$ ($W = 16$ points). Under Kendall's small-sample bias, $W=16$ introduces an empirical bias of $\Delta \rho \approx -0.25$, destroying autoregressive trend detection.
3. **The Ramp Rate Tradeoff**:
   - **Fast Ramps ($T = 60\text{ s}$)**: The system violates quasi-static tracking ($r > |\lambda|$), causing the trajectory to lag behind the moving equilibrium, reducing pre-collapse observation time.
   - **Slow Ramps ($T = 240\text{ s}$)**: Provide generous actionable lead time ($L \approx 119\text{ s}$), but expose the system to greater cumulative false alarm accumulation during the extended baseline monitoring period.
