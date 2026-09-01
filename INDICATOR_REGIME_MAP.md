# INDICATOR REGIME MAP: THE ECOLOGY OF EARLY-WARNING SIGNALS

**Project**: Early-Warning Mathematics for Complex Systems  
**Stage**: Phase 4 Systematic Regime Characterization (EXP-010)  
**Date**: September 2026  
**Auditor**: Principal Investigator & Hostile Scientific Reviewer  

---

## 1. Executive Summary of the Indicator Ecology

Early-warning indicators are not interchangeable prognostic tools. Each indicator monitors a distinct mathematical projection of the underlying dynamical system:
- **Variance / Energy Indicators**: Monitor potential well curvature ($\partial^2 V / \partial x^2 \to 0$) and total fluctuation dispersion.
- **Autoregressive / Correlation Indicators**: Monitor propagator relaxation rates ($e^{\lambda \Delta t}$) along the real eigenvalue axis.
- **Spectral Indicators**: Monitor low-frequency power density accumulation ($S(\omega) \sim (\omega^2 + \lambda^2)^{-1}$).
- **Symbolic / Information-Theoretic Indicators**: Monitor ordinal sequence permutation probability distributions ($H_{\text{perm}}$).
- **Multivariate Spatial Indicators**: Monitor collective network mode coordination and dominant spatial covariance eigenvalues ($\lambda_{\max}(\mathbf{\Sigma})$).

Based on our empirical tensor benchmark across 6 dynamical systems and 4 noise regimes (EXP-010, `results/validated/tables/phase4_indicator_tensor.csv`), we construct the definitive Indicator Operating Regime Map.

---

## 2. Comprehensive Indicator Performance Tensor (EXP-010)

### 2.1 Trajectory-Level ROC-AUC on Clean Observations ($\sigma_{\text{obs}} = 0.00$)

| System | Bifurcation Topology | Variance | AR(1) | PermutationEntropy | SpectralReddening | RecoveryRate | PCA1_Variance |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **SYS1_May_Fold** | 1D Saddle-Node Fold | **1.0000** | 0.5733 | 0.0622 | 0.8089 | 0.0356 | **1.0000** |
| **SYS2_FHN_Hopf** | 2D Supercritical Hopf | **1.0000** | 0.4178 | 0.2378 | 0.4756 | 0.2756 | **1.0000** |
| **SYS3_Pitchfork** | 1D Subcritical Jump | **0.9556** | 0.6444 | 0.2944 | 0.6556 | 0.4111 | **0.9556** |
| **SYS4_Stommel_AMOC**| 2D Non-Smooth Density | 0.2400 | 0.2978 | 0.1533 | 0.1244 | 0.3378 | 0.4578 |
| **SYS5_Coupled_Network**| 10D Mutualistic Network| **1.0000** | 0.7422 | 0.0044 | 0.9422 | 0.0000 | **1.0000** |
| **SYS6_Adler_SNIC** | 1D Global SNIC | **1.0000** | 0.6489 | 0.3044 | 0.5378 | 0.2800 | **1.0000** |

### 2.2 Trajectory-Level ROC-AUC on Severe Noise ($\sigma_{\text{obs}} = 0.50$, Low SNR)

| System | Bifurcation Topology | Variance | AR(1) | PermutationEntropy | SpectralReddening | RecoveryRate | PCA1_Variance |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **SYS1_May_Fold** | 1D Saddle-Node Fold | 0.5111 | 0.6267 | 0.3511 | 0.5067 | 0.5000 | 0.5111 |
| **SYS2_FHN_Hopf** | 2D Supercritical Hopf | 0.3244 | 0.3422 | 0.2489 | 0.2756 | 0.5000 | 0.2667 |
| **SYS3_Pitchfork** | 1D Subcritical Jump | 0.4111 | 0.7889 | 0.3500 | 0.5667 | 0.5000 | 0.4111 |
| **SYS4_Stommel_AMOC**| 2D Non-Smooth Density | 0.2933 | 0.1822 | 0.1622 | 0.1378 | 0.5000 | 0.2400 |
| **SYS5_Coupled_Network**| 10D Mutualistic Network| 0.6222 | 0.7244 | 0.5400 | 0.4933 | 0.5000 | **1.0000** |
| **SYS6_Adler_SNIC** | 1D Global SNIC | 0.4667 | 0.6089 | 0.3467 | 0.5733 | 0.5000 | 0.4667 |

---

## 3. Individual Indicator Operating Profiles

### 1. Variance ($\sigma^2$)
- **Operating Regime**: Smooth local bifurcations (Fold, Pitchfork, Hopf) and network topologies with moderate noise.
- **Strengths**: Highest raw SNR on clean data; integrates total energy across all frequencies.
- **Failure Regime**: High measurement noise ($\sigma_{\text{obs}} \ge 0.35$), where additive sensor noise swamps dynamical variance; non-smooth density flows (Stommel AMOC) where convective damping contracts variance.
- **Directionality**: Strictly positive (+1).

### 2. Lag-1 Autocorrelation ($AR(1)$ / $\rho_1$)
- **Operating Regime**: Systems with smooth real eigenvalue slowing down ($\lambda \to 0^-$) at moderate sampling rates ($\Delta t \approx 0.05 - 0.25$).
- **Strengths**: Robust to scalar amplitude shifts; scale-invariant.
- **Failure Regime**: High-frequency measurement noise (which biases $\hat{\rho}_1 \to 0$); complex conjugate oscillatory eigenvalues (Hopf bifurcation), where sinusoidal autocorrelation cancels out ($\rho(\Delta t) \approx 0$); small sliding windows ($W \le 30$) due to Kendall's negative bias.
- **Directionality**: Positive (+1).

### 3. Permutation Entropy ($H_{\text{perm}}$)
- **Operating Regime**: Transitions characterized by sudden onset of deterministic periodic orbits or limit cycle coherence.
- **Strengths**: Robust to nonlinear monotonic transformations.
- **Failure Regime**: Gaussian stochastic slowing down; circular angular manifolds (SNIC); noise-dominated time series.
- **Critical Insight**: Permutation entropy **decreases** ($\Delta H < 0$) as critical slowing down increases temporal order. Unweighted rank averaging that treats it as an increasing indicator directly cancels the variance signal.
- **Directionality**: Strictly negative (-1).

### 4. PCA1 Leading Eigenvalue ($\lambda_{\max}(\mathbf{\Sigma})$)
- **Operating Regime**: Multi-node coupled networks and high-dimensional observations.
- **Strengths**: Outstanding noise-rejection capability. In a $D$-node network with independent sensor noise, spatial eigenvector projection filters out i.i.d. noise by a factor of $\sqrt{D}$, maintaining $\text{ROC-AUC} = 1.000$ at $\sigma_{\text{obs}} = 0.50$ where scalar variance drops to $0.622$.
- **Failure Regime**: Unobserved critical nodes (hidden variables); 1D scalar time series.
- **Directionality**: Positive (+1).

---

## 4. Indicator Selection Decision Matrix

```mermaid
flowchart TD
    Start["New System / Observation Channel"] --> DimCheck{"Dimensionality D"}
    DimCheck -->|D > 1 (Network / Multi-sensor)| MultiBranch["Deploy PCA1 Dominant Eigenvalue + Multi-channel Mahalanobis"]
    DimCheck -->|D = 1 (Scalar Series)| NoiseCheck{"Estimate Noise Ratio Var(diff)/Var(tot)"}
    
    NoiseCheck -->|Ratio > 1.2 (High Sensor Noise)| HighNoiseBranch["Reject AR(1); Rely on Baseline-Subtracted Energy Variance"]
    NoiseCheck -->|Ratio < 0.8 (Clean Dynamics)| CleanBranch["Check Oscillation / Power Spectrum"]
    
    CleanBranch -->|Peak at omega > 0 (Hopf / Oscillator)| HopfBranch["Use Spectral Reddening + Cycle Autocorrelation; Reject AR(1)"]
    CleanBranch -->|Broadband Dissipative (Fold / Pitchfork)| FoldBranch["Use Variance + AR(1) with Kendall Small-Sample Bias Correction"]
```
