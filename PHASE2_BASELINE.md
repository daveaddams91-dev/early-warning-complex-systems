# PHASE 2 BASELINE STATE SNAPSHOT

**Audit Timestamp**: September 2026  
**Repository Commit**: `188bea7` ("Complete early-warning complex systems research project: benchmark levels 1-6, deliverables, docs, critical review, and final report")  
**Branch**: `main`  
**Remote**: `https://github.com/Raj123-0/early-warning-complex-systems`

---

## 1. System Classes & Mathematical Formulations

| System Identifier | Class Name | Dimension | Bifurcation / Mechanism | Key Equations | Critical Parameter ($\mu_c$) |
| :--- | :--- | :---: | :--- | :--- | :---: |
| `SYS-1` | `MayHarvestingSystem` | 1D | Fold / Saddle-Node | $\dot{x} = r x (1 - x/K) - c \frac{x^2}{x^2 + d^2} + \sigma dW$ | $c_c \approx 2.6044$ |
| `SYS-2` | `FitzHughNagumoSystem` | 2D | Supercritical Hopf | $\dot{v} = v - v^3/3 - w + I_{\text{ext}} + \sigma dW_1, \; \dot{w} = \epsilon (v + a - b w) + \sigma dW_2$ | $I_c \approx 0.332$ |
| `SYS-3` | `SubcriticalPitchforkSystem` | 1D | Subcritical Pitchfork | $\dot{x} = \mu x + x^3 - x^5 + \sigma dW$ | $\mu_c = 0.0$ |
| `SYS-4` | `StommelBoxSystem` | 2D | Non-Smooth Fold (AMOC) | $\dot{T} = \eta_1 (T_e - T) - \|T-S\| T, \; \dot{S} = \eta_2 (S_e - S) - \|T-S\| S + \sigma dW$ | $F_{\text{fresh}} \approx 1.15$ |
| `SYS-5` | `CoupledNetworkSystem` | 10D | Mutualistic Network Fold | $\dot{x}_i = r x_i (1 - x_i/K) + \frac{\gamma \sum A_{ij} x_j}{1 + h \sum A_{ik} x_k} - c \frac{x_i^2}{x_i^2 + d^2} + \sigma dW_i$ | $c_c \approx 4.80$ |

---

## 2. Algorithms & Indicators Implemented

### 2.1 Univariate Indicators (`src/indicators/univariate.py`)
- `VarianceIndicator`: Sliding sample variance with Bessel's correction ($ddof=1$).
- `AutocorrelationLag1Indicator`: Pearson correlation at lag 1.
- `SkewnessIndicator`: Analytical 3rd standardized moment $m_3 / s_2^{1.5}$.
- `KurtosisIndicator`: Analytical 4th standardized excess moment $m_4 / s_2^2 - 3$.
- `PermutationEntropyIndicator`: Bandt-Pompe (2002) symbolic ordinal permutation entropy ($m=3, \tau=1$).
- `SpectralReddeningIndicator`: Fraction of FFT power in the lowest $20\%$ frequency band.
- `RecoveryRateIndicator`: Empirical decay rate $\hat{\kappa} = -\ln(\rho_1) / \Delta t$.

### 2.2 Multivariate Indicators (`src/indicators/multivariate.py`)
- `PCA1VarianceIndicator`: Variance of 1st principal component of multi-channel series.
- `GeneralizedVarianceIndicator`: Determinant of covariance matrix $\det(\mathbf{C})$.
- `MahalanobisDistanceIndicator`: Observation vector anomaly distance from baseline centroid.
- `DynamicalNetworkBiomarkerIndicator`: DNB index $\frac{\bar{s}_{\text{in}} \cdot \bar{r}_{\text{in}}}{\bar{r}_{\text{out}}}$.

### 2.3 Trend & Composite Models (`src/models/`, `src/indicators/kendall_trend.py`)
- `RollingKendallTrend`: Causal non-parametric Kendall $\tau$ rank trend estimator.
- `LinearCompositeModel` (`CEWF-Linear`): Calibrated weighted sum of normalized indicators.
- `RankAggregationModel` (`CEWF-Rank`): Aggregation (mean/median/max) of positive Kendall $\tau$ trends.
- `MultiIndicatorMahalanobisModel` (`CEWF-Mahalanobis`): Multi-indicator feature distance with Tikhonov covariance regularization $(\mathbf{\Sigma} + \epsilon \mathbf{I})^{-1}$.
- `ElasticNetWarningModel` (`CEWF-ElasticNet`): Regularized logistic regression calibrated on baseline null data.
- `BayesianChangepointModel` (`CEWF-BOCPD`): Adams & MacKay (2007) Bayesian Online Changepoint Detection.

---

## 3. Benchmark Structure & Experimental Hierarchy

- **Ensemble Size**: $N=25$ realization trajectories per condition.
- **Simulation Time Step**: $\Delta t_{\text{sim}} = 0.01$ s, Observation $\Delta t_{\text{obs}} = 0.05$ s.
- **Sliding Window**: $W = 50$ points ($2.5$ s window duration).
- **Levels Evaluated**:
  - **Level 1**: Clean synthetic data across 5 canonical systems.
  - **Level 2**: Noise regimes (Gaussian SNR 20dB to 0dB, Student-t $\nu=3$, Colored red noise $\gamma=0.4$).
  - **Level 3**: Downsampling ($1\times, 2\times, 5\times, 10\times$).
  - **Level 4**: Distractor variables ($0, 2, 5, 10, 20$ uncoupled noise channels).
  - **Level 5**: Zero-shot cross-system transfer (SYS-1 $\to$ SYS-2, 3, 4, 5).
  - **Level 6**: Adversarial deceivers (Transient shock, Benign drift, Pure N-tipping, Fast R-tipping).

---

## 4. Summary of Reported Results (Commit `188bea7`)

| Level | Key Condition | Baseline Variance AUC | Baseline AR(1) AUC | CEWF-Rank AUC | CEWF-Mahalanobis AUC |
| :--- | :--- | :---: | :---: | :---: | :---: |
| **Level 1** | SYS1 (May Fold) | 0.9971 | 0.9002 | 0.6525 | 0.9638 |
| **Level 1** | SYS2 (FitzHugh Hopf) | 0.7775 | 0.6965 | 0.5939 | 0.6536 |
| **Level 1** | SYS3 (Pitchfork) | 0.6798 | 0.6207 | 0.5315 | 0.5606 |
| **Level 1** | SYS4 (Stommel AMOC) | 0.5134 | 0.5095 | 0.5060 | 0.5167 |
| **Level 1** | SYS5 (Coupled Network)| 0.9995 | 0.9265 | 0.7627 | 0.9939 |
| **Level 2** | Gaussian SNR 0 dB | 0.7724 | 0.5361 | 0.5670 | **0.8258** |
| **Level 2** | Colored Red Noise | 0.9926 | 0.5180 | 0.5916 | **0.9542** |
| **Level 5** | Zero-Shot $\to$ Network | 0.9960 | 0.7791 | 0.7298 | **0.9926** |
| **Level 5** | Zero-Shot $\to$ Stommel | 0.5205 | 0.5182 | 0.4915 | **0.4667** |
| **Level 6** | 6A Transient Shock | FAR = 1.00 | FAR = 1.00 | FAR = 1.00 | FAR = 1.00 |
| **Level 6** | 6C Pure N-Tipping | Det = 0.0% | Det = 0.0% | Det = 0.0% | Det = 0.0% |
| **Level 6** | 6D Fast R-Tipping | Det = 0.0% | Det = 0.0% | Det = 0.0% | Det = 0.0% |

---

## 5. Known Failures & Open Research Questions

1. **Uninformative Indicator Dilution**: Naive rank aggregation is degraded by non-monotonic indicators. How can a model dynamically learn which indicators are informative online without test-set supervision?
2. **The Detectability Boundary**: Under what exact analytical and empirical thresholds ($SNR$, $\Delta t$, $d\mu/dt$, distance to bifurcation) does critical slowing down transition from mathematically detectable to undetectable?
3. **Shock vs Tipping Disambiguation**: Can counterfactual or active probing distinguish a reversible exogenous shock from true loss of resilience?
4. **Generalization to Unseen Transition Classes**: How do statistical indicators behave on novel transition mechanisms (e.g. homoclinic bifurcations, boundary crises, noise-induced P-bifurcations)?
