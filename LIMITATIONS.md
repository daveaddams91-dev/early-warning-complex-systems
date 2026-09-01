# SYSTEM BOUNDARY CONDITIONS & SCIENTIFIC LIMITATIONS

**Project**: Early-Warning Mathematics for Complex Systems  
**Stage**: Phase 3 Definitive Limitations Audit  
**Author**: Principal Investigator & Hostile Scientific Auditor  
**Date**: September 2026  

---

## 1. Fundamental Mathematical Limitations

1. **Non-Smooth & Discontinuous Dynamics**:
   - Critical slowing down (CSD) theory is derived from the Taylor expansion of smooth vector fields near non-hyperbolic fixed points ($J \mathbf{v} = \lambda \mathbf{v}, \operatorname{Re}(\lambda) \to 0^-$).
   - In systems with piecewise-smooth or non-smooth vector fields—such as the Stommel ocean model ($\dot{T} \sim |T - S| T$) or stick-slip friction—the derivative $d|q|/dq$ is discontinuous. The local potential well does not flatten in a classical quadratic fashion, causing variance and autocorrelation divergence to fail completely ($\text{ROC-AUC} \le 0.490$, EXP-001).
2. **Hopf & Complex Conjugate Bifurcations**:
   - At a supercritical Hopf bifurcation, the Jacobian eigenvalues cross the imaginary axis as a complex conjugate pair $\alpha \pm i \omega$.
   - Because the autocorrelation function oscillates ($\rho(\tau) = e^{\alpha \tau} \cos(\omega \tau)$), scalar lag-1 autocorrelation $\operatorname{AR}(1)$ at fixed sampling lag $\Delta t$ can be zero or negative even when the system is on the verge of instability ($\text{AUC} = 0.507$, EXP-001).
3. **Noise-Induced (N-Tipping) & Rate-Induced (R-Tipping) Blindness**:
   - **N-Tipping**: When transitions occur via stochastic basin hopping across a deep barrier, eigenvalues remain strongly negative. CSD indicators exhibit zero prior warning ($0.0\%$ detection rate, EXP-007).
   - **R-Tipping**: When parameter drift rate $d\mu/dt$ exceeds the internal relaxation rate, the state escapes because it cannot track the moving equilibrium, not because eigenvalues vanish. CSD indicators cannot predict R-tipping ($0.0\%$ detection rate, EXP-007).

---

## 2. Observational & Sensor Limitations

1. **The Detectability Phase Boundary ($\text{SNR}_{\text{dyn}} < 1.0$)**:
   - When measurement noise $\sigma_{\text{obs}} \ge 0.20$, the observation noise variance completely masks dynamical critical slowing down fluctuations ($\text{ROC-AUC} \le 0.60$, EXP-004). Statistical early warning is fundamentally impossible unless measurement noise is reduced below the dynamical variance scale.
2. **Hidden Variables & Partial Observability**:
   - In coupled multi-dimensional systems where the unstable manifold is localized to unobserved state variables (e.g. unobserved species in an ecological web or deep ocean salinity), projections onto observed coordinates remain linear and calm until instantaneous collapse occurs ($0.0\%$ detection rate, EXP-007). Full state observability or leading eigenvector projection is a strict prerequisite.
3. **Sensor Noise Coloration**:
   - Autoregressive or red sensor noise simulates critical slowing down, causing scalar $\text{AR}(1)$ to collapse into $100\%$ false alarms under stationary conditions ($\text{AUC} = 0.384$, EXP-003).

---

## 3. Statistical & Methodological Limitations

1. **Finite-Window Kendall Bias (Small-Sample Downward Bias)**:
   - Rolling sliding-window estimators suffer from Kendall's 1954 small-sample bias:
     $$\mathbb{E}[\hat{\rho}_{1, W}] \approx \rho_{1} - \frac{1 + 3\rho_{1}}{W}$$
     For typical operational windows $W = 30$, empirical autocorrelation underestimates true physical correlation by up to $22\%$ ($\Delta \rho \approx -0.22$, EXP-008).
2. **Cumulative False Alarm Probability (False Alarm Cascades)**:
   - When an operational threshold $\theta$ is set at the 95th percentile ($\alpha = 0.05$), the probability of triggering at least one false alarm across $M = 400$ independent monitoring steps is:
     $$P(\text{False Alarm}) = 1 - (1 - 0.05)^{400} \approx 99.9999999\%$$
     Single-point thresholding guarantees false alarm cascades ($100\%$ early false alarm rate, EXP-001) unless strict temporal persistence filters ($K_{\text{persist}} \ge 5$) or consensus filters are applied.
3. **Informational Latency in Distinguishing Disturbances from Collapse**:
   - Immediately following an exogenous shock ($t \in [0, 15]\text{ s}$ post-shock), the Kolmogorov-Smirnov distance and Wasserstein distance between a resilient recovery trajectory and an impending collapse trajectory are near zero ($W_1 < 0.05$, EXP-005). Passive statistics cannot determine whether the system will recover or tip until an irreducible informational latency has elapsed.

---

## 4. Operational, Control & Real-World Limitations

1. **No Real-World Guarantee**:
   - Success in synthetic SDE models does NOT guarantee real-world forecasting accuracy in climate, ecological, neurological, or financial systems where governing equations are unknown, non-stationary, and subjected to non-Gaussian Levy flights.
2. **Control Authority Window**:
   - Stabilizing feedback control ($u(t) = -K (x - x_{\text{target}})$) can arrest tipping only if actuated with positive lead time ($L \ge 5\text{ s}$) before the saddle-node crossing. Once the bifurcation point is passed, the operational equilibrium ceases to exist, and stabilizing control fails (EXP-006).
3. **Absence of Actuators in Planetary and Ecological Systems**:
   - While active perturbation probing and feedback control resolve passive observation ambiguities in software simulations, real-world climate tipping elements (e.g. AMOC, Greenland Ice Sheet) lack physical actuators for controlled planetary-scale interventions.
