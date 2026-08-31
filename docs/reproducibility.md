# Reproducibility Guide & Benchmark Replication

This guide provides step-by-step instructions to replicate all experimental figures, tables, and test suites reported in the research paper.

---

## 1. Requirements & Installation

- **Python**: Version 3.10 to 3.14
- **Required Packages**:
  ```bash
  pip install numpy scipy pandas scikit-learn matplotlib statsmodels networkx pytest
  ```

---

## 2. Running the Verification Test Suite

To verify the mathematical correctness of all SDE integrators, analytical steady states, continuous Lyapunov solvers, and early-warning indicators:
```bash
python -m pytest tests/ -v
```
All 20 test suites must pass.

---

## 3. Replicating the 6-Level Experimental Benchmark

To run the complete benchmark suite from scratch and regenerate all CSV tables in `experiments/results/tables/` and PNG figures in `experiments/results/figures/`:
```bash
python experiments/scripts/run_all_experiments.py
```
Expected execution time: ~3 minutes on modern multicore CPU.

---

## 4. Benchmark Artifact Output Structure

- `experiments/results/tables/level1_clean_benchmark.csv`: Full performance metrics on 5 canonical systems.
- `experiments/results/tables/level2_noise_benchmark.csv`: Robustness across 6 noise regimes.
- `experiments/results/tables/level3_4_sparse_distractors.csv`: Downsampling and distractor channel scaling.
- `experiments/results/tables/level5_cross_system_generalization.csv`: Zero-shot cross-system transfer.
- `experiments/results/tables/level6_adversarial_benchmark.csv`: Adversarial stress tests (N-tipping, R-tipping, false alarm shocks).
- `experiments/results/tables/statistical_significance_delong.csv`: Paired DeLong statistical significance tests.
- `experiments/results/figures/*.png`: Generated ROC curves and multi-indicator trajectory plots.
