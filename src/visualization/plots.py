"""
Publication-ready visualization routines for early-warning indicators,
trajectories, ROC curves, lead-time distributions, and adversarial stress-tests.
"""

from typing import Dict, Any, List, Optional
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt


def plot_trajectory_and_indicators(
    time: np.ndarray,
    state: np.ndarray,
    mu: np.ndarray,
    indicators_dict: Dict[str, np.ndarray],
    t_crit: Optional[float] = None,
    system_name: str = "Dynamical System",
    save_path: Optional[str] = None
):
    """
    Plots the state trajectory, parameter ramp, and multiple early-warning indicator signals.
    """
    n_plots = 2 + len(indicators_dict)
    fig, axes = plt.subplots(n_plots, 1, figsize=(10, 2.2 * n_plots), sharex=True)
    
    # 1. State trajectory
    ax0 = axes[0]
    if state.ndim == 1 or state.shape[1] == 1:
        ax0.plot(time, state, 'k-', lw=1.2, label='Observed State $x(t)$')
    else:
        for i in range(min(state.shape[1], 5)):
            ax0.plot(time, state[:, i], lw=1.0, label=f'Node {i+1}')
            
    if t_crit is not None and not np.isnan(t_crit):
        ax0.axvline(t_crit, color='r', linestyle='--', lw=1.5, label='Collapse $T_{crit}$')
    ax0.set_ylabel('State')
    ax0.set_title(f'Early-Warning Dynamics: {system_name}', fontsize=12, fontweight='bold')
    ax0.legend(loc='upper left', framealpha=0.9, fontsize=9)
    ax0.grid(True, alpha=0.3)
    
    # 2. Control Parameter Ramp
    ax1 = axes[1]
    ax1.plot(time, mu, 'b-', lw=1.2, label='Control Parameter $\\mu(t)$')
    if t_crit is not None and not np.isnan(t_crit):
        ax1.axvline(t_crit, color='r', linestyle='--', lw=1.5)
    ax1.set_ylabel('$\\mu(t)$')
    ax1.legend(loc='upper left', framealpha=0.9, fontsize=9)
    ax1.grid(True, alpha=0.3)
    
    # 3+ Indicators
    colors = plt.cm.tab10(np.linspace(0, 1, len(indicators_dict)))
    for idx, (name, values) in enumerate(indicators_dict.items()):
        ax = axes[2 + idx]
        ax.plot(time, values, color=colors[idx], lw=1.4, label=name)
        if t_crit is not None and not np.isnan(t_crit):
            ax.axvline(t_crit, color='r', linestyle='--', lw=1.5)
        ax.set_ylabel(name, fontsize=9)
        ax.legend(loc='upper left', framealpha=0.9, fontsize=9)
        ax.grid(True, alpha=0.3)
        
    axes[-1].set_xlabel('Time $t$', fontsize=10)
    plt.tight_layout()
    
    if save_path:
        Path(save_path).parent.mkdir(parents=True, exist_ok=True)
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
    plt.close()


def plot_roc_curves_comparison(
    roc_results: Dict[str, Dict[str, Any]],
    title: str = "ROC Curves Comparison",
    save_path: Optional[str] = None
):
    """
    Plots comparative ROC curves for multiple indicators and composite models.
    """
    plt.figure(figsize=(7, 6))
    plt.plot([0, 1], [0, 1], 'k--', lw=1.0, alpha=0.7, label='Random Chance (AUC = 0.50)')
    
    colors = plt.cm.tab10(np.linspace(0, 1, len(roc_results)))
    for idx, (name, res) in enumerate(roc_results.items()):
        fpr = res.get('fpr', [])
        tpr = res.get('tpr', [])
        auc = res.get('roc_auc', np.nan)
        if len(fpr) > 0 and len(tpr) > 0 and not np.isnan(auc):
            plt.plot(fpr, tpr, color=colors[idx], lw=1.8, label=f'{name} (AUC = {auc:.3f})')
            
    plt.xlim([-0.02, 1.02])
    plt.ylim([-0.02, 1.02])
    plt.xlabel('False Positive Rate (FPR)', fontsize=11)
    plt.ylabel('True Positive Rate (TPR)', fontsize=11)
    plt.title(title, fontsize=12, fontweight='bold')
    plt.legend(loc='lower right', framealpha=0.95, fontsize=9)
    plt.grid(True, alpha=0.3)
    
    if save_path:
        Path(save_path).parent.mkdir(parents=True, exist_ok=True)
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
    plt.close()


def plot_lead_time_distributions(
    lead_time_data: Dict[str, np.ndarray],
    title: str = "Lead-Time Distributions ($T_{crit} - t_{alarm}$)",
    save_path: Optional[str] = None
):
    """
    Plots boxplot / violin comparative lead-time distributions across indicators.
    """
    plt.figure(figsize=(9, 5))
    names = []
    data_list = []
    
    for name, arr in lead_time_data.items():
        if len(arr) > 0:
            names.append(name)
            data_list.append(arr)
            
    if len(data_list) > 0:
        bp = plt.boxplot(data_list, labels=names, patch_artist=True,
                         medianprops=dict(color='black', lw=1.5),
                         boxprops=dict(facecolor='lightblue', color='navy', alpha=0.7))
        plt.ylabel('Warning Lead Time $\\Delta t_{lead}$', fontsize=11)
        plt.title(title, fontsize=12, fontweight='bold')
        plt.xticks(rotation=25, ha='right', fontsize=9)
        plt.grid(True, alpha=0.3, axis='y')
        
    if save_path:
        Path(save_path).parent.mkdir(parents=True, exist_ok=True)
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
    plt.close()
