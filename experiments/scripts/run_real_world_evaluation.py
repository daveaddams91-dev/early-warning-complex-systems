"""
Evaluation of Early-Warning Indicators on Real-World GISP2 Paleoclimate Data.
Evaluates Variance, AR(1), Permutation Entropy, Spectral Reddening, AEWIF, and DeepEWS
on the historical Younger Dryas abrupt climate transition (~11.7 ka BP).
"""

import sys
from pathlib import Path
import numpy as np
import pandas as pd
from scipy.stats import kendalltau
import matplotlib.pyplot as plt

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from src.systems.real_world.loader import load_younger_dryas_proxy
from src.indicators.univariate import (
    VarianceIndicator,
    AutocorrelationLag1Indicator,
    PermutationEntropyIndicator,
    SpectralReddeningIndicator
)
from src.advancements.adaptive_inference_framework import AdaptiveInferenceFramework
from src.models.deep_ews import DeepEWSModel


def run_real_world_evaluation() -> pd.DataFrame:
    """Worker function for real world evaluation.
    
    Returns:
        The computed result
    
    """
    print("=" * 70, flush=True)
    print("EVALUATING INDICATORS ON REAL-WORLD GISP2 PALEOCLIMATE TRANSITION", flush=True)
    print("=" * 70, flush=True)

    fig_dir = Path("experiments/results/figures")
    table_dir = Path("experiments/results/tables")
    fig_dir.mkdir(parents=True, exist_ok=True)
    table_dir.mkdir(parents=True, exist_ok=True)

    # 1. Load data
    data = load_younger_dryas_proxy(detrend_window=15)
    t = data['time']  # elapsed years from start of YD
    raw = data['raw']
    res = data['residuals']
    t_trans = data['transition_time']  # ~1200 yr elapsed (11,700 BP)

    # Pre-transition mask (only evaluate before the abrupt warming onset)
    pre_mask = (t <= t_trans)
    t_pre = t[pre_mask]
    res_pre = res[pre_mask]
    n_pre = len(res_pre)

    # Window size: 15 steps = 300 years
    w_size = 15
    step = 1

    # 2. Compute indicators
    ind_var = VarianceIndicator()
    ind_ar1 = AutocorrelationLag1Indicator()
    ind_pe = PermutationEntropyIndicator(m=3, tau=1)
    ind_sr = SpectralReddeningIndicator(low_freq_fraction=0.20)

    var_scores = ind_var.compute_rolling(res_pre, window_size=w_size, step=step)
    ar1_scores = ind_ar1.compute_rolling(res_pre, window_size=w_size, step=step)
    pe_scores = ind_pe.compute_rolling(res_pre, window_size=w_size, step=step)
    sr_scores = ind_sr.compute_rolling(res_pre, window_size=w_size, step=step)

    # 3. Compute AEWIF (calibrated on early pre-transition baseline)
    aewif = AdaptiveInferenceFramework(window_size=w_size, trend_window=10, reliability_threshold=0.25)
    baseline_slice = [res_pre[:25].reshape(-1, 1)]
    aewif.calibrate_baseline(baseline_slice, step=1)
    aewif_res = aewif.predict_trajectory(res_pre, step=step)
    aewif_scores = aewif_res['warning_score']
    aewif_rel = aewif_res['reliability_score']

    # 4. Compute DeepEWS (Bury et al. protocol: pre-trained on simulated SDE transitions)
    deep_model = DeepEWSModel(seed=42)
    rng = np.random.default_rng(42)
    # Generate 10 synthetic training trajectories
    synth_null = [rng.normal(0, 0.5, size=150) for _ in range(10)]
    synth_ramp = [rng.normal(0, 0.5, size=150) + np.linspace(0, 1.5, 150) for _ in range(10)]
    deep_model.fit_supervised(synth_null, synth_ramp, window_size=w_size, step=2, epochs=15)
    deep_scores = deep_model.predict_score(res_pre, window_size=w_size, step=step)

    methods = {
        'Variance': var_scores,
        'AR(1)': ar1_scores,
        'PermutationEntropy': pe_scores,
        'SpectralReddening': sr_scores,
        'AEWIF': aewif_scores,
        'DeepEWS': deep_scores
    }

    records = []

    # Calculate Kendall Tau trend on pre-transition indicators (evaluating after initial window)
    eval_start = w_size + 5
    for name, s_arr in methods.items():
        valid_idx = np.where(~np.isnan(s_arr[eval_start:]))[0] + eval_start
        if len(valid_idx) >= 5:
            series = s_arr[valid_idx]
            tau, p_val = kendalltau(np.arange(len(series)), series)
            tau = float(tau) if not np.isnan(tau) else 0.0
            p_val = float(p_val) if not np.isnan(p_val) else 1.0

            # Operational lead time: first 2-sigma exceedance sustained for 3 steps
            baseline_mean = np.mean(series[:15])
            baseline_std = np.std(series[:15]) + 1e-6
            threshold = baseline_mean + 2.0 * baseline_std

            exceed = (series >= threshold)
            lead_time_yr = 0.0
            for k in range(len(exceed) - 2):
                if exceed[k] and exceed[k+1] and exceed[k+2]:
                    alarm_idx = valid_idx[k]
                    alarm_time = t_pre[alarm_idx]
                    lead_time_yr = max(0.0, float(t_trans - alarm_time))
                    break
        else:
            tau, p_val, lead_time_yr = 0.0, 1.0, 0.0

        records.append({
            'Dataset': 'GISP2_Younger_Dryas',
            'Indicator_Method': name,
            'Kendall_Tau': tau,
            'Tau_p_value': p_val,
            'Lead_Time_Years': lead_time_yr,
            'Trend_Verdict': 'POSITIVE_WARNING' if (tau > 0.3 and p_val < 0.05) else ('INVERTED' if (tau < -0.3 and p_val < 0.05) else 'INCONCLUSIVE')
        })
        print(f"  {name:<20} | Kendall Tau: {tau:+6.3f} (p={p_val:.4f}) | Lead Time: {lead_time_yr:5.1f} yr", flush=True)

    df_out = pd.DataFrame(records)
    out_csv = table_dir / "real_world_evaluation.csv"
    df_out.to_csv(out_csv, index=False)
    print(f"\nSaved real-world evaluation table to {out_csv}", flush=True)

    # 5. Multi-panel figure
    fig, axes = plt.subplots(4, 1, figsize=(10, 10), sharex=True)

    # Panel 1: Raw & Residual delta18O
    axes[0].plot(t_pre, res_pre, color='steelblue', lw=1.5, label=r'Detrended Residuals $\delta^{18}\mathrm{O}$')
    axes[0].axvline(t_trans, color='crimson', linestyle='--', lw=2, label='Transition Onset (11.7 ka BP)')
    axes[0].set_ylabel(r'$\delta^{18}\mathrm{O}$ (permil)', fontsize=10)
    axes[0].set_title("GISP2 Ice Core Record: Termination of the Younger Dryas", fontsize=12, fontweight='bold')
    axes[0].grid(True, linestyle='--', alpha=0.5)
    axes[0].legend(loc='upper left')

    # Panel 2: Classical Indicators (Variance & AR1)
    ax2 = axes[1].twinx()
    axes[1].plot(t_pre, var_scores, color='darkorange', lw=2, label='Variance')
    ax2.plot(t_pre, ar1_scores, color='forestgreen', lw=2, linestyle=':', label='AR(1)')
    axes[1].set_ylabel('Variance', color='darkorange', fontsize=10)
    ax2.set_ylabel('AR(1)', color='forestgreen', fontsize=10)
    axes[1].grid(True, linestyle='--', alpha=0.5)

    # Panel 3: AEWIF Warning & Reliability
    ax3 = axes[2].twinx()
    axes[2].plot(t_pre, aewif_scores, color='purple', lw=2, label='AEWIF Warning Score')
    ax3.plot(t_pre, aewif_rel, color='gray', lw=1.5, linestyle='--', label='Reliability R(t)')
    axes[2].set_ylabel('AEWIF Score', color='purple', fontsize=10)
    ax3.set_ylabel('Reliability', color='gray', fontsize=10)
    axes[2].grid(True, linestyle='--', alpha=0.5)

    # Panel 4: DeepEWS
    axes[3].plot(t_pre, deep_scores, color='teal', lw=2, label='DeepEWS Probability')
    axes[3].axhline(0.5, color='red', linestyle='--', alpha=0.7, label='Threshold 0.5')
    axes[3].set_ylabel('DeepEWS P', fontsize=10)
    axes[3].set_xlabel('Elapsed Time into Younger Dryas (Years)', fontsize=11)
    axes[3].grid(True, linestyle='--', alpha=0.5)
    axes[3].legend(loc='upper left')

    plt.tight_layout()
    fig_path = fig_dir / "real_world_younger_dryas_indicators.png"
    plt.savefig(fig_path, dpi=300)
    plt.close()
    print(f"Saved real-world diagnostic figure to {fig_path}", flush=True)

    return df_out


if __name__ == '__main__':
    df = run_real_world_evaluation()
