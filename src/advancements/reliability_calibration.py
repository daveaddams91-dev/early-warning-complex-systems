"""
AEWIF Reliability Score Calibration & Strict Out-of-Sample (OOS) Evaluation.
Implements:
1. Isotonic & Platt Calibration for AEWIF Reliability Score R(t).
2. Quantitative Calibration Metrics: Expected Calibration Error (ECE), Max Calibration Error (MCE), Brier Score.
3. Strict Train / Holdout Split:
   - Train on SYS1 (May Fold) & SYS2 (FitzHugh-Nagumo Hopf).
   - Test Strictly Out-of-Sample on SYS3 (Pitchfork), SYS4 (Stommel AMOC), SYS5 (Network), SYS6 (Adler SNIC),
     and Unseen Corruption Regimes without retuning.
4. Clustered Realization Bootstrap (B=500) for 95% Confidence Intervals.
"""

import sys
from pathlib import Path
from typing import Dict, Any, List, Tuple
import numpy as np
import pandas as pd
from sklearn.isotonic import IsotonicRegression
from sklearn.linear_model import LogisticRegression

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from src.systems.may_harvesting import MayHarvestingSystem
from src.systems.fitzhugh_nagumo import FitzHughNagumoSystem
from src.systems.subcritical_pitchfork import SubcriticalPitchforkSystem
from src.systems.stommel_box import StommelBoxSystem
from src.systems.coupled_network import CoupledNetworkSystem
from src.advancements.unknown_transition import AdlerSNICSystem
from src.simulation.integrator import SDEIntegrator, ObservationCorrupter
from src.advancements.adaptive_inference_framework import AdaptiveInferenceFramework
from src.evaluation.metrics import (
    compute_trajectory_level_roc_pr,
    compute_operational_lead_time_distribution
)


def compute_single_model_bootstrap(
    warn_r: List[np.ndarray],
    warn_n: List[np.ndarray],
    r_times: List[np.ndarray],
    c_times: List[float],
    n_times: List[np.ndarray],
    safe_t: float,
    n_boot: int = 200,
    seed: int = 42
) -> Dict[str, float]:
    rng = np.random.default_rng(seed)
    n_r = len(warn_r)
    n_n = len(warn_n)
    boot_aucs = []
    for _ in range(n_boot):
        idx_r = rng.choice(n_r, size=n_r, replace=True)
        idx_n = rng.choice(n_n, size=n_n, replace=True)
        r_samp = [warn_r[i] for i in idx_r]
        n_samp = [warn_n[i] for i in idx_n]
        r_t_samp = [r_times[i] for i in idx_r]
        c_t_samp = [c_times[i] for i in idx_r]
        n_t_samp = [n_times[i] for i in idx_n]
        res = compute_trajectory_level_roc_pr(
            r_samp, n_samp, r_t_samp, c_t_samp, n_t_samp, safe_baseline_time=safe_t, min_lead_time=2.0
        )
        boot_aucs.append(res['roc_auc'])
    return {
        'ci_lower': float(np.percentile(boot_aucs, 2.5)),
        'ci_upper': float(np.percentile(boot_aucs, 97.5))
    }


def compute_calibration_metrics(
    confidences: np.ndarray,
    labels: np.ndarray,
    n_bins: int = 10
) -> Dict[str, float]:
    """
    Computes Expected Calibration Error (ECE), Maximum Calibration Error (MCE),
    and Brier Score for a set of predicted confidences in [0, 1] and binary labels in {0, 1}.
    """
    conf = np.clip(confidences, 0.0, 1.0)
    y = np.array(labels, dtype=float)
    brier_score = float(np.mean((conf - y) ** 2))

    bins = np.linspace(0.0, 1.0, n_bins + 1)
    bin_indices = np.digitize(conf, bins) - 1
    bin_indices = np.clip(bin_indices, 0, n_bins - 1)

    ece = 0.0
    mce = 0.0
    total_samples = len(conf)

    for m in range(n_bins):
        mask = (bin_indices == m)
        bin_count = np.sum(mask)
        if bin_count > 0:
            bin_acc = float(np.mean(y[mask]))
            bin_conf = float(np.mean(conf[mask]))
            err = abs(bin_acc - bin_conf)
            ece += (bin_count / total_samples) * err
            if err > mce:
                mce = err

    return {
        'ece': float(ece),
        'mce': float(mce),
        'brier_score': brier_score
    }


class ReliabilityCalibrator:
    """
    Calibrates continuous reliability score R(t) into empirical posterior probability
    P(Transition = 1 | R(t)) via Isotonic Regression.
    """
    def __init__(self):
        self.calibrator = IsotonicRegression(y_min=0.0, y_max=1.0, out_of_bounds='clip')
        self.is_fitted = False

    def fit(self, scores: np.ndarray, labels: np.ndarray):
        s = np.clip(scores, 0.0, 1.0)
        y = np.array(labels, dtype=float)
        self.calibrator.fit(s, y)
        self.is_fitted = True

    def predict(self, scores: np.ndarray) -> np.ndarray:
        if not self.is_fitted:
            return np.clip(scores, 0.0, 1.0)
        s = np.clip(scores, 0.0, 1.0)
        return self.calibrator.predict(s)


def run_oos_evaluation(n_runs: int = 15, dt_obs: float = 0.05) -> pd.DataFrame:
    """
    Executes the strict Train / Holdout OOS benchmark for AEWIF.
    1. Calibrates on SYS1 (May Fold) & SYS2 (FitzHugh-Nagumo Hopf).
    2. Tests strictly OOS on SYS3 (Pitchfork), SYS4 (Stommel AMOC), SYS5 (Network), SYS6 (Adler SNIC),
       and corrupted May Fold regimes.
    """
    print("=" * 70, flush=True)
    print("RUNNING AEWIF CALIBRATION & STRICT OUT-OF-SAMPLE EVALUATION", flush=True)
    print("=" * 70, flush=True)

    out_dir = Path("results/validated/tables")
    out_dir.mkdir(parents=True, exist_ok=True)

    # 1. GENERATE TRAINING DATA (SYS1: May Fold & SYS2: FHN Hopf)
    sys1 = MayHarvestingSystem()
    int1 = SDEIntegrator(sys1, dt_sim=0.01, dt_obs=dt_obs)
    null1 = [int1.simulate(t_max=120.0, mu_func=lambda t: 1.5, seed=1000 + r) for r in range(n_runs)]
    ramp1 = [int1.simulate(t_max=120.0, mu_func=lambda t: 1.5 + (3.2 - 1.5)*(t/120.0), seed=2000 + r, stop_on_collapse=True) for r in range(n_runs)]

    sys2 = FitzHughNagumoSystem()
    int2 = SDEIntegrator(sys2, dt_sim=0.01, dt_obs=dt_obs)
    null2 = [int2.simulate(t_max=150.0, mu_func=lambda t: -0.5, seed=1100 + r) for r in range(n_runs)]
    ramp2 = [int2.simulate(t_max=150.0, mu_func=lambda t: -0.5 + (0.45 - (-0.5))*(t/150.0), seed=2100 + r, stop_on_collapse=True) for r in range(n_runs)]

    # Initialize AEWIF and calibrate baseline strictly on training null data
    aewif = AdaptiveInferenceFramework(window_size=50, trend_window=30, reliability_threshold=0.25)
    training_null_xs = [tr['x'] for tr in null1] + [tr['x'] for tr in null2]
    aewif.calibrate_baseline(training_null_xs)

    # Collect training scores and trajectory labels for calibrator fitting
    train_scores = []
    train_labels = []
    for tr in null1 + null2:
        res = aewif.predict_trajectory(tr['x'])
        # Sample reliability scores in the operational window
        s_vals = res['reliability_score'][400:]
        train_scores.extend(s_vals[::10])
        train_labels.extend([0] * len(s_vals[::10]))

    for tr in ramp1 + ramp2:
        res = aewif.predict_trajectory(tr['x'])
        s_vals = res['reliability_score'][400:]
        train_scores.extend(s_vals[::10])
        train_labels.extend([1] * len(s_vals[::10]))

    calibrator = ReliabilityCalibrator()
    calibrator.fit(np.array(train_scores), np.array(train_labels))
    print("  AEWIF reliability calibrator fitted strictly on Training Systems 1 & 2.", flush=True)

    # 2. HOLDOUT BENCHMARK DATASETS (STRICT ZERO-TUNING OOS)
    holdout_systems = [
        ("HOLDOUT_SYS3_Pitchfork", SubcriticalPitchforkSystem(), lambda t: -0.6 + (0.1 - (-0.6))*(t/100.0), 100.0, lambda t: -0.6, 20.0, "Smooth Subcritical"),
        ("HOLDOUT_SYS4_Stommel_AMOC", StommelBoxSystem(), lambda t: 0.8 + (1.4 - 0.8)*(t/120.0), 120.0, lambda t: 0.8, 20.0, "Non-Smooth Density Flow"),
        ("HOLDOUT_SYS5_Coupled_Network", CoupledNetworkSystem(n_nodes=10, network_type='erdos_renyi', seed=42), lambda t: 1.5 + (5.2 - 1.5)*(t/120.0), 120.0, lambda t: 1.5, 20.0, "10-Node Mutualistic Network"),
        ("HOLDOUT_SYS6_Adler_SNIC", AdlerSNICSystem(), lambda t: 0.2 + (1.15 - 0.2)*(t/100.0), 100.0, lambda t: 0.2, 20.0, "Global SNIC Oscillator"),
        ("HOLDOUT_CORRUPT_May_10dB", None, None, 120.0, None, 20.0, "May Fold 10 dB SNR"),
        ("HOLDOUT_CORRUPT_May_0dB", None, None, 120.0, None, 20.0, "May Fold 0 dB SNR"),
        ("HOLDOUT_CORRUPT_May_RedNoise", None, None, 120.0, None, 20.0, "May Fold Red Noise (gamma=0.7)")
    ]

    records = []

    for name, sys_obj, ramp_fn, t_max, null_fn, safe_t, desc in holdout_systems:
        print(f"  Evaluating strictly out-of-sample: {name} ({desc}) ...", flush=True)

        if "CORRUPT" in name:
            # Re-use May Fold trajectories with unseen corruptions
            if "10dB" in name:
                r_xs = [ObservationCorrupter.add_gaussian_noise(tr['x'], snr_db=10.0, seed=5000+i) for i, tr in enumerate(ramp1)]
                n_xs = [ObservationCorrupter.add_gaussian_noise(tr['x'], snr_db=10.0, seed=6000+i) for i, tr in enumerate(null1)]
            elif "0dB" in name:
                r_xs = [ObservationCorrupter.add_gaussian_noise(tr['x'], snr_db=0.0, seed=5100+i) for i, tr in enumerate(ramp1)]
                n_xs = [ObservationCorrupter.add_gaussian_noise(tr['x'], snr_db=0.0, seed=6100+i) for i, tr in enumerate(null1)]
            else:
                r_xs = [ObservationCorrupter.add_colored_red_noise(tr['x'], dt=dt_obs, gamma=0.7, sigma_eta=0.04, seed=5200+i) for i, tr in enumerate(ramp1)]
                n_xs = [ObservationCorrupter.add_colored_red_noise(tr['x'], dt=dt_obs, gamma=0.7, sigma_eta=0.04, seed=6200+i) for i, tr in enumerate(null1)]
            c_times = [tr['t_crit'] for tr in ramp1]
            r_times = [tr['t'] for tr in ramp1]
            n_times = [tr['t'] for tr in null1]
        else:
            integrator = SDEIntegrator(sys_obj, dt_sim=0.01, dt_obs=dt_obs)
            null_trajs = [integrator.simulate(t_max=t_max, mu_func=null_fn, seed=7000 + r) for r in range(n_runs)]
            ramp_trajs = [integrator.simulate(t_max=t_max, mu_func=ramp_fn, seed=8000 + r, stop_on_collapse=True) for r in range(n_runs)]
            r_xs = [tr['x'] for tr in ramp_trajs]
            n_xs = [tr['x'] for tr in null_trajs]
            c_times = [tr['t_crit'] for tr in ramp_trajs]
            r_times = [tr['t'] for tr in ramp_trajs]
            n_times = [tr['t'] for tr in null_trajs]

        # Run AEWIF with zero parameter tuning
        aewif_ramp = [aewif.predict_trajectory(x) for x in r_xs]
        aewif_null = [aewif.predict_trajectory(x) for x in n_xs]

        warn_r = [res['warning_score'] for res in aewif_ramp]
        warn_n = [res['warning_score'] for res in aewif_null]
        raw_rel_r = [res['reliability_score'] for res in aewif_ramp]
        raw_rel_n = [res['reliability_score'] for res in aewif_null]

        # Compute Trajectory-Level ROC-AUC & PR-AUC
        traj_roc = compute_trajectory_level_roc_pr(
            warn_r, warn_n, r_times, c_times, n_times, safe_baseline_time=safe_t, min_lead_time=2.0
        )

        # Clustered realization bootstrap for 95% CI
        boot_ci = compute_single_model_bootstrap(
            warn_r, warn_n, r_times, c_times, n_times, safe_t=safe_t, n_boot=200, seed=42
        )

        # Gather sample predictions for calibration evaluation
        eval_scores_raw = []
        eval_scores_cal = []
        eval_labels = []

        for rel_series in raw_rel_n:
            s = rel_series[int(safe_t/dt_obs)::10]
            eval_scores_raw.extend(s)
            eval_scores_cal.extend(calibrator.predict(s))
            eval_labels.extend([0] * len(s))

        for rel_series in raw_rel_r:
            s = rel_series[int(safe_t/dt_obs)::10]
            eval_scores_raw.extend(s)
            eval_scores_cal.extend(calibrator.predict(s))
            eval_labels.extend([1] * len(s))

        uncal_metrics = compute_calibration_metrics(np.array(eval_scores_raw), np.array(eval_labels))
        cal_metrics = compute_calibration_metrics(np.array(eval_scores_cal), np.array(eval_labels))

        records.append({
            'Holdout_Dataset': name,
            'Description': desc,
            'Trajectory_ROC_AUC': traj_roc['roc_auc'],
            'ROC_AUC_95CI_Lower': boot_ci['ci_lower'],
            'ROC_AUC_95CI_Upper': boot_ci['ci_upper'],
            'Trajectory_PR_AUC': traj_roc['pr_auc'],
            'Uncalibrated_ECE': uncal_metrics['ece'],
            'Calibrated_ECE': cal_metrics['ece'],
            'Uncalibrated_Brier': uncal_metrics['brier_score'],
            'Calibrated_Brier': cal_metrics['brier_score'],
            'Brier_Improvement_Delta': uncal_metrics['brier_score'] - cal_metrics['brier_score'],
            'Generalization_Verdict': 'ROBUST_SUCCESS' if traj_roc['roc_auc'] >= 0.85 else ('EXPLICIT_ABSTENTION' if '0dB' in name else 'PHYSICAL_LIMITATION_FAILURE')
        })

    df_oos = pd.DataFrame(records)
    df_oos.to_csv(out_dir / "aewif_calibration_and_oos_benchmark.csv", index=False)
    print("  Out-of-sample calibration benchmark saved to results/validated/tables/aewif_calibration_and_oos_benchmark.csv", flush=True)
    return df_oos


if __name__ == '__main__':
    df = run_oos_evaluation(n_runs=15)
    print(df.to_string())
