# CHANGELOG: Early-Warning Mathematics for Complex Systems

All notable changes, theoretical advances, empirical discoveries, and bug fixes to this research repository are documented in this ledger.

---

## [Phase 4 Final & Scientific Advancement] - September 2026

### 1. AMOC (SYS-4) Mechanistic Failure Analysis & Ablation
- **Ablation Framework**: Implemented `experiments/scripts/ablate_amoc_failure.py` testing 6 early-warning indicators across 5 mathematical coordinate representations (`raw`, `log_transform`, `first_difference`, `local_detrend`, and `linearizing_reparam`), alongside direct volume overturning flux $q = |T - S|$.
- **Discovery of Mean Drift Artifact**: Revealed that raw 2D Mahalanobis distance achieved $\mathrm{ROC-AUC} = 1.0000$ solely by detecting **mean state displacement** in the $(T, S)$ plane rather than dynamical critical slowing down. When locally detrended or first-differenced to isolate stochastic fluctuations, Mahalanobis collapsed to $\mathrm{ROC-AUC} = 0.1712$ and $0.2208$.
- **Analytical Cause**: Proven that fast thermal relaxation ($\eta_1 = 1.0$) vs. slow salinity relaxation ($\eta_2 = 0.3$) rotates the critical slowing down eigenvector $66.16^\circ$ into the salinity subspace, while convective density drag $|T - S|$ contracts fluctuations along the fast manifold, completely eliminating CSD fluctuation softening on the observed temperature manifold.
- **Artifacts**: Persisted data table to `experiments/results/tables/amoc_failure_ablation.csv`, detailed report in `docs/AMOC_FAILURE_ANALYSIS.md`, and unit tests in `tests/test_amoc_ablation.py`.

### 2. Operational Lead-Time vs. False-Alarm-Rate (FAR) Benchmark
- **Operational Lead-Time Module**: Implemented `src/evaluation/lead_time.py` with `find_threshold_at_far()`, `compute_lead_time_distribution()`, and `generate_lead_time_vs_far_curve()`.
- **The Lead-Time vs. AUC Divergence Paradox**: Discovered that while `Variance` and `CEWF-Mahalanobis` both achieve perfect trajectory discrimination ($\mathrm{ROC-AUC} = 1.0000$) on the May Fold, operational lead times diverge catastrophically:
  - At $\mathrm{FAR} = 1\%$, `Variance` achieves a $100\%$ detection rate with **$38.86\text{ s}$ of advance warning**.
  - At $\mathrm{FAR} = 1\%$, `CEWF-Mahalanobis` achieves a **$0\%$ detection rate ($0.00\text{ s}$ lead time)** due to elevated null threshold calibration from multi-indicator extreme values.
- **Artifacts**: Published lead-time curves to `experiments/results/figures/lead_time_vs_far_*.png`, benchmark table to `experiments/results/tables/lead_time_benchmark.csv`, and unit tests in `tests/test_lead_time.py`.

### 3. Deep Learning Early-Warning Baseline (Bury et al. 2021 Style)
- **Architecture**: Implemented `src/models/deep_ews.py` with causal 1D Convolutional Neural Network (Conv1D + BatchNorm + AdaptiveAvgPool + Linear) operating on raw standardized rolling time series windows ($W=50$).
- **Benchmark & DeLong Significance Tests**: Implemented `experiments/scripts/run_deep_ews_benchmark.py` pre-training on independent SDE systems (SYS-1 May Fold and SYS-2 FHN Hopf) and evaluating zero-shot out-of-distribution across all 5 canonical systems:
  - `SYS-1 May Fold`: DeepEWS $\mathrm{AUC} = 1.0000$ vs. Mahalanobis $1.0000$ (DeLong $p = 1.0000$, Neutral).
  - `SYS-2 FHN Hopf`: DeepEWS $\mathrm{AUC} = 0.9984$ vs. Mahalanobis $0.9536$ (DeLong $p = 0.1019$, Neutral).
  - `SYS-3 Pitchfork`: DeepEWS $\mathrm{AUC} = 0.8000$ vs. Mahalanobis $0.4933$ (DeLong $p = 0.0509$, Marginally favors DeepEWS).
  - `SYS-4 Stommel AMOC`: DeepEWS $\mathrm{AUC} = 0.2944$ vs. Mahalanobis $0.2096$ (DeLong $p = 0.4264$, Both fail catastrophically).
  - `SYS-5 Coupled Network`: DeepEWS $\mathrm{AUC} = 1.0000$ vs. Mahalanobis $1.0000$ (DeLong $p = 1.0000$, Neutral).
- **Artifacts**: Saved table to `experiments/results/tables/deep_ews_benchmark.csv` and unit tests in `tests/test_deep_ews.py`.

### 4. Quantitative Noise-Detectability Phase Diagram
- **Multi-Grid Sweep**: Implemented `experiments/scripts/run_noise_phase_diagram.py` sweeping observation noise from $\mathrm{SNR} = -6.0\text{ dB}$ to $+12.0\text{ dB}$ across all 5 dynamical systems for Variance, AR(1), and CEWF-Mahalanobis.
- **Empirical Findings**: Quantified that AR(1) suffers catastrophic dilution ($\mathrm{ROC-AUC} \le 0.05$ across all systems for $\mathrm{SNR} \le 0\text{ dB}$) due to observation noise uncorrelatedness, while CEWF-Mahalanobis exhibits a sharp monotonic phase boundary ($0.329 \to 0.924$ on FHN Hopf).
- **Artifacts**: Saved heatmaps to `experiments/results/figures/noise_detectability_phase_diagram_*.png`, table to `experiments/results/tables/noise_detectability_phase_diagram.csv`, and updated `LIMITATIONS.md`.

### 5. Real-World Empirical Dataset (GISP2 Paleoclimate Record)
- **Data Integration**: Integrated Greenland GISP2 ice core $\delta^{18}\mathrm{O}$ temperature proxy record across the abrupt Younger Dryas climate transition ($\sim 11,700\text{ yr BP}$) from NOAA World Data Service for Paleoclimatology (`data/real_world/gisp2_younger_dryas.csv`).
- **Empirical Suite Evaluation**: Implemented `src/systems/real_world/loader.py` and `experiments/scripts/run_real_world_evaluation.py`:
  - `Variance`: Statistically significant upward trend ($\tau = +0.415, p = 0.0001$) with **$140.0\text{ years}$ of actionable lead time**.
  - `Permutation Entropy`: Upward trend ($\tau = +0.625, p < 0.0001$) with **$300.0\text{ years}$ of advance warning**.
  - `AR(1)`: Inverted downward trend ($\tau = -0.424, p = 0.0001$) due to high-frequency firn diffusion.
  - `AEWIF`: Successfully identified indicator conflict and engaged its **Abstention State** ($\tau = 0.000$), refusing to emit false alarms.
- **Artifacts**: Provenance documented in `docs/REAL_WORLD_DATA.md`, diagnostic figure in `experiments/results/figures/real_world_younger_dryas_indicators.png`, results table in `experiments/results/tables/real_world_evaluation.csv`, and unit tests in `tests/test_real_world_loader.py`.

### 6. Reframing Headline Claims to Match Empirical Statistics
- Plainly stated across `README.md` and `FINAL_REPORT.md` that:
  - Composite models significantly help over simple scalar indicators on only **1 of 5 systems** (`SYS-2`).
  - Composite models are statistically indistinguishable from simple variance on **2 systems** (`SYS-1`, `SYS-5`, $p \ge 0.08$).
  - Composite models significantly underperform simple variance on **1 system** (`SYS-3`).
  - All models (composite, deep learning, univariate) fail catastrophically on **1 system** (`SYS-4`).

### 7. Continuous Integration (CI)
- Created `.github/workflows/ci.yml` running `pytest tests/ -v` on Python 3.10, 3.11, and 3.12 on all pushes and pull requests to `main`.
- Created standardized `requirements.txt`.
- Expanded test suite from 38 to **50 unit tests**, passing 100% locally.
- Verified 100% compliance with KaTeX formatting rules (zero operatorname macros across all markdown files).
- Integrated Author ORCID (0009-0004-7838-4064) across CITATION.cff, README.md, and FINAL_REPORT.md.

### 8. Rigorous Primary-Source Bibliography Audit
- Executed automated Crossref REST API verification across all citations in `REFERENCES.md`.
- Disentangled the spliced entry #9 (Weinans et al.) into two verified entries: Weinans et al. 2019 (*J. R. Soc. Interface*, DOI `10.1098/rsif.2019.0629`) and Weinans et al. 2021 (*Sci. Rep.*, DOI `10.1038/s41598-021-87839-y`).
- Corrected author list and title for entry #12 (Bury et al. 2021 *PNAS*, DOI `10.1073/pnas.2106140118`).
- Fixed transposed DOI on entry #15 (Boettiger et al. 2013 *Theor. Ecol.*, DOI `10.1007/s12080-013-0192-6`).
- Replaced mismatched radar DOI on entry #16 with genuine publication DOI for Ritchie & Sieber 2016 (*Chaos*, DOI `10.1063/1.4963012`).
- Expanded bibliography to **24 fully verified, resolving citations** with zero dead links or hallucinated authors, audited in `docs/BIBLIOGRAPHY_AUDIT.md`.
- Added regression test `tests/test_references.py` ensuring bibliography completeness and valid DOIs.
