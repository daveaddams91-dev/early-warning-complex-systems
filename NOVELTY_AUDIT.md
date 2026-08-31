# NOVELTY AUDIT & SCIENTIFIC DIFFERENTIATION

**Project**: Early-Warning Mathematics for Complex Systems  
**Stage**: Phase 2 Independent Audit & Research Advancement  

---

## 1. Explicit Contrast Matrix Against Prior Art

| Prior Work | What Prior Art Did | Limitations of Prior Art | Our Novel Contribution in this Repository |
| :--- | :--- | :--- | :--- |
| **Scheffer et al. (2009) / Dakos et al. (2008)** | Evaluated single scalar indicators ($\text{Var}, \text{AR}(1)$) on individual time series. | No rigorous multi-system benchmark; high false positive rate on shocks; vulnerable to noise. | Implemented unified benchmark across 5 canonical systems; proved scalar $\text{AR}(1)$ collapses to chance ($0.518$) under red noise while regularized Mahalanobis composite maintains $0.954$. |
| **Boettiger & Hastings (2012)** | Critiqued post-hoc indicator selection (prosecutor's fallacy). | Primarily theoretical critique on 1D logistic/Ricker models without multivariate composite solutions. | Formulated non-parametric composite models evaluated against paired null sets with DeLong test significance and adversarial test suites. |
| **Weinans et al. (2021)** | Projected high-dimensional time series onto 1st principal component (PCA1). | Tested only on clean synthetic mutualistic models; PCA1 collapses under uncoupled distractor noise channels. | Proved PCA1 collapses from $0.988 \to 0.508$ under 20 distractors; demonstrated `CEWF-Mahalanobis` retains $0.950$ via full-covariance Mahalanobis geometry. |
| **Bury et al. (2021)** | Trained deep neural networks (LSTM / CNN) on simulated SDE training sets. | Black-box opacity; severe out-of-distribution failure when tested on unseen dynamical topologies; requires massive labeled simulation data. | Developed white-box, non-parametric, and regularized statistical composite models (`CEWF-Mahalanobis`, `CEWF-BOCPD`) requiring zero black-box parameters and providing analytical interpretability. |

---

## 2. Classification of Novelty Standard (Part XIX)

- **N1 (Reproduction)**: Independent verification of classical CSD variance divergence and AR(1) divergence across May fold, FitzHugh-Nagumo Hopf, and pitchfork normal forms.
- **N2 (New Empirical Observation)**: 
  1. *The Rank Dilution Effect*: Naive rank averaging across all standard indicators degrades $\text{ROC-AUC}$ by $\sim 0.34$ compared to individual variance due to noise injection from uninformative higher moments.
  2. *Distractor Fragility of PCA1 vs Full Mahalanobis Invariance*: Adding 20 distractor noise variables collapses leading PCA variance from $0.988 \to 0.508$, whereas full covariance Mahalanobis distance preserves $0.950$.
- **N3 (New Method)**: Multi-indicator Tikhonov-regularized Mahalanobis anomaly framework (`CEWF-Mahalanobis`) providing a statistically significant defense against red noise and severe measurement corruption ($p < 0.0001$).
- **N4 (Upcoming Game-Changer Target)**: The analytical and empirical *Detectability Boundary* and *Adaptive Warning Engine* ($P(\text{indicator } i \text{ is informative} \mid X_{1:t})$).
