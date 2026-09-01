"""
Evaluation metrics and statistical significance testing for early-warning systems.
Provides ROC-AUC, PR-AUC, lead-time distributions, false alarm rates, and DeLong tests.
"""

from typing import Dict, Any, List, Tuple, Optional
import numpy as np
import scipy.stats as st
from sklearn.metrics import roc_curve, roc_auc_score, precision_recall_curve, average_precision_score


def compute_roc_pr(y_true: np.ndarray, y_score: np.ndarray) -> Dict[str, Any]:
    """
    Computes ROC-AUC and PR-AUC for binary early-warning classification.
    """
    valid = ~np.isnan(y_score) & ~np.isnan(y_true)
    y_t = y_true[valid].astype(int)
    y_s = y_score[valid]
    
    if len(np.unique(y_t)) < 2:
        return {
            'roc_auc': np.nan,
            'pr_auc': np.nan,
            'fpr': np.array([]),
            'tpr': np.array([]),
            'precision': np.array([]),
            'recall': np.array([])
        }
        
    roc_auc = float(roc_auc_score(y_t, y_s))
    pr_auc = float(average_precision_score(y_t, y_s))
    fpr, tpr, roc_thresh = roc_curve(y_t, y_s)
    precision, recall, pr_thresh = precision_recall_curve(y_t, y_s)
    
    return {
        'roc_auc': roc_auc,
        'pr_auc': pr_auc,
        'fpr': fpr,
        'tpr': tpr,
        'precision': precision,
        'recall': recall
    }


def compute_operational_lead_time_distribution(
    warning_scores: List[np.ndarray],
    time_arrays: List[np.ndarray],
    collapse_times: List[float],
    threshold: float,
    safe_baseline_time: float = 20.0,
    min_actionable_lead_time: float = 2.0
) -> Dict[str, Any]:
    """
    Computes strict operational early-warning metrics across realizations.
    
    Partitions time into:
      1. Safe Baseline Window [0, safe_baseline_time]: Trigger = Early False Alarm
      2. Actionable Warning Window [safe_baseline_time, T_crit - min_actionable_lead_time]: Trigger = True Positive
      3. Late Window (T_crit - min_actionable_lead_time, T_crit]: Trigger = Late Warning (Unactionable)
      4. Post-Collapse (> T_crit): Missed detection
    """
    lead_times = []
    tp_count = 0
    early_fa_count = 0
    late_alarm_count = 0
    missed_count = 0
    total_collapses = 0
    
    for scores, times, t_crit in zip(warning_scores, time_arrays, collapse_times):
        if np.isnan(t_crit):
            continue
            
        total_collapses += 1
        alarms = (scores >= threshold)
        alarm_indices = np.where(alarms)[0]
        
        if len(alarm_indices) == 0:
            missed_count += 1
            continue
            
        first_alarm_time = float(times[alarm_indices[0]])
        
        if first_alarm_time < safe_baseline_time:
            # Triggered prematurely during calm baseline
            early_fa_count += 1
        elif first_alarm_time <= t_crit - min_actionable_lead_time:
            # Valid, actionable early warning
            lead_time = t_crit - first_alarm_time
            lead_times.append(lead_time)
            tp_count += 1
        elif first_alarm_time <= t_crit:
            # Alarm sounded, but too late to take preventive action
            late_alarm_count += 1
        else:
            missed_count += 1
            
    lead_times_arr = np.array(lead_times, dtype=np.float64)
    n_tot = max(1, total_collapses)
    
    return {
        'true_positive_rate': float(tp_count / n_tot),
        'early_false_alarm_rate': float(early_fa_count / n_tot),
        'late_alarm_rate': float(late_alarm_count / n_tot),
        'missed_detection_rate': float(missed_count / n_tot),
        'mean_lead_time': float(np.mean(lead_times_arr)) if len(lead_times_arr) > 0 else np.nan,
        'median_lead_time': float(np.median(lead_times_arr)) if len(lead_times_arr) > 0 else np.nan,
        'std_lead_time': float(np.std(lead_times_arr)) if len(lead_times_arr) > 0 else np.nan,
        'p10_lead_time': float(np.percentile(lead_times_arr, 10)) if len(lead_times_arr) > 0 else np.nan,
        'p90_lead_time': float(np.percentile(lead_times_arr, 90)) if len(lead_times_arr) > 0 else np.nan,
        'iqr_lead_time': float(st.iqr(lead_times_arr)) if len(lead_times_arr) > 0 else np.nan,
        'n_true_positives': tp_count,
        'n_early_false_alarms': early_fa_count,
        'n_total': total_collapses,
        'raw_lead_times': lead_times_arr
    }


def compute_trajectory_level_roc_pr(
    ramp_scores: List[np.ndarray],
    null_scores: List[np.ndarray],
    time_arrays_ramp: List[np.ndarray],
    collapse_times: List[float],
    time_arrays_null: List[np.ndarray],
    safe_baseline_time: float = 20.0,
    min_lead_time: float = 2.0
) -> Dict[str, Any]:
    """
    Computes rigorous trajectory-level ROC-AUC and PR-AUC where each realization is exactly 1 independent sample.
    Eliminates time-step pseudoreplication.
    """
    y_traj_score = []
    y_traj_true = []
    
    # Positive class: peak warning score in actionable window [safe_baseline_time, T_crit - min_lead_time]
    for sc, times, t_crit in zip(ramp_scores, time_arrays_ramp, collapse_times):
        if np.isnan(t_crit):
            continue
        mask = (times >= safe_baseline_time) & (times <= t_crit - min_lead_time) & (~np.isnan(sc))
        valid_vals = sc[mask]
        peak_score = float(np.max(valid_vals)) if len(valid_vals) > 0 else -1e9
        y_traj_true.append(1)
        y_traj_score.append(peak_score)
        
    # Negative class: peak score in null series after safe baseline time
    for sc, times in zip(null_scores, time_arrays_null):
        mask = (times >= safe_baseline_time) & (~np.isnan(sc))
        valid_vals = sc[mask]
        peak_score = float(np.max(valid_vals)) if len(valid_vals) > 0 else -1e9
        y_traj_true.append(0)
        y_traj_score.append(peak_score)
        
    yt = np.array(y_traj_true)
    ys = np.array(y_traj_score)
    
    return compute_roc_pr(yt, ys)


def clustered_bootstrap_auc_diff(
    ramp_scores_a: List[np.ndarray],
    ramp_scores_b: List[np.ndarray],
    null_scores_a: List[np.ndarray],
    null_scores_b: List[np.ndarray],
    time_arrays_ramp: List[np.ndarray],
    collapse_times: List[float],
    time_arrays_null: List[np.ndarray],
    n_boot: int = 1000,
    seed: int = 42
) -> Dict[str, float]:
    """
    Clustered bootstrap over trajectories to calculate valid confidence intervals for Delta AUC.
    Resamples whole realizations with replacement to preserve internal temporal autocorrelation.
    """
    rng = np.random.default_rng(seed)
    n_ramp = len(ramp_scores_a)
    n_null = len(null_scores_a)
    
    diffs = []
    
    for _ in range(n_boot):
        idx_r = rng.choice(n_ramp, size=n_ramp, replace=True)
        idx_n = rng.choice(n_null, size=n_null, replace=True)
        
        r_sc_a = [ramp_scores_a[i] for i in idx_r]
        r_sc_b = [ramp_scores_b[i] for i in idx_r]
        n_sc_a = [null_scores_a[i] for i in idx_n]
        n_sc_b = [null_scores_b[i] for i in idx_n]
        t_r = [time_arrays_ramp[i] for i in idx_r]
        t_c = [collapse_times[i] for i in idx_r]
        t_n = [time_arrays_null[i] for i in idx_n]
        
        res_a = compute_trajectory_level_roc_pr(r_sc_a, n_sc_a, t_r, t_c, t_n)
        res_b = compute_trajectory_level_roc_pr(r_sc_b, n_sc_b, t_r, t_c, t_n)
        
        if not np.isnan(res_a['roc_auc']) and not np.isnan(res_b['roc_auc']):
            diffs.append(res_a['roc_auc'] - res_b['roc_auc'])
            
    diffs_arr = np.array(diffs)
    if len(diffs_arr) == 0:
        return {'diff_mean': np.nan, 'ci_lower': np.nan, 'ci_upper': np.nan, 'p_value': np.nan}
        
    diff_mean = float(np.mean(diffs_arr))
    ci_lower = float(np.percentile(diffs_arr, 2.5))
    ci_upper = float(np.percentile(diffs_arr, 97.5))
    # Two-sided bootstrap p-value
    p_val = float(2.0 * min(np.mean(diffs_arr <= 0), np.mean(diffs_arr >= 0)))
    p_val = min(1.0, p_val)
    
    return {
        'diff_mean': diff_mean,
        'ci_lower': ci_lower,
        'ci_upper': ci_upper,
        'p_value': p_val
    }


def compute_lead_time_distribution(
    warning_scores: List[np.ndarray],
    time_arrays: List[np.ndarray],
    collapse_times: List[float],
    threshold: float,
    min_lead_time: float = 0.0
) -> Dict[str, Any]:
    """
    Computes the lead-time distribution across multiple stochastic realization runs.
    Lead time: Delta t_lead = T_crit - t_alarm.
    """
    lead_times = []
    detected_count = 0
    false_alarm_early = 0
    total_collapses = 0
    
    for scores, times, t_crit in zip(warning_scores, time_arrays, collapse_times):
        if np.isnan(t_crit):
            continue
            
        total_collapses += 1
        alarms = (scores >= threshold)
        alarm_indices = np.where(alarms)[0]
        
        if len(alarm_indices) == 0:
            # Missed warning
            continue
            
        # First alarm time
        first_alarm_time = times[alarm_indices[0]]
        
        if first_alarm_time <= t_crit - min_lead_time:
            lead_time = t_crit - first_alarm_time
            lead_times.append(lead_time)
            detected_count += 1
            
    lead_times_arr = np.array(lead_times, dtype=np.float64)
    
    if len(lead_times_arr) == 0:
        return {
            'detection_rate': 0.0,
            'mean_lead_time': np.nan,
            'median_lead_time': np.nan,
            'std_lead_time': np.nan,
            'p10_lead_time': np.nan,
            'p90_lead_time': np.nan,
            'iqr_lead_time': np.nan,
            'n_detected': 0,
            'n_total': total_collapses
        }
        
    return {
        'detection_rate': float(detected_count / max(1, total_collapses)),
        'mean_lead_time': float(np.mean(lead_times_arr)),
        'median_lead_time': float(np.median(lead_times_arr)),
        'std_lead_time': float(np.std(lead_times_arr)),
        'p10_lead_time': float(np.percentile(lead_times_arr, 10)),
        'p90_lead_time': float(np.percentile(lead_times_arr, 90)),
        'iqr_lead_time': float(st.iqr(lead_times_arr)),
        'n_detected': detected_count,
        'n_total': total_collapses,
        'raw_lead_times': lead_times_arr
    }


def compute_false_alarm_rate(
    warning_scores: List[np.ndarray],
    threshold: float
) -> float:
    """
    Computes false alarm rate on stationary / null runs where NO collapse occurs.
    """
    if len(warning_scores) == 0:
        return 0.0
    false_positives = 0
    for scores in warning_scores:
        valid_scores = scores[~np.isnan(scores)]
        if len(valid_scores) > 0 and np.any(valid_scores >= threshold):
            false_positives += 1
    return float(false_positives / len(warning_scores))


def delong_roc_variance(y_true: np.ndarray, y_score: np.ndarray) -> Tuple[float, np.ndarray]:
    """
    Computes structural components of AUC variance for DeLong test.
    """
    pos_mask = (y_true == 1)
    neg_mask = (y_true == 0)
    
    m = np.sum(pos_mask)
    n = np.sum(neg_mask)
    
    if m == 0 or n == 0:
        return np.nan, np.array([])
        
    pos_scores = y_score[pos_mask]
    neg_scores = y_score[neg_mask]
    
    # Kernel matrix: V_10(i) = 1/n sum_j I(X_i > Y_j)
    v10 = np.mean((pos_scores[:, None] > neg_scores[None, :]).astype(float) + 
                  0.5 * (pos_scores[:, None] == neg_scores[None, :]).astype(float), axis=1)
    # Kernel matrix: V_01(j) = 1/m sum_i I(X_i > Y_j)
    v01 = np.mean((pos_scores[:, None] > neg_scores[None, :]).astype(float) + 
                  0.5 * (pos_scores[:, None] == neg_scores[None, :]).astype(float), axis=0)
                  
    auc = np.mean(v10)
    var = (np.var(v10, ddof=1) / m) + (np.var(v01, ddof=1) / n)
    return float(auc), np.concatenate([v10, v01])


def delong_paired_test(
    y_true: np.ndarray,
    y_score_a: np.ndarray,
    y_score_b: np.ndarray
) -> Dict[str, float]:
    """
    DeLong test comparing AUC of model A vs model B on identical test cases.
    """
    valid = ~np.isnan(y_score_a) & ~np.isnan(y_score_b) & ~np.isnan(y_true)
    yt = y_true[valid].astype(int)
    sa = y_score_a[valid]
    sb = y_score_b[valid]
    
    auc_a, v_a = delong_roc_variance(yt, sa)
    auc_b, v_b = delong_roc_variance(yt, sb)
    
    if np.isnan(auc_a) or np.isnan(auc_b) or len(v_a) == 0:
        return {'auc_a': np.nan, 'auc_b': np.nan, 'diff': np.nan, 'z_stat': np.nan, 'p_value': np.nan}
        
    # Covariance between structural components
    m = np.sum(yt == 1)
    n = np.sum(yt == 0)
    v10_a, v01_a = v_a[:m], v_a[m:]
    v10_b, v01_b = v_b[:m], v_b[m:]
    
    cov10 = np.cov(v10_a, v10_b)[0, 1] if m > 1 else 0.0
    cov01 = np.cov(v01_a, v01_b)[0, 1] if n > 1 else 0.0
    
    var_a = np.var(v10_a, ddof=1) / m + np.var(v01_a, ddof=1) / n
    var_b = np.var(v10_b, ddof=1) / m + np.var(v01_b, ddof=1) / n
    cov_ab = cov10 / m + cov01 / n
    
    var_diff = max(1e-12, var_a + var_b - 2.0 * cov_ab)
    diff = auc_a - auc_b
    z_stat = diff / np.sqrt(var_diff)
    p_value = 2.0 * (1.0 - st.norm.cdf(abs(z_stat)))
    
    return {
        'auc_a': float(auc_a),
        'auc_b': float(auc_b),
        'diff': float(diff),
        'z_stat': float(z_stat),
        'p_value': float(p_value)
    }
