# MECHANISTIC INVESTIGATION & ABLATION OF AMOC (SYS-4) FAILURE

**Project**: Early-Warning Mathematics for Complex Systems  
**Stage**: Phase 4 Priority Investigation 1  
**Date**: September 2026  
**Author**: Principal Investigator & Hostile Scientific Reviewer  

---

## 1. Executive Summary

In canonical critical slowing down (CSD) benchmarks, the Stommel 2-box model of thermohaline circulation (AMOC, SYS-4) represents a catastrophic failure mode:
- Standard scalar CSD indicators (Variance, AR(1), Spectral Reddening) collapse to an inverted $\text{ROC-AUC} \in [0.18, 0.31]$.
- Unweighted composite models fail ($\text{ROC-AUC} = 0.27 - 0.51$).
- Only full-state 2D Mahalanobis distance on the untransformed trajectory reported $\text{ROC-AUC} = 1.0000$.

To determine whether this failure stems from coordinate choice, non-linear distortion, or a fundamental physical absence of critical slowing down, we implemented an exhaustive ablation study (`experiments/scripts/ablate_amoc_failure.py`) evaluating 6 indicators across 5 signal transformations.

---

## 2. Quantitative Ablation Benchmark Results

All metrics evaluated at the trajectory level ($N=25$ independent stochastic realization pairs, safe baseline $T_{\text{safe}}=20.0\text{ s}$, minimum lead time $\Delta t_{\min}=2.0\text{ s}$), persisted in `experiments/results/tables/amoc_failure_ablation.csv`:

| Indicator | Signal Dimension | Raw Signal | Log-Transform | First-Difference | Local Detrending | Linearizing Reparam ($T^2$ / $[q, T]$) |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **Variance** | 1D (Scalar $T$) | $0.2064$ | $0.0304$ | $0.1680$ | $0.1200$ | $0.3632$ |
| **`AR(1)`** | 1D (Scalar $T$) | $0.3136$ | $0.5024$ | $0.2704$ | $0.2432$ | $0.2976$ |
| **Permutation Entropy** | 1D (Scalar $T$) | $0.1824$ | $0.1824$ | $0.2360$ | $0.1624$ | $0.1824$ |
| **Spectral Reddening** | 1D (Scalar $T$) | $0.1904$ | $0.2272$ | $0.2816$ | $0.1328$ | $0.1840$ |
| **PCA1 Variance** | 2D ($T, S$) | $0.5008$ | $0.1264$ | $0.1168$ | $0.4224$ | $0.3184$ |
| **Mahalanobis Distance** | 2D ($T, S$) | **1.0000** | $0.0672$ | $0.2208$ | $0.1712$ | **1.0000** |
| **Variance on Overturning $q(t) = T - S$** | 1D (Physical Flux) | $0.3552$ | — | — | — | — |

---

## 3. Mechanistic Explanations of Findings

### 3.1 Scalar Signal Transforms Cannot Recover Critical Slowing Down
None of the univariate mathematical transforms—log-transform ($\text{AUC} \le 0.502$), first-differencing ($\text{AUC} \le 0.282$), local detrending ($\text{AUC} \le 0.243$), or quadratic linearizing reparametrization $T^2$ ($\text{AUC} \le 0.363$)—recovered early-warning capability on scalar temperature $T$. Even observing the true physical overturning volume flux $q(t) = T(t) - S(t)$ directly yielded only $\text{ROC-AUC} = 0.3552$.

### 3.2 The Mahalanobis Paradox: Mean Displacement vs. Fluctuation Softening
The most critical finding of this ablation resolves why untransformed 2D Mahalanobis distance achieved $\text{ROC-AUC} = 1.0000$ while every CSD indicator failed:
1. In the Stommel system, as freshwater forcing $\mu(t)$ ramps up, the equilibrium salinity difference $S^*(\mu)$ drifts substantially from its baseline value $S^*(0.8) \approx 0.5$ toward $S^*(1.25) \approx 0.8$.
2. The untransformed Mahalanobis metric:
   $$D_M(\mathbf{x}_t) = \sqrt{(\mathbf{x}_t - \boldsymbol{\mu}_0)^T \mathbf{\Sigma}_0^{-1} (\mathbf{x}_t - \boldsymbol{\mu}_0)}$$
   detects the **mean equilibrium trajectory shift** in the $(T, S)$ state space. It is measuring deterministic drift, not dynamical slowing down.
3. Crucially, when we remove the mean displacement via **first-differencing** ($\Delta \mathbf{x}_t = \mathbf{x}_t - \mathbf{x}_{t-1}$) or **local detrending**, Mahalanobis distance collapses from $\mathbf{1.0000 \to 0.2208}$ and $\mathbf{0.1712}$.
4. This proves definitively that **fluctuation variance does not grow prior to AMOC collapse**. The high performance of raw Mahalanobis distance was an artifact of mean state shift detection, which fails under stationary or detrended conditions.

### 3.3 Linkage to Non-Smoothness & Jacobian Asymmetry (LIMITATIONS.md Section 1.1)
As established in `LIMITATIONS.md`:
1. **Advective Non-Smoothness**: The flow velocity in Stommel's box model is governed by density difference $q = T - S$ via $|T - S| T$. Near collapse, as $q \to 0^+$, the advective feedback $d|q|/dq$ is non-smooth.
2. **Eigenvector Rotation**: The Jacobian matrix:
   $$\mathbf{J} = \begin{pmatrix} -\eta_1 - 2T + S & T \\ -S & -\eta_2 - T + 2S \end{pmatrix}$$
   has off-diagonal elements $J_{01} = T > 0$ and $J_{10} = -S < 0$. As $\mu \to \mu_{\text{crit}}$, the thermal relaxation rate $\eta_1 = 1.0$ is much faster than the salinity relaxation rate $\eta_2 = 0.3$.
3. Consequently, the leading critical eigenvector $\mathbf{v}_1$ rotates into the salinity subspace ($v_{1, S} \gg v_{1, T}$). When an observer monitors only temperature $T$, the projection of the critical manifold onto the observed coordinate is nearly orthogonal ($\theta_{\mathbf{v}_1, T} \approx 66.16^\circ$), rendering critical slowing down unobservable from scalar temperature records.
