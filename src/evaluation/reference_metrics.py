"""
Independent reference implementations of all critical statistical metrics.
Used to mathematically audit and verify production metric implementations.
"""

from typing import Dict, Any, List, Tuple
import numpy as np


def reference_roc_auc(y_true: np.ndarray, y_score: np.ndarray) -> float:
    """
    Independent reference implementation of ROC-AUC using exact Mann-Whitney U formulation:
        AUC = (sum_{i in Pos, j in Neg} I(s_i > s_j) + 0.5 * I(s_i == s_j)) / (N_pos * N_neg)
    """
    valid = ~np.isnan(y_score) & ~np.isnan(y_true)
    yt = y_true[valid].astype(int)
    ys = y_score[valid]
    
    pos_scores = ys[yt == 1]
    neg_scores = ys[yt == 0]
    n_pos = len(pos_scores)
    n_neg = len(neg_scores)
    
    if n_pos == 0 or n_neg == 0:
        return float('nan')
        
    diff = pos_scores[:, None] - neg_scores[None, :]
    concordant = np.sum(diff > 0)
    ties = np.sum(diff == 0)
    
    auc = (concordant + 0.5 * ties) / (n_pos * n_neg)
    return float(auc)


def reference_pr_auc(y_true: np.ndarray, y_score: np.ndarray) -> float:
    """
    Independent reference implementation of Average Precision (PR-AUC):
        AP = sum_n (R_n - R_{n-1}) * P_n
    """
    valid = ~np.isnan(y_score) & ~np.isnan(y_true)
    yt = y_true[valid].astype(int)
    ys = y_score[valid]
    
    n_pos = np.sum(yt == 1)
    if n_pos == 0 or len(yt) == 0:
        return float('nan')
        
    # Sort descending
    sort_idx = np.argsort(-ys)
    yt_sorted = yt[sort_idx]
    
    cum_tp = np.cumsum(yt_sorted == 1)
    cum_fp = np.cumsum(yt_sorted == 0)
    
    recalls = cum_tp / n_pos
    precisions = cum_tp / (cum_tp + cum_fp)
    
    # Prepend 0 for recall
    recalls_diff = np.diff(np.concatenate([[0.0], recalls]))
    # Average precision sum over positive instances
    ap = np.sum(precisions * (yt_sorted == 1)) / n_pos
    return float(ap)


def reference_confusion_metrics(y_true: np.ndarray, y_score: np.ndarray, threshold: float) -> Dict[str, float]:
    """
    Independent reference computation of binary classification rates at fixed threshold.
    """
    valid = ~np.isnan(y_score) & ~np.isnan(y_true)
    yt = y_true[valid].astype(int)
    pred = (y_score[valid] >= threshold).astype(int)
    
    tp = float(np.sum((yt == 1) & (pred == 1)))
    fp = float(np.sum((yt == 0) & (pred == 1)))
    tn = float(np.sum((yt == 0) & (pred == 0)))
    fn = float(np.sum((yt == 1) & (pred == 0)))
    
    tpr = tp / (tp + fn) if (tp + fn) > 0 else 0.0
    fpr = fp / (fp + tn) if (fp + tn) > 0 else 0.0
    precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
    recall = tpr
    f1 = 2.0 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0.0
    
    return {
        'tp': tp,
        'fp': fp,
        'tn': tn,
        'fn': fn,
        'tpr': tpr,
        'fpr': fpr,
        'precision': precision,
        'recall': recall,
        'f1': f1
    }


def reference_trajectory_roc_auc(
    ramp_trajectories_scores: List[np.ndarray],
    null_trajectories_scores: List[np.ndarray],
    safe_skip_steps: int = 20
) -> Dict[str, Any]:
    """
    Independent reference implementation of Trajectory-Level ROC:
    A ramp trajectory is a True Positive if max(score) >= threshold in the warning window.
    A null trajectory is a False Alarm if max(score) >= threshold outside the safe skip steps.
    """
    ramp_max = []
    for sc in ramp_trajectories_scores:
        valid_sc = sc[safe_skip_steps:][~np.isnan(sc[safe_skip_steps:])]
        ramp_max.append(np.max(valid_sc) if len(valid_sc) > 0 else -1e9)
        
    null_max = []
    for sc in null_trajectories_scores:
        valid_sc = sc[safe_skip_steps:][~np.isnan(sc[safe_skip_steps:])]
        null_max.append(np.max(valid_sc) if len(valid_sc) > 0 else -1e9)
        
    ramp_max = np.array(ramp_max)
    null_max = np.array(null_max)
    
    all_scores = np.concatenate([ramp_max, null_max])
    all_labels = np.concatenate([np.ones(len(ramp_max)), np.zeros(len(null_max))])
    
    auc = reference_roc_auc(all_labels, all_scores)
    pr_auc = reference_pr_auc(all_labels, all_scores)
    
    return {
        'trajectory_roc_auc': auc,
        'trajectory_pr_auc': pr_auc,
        'ramp_max_scores': ramp_max,
        'null_max_scores': null_max
    }
