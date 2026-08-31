# SYSTEM LIMITATIONS & OPERATIONAL BOUNDARIES

**Project Title**: Early-Warning Mathematics for Complex Systems: A Rigorous Multivariate and Adversarial Benchmark  
**Document**: Mathematical & Empirical Boundaries of Early-Warning Signals (EWS)

---

## 1. Mathematical Boundaries (Where Theory Forbids EWS)

The mathematical theory of Critical Slowing Down (CSD) rests on three explicit mathematical assumptions:
1. **Quasistatic Parameter Evolution**: $\left| \frac{d\mu}{dt} \right| \ll \left| \operatorname{Re}(\lambda_{\max}(\mathbf{J})) \right|$.
2. **Local Bifurcation Manifold (B-Tipping)**: The transition occurs as a real eigenvalue or pair of complex conjugate eigenvalues crosses the imaginary axis: $\lim_{\mu \to \mu_c} \operatorname{Re}(\lambda_{\max}(\mu)) = 0^-$.
3. **Small Perturbation Gaussianity**: Fluctuation dynamics can be linearized: $d\mathbf{y} \approx \mathbf{J} \mathbf{y} dt + \mathbf{\Sigma} d\mathbf{W}$.

### 1.1 Pure Noise-Induced Transitions (N-Tipping)
* **Definition**: A non-linear stochastic transition occurring in a bistable potential where the parameter $\mu$ is stationary ($\frac{d\mu}{dt} = 0$) and far from any bifurcation point ($\mu \ll \mu_c$). Escape occurs purely due to large, rare Brownian excursions across the saddle point separating basins of attraction (Kramers' escape rate $\tau_K \propto \exp(\Delta U / \sigma^2)$).
* **Failure Mechanism**: Since $\mu$ is constant, $\mathbf{J}(\mathbf{x}^*)$ and $\operatorname{Re}(\lambda_{\max})$ are strictly constant. The stationary covariance $\mathbf{C} = \mathbb{E}[\mathbf{y} \mathbf{y}^T]$ remains constant up to the moment of escape.
* **Empirical Validation**: In Benchmark Level 6C, **all** 16 tested indicators and composite models produced exactly **$0.0\%$ detection rate** and **$0.0\text{ s}$ lead time**.
* **Takeaway**: EWS methods based on CSD *cannot* detect N-tipping transitions.

### 1.2 Rate-Induced Transitions (R-Tipping)
* **Definition**: Transitions occurring when a parameter ramps faster than the system's intrinsic relaxation timescale ($\left| \frac{d\mu}{dt} \right| > \left| \lambda_{\max} \right|$), causing the state trajectory to track outside the moving basin of attraction even if no static bifurcation occurs.
* **Failure Mechanism**: The quasistatic ergodic assumption fails. The trajectory is in a non-equilibrium transient state. Sliding estimation windows $W$ cannot accumulate sufficient samples from an instantaneous local equilibrium to estimate the changing autocorrelation structure before the transition has already taken place.
* **Empirical Validation**: In Benchmark Level 6D (Fast R-Tipping), all indicators yielded a **$0.0\%$ advance detection rate**.
* **Takeaway**: EWS methods require adiabatic separation of timescales.

---

## 2. Statistical & Observational Limitations

### 2.1 Bandwidth-Variance Tradeoff in Sliding Windows
* **The Dilemma**: 
  - To detect critical slowing down, the sliding window width $W$ must be large enough to obtain low-variance sample estimates ($W \gg 1 / |\lambda|$).
  - Simultaneously, $W$ must be small enough that the parameter $\mu(t)$ is approximately constant within the window ($W \ll \mu_c / |d\mu/dt|$).
* **Failure Mode**: When the parameter ramp is moderately fast, this admissible window interval shrinks to the empty set ($\emptyset$), rendering reliable sample estimation mathematically impossible.

### 2.2 Sensitivity to Exogenous Shocks (Level 6A)
* **The Mechanism**: A single exogenous impulse shock (e.g. extreme environmental event, economic shock) introduces a large step discontinuity into the time series.
* **Failure Mode**: As the system relaxes back to equilibrium, the transient return trajectory exhibits high sample variance and high autocorrelation over the sliding window, causing Kendall trend and threshold detectors to trigger a **$100\%$ False Alarm Rate ($\text{FAR} = 1.0$)** despite the system possessing a deep, stable potential well.

### 2.3 Non-Smooth / Discontinuous Vector Fields (Level 1 SYS-4)
* **The Mechanism**: Systems with non-smooth switching dynamics (such as the Stommel ocean convection model governed by absolute flow rates $|T - S|$) violate the smooth Taylor-series expansions underlying fold normal forms ($dx/dt = \mu - x^2$).
* **Failure Mode**: The analytical covariance and autocorrelation do not exhibit monotonic $1/\sqrt{\mu_c - \mu}$ divergence, reducing detection metrics to near chance ($\text{ROC-AUC} \approx 0.51$).

---

## 3. Practical Prescriptions for Practitioners

1. **Never Rely on a Single Indicator**: Univariate indicators (especially AR(1)) are easily tricked by colored noise or non-monotonic drift.
2. **Apply Covariance-Regularized Distance**: Use `CEWF-Mahalanobis` with Tikhonov regularization ($\mathbf{\Sigma} + \epsilon \mathbf{I}$) to guard against multi-collinearity and measurement noise.
3. **Audit for Non-Bifurcation Regimes**: If the system is subject to fast parameter ramps or rare heavy-tailed shocks, complement EWS with mechanistic physics-based basin modeling and Bayesian online changepoint detection.
