# PHASE 4 RESEARCH CHECKPOINT

Central hypothesis:
«The usefulness of an early-warning indicator is conditional on the dynamical mechanism, observation process, and noise structure of the system; therefore, indicator aggregation should be adaptive rather than universal.»

Status:
SUPPORTED & FORMALIZED. The empirical contradiction in prior benchmarks has been resolved: unweighted static indicator aggregation degrades clean-signal performance via Noise Dilution and Directional Cancellation, whereas multi-dimensional eigenvector projection filters sensor noise by \sqrt{D}. Aggregation must be state-dependent, mechanism-conditioned, and equipped with an abstention rejection state.

Most important discovery:
The Noise Dilution & Directional Cancellation Theorem paired with Spatial Mode Covariance Filtering. Adding uninformative indicators strictly degrades composite Signal-to-Noise Ratio by \sqrt{K_0 / (K_0 + K_{\text{noise}})}, and unweighted rank aggregation causes opposing trends (e.g. Variance \uparrow vs Permutation Entropy \downarrow) to annihilate the precursor signal (collapsing clean May Fold ROC-AUC from 1.000 to 0.322). Conversely, in multi-node networks, spatial eigenvector projection (PCA1) averages out independent sensor noise by \sqrt{D}, maintaining ROC-AUC = 1.000 at \sigma_{\text{obs}} = 0.50 where scalar variance collapses.

Strongest supporting evidence:
1. In EXP-010, on clean May Fold, pure Variance achieves ROC-AUC = 1.0000, while naive rank composite CEWF-Rank drops to 0.3224 due to Permutation Entropy's negative trend.
2. In EXP-010, on a 10-node coupled network under severe noise (\sigma_{\text{obs}} = 0.50), PCA1_Variance maintains ROC-AUC = 1.0000 while scalar variance drops to 0.6222.
3. In EXP-011 (36-configuration phase space), detectability collapses whenever \mathrm{SNR}_{\text{dyn}} < 1.0.
4. In EXP-013, the Adaptive Early-Warning Inference Framework (AEWIF) triggers its UNRELIABLE abstention state under 0 dB noise, where reliability score R(t) plummets to 6.17 \times 10^{-8}, eliminating false positive alarms.

Strongest contradictory evidence:
1. Passive statistical indicators are universally vulnerable to Adversarial False Consensus: in EXP-014, an exogenous non-collapsing step shock excited all energy moments and autocorrelation simultaneously, triggering 100% false alarms across both redundant and diverse ensembles.
2. CSD indicators fail completely on Stommel AMOC (ROC-AUC \le 0.458) due to convective non-smoothness and 66.16^\circ eigenvector rotation away from the observed temperature coordinate.
3. N-tipping and R-tipping exhibit 0.0% detection rate because local potential curvature remains steep and non-zero up to tipping.

Current best method:
Adaptive Early-Warning Inference Framework (AEWIF) with online informativeness estimation P(\text{indicator } i \text{ is informative} \mid X_{1:t}), state-dependent dynamic weighting, and a mandatory UNRELIABLE abstention rejection state for R(t) < 0.25.

Current best baseline:
- Clean 1D / 2D local bifurcations: Univariate Sample Variance (\sigma^2).
- Multi-channel / network topologies: Dominant Covariance Eigenvector Variance (PCA1_Variance).
- High-noise multi-indicator benchmark: Tikhonov-regularized Mahalanobis Distance (CEWF-Mahalanobis).

False-alarm behavior:
- Single-point \alpha = 0.05 thresholding generates an 80% - 100% cumulative false alarm rate over M = 400 steps (1 - (1-\alpha)^M \to 1).
- Multi-step persistence filtering (P \ge 4 consecutive steps) and the AEWIF abstention state reduce the false alarm rate to 0.0% on uncorrupted baselines and suppress alarms during extreme observation noise.
- Under sudden non-collapsing transient shocks, passive indicators remain vulnerable to false consensus, necessitating active perturbation probing or waiting out the 15s informational latency window.

Generalization:
- Zero-shot cross-system transfer succeeds across smooth local and global bifurcations (May Fold \to FitzHugh-Nagumo Hopf \to Coupled Network \to Adler SNIC Oscillator, achieving ROC-AUC \ge 0.960).
- Generalization fails completely when transferring to non-smooth vector fields (Stommel AMOC) or non-bifurcation escape (N-tipping and R-tipping).

Detectability boundary:
Finite-sample non-stationary minimax bound: \mathrm{SNR}_{\text{dyn}} < \sqrt{C(\alpha, \beta) \cdot \frac{r \Delta t}{\delta_{\mu}}}.
Because parameter drift at rate r bounds the allowable quasi-stationary window (N_{\max} \le \delta_{\mu}/(r \Delta t)), observation noise \sigma_{\text{obs}}^2 raises the required sample size (N_{\text{req}} \propto \sigma_{\text{obs}}^4). When N_{\max} < N_{\text{req}}, distinguishing critical slowing down from null fluctuations is mathematically impossible for any causal sliding-window estimator.
Empirically mapped across 36 configurations (EXP-011): collapses to ROC-AUC \le 0.591 when \sigma_{\text{obs}} \ge 0.35, \Delta t \ge 0.15\text{ s}.

Information requirement:
In EXP-012, post-shock collapse and recovery futures remain statistically indistinguishable for \Delta t_{\text{latency}} \approx 15.0\text{ s} (Wasserstein distance W_1 < 0.15, empirical Bayes error \approx 42%). Distinguishability requires waiting for \Delta t > 15.0\text{ s} (W_1 = 0.268, Bayes error drops to 0.0%). Rolling window estimation requires at least W = 50 steps (2.5s) to prevent covariance condition number explosion (\kappa \le 2.0).

Mathematical result:
1. Proof of the Noise Dilution Theorem: \mathrm{SNR}_{\text{comp}} = \sqrt{K_0 / (K_0 + K_{\text{noise}})} \cdot \mathrm{SNR}_{\text{clean}} (Theorem 1, docs/THEORETICAL_PROOFS.md).
2. Proof of Directional Cancellation: \Delta_{\text{comp}} = \frac{1}{2}(\Delta_1 + \Delta_2) = 0 when \Delta_1 = -\Delta_2 (Theorem 2).
3. Proof of Spatial Noise Averaging: In a D-node network with i.i.d. sensor noise, spatial eigenvector projection filters sensor noise by 1/\sqrt{D} (Theorem 3).
4. Finite-Window Minimax Bound: N_{\text{req}} > N_{\max} threshold (Proposition 1).
5. Participation ratio formulation of indicator diversity: K_{\text{eff}} = (\mathrm{Tr}\mathbf{R})^2 / \mathrm{Tr}(\mathbf{R}^2).

Empirical result:
Validated across 14 computational experiments (EXP-001 to EXP-014) on 6 dynamical systems:
- Trajectory-level ROC-AUC and PR-AUC with clustered realization bootstrap (B=500).
- Strict out-of-sample evaluation: AEWIF achieves ROC-AUC = 0.9200 on unseen Pitchfork and 0.9956 on unseen Adler SNIC, while Isotonic Calibration reduces Expected Calibration Error (ECE) by >60% across all holdouts (CALIBRATION_AND_OOS_EVALUATION.md).
- Documented complete failures: Stommel AMOC (AUC = 0.5289) and unobserved multi-node networks (AUC = 0.0000).
- 52/52 unit tests passing with zero causal look-ahead leakage and zero runtime warnings.

Novelty level:
N3 / N4 (Downgraded from N5 following rigorous comparison against Hotelling 1931, John 1971, Chow 1970, and Boettiger & Hastings 2012).

Biggest unresolved problem:
Passive observational indicators cannot distinguish between an impending critical collapse and an exogenous non-collapsing transient shock during the initial informational latency window (\Delta t \le 15.0\text{ s}), where all energy moments spike simultaneously. Resolving this without latency requires active perturbation probing, which is invasive or physically impossible in planetary-scale systems (e.g. Earth AMOC).

Should the project continue in this direction?
YES

Reason:
The project has successfully explained the standing contradiction in the field, established the mathematical theory of noise dilution and spatial filtering, derived the detectability boundary, developed the adaptive AEWIF framework with verified abstention, and proven the fundamental limits of passive observation. The logical next horizon is empirical validation on high-resolution real-world observational records (e.g. paleoclimate NGRIP ice-core records and clinical EEG telemetry).

Next experiment:
EXP-015: Empirical Testing of AEWIF on High-Frequency Dansgaard-Oeschger Paleoclimate Ice-Core Proxy Data and Pre-Ictal Epileptic Telemetry.
