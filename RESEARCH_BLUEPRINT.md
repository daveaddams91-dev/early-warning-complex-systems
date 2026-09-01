# Research Blueprint: Early-Warning Mathematics for Complex Systems

## 1. Problem Formulation and Mathematical Definition

### 1.1. Core Mathematical Problem
Consider an autonomous or non-autonomous $N$-dimensional continuous-time stochastic dynamical system governed by the Itô Stochastic Differential Equation (SDE):
$$\mathrm{d}\mathbf{x}(t) = \mathbf{f}(\mathbf{x}(t), \boldsymbol{\mu}(t))\,\mathrm{d}t + \mathbf{G}(\mathbf{x}(t), \boldsymbol{\mu}(t))\,\mathrm{d}\mathbf{W}(t)$$
where:
- $\mathbf{x}(t) \in \mathcal{X} \subseteq \mathbb{R}^N$ is the state vector at time $t \ge 0$.
- $\boldsymbol{\mu}(t) \in \mathcal{P} \subseteq \mathbb{R}^P$ is a time-dependent control parameter vector moving quasi-statically or at finite rate $\dot{\boldsymbol{\mu}} = \mathbf{v}$.
- $\mathbf{f}: \mathcal{X} \times \mathcal{P} \to \mathbb{R}^N$ is a smooth nonlinear vector field admitting equilibria $\mathbf{x}^*(\boldsymbol{\mu})$ such that $\mathbf{f}(\mathbf{x}^*(\boldsymbol{\mu}), \boldsymbol{\mu}) = \mathbf{0}$.
- $\mathbf{G}: \mathcal{X} \times \mathcal{P} \to \mathbb{R}^{N \times M}$ is the state/parameter-dependent noise dispersion matrix.
- $\mathbf{W}(t)$ is an $M$-dimensional standard Wiener process with $\mathbb{E}[\mathrm{d}\mathbf{W}(t)] = \mathbf{0}$ and $\mathbb{E}[\mathrm{d}\mathbf{W}(t)\mathrm{d}\mathbf{W}(t)^T] = \mathbf{I}_M \mathrm{d}t$.

### 1.2. Observation Model and Non-Leakage Constraint
The system is observed through a discrete measurement operator $\mathbf{h}: \mathbb{R}^N \to \mathbb{R}^K$ at discrete sampling instances $t_k = k \Delta t$ ($k = 1, 2, \dots, T$):
$$\mathbf{y}_k = \mathbf{h}(\mathbf{x}(t_k)) + \boldsymbol{\epsilon}_k, \quad \boldsymbol{\epsilon}_k \sim \mathcal{D}_{\text{noise}}(\mathbf{0}, \mathbf{R})$$
At any observation index $k$, an early warning algorithm $\mathcal{A}$ evaluates a warning score $W_k$:
$$W_k = \mathcal{A}(\{\mathbf{y}_1, \mathbf{y}_2, \dots, \mathbf{y}_k\})$$
**Strict Non-Leakage Axiom:** For all $k$, $\mathcal{A}$ depends strictly on historical and current measurements $\{\mathbf{y}_j\}_{j \le k}$. It has zero access to future observations $\{\mathbf{y}_j\}_{j > k}$, future parameter trajectories $\boldsymbol{\mu}(t > t_k)$, or the ground-truth collapse time $T_{\text{crit}}$.

### 1.3. Definition of Collapse and Critical Transition
Let $\mathcal{B}(\boldsymbol{\mu}) \subset \mathcal{X}$ denote the basin of attraction of a desirable/operational steady state $\mathbf{x}^*(\boldsymbol{\mu})$.
A **Critical Transition (Collapse)** occurs at time $T_{\text{crit}}$ if:
1. **Bifurcation-Induced (B-tipping):** For $\boldsymbol{\mu} \to \boldsymbol{\mu}_{\text{crit}}$, the real part of the leading eigenvalue $\lambda_{\max}(\mathbf{J})$ of the Jacobian $\mathbf{J} = \left.\frac{\partial \mathbf{f}}{\partial \mathbf{x}}\right|_{\mathbf{x}^*}$ crosses zero ($\mathrm{Re}(\lambda_{\max}) \to 0^-$), causing $\mathbf{x}^*(\boldsymbol{\mu})$ to undergo a codimension-1 bifurcation (Fold, Hopf, Transcritical, Pitchfork), and the state trajectory rapidly transitions to an alternative attractor or divergent state $\mathbf{x}_{\text{alt}} \notin \mathcal{B}_0$.
2. **Noise-Induced (N-tipping):** A large stochastic fluctuation $\int \mathbf{G}\mathrm{d}\mathbf{W}$ forces $\mathbf{x}(t)$ across the separatrix $\partial \mathcal{B}(\boldsymbol{\mu})$ at stationary $\boldsymbol{\mu} < \boldsymbol{\mu}_{\text{crit}}$.
3. **Rate-Induced (R-tipping):** The parameter drift speed $\|\dot{\boldsymbol{\mu}}\|$ exceeds the maximum contraction rate of the basin boundary, forcing $\mathbf{x}(t)$ out of the moving basin.

A valid early warning signal must trigger a binary alarm $\mathcal{A}_k = 1$ at time $t_{\text{alarm}} \le T_{\text{crit}} - \Delta t_{\min}$ with lead time $\Delta t_{\text{lead}} = T_{\text{crit}} - t_{\text{alarm}} > 0$.

---

## 2. Motivation and Research Questions

### Motivation
Abrupt critical transitions in real-world complex systems (ecosystem collapse, power grid blackouts, cardiac arrhythmias, financial crashes, ocean circulation shutdown) entail catastrophic systemic costs. If mathematical indicators can reliably forecast resilience loss prior to irreversible transition, preventive intervention becomes possible.

### Primary Research Questions
1. **RQ1 (Multivariate vs Univariate Efficacy):** Does combining statistical, dynamical, information-theoretic, and network spectral indicators into a composite score provide statistically significant improvements in ROC-AUC, PR-AUC, and Lead-Time $\Delta t_{\text{lead}}$ over any individual univariate indicator?
2. **RQ2 (Bifurcation Invariance):** Can a unified composite framework detect both Fold (real eigenvalue zero-crossing) and Hopf (complex conjugate imaginary axis crossing) transitions without manual parameter re-tuning?
3. **RQ3 (Adversarial Robustness & False Alarms):** How do individual vs composite indicators perform under Level 6 adversarial conditions (transient shocks, non-bifurcating parameter drift, colored red noise, and distractor noise channels)?
4. **RQ4 (Theoretical Limits):** What are the empirical boundary conditions where all early-warning indicators fail (e.g., pure N-tipping and high-rate R-tipping)?

---

## 3. Falsifiable Hypotheses

- **Hypothesis $H_1$ (Superiority of Composite Fusion):** Under stationary Gaussian measurement noise (Levels 1-2), a regularized multi-signal composite score achieves higher ROC-AUC ($p < 0.01$, Wilcoxon signed-rank test) than the single best univariate indicator ($AR(1)$ or Variance) across a benchmark suite of 5 diverse dynamical systems.
- **Hypothesis $H_2$ (Mitigation of Sensor Blindness):** In multi-node networks where observations are restricted to a random subset of nodes, multivariate/network composite indicators (e.g. PC1 variance / Mahalanobis / Algebraic connectivity) maintain ROC-AUC $> 0.80$, whereas single-node univariate indicators drop below ROC-AUC $0.65$ when the monitored node has low critical eigenvector centrality.
- **Hypothesis $H_3$ (Falsification under Adversarial Null Scenarios):** Under non-bifurcating parameter drift and transient non-collapsing shocks (Level 6), univariate variance and $AR(1)$ exhibit False Alarm Rates $> 35\%$, whereas a multi-metric rank-consistency or anomaly fusion framework reduces False Alarm Rates to $< 10\%$.
- **Hypothesis $H_4$ (Fundamental Failure Boundary on N-Tipping):** When transitions are driven purely by noise-induced basin escape (N-tipping) with constant control parameter $\boldsymbol{\mu}$, both univariate and composite CSD indicators perform no better than a random guess ($\text{ROC-AUC} \in [0.45, 0.55]$).

---

## 4. Mathematical Indicator Formulations

Let $\mathbf{z}_w = \{y_{k-w+1}, \dots, y_k\}$ be the sliding window of length $w$ for a univariate series (or multivariate matrix $\mathbf{Z}_w \in \mathbb{R}^{w \times K}$).

### 4.1. Statistical Indicators
1. **Variance ($\sigma^2$):**
   $$\sigma^2_k = \frac{1}{w-1} \sum_{j=1}^w (y_{k-w+j} - \bar{y}_w)^2$$
   *Theoretical scaling:* $\sigma^2 \propto \frac{\sigma_{\text{noise}}^2}{2 |\mathrm{Re}(\lambda_{\max})|} \to \infty$ as $\lambda_{\max} \to 0$.
2. **Lag-1 Autocorrelation ($AR(1)$ / $\rho_1$):**
   $$\rho_{1,k} = \frac{\sum_{j=1}^{w-1} (y_{k-w+j} - \bar{y}_w)(y_{k-w+j+1} - \bar{y}_w)}{\sum_{j=1}^w (y_{k-w+j} - \bar{y}_w)^2}$$
   *Theoretical scaling:* $\rho_1 = e^{-|\mathrm{Re}(\lambda_{\max})| \Delta t} \to 1$ as $\lambda_{\max} \to 0$.
3. **Skewness ($\gamma_1$):**
   $$\gamma_{1,k} = \frac{\frac{1}{w}\sum_{j=1}^w (y_{k-w+j} - \bar{y}_w)^3}{\sigma_k^3}$$
   *Theoretical scaling:* Asymmetry increases near asymmetric fold potential wells.
4. **Kurtosis ($\kappa$):**
   $$\kappa_k = \frac{\frac{1}{w}\sum_{j=1}^w (y_{k-w+j} - \bar{y}_w)^4}{\sigma_k^4} - 3$$
   *Theoretical scaling:* Fat tails emerge due to critical flickering between metastable states.

### 4.2. Dynamical & Spectral Indicators
5. **Autoregressive Recovery Rate ($\lambda_{\text{est}}$):**
   Fit $y_{j+1} = c + a_1 y_j + \epsilon_j$, estimate relaxation rate $\kappa_{\text{est}} = -\frac{\ln(a_1)}{\Delta t}$. $\kappa_{\text{est}} \to 0$ as CSD occurs.
6. **Spectral Peak Ratio / Low-Frequency Power Fraction ($S_{\text{low}}$):**
   Let $P(f)$ be the Welch periodogram. $S_{\text{low}} = \frac{\int_0^{f_{\text{cutoff}}} P(f)\mathrm{d}f}{\int_0^{f_{\text{Nyquist}}} P(f)\mathrm{d}f}$. Power shifts to zero frequency (reddening of spectrum) for Fold, and to $f_{\text{Hopf}}$ for Hopf.

### 4.3. Information-Theoretic Indicators
7. **Permutation Entropy ($H_{\text{perm}}$):**
   For embedding dimension $m$ (default $m=3$) and delay $\tau=1$, extract ordinal patterns $\pi \in S_m$. Compute empirical distribution $p(\pi)$, then:
   $$H_{\text{perm}} = -\frac{1}{\ln(m!)} \sum_{\pi} p(\pi) \ln p(\pi)$$
   *Theoretical scaling:* Approaches lower entropy as deterministic low-dimensional dynamics dominate over high-dimensional noise.

### 4.4. Multivariate & Network Spectral Indicators
8. **Leading Eigenvalue of Covariance Matrix ($\lambda_{\max}(\mathbf{\Sigma})$) / PCA-1 Variance:**
   Compute sample covariance $\mathbf{S}_w = \frac{1}{w-1} (\mathbf{Z}_w - \bar{\mathbf{Z}})^T (\mathbf{Z}_w - \bar{\mathbf{Z}})$. Compute $\lambda_{\max}(\mathbf{S}_w)$.
9. **Mahalanobis Distance ($D_M$):**
   Relative to baseline reference mean $\boldsymbol{\mu}_0$ and reference covariance $\mathbf{S}_0$:
   $$D_{M,k} = \sqrt{(\mathbf{y}_k - \boldsymbol{\mu}_0)^T (\mathbf{S}_0 + \delta \mathbf{I})^{-1} (\mathbf{y}_k - \boldsymbol{\mu}_0)}$$
10. **Dynamical Network Biomarker Index ($I_{\text{DNB}}$):**
    For a graph with $K$ nodes:
    $$I_{\text{DNB}} = \frac{\bar{\sigma}_{\text{nodes}} \cdot |\bar{r}_{\text{internal}}|}{1 + |\bar{r}_{\text{external}}|}$$
11. **Graph Algebraic Connectivity ($\lambda_2(\mathbf{L})$):**
    Compute empirical correlation graph thresholded at significance $\alpha$, construct Laplacian $\mathbf{L} = \mathbf{D} - \mathbf{A}$, compute Fiedler eigenvalue $\lambda_2$.

---

## 5. Candidate Composite Fusion Architectures

We will systematically evaluate and compare 5 distinct aggregation paradigms:
1. **CEWF-Linear (Standard Weighted Sum):**
   $$W_{\text{linear}}(t) = \sum_{i=1}^M w_i \tilde{S}_i(t), \quad w_i = 1/M \text{ (uniform) or inverse historical variance}$$
2. **CEWF-Rank (Non-Parametric Borda/Kendall Rank Aggregation):**
   Compute Kendall trend statistic $\tau(S_i, t)$ over past trend window $w_{\text{trend}}$. Composite score is the median/Borda rank of positive trend consensus:
   $$W_{\text{rank}}(t) = \frac{1}{M} \sum_{i=1}^M \max(0, \tau_{w_{\text{trend}}}(S_i))$$
3. **CEWF-Mahalanobis (Multi-Indicator Anomaly Distance):**
   Stack all normalized indicators into $\mathbf{s}(t) \in \mathbb{R}^M$. Measure distance from baseline stable regime distribution $\mathcal{N}(\boldsymbol{\mu}_{S,0}, \mathbf{\Sigma}_{S,0})$:
   $$W_{\text{Mahal}}(t) = (\mathbf{s}(t) - \boldsymbol{\mu}_{S,0})^T \mathbf{\Sigma}_{S,0}^{-1} (\mathbf{s}(t) - \boldsymbol{\mu}_{S,0})$$
4. **CEWF-ElasticNet (Penalized Logistic Regression):**
   Train regularized logistic classifier $P(\text{Transition within } \Delta T \mid \mathbf{s}(t)) = \sigma(\boldsymbol{\beta}^T \mathbf{s}(t) + \beta_0)$ with $L_1/L_2$ penalty strictly trained on separate synthetic training runs (cross-system evaluated).
5. **CEWF-BOCPD (Bayesian Online Changepoint Detection):**
   Recursive inference of hazard rate and run-length distribution over multi-indicator vector without future leakage (Adams & MacKay, 2007).

---

## 6. Experimental Benchmark Systems

| System ID | System Name | Dimension | Bifurcation / Transition Type | Key Equations & Parameter Ramp |
| :--- | :--- | :--- | :--- | :--- |
| **SYS-1** | May Harvesting Model | 1D | Fold (Saddle-Node) | $\frac{dx}{dt} = rx(1 - x/K) - \frac{c(t)x^2}{x^2 + d^2} + \sigma dW_t$, $c(t) \uparrow c_{\text{crit}} \approx 2.604$ |
| **SYS-2** | FitzHugh-Nagumo Oscillator | 2D | Supercritical Hopf | $\dot{v} = v - v^3/3 - w + I(t) + \sigma dW_1, \dot{w} = \epsilon(v + a - b w) + \sigma dW_2$, $I(t) \uparrow I_{\text{crit}}$ |
| **SYS-3** | Subcritical Pitchfork Model | 1D | Subcritical Pitchfork (Catastrophic jump) | $\dot{x} = \mu(t) x + x^3 - x^5 + \sigma dW_t$, $\mu(t) \uparrow \mu_{\text{crit}} = 0$ |
| **SYS-4** | Stommel 2-Box Ocean Model | 2D | Fold (AMOC shutdown) | $\dot{T} = \eta_1(T_0 - T) - |q(T,S)|T, \dot{S} = \eta_2(S_0 - S) - |q(T,S)|S + F(t) + \sigma dW_t$, $q = \alpha T - \beta S$ |
| **SYS-5** | Coupled Mutualistic Network | 10D / 20D | Network Cascade / Generalized Saddle-Node | $\dot{x}_i = x_i\left(\alpha_i - \beta_i x_i + \sum_{j} \frac{A_{ij} x_j}{1 + h \sum_k A_{ik} x_k}\right) - c(t)\frac{x_i^2}{x_i^2 + d^2} + \sigma dW_i$ |

---

## 7. Hierarchical 6-Level Experimental Design

- **Level 1 (Ideal Clean Synthetic):** No observation noise ($\mathbf{R} = \mathbf{0}$), fine sampling ($\Delta t = 0.05$). Verification of theoretical scaling laws.
- **Level 2 (Measurement Noise Regimes):** Add Gaussian white noise ($\mathrm{SNR} \in \{20, 10, 5, 0\text{ dB}\}$), heavy-tailed Student-$t$ ($\nu=3$), and colored red noise ($\dot{\eta} = -\gamma \eta + \sigma_{\eta}\xi$).
- **Level 3 (Sparse & Irregular Sampling):** Downsampling factors $k \in \{2, 5, 10, 20\}$; random dropout probability $p_{\text{drop}} \in \{0.1, 0.3, 0.5\}$.
- **Level 4 (Distractor Noise Variables):** Add $D \in \{1, 5, 10, 20\}$ uncoupled noise channels (AR(1) and random walks) to test multi-sensor robustness.
- **Level 5 (Cross-System Generalization):** Train composite models on SYS-1 (May), test zero-shot on SYS-2 (Hopf), SYS-4 (Stommel), and SYS-5 (Network).
- **Level 6 (Adversarial "Deceiver" Test Suite):**
  1. *Scenario 6A (Transient Shock):* Large pulse perturbation returning to stable basin.
  2. *Scenario 6B (Benign Parameter Drift):* Parameter ramps within stable interior without reaching bifurcation.
  3. *Scenario 6C (Pure N-Tipping):* Constant parameter, transition occurs via rare noise excursion.
  4. *Scenario 6D (Rate-Induced R-Tipping):* High ramp rate $\dot{\mu} \gg \lambda_{\text{relax}}$.

---

## 8. Evaluation Metrics & Statistical Verification Plan

1. **Receiver Operating Characteristic (ROC-AUC):** Sliding threshold classification performance distinguishing pre-transition windows from stationary baseline windows.
2. **Precision-Recall Area Under Curve (PR-AUC):** Performance under realistic imbalanced event frequencies.
3. **Lead-Time Distribution:** Report Median, 10th percentile, 90th percentile, and Interquartile Range (IQR) of $\Delta t_{\text{lead}} = T_{\text{crit}} - t_{\text{alarm}}$.
4. **False Alarm Rate on Null Series ($FAR_{\text{null}}$):** Fraction of null/stationary trajectories incorrectly flagged before $T_{\text{end}}$.
5. **Statistical Significance Testing:**
   - DeLong test for ROC-AUC differences between composite vs univariate indicators.
   - Wilcoxon signed-rank test across $N_{\text{sim}} \ge 100$ independent stochastic realizations per condition.
   - Bonferroni / Benjamini-Hochberg FDR correction across multi-hypothesis comparisons.
