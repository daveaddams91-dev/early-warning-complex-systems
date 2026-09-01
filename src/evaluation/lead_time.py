"""
Lead-Time Evaluation Module.
Computes the distribution of operational lead times across Monte Carlo trials
at fixed False Alarm Rate (FAR) operating points (e.g. 1%, 5%, 10%),
and produces Lead-Time vs False-Alarm-Rate curves.
"""

from typing import Dict, Any, List, Tuple, Optional
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


def find_threshold_at_far(
    null_scores: List[np.ndarray],
    time_arrays_null: List[np.ndarray],
    safe_baseline_time: float,
    target_far: float,
    persistence_steps: int = 4
) -> float:
    """
    Finds the operational detection threshold theta such that the fraction of
    null trajectories triggering a false alarm (sustained for persistence_steps)
    equals target_far.
    """
    n_null = len(null_scores)
    peak_sustained_scores = []

    for s_arr, t_arr in zip(null_scores, time_arrays_null):
        mask = (t_arr >= safe_baseline_time)
        eval_scores = s_arr[mask]
        
        if len(eval_scores) < persistence_steps:
            peak_sustained_scores.append(0.0)
            continue

        # Rolling minimum over persistence_steps to enforce sustained crossing
        # A threshold is crossed for P consecutive steps iff rolling min over P steps >= theta
        rolling_min_p = np.convolve(eval_scores, np.ones(persistence_steps) / persistence_steps, mode='valid')
        # Exact sustained: min over rolling window of length P
        # Using 1D sliding window min:
        shape = (len(eval_scores) - persistence_steps + 1, persistence_steps)
        strides = (eval_scores.strides[0], eval_scores.strides[0])
        windows = np.lib.stride_tricks.as_strided(eval_scores, shape=shape, strides=strides)
        sustained_max = np.max(np.min(windows, axis=1))
        peak_sustained_scores.append(sustained_max)

    peak_sustained_scores = np.sort(peak_sustained_scores)
    # The threshold at target_far is the (1 - target_far) quantile
    idx = int(np.clip(np.floor((1.0 - target_far) * n_null), 0, n_null - 1))
    return float(peak_sustained_scores[idx])


def compute_lead_time_distribution(
    ramp_scores: List[np.ndarray],
    null_scores: List[np.ndarray],
    time_arrays_ramp: List[np.ndarray],
    collapse_times: List[float],
    time_arrays_null: List[np.ndarray],
    safe_baseline_time: float = 20.0,
    min_lead_time: float = 2.0,
    far_points: Tuple[float, ...] = (0.01, 0.05, 0.10),
    persistence_steps: int = 4
) -> Dict[str, Any]:
    """
    Computes empirical lead time distributions across Monte Carlo ramp trajectories
    at specified False Alarm Rate operating points.
    """
    results_by_far = {}

    for far in far_points:
        theta = find_threshold_at_far(
            null_scores, time_arrays_null, safe_baseline_time, far, persistence_steps
        )
        
        lead_times = []
        detected_flags = []

        for s_arr, t_arr, t_crit in zip(ramp_scores, time_arrays_ramp, collapse_times):
            mask = (t_arr >= safe_baseline_time) & (t_arr <= t_crit)
            eval_scores = s_arr[mask]
            eval_times = t_arr[mask]

            if len(eval_scores) < persistence_steps:
                lead_times.append(0.0)
                detected_flags.append(False)
                continue

            shape = (len(eval_scores) - persistence_steps + 1, persistence_steps)
            strides = (eval_scores.strides[0], eval_scores.strides[0])
            windows = np.lib.stride_tricks.as_strided(eval_scores, shape=shape, strides=strides)
            sustained_mask = np.min(windows, axis=1) >= theta

            if np.any(sustained_mask):
                first_idx = int(np.argmax(sustained_mask)) + persistence_steps - 1
                t_alarm = float(eval_times[first_idx])
                lead = max(0.0, float(t_crit - t_alarm))
                if lead >= min_lead_time:
                    lead_times.append(lead)
                    detected_flags.append(True)
                else:
                    lead_times.append(lead)
                    detected_flags.append(False)
            else:
                lead_times.append(0.0)
                detected_flags.append(False)

        lt_arr = np.array(lead_times)
        det_arr = np.array(detected_flags)

        results_by_far[far] = {
            'threshold': theta,
            'detection_rate': float(np.mean(det_arr)),
            'lead_time_mean': float(np.mean(lt_arr)),
            'lead_time_std': float(np.std(lt_arr)),
            'lead_time_median': float(np.median(lt_arr)),
            'lead_time_q25': float(np.percentile(lt_arr, 25)),
            'lead_time_q75': float(np.percentile(lt_arr, 75)),
            'raw_lead_times': lead_times
        }

    return results_by_far


def generate_lead_time_vs_far_curve(
    system_name: str,
    method_data: Dict[str, Dict[str, Any]],
    output_figure_path: Path,
    far_grid: Optional[np.ndarray] = None,
    safe_baseline_time: float = 20.0,
    min_lead_time: float = 2.0,
    persistence_steps: int = 4
) -> pd.DataFrame:
    """
    Computes and plots Lead Time vs FAR curve across methods for a given system.
    method_data: Dict[method_name -> {'ramp_scores', 'null_scores', 'time_ramp', 't_crit', 'time_null'}]
    """
    if far_grid is None:
        far_grid = np.linspace(0.01, 0.20, 20)

    records = []
    plt.figure(figsize=(8, 5))

    for method_name, data in method_data.items():
        mean_lts = []
        det_rates = []

        for far in far_grid:
            dist = compute_lead_time_distribution(
                data['ramp_scores'], data['null_scores'],
                data['time_ramp'], data['t_crit'], data['time_null'],
                safe_baseline_time=safe_baseline_time,
                min_lead_time=min_lead_time,
                far_points=(float(far),),
                persistence_steps=persistence_steps
            )[float(far)]

            mean_lts.append(dist['lead_time_mean'])
            det_rates.append(dist['detection_rate'])

            records.append({
                'System': system_name,
                'Method': method_name,
                'FAR': float(far),
                'Lead_Time_Mean': dist['lead_time_mean'],
                'Lead_Time_Median': dist['lead_time_median'],
                'Detection_Rate': dist['detection_rate']
            })

        plt.plot(far_grid * 100.0, mean_lts, label=method_name, lw=2)

    plt.xlabel("False Alarm Rate Operating Point (%)", fontsize=11)
    plt.ylabel("Mean Operational Lead Time (seconds)", fontsize=11)
    plt.title(f"Operational Lead-Time vs. FAR: {system_name}", fontsize=12, fontweight='bold')
    plt.grid(True, linestyle='--', alpha=0.5)
    plt.legend(loc='lower right', frameon=True)
    plt.tight_layout()

    output_figure_path.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(output_figure_path, dpi=300)
    plt.close()

    return pd.DataFrame(records)
