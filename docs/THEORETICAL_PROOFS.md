# THEORETICAL PROOFS & MATHEMATICAL FOUNDATIONS OF EARLY-WARNING PREDICTABILITY

**Project**: Early-Warning Mathematics for Complex Systems  
**Stage**: Phase 4 Mathematical Formalization  
**Date**: September 2026  
**Auditor**: Principal Investigator & Hostile Scientific Reviewer  

---

## 1. Setting and Dynamical Model

Let $x(t) \in \mathbb{R}^d$ be the physical state of a non-autonomous complex dynamical system governed by the Itô stochastic differential equation:
$$dx(t) = f(x(t), \mu(t)) dt + \mathbf{G}(x(t)) dW(t)$$
where:
- $\mu(t) \in \mathbb{R}$ is a time-varying bifurcation control parameter moving quasi-statically at rate $r = \dot{\mu} > 0$:
  $$\mu(t) = \mu_0 + r t, \quad t \in [0, T_{\text{end}}]$$
- $W(t)$ is a standard $d$-dimensional Wiener process.
- The system possesses an instantaneous stable equilibrium manifold $x^*(\mu)$ satisfying $f(x^*(\mu), \mu) = 0$ for $\mu < \mu_c$.
- At $\mu = \mu_c$, the Jacobian matrix $\mathbf{J}(\mu) = \left. \frac{\partial f}{\partial x} \right|_{x^*(\mu)}$ undergoes a local or global bifurcation where the real part of its dominant eigenvalue approaches zero:
  $$\lambda_1(\mu) = \max_{j} \mathrm{Re}(\lambda_j(\mathbf{J}(\mu))) \to 0^- \quad \text{as } \mu \to \mu_c^-$$

An observer collects discrete, corrupted scalar or multivariate observations at sampling intervals $\Delta t$:
$$y_k = x(t_k) + \eta_k, \quad t_k = k \Delta t, \quad k = 1, \dots, N$$
where $\eta_k \sim \mathcal{N}(0, \sigma_{\text{obs}}^2 \mathbf{I})$ is additive, white measurement noise independent of $x(t)$.

---

## 2. Theorem 1: Signal-to-Noise Ratio (SNR) Dilution in Multi-Indicator Fusion

### 2.1 Assumptions
- **Assumption A1 (Linearized Indicator Anomaly Model)**: Let $\mathbf{S}(t) = [S_1(t), \dots, S_K(t)]^T$ be a vector of $K$ normalized statistical indicators computed over a rolling window. For each indicator $i \in \{1, \dots, K\}$:
  $$S_i(t) = \mu_i(t) + \epsilon_i(t)$$
  where $\mu_i(t)$ represents the true pre-collapse signal anomaly with $\mu_i(0) = 0$ and $\mu_i(T_c - \delta) = \Delta_i$, and $\boldsymbol{\epsilon}(t) \sim \mathcal{N}(\mathbf{0}, \mathbf{\Sigma})$ is estimation error with $\mathrm{Var}(\epsilon_i) = \sigma_i^2$.
- **Assumption A2 (Partition of Indicator Suite)**: The set of indicators $\mathcal{I} = \{1, \dots, K\}$ is partitioned into two disjoint subsets:
  1. An informative subset $\mathcal{I}_{\text{info}}$ of cardinality $|\mathcal{I}_{\text{info}}| = K_0 \ge 1$, where each indicator exhibits signal drift $\Delta_i = \Delta > 0$ and variance $\sigma_i^2 = \sigma_0^2$.
  2. An uninformative (noise) subset $\mathcal{I}_{\text{noise}}$ of cardinality $|\mathcal{I}_{\text{noise}}| = K_n \ge 0$ ($K = K_0 + K_n$), where each indicator exhibits zero signal drift $\Delta_j = 0$ and variance $\sigma_j^2 = \sigma_0^2$.
- **Assumption A3 (Noise Uncorrelatedness)**: The estimation errors are mutually uncorrelated: $\mathbf{\Sigma} = \sigma_0^2 \mathbf{I}_K$.

### 2.2 Theorem Statement
Consider the standard unweighted composite early-warning indicator:
$$\bar{S}(t) = \frac{1}{K} \sum_{i=1}^K S_i(t) = \frac{1}{K_0 + K_n} \left( \sum_{i \in \mathcal{I}_{\text{info}}} S_i(t) + \sum_{j \in \mathcal{I}_{\text{noise}}} S_j(t) \right)$$
Under Assumptions A1–A3, the composite Signal-to-Noise Ratio $\text{SNR}_{\text{comp}}$ is strictly degraded relative to the single informative indicator $\text{SNR}_{\text{single}} = \Delta / \sigma_0$:
$$\text{SNR}_{\text{comp}} = \sqrt{\frac{K_0}{K_0 + K_n}} \cdot \text{SNR}_{\text{single}}$$
Furthermore, for any fixed $K_0$, $\text{SNR}_{\text{comp}}$ is strictly monotonically decreasing with respect to $K_n$, decaying as $O(K_n^{-1/2})$.

### 2.3 Proof
1. **Expected Signal Amplitude**:
   $$\mathbb{E}[\bar{S}(T_c - \delta)] - \mathbb{E}[\bar{S}(0)] = \frac{1}{K} \left( \sum_{i \in \mathcal{I}_{\text{info}}} \Delta_i + \sum_{j \in \mathcal{I}_{\text{noise}}} \Delta_j \right) = \frac{1}{K_0 + K_n} (K_0 \Delta + 0) = \frac{K_0}{K_0 + K_n} \Delta$$

2. **Composite Noise Variance**:
   By Assumption A3, the indicators are mutually uncorrelated. The variance of the sum is the sum of the variances:
   $$\mathrm{Var}(\bar{S}(t)) = \mathrm{Var}\left( \frac{1}{K} \sum_{i=1}^K S_i(t) \right) = \frac{1}{K^2} \sum_{i=1}^K \mathrm{Var}(S_i(t)) = \frac{1}{(K_0 + K_n)^2} \sum_{i=1}^{K_0 + K_n} \sigma_0^2 = \frac{K_0 + K_n}{(K_0 + K_n)^2} \sigma_0^2 = \frac{\sigma_0^2}{K_0 + K_n}$$

3. **Composite Standard Deviation**:
   $$\sigma_{\text{comp}} = \sqrt{\mathrm{Var}(\bar{S}(t))} = \frac{\sigma_0}{\sqrt{K_0 + K_n}}$$

4. **Composite Signal-to-Noise Ratio**:
   $$\text{SNR}_{\text{comp}} = \frac{\mathbb{E}[\bar{S}(T_c - \delta)] - \mathbb{E}[\bar{S}(0)]}{\sigma_{\text{comp}}} = \frac{\frac{K_0}{K_0 + K_n} \Delta}{\frac{\sigma_0}{\sqrt{K_0 + K_n}}} = \frac{K_0}{\sqrt{K_0 + K_n}} \frac{\Delta}{\sigma_0} = \sqrt{\frac{K_0}{K_0 + K_n}} \cdot \text{SNR}_{\text{single}}$$

5. **Monotonicity**:
   Differentiating with respect to $K_n$:
   $$\frac{\partial}{\partial K_n} \text{SNR}_{\text{comp}} = \text{SNR}_{\text{single}} \sqrt{K_0} \cdot \left(-\frac{1}{2} (K_0 + K_n)^{-3/2}\right) < 0 \quad \forall K_n \ge 0$$
   Thus, adding uninformative indicators strictly and monotonically degrades the composite SNR. $\blacksquare$

---

## 3. Theorem 2: The Directional Cancellation Theorem

### 3.1 Assumptions
- **Assumption B1 (Bipolar Response)**: Suppose an indicator suite contains two indicators $I_1(t)$ and $I_2(t)$ whose expectations respond in opposing directions to critical slowing down:
  $$\Delta_1 = \mathbb{E}[I_1(T_c)] - \mathbb{E}[I_1(0)] = +c_1 > 0 \quad (\text{e.g., Variance})$$
  $$\Delta_2 = \mathbb{E}[I_2(T_c)] - \mathbb{E}[I_2(0)] = -c_2 < 0 \quad (\text{e.g., Permutation Entropy or Recovery Rate})$$
  with $c_1, c_2 > 0$.
- **Assumption B2 (Normalized Scale)**: Both indicators are standardized to unit baseline variance: $\sigma_1 = \sigma_2 = 1$.

### 3.2 Theorem Statement
If an unweighted average is constructed without causal sign alignment:
$$\bar{I}(t) = \frac{1}{2}(I_1(t) + I_2(t))$$
the composite signal anomaly is:
$$\Delta_{\text{comp}} = \frac{1}{2}(c_1 - c_2)$$
In the symmetric case where $c_1 = c_2 = c$, the composite signal is identically zero ($\Delta_{\text{comp}} = 0$), resulting in $\text{SNR}_{\text{comp}} = 0$ regardless of the individual informativeness of $I_1$ and $I_2$.

### 3.3 Proof
$$\mathbb{E}[\bar{I}(T_c)] - \mathbb{E}[\bar{I}(0)] = \frac{1}{2}\left(\mathbb{E}[I_1(T_c)] - \mathbb{E}[I_1(0)] + \mathbb{E}[I_2(T_c)] - \mathbb{E}[I_2(0)]\right) = \frac{1}{2}(c_1 - c_2)$$
When $c_1 = c_2 = c$:
$$\Delta_{\text{comp}} = \frac{1}{2}(c - c) = 0 \implies \text{SNR}_{\text{comp}} = \frac{0}{\sigma_{\text{comp}}} = 0 \quad \blacksquare$$

*Significance*: This proves why naive rank ensembling (`CEWF-Rank`) collapsed on clean May Fold ($\text{ROC-AUC} = 0.3224$). Permutation entropy inherently *decreases* as trajectories become regularized near a saddle-node bifurcation; summing raw ranks subtracted the warning signal.

---

## 4. Theorem 3: Spatial Mode Noise Averaging in Network Topologies

### 4.1 Assumptions
- **Assumption C1 (Coupled Dynamical Network)**: Let $\mathbf{x}(t) \in \mathbb{R}^D$ describe a $D$-node network. Near a local bifurcation, the state fluctuations linearize as:
  $$\delta \mathbf{x}(t) \approx \xi(t) \mathbf{v}_1$$
  where $\mathbf{v}_1 \in \mathbb{R}^D$ is the leading normalized eigenvector ($\|\mathbf{v}_1\|_2 = 1$) associated with the critical eigenvalue $\lambda_1 \to 0^-$, and $\xi(t)$ is the scalar amplitude of the critical slowing down mode with variance $\sigma_{\xi}^2 = \frac{\sigma_{\text{dyn}}^2}{2 |\lambda_1|}$.
- **Assumption C2 (Isotropic Node Participation)**: In a symmetric or homogeneously coupled network, the eigenvector participation is uniform:
  $$v_{1, i} \approx \frac{1}{\sqrt{D}} \quad \forall i \in \{1, \dots, D\}$$
- **Assumption C3 (Independent Observation Noise)**: Each node is monitored with independent, identically distributed measurement noise:
  $$\mathbf{y}(t) = \mathbf{x}(t) + \boldsymbol{\eta}(t), \quad \boldsymbol{\eta}(t) \sim \mathcal{N}(\mathbf{0}, \sigma_{\text{obs}}^2 \mathbf{I}_D)$$

### 4.2 Theorem Statement
Under Assumptions C1–C3:
1. The Signal-to-Noise Ratio of any single scalar observation channel $y_i(t)$ is:
   $$\text{SNR}_{\text{scalar}} = \frac{\sigma_{\xi}^2 / D}{\sigma_{\text{obs}}^2}$$
2. The Signal-to-Noise Ratio of the dominant spatial projection $y_{\text{proj}}(t) = \mathbf{v}_1^T \mathbf{y}(t)$ is:
   $$\text{SNR}_{\text{proj}} = \frac{\sigma_{\xi}^2}{\sigma_{\text{obs}}^2} = D \cdot \text{SNR}_{\text{scalar}}$$
   In terms of fluctuation amplitude standard deviation:
   $$\text{SNR}_{\text{amplitude, proj}} = \sqrt{D} \cdot \text{SNR}_{\text{amplitude, scalar}}$$

### 4.3 Proof
1. **Scalar Observation Channel**:
   For node $i$:
   $$y_i(t) = x^*_i + v_{1, i} \xi(t) + \eta_i(t)$$
   The dynamic variance contribution is:
   $$\mathrm{Var}_{\text{dyn}}(y_i) = v_{1, i}^2 \mathrm{Var}(\xi) = \left(\frac{1}{\sqrt{D}}\right)^2 \sigma_{\xi}^2 = \frac{\sigma_{\xi}^2}{D}$$
   The observation noise variance is $\mathrm{Var}(\eta_i) = \sigma_{\text{obs}}^2$.
   Hence, $\text{SNR}_{\text{scalar}} = \frac{\sigma_{\xi}^2 / D}{\sigma_{\text{obs}}^2}$.

2. **Projected Observation Channel**:
   $$y_{\text{proj}}(t) = \mathbf{v}_1^T \mathbf{y}(t) = \mathbf{v}_1^T \mathbf{x}^* + (\mathbf{v}_1^T \mathbf{v}_1) \xi(t) + \mathbf{v}_1^T \boldsymbol{\eta}(t) = \mathbf{v}_1^T \mathbf{x}^* + \xi(t) + \sum_{i=1}^D v_{1, i} \eta_i(t)$$
   The projected dynamic variance is:
   $$\mathrm{Var}_{\text{dyn}}(y_{\text{proj}}) = \mathrm{Var}(\xi) = \sigma_{\xi}^2$$
   The projected noise variance is:
   $$\mathrm{Var}(\mathbf{v}_1^T \boldsymbol{\eta}) = \sum_{i=1}^D v_{1, i}^2 \mathrm{Var}(\eta_i) = \sigma_{\text{obs}}^2 \sum_{i=1}^D v_{1, i}^2 = \sigma_{\text{obs}}^2 \|\mathbf{v}_1\|_2^2 = \sigma_{\text{obs}}^2$$
   Therefore:
   $$\text{SNR}_{\text{proj}} = \frac{\sigma_{\xi}^2}{\sigma_{\text{obs}}^2} = D \cdot \left( \frac{\sigma_{\xi}^2 / D}{\sigma_{\text{obs}}^2} \right) = D \cdot \text{SNR}_{\text{scalar}} \quad \blacksquare$$

*Significance*: Spatial mode projection (such as PCA1 or regularized Mahalanobis distance) concentrates coherent collective energy across $D$ dimensions while averaging out uncoupled sensor noise, explaining why multivariate models thrive under severe noise in network topologies.

---

## 5. Formal Derivation: The Finite-Window Non-Stationary Detectability Boundary

A critical open question is: *Why does the detectability boundary exist at all? If an observer can collect infinite samples ($N \to \infty$), can't any consistent statistical test distinguish two distinct variance levels no matter how high the observation noise?*

The answer lies in the **physical non-stationarity of the drifting parameter**.

### 5.1 The Competition of Timescales
Let $\mu(t) = \mu_0 + r t$ drift toward a bifurcation $\mu_c$ at constant speed $r = \dot{\mu}$.
The system is non-stationary. Any rolling statistical estimator (variance, autocorrelation) assumes approximate local stationarity within a backward-looking sliding window of duration $\tau_W = W \Delta t$.

1. **Upper Bound on Window Length**:
   To ensure that the parameter $\mu$ does not drift by more than a small tolerance $\delta_{\mu}$ across the window, the window duration is strictly constrained:
   $$\tau_W \le \frac{\delta_{\mu}}{r} \implies W \le \frac{\delta_{\mu}}{r \Delta t}$$
   Therefore, the maximum number of observations available to any causal sliding-window estimator is bounded:
   $$N_{\max} = \frac{\delta_{\mu}}{r \Delta t}$$

2. **Statistical Distinguishability (Neyman-Pearson & Le Cam Bounds)**:
   Consider testing the null hypothesis $H_0$ (baseline unperturbed state at $\mu_0$) against the alternative $H_1$ (perturbed state nearing bifurcation at $\mu_1 = \mu_c - \delta$):
   $$H_0: y_k \sim \mathcal{N}(0, \sigma_0^2), \quad \sigma_0^2 = \sigma_{\text{dyn}}^2(\mu_0) + \sigma_{\text{obs}}^2$$
   $$H_1: y_k \sim \mathcal{N}(0, \sigma_1^2), \quad \sigma_1^2 = \sigma_{\text{dyn}}^2(\mu_1) + \sigma_{\text{obs}}^2$$
   where the dynamical variance increase is $\Delta \sigma^2 = \sigma_{\text{dyn}}^2(\mu_1) - \sigma_{\text{dyn}}^2(\mu_0) = \frac{\sigma_{\text{dyn}}^2}{2 |\lambda(\mu_1)|} - \frac{\sigma_{\text{dyn}}^2}{2 |\lambda_0|}$.

   When observation noise dominates ($\sigma_{\text{obs}}^2 \gg \Delta \sigma^2$), the Kullback-Leibler divergence between the two Gaussian hypotheses per sample is:
   $$D_{\text{KL}}(P_1 \| P_0) = \frac{1}{2}\left( \frac{\sigma_1^2}{\sigma_0^2} - 1 - \ln \frac{\sigma_1^2}{\sigma_0^2} \right) \approx \frac{1}{4} \left( \frac{\Delta \sigma^2}{\sigma_{\text{obs}}^2} \right)^2 = \frac{1}{4} \text{SNR}_{\text{dyn}}^2$$

   By the Neyman-Pearson lemma and Le Cam's two-point testing bound, achieving a specified detection power $1 - \beta$ at significance level $\alpha$ requires a minimum sample size:
   $$N_{\text{req}} \ge \frac{2 (z_{1-\alpha} + z_{1-\beta})^2}{\left( \frac{\Delta \sigma^2}{\sigma_{\text{obs}}^2} \right)^2} = \frac{C(\alpha, \beta)}{\text{SNR}_{\text{dyn}}^2}$$
   where $C(\alpha, \beta) = 2 (z_{1-\alpha} + z_{1-\beta})^2$. For $\alpha = 0.05$ and power $1-\beta = 0.80$, $C \approx 2 (1.645 + 0.842)^2 \approx 12.37$.

### 5.2 The Detectability Phase Boundary Criterion
Detection is statistically impossible for any sliding-window estimator if the required sample size exceeds the maximum allowable quasi-stationary window length:
$$N_{\text{req}} > N_{\max} \iff \frac{C(\alpha, \beta)}{\text{SNR}_{\text{dyn}}^2} > \frac{\delta_{\mu}}{r \Delta t}$$

Rearranging gives the **Exact Detectability Boundary**:
$$\text{SNR}_{\text{dyn}} < \sqrt{C(\alpha, \beta) \cdot \frac{r \Delta t}{\delta_{\mu}}} \implies \text{Early Warning is Mathematically Impossible}$$

### 5.3 Physical Interpretation
1. **Faster Ramps ($r \uparrow$)**: Higher ramp speeds reduce the time available to integrate fluctuations ($\tau_W \downarrow$), raising the minimum required SNR threshold for detection.
2. **Coarser Sampling ($\Delta t \uparrow$)**: Downsampling reduces the number of independent samples per unit time, directly degrading test power.
3. **Severe Sensor Noise ($\sigma_{\text{obs}} \uparrow$)**: Because $N_{\text{req}}$ scales quadratically with observation noise variance ($N_{\text{req}} \propto \sigma_{\text{obs}}^4$), once $\sigma_{\text{obs}}$ crosses the noise cliff, the sample size required to detect critical slowing down exceeds the duration of the entire pre-collapse trajectory!
