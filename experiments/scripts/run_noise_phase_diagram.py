"""
Quantitative Noise-Detectability Phase Diagram.
Sweeps observation noise level (SNR = -6dB to +12dB) across all 5 canonical systems
and top 3 indicators/models (Variance, AR(1), CEWF-Mahalanobis).
Generates heatmaps and quantitative phase boundary tables.
"""

import sys
from pathlib import Path
from typing import Dict, Any, List
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from src.systems.may_harvesting import MayHarvestingSystem
from src.systems.fitzhugh_nagumo import FitzHughNagumoSystem
from src.systems.subcritical_pitchfork import SubcriticalPitchforkSystem
from src.systems.stommel_box import StommelBoxSystem
from src.systems.coupled_network import CoupledNetworkSystem
from src.simulation.integrator import SDEIntegrator, ObservationCorrupter
from src.indicators.univariate import VarianceIndicator, AutocorrelationLag1Indicator
from src.models.mahalanobis_composite import MultiIndicatorMahalanobisModel
from src.evaluation.metrics import compute_trajectory_level_roc_pr


def run_noise_detectability_sweep(n_runs: int = 15, dt_obs: float = 0.05) -> pd.DataFrame:
    print("=" * 70, flush=True)
    print("RUNNING QUANTITATIVE NOISE-DETECTABILITY PHASE DIAGRAM SWEEP", flush=True)
    print("=" * 70, flush=True)

    fig_dir = Path("experiments/results/figures")
    table_dir = Path("experiments/results/tables")
    fig_dir.mkdir(parents=True, exist_ok=True)
    table_dir.mkdir(parents=True, exist_ok=True)

    snr_grid = [-6.0, -3.0, 0.0, 3.0, 6.0, 9.0, 12.0]
    systems = [
        ("SYS1_May_Fold", MayHarvestingSystem(), lambda t: 1.5 + (3.2 - 1.5)*(t/120.0), 120.0, lambda t: 1.5, 20.0),
        ("SYS2_FitzHughNagumo_Hopf", FitzHughNagumoSystem(), lambda t: -0.5 + (0.45 - (-0.5))*(t/150.0), 150.0, lambda t: -0.5, 20.0),
        ("SYS3_Subcritical_Pitchfork", SubcriticalPitchforkSystem(), lambda t: -0.6 + (0.1 - (-0.6))*(t/100.0), 100.0, lambda t: -0.6, 20.0),
        ("SYS4_Stommel_AMOC", StommelBoxSystem(), lambda t: 0.8 + (1.4 - 0.8)*(t/120.0), 120.0, lambda t: 0.8, 20.0),
        ("SYS5_Coupled_Network", CoupledNetworkSystem(n_nodes=10, network_type='erdos_renyi', seed=42), lambda t: 1.5 + (5.2 - 1.5)*(t/120.0), 120.0, lambda t: 1.5, 20.0)
    ]

    records = []

    # Cache clean simulations per system
    clean_sims = {}
    for sys_name, sys_obj, ramp_fn, t_max, null_fn, safe_t in systems:
        print(f"  Simulating clean runs for {sys_name} ...", flush=True)
        integrator = SDEIntegrator(sys_obj, dt_sim=0.01, dt_obs=dt_obs)
        null_trajs = [integrator.simulate(t_max=t_max, mu_func=null_fn, seed=1000 + r) for r in range(n_runs)]
        ramp_trajs = [integrator.simulate(t_max=t_max, mu_func=ramp_fn, seed=2000 + r, stop_on_collapse=True) for r in range(n_runs)]
        clean_sims[sys_name] = {
            'null': null_trajs,
            'ramp': ramp_trajs,
            'safe_t': safe_t
        }

    var_ind = VarianceIndicator()
    ar1_ind = AutocorrelationLag1Indicator()
    core_subset = [VarianceIndicator(), AutocorrelationLag1Indicator()]

    for snr in snr_grid:
        print(f"\n>>> Evaluating at SNR = {snr:+.1f} dB ...", flush=True)
        for sys_name, _, _, _, _, safe_t in systems:
            sim_data = clean_sims[sys_name]
            null_trajs = sim_data['null']
            ramp_trajs = sim_data['ramp']

            r_times = [tr['t'] for tr in ramp_trajs]
            c_times = [tr['t_crit'] for tr in ramp_trajs]
            n_times = [tr['t'] for tr in null_trajs]

            # Corrupt with observation noise
            corr_ramp_xs = [ObservationCorrupter.add_gaussian_noise(tr['x'], snr_db=snr, seed=3000 + i) for i, tr in enumerate(ramp_trajs)]
            corr_null_xs = [ObservationCorrupter.add_gaussian_noise(tr['x'], snr_db=snr, seed=4000 + i) for i, tr in enumerate(null_trajs)]

            r_1d = [x[:, 0] if x.ndim > 1 else x for x in corr_ramp_xs]
            n_1d = [x[:, 0] if x.ndim > 1 else x for x in corr_null_xs]

            # 1. Variance
            v_r = [var_ind.compute_rolling(x, window_size=50, step=4) for x in r_1d]
            v_n = [var_ind.compute_rolling(x, window_size=50, step=4) for x in n_1d]
            auc_var = compute_trajectory_level_roc_pr(v_r, v_n, r_times, c_times, n_times, safe_baseline_time=safe_t, min_lead_time=2.0)['roc_auc']

            # 2. AR(1)
            a_r = [ar1_ind.compute_rolling(x, window_size=50, step=4) for x in r_1d]
            a_n = [ar1_ind.compute_rolling(x, window_size=50, step=4) for x in n_1d]
            auc_ar1 = compute_trajectory_level_roc_pr(a_r, a_n, r_times, c_times, n_times, safe_baseline_time=safe_t, min_lead_time=2.0)['roc_auc']

            # 3. CEWF-Mahalanobis
            mah = MultiIndicatorMahalanobisModel(indicators=core_subset, regularization=1e-3)
            mah.fit(corr_null_xs, window_size=50, step=4)
            m_r = [mah.predict_score(x, window_size=50, step=4) for x in corr_ramp_xs]
            m_n = [mah.predict_score(x, window_size=50, step=4) for x in corr_null_xs]
            auc_mah = compute_trajectory_level_roc_pr(m_r, m_n, r_times, c_times, n_times, safe_baseline_time=safe_t, min_lead_time=2.0)['roc_auc']

            records.append({'SNR_dB': snr, 'System': sys_name, 'Method': 'Variance', 'ROC_AUC': float(auc_var)})
            records.append({'SNR_dB': snr, 'System': sys_name, 'Method': 'AR(1)', 'ROC_AUC': float(auc_ar1)})
            records.append({'SNR_dB': snr, 'System': sys_name, 'Method': 'CEWF-Mahalanobis', 'ROC_AUC': float(auc_mah)})

            print(f"  {sys_name:<26} | Var: {auc_var:.3f} | AR(1): {auc_ar1:.3f} | Mah: {auc_mah:.3f}", flush=True)

    df_sweep = pd.DataFrame(records)
    out_csv = table_dir / "noise_detectability_phase_diagram.csv"
    df_sweep.to_csv(out_csv, index=False)
    print(f"\nSaved phase diagram data to {out_csv}", flush=True)

    # Generate Heatmaps for each method
    methods = ['Variance', 'AR(1)', 'CEWF-Mahalanobis']
    sys_order = [s[0] for s in systems]

    for m in methods:
        sub_df = df_sweep[df_sweep['Method'] == m]
        pivot = sub_df.pivot(index='SNR_dB', columns='System', values='ROC_AUC')
        # Sort columns according to systems list
        pivot = pivot[[col for col in sys_order if col in pivot.columns]]
        pivot = pivot.sort_index(ascending=False)  # Higher SNR at top

        fig, ax = plt.subplots(figsize=(8, 6))
        cax = ax.imshow(pivot.values, cmap='RdYlGn', vmin=0.0, vmax=1.0, aspect='auto')

        ax.set_xticks(np.arange(len(pivot.columns)))
        ax.set_yticks(np.arange(len(pivot.index)))
        ax.set_xticklabels([c.replace("SYS", "S").replace("_", " ") for c in pivot.columns], rotation=25, ha='right', fontsize=9)
        ax.set_yticklabels([f"{val:+.1f} dB" for val in pivot.index], fontsize=10)

        # Annotate text
        for i in range(len(pivot.index)):
            for j in range(len(pivot.columns)):
                val = pivot.values[i, j]
                color = 'black' if 0.25 < val < 0.75 else 'white'
                ax.text(j, i, f"{val:.2f}", ha='center', va='center', color=color, fontweight='bold', fontsize=9)

        cbar = fig.colorbar(cax, ax=ax)
        cbar.set_label("Trajectory ROC-AUC", fontsize=11)
        ax.set_xlabel("Dynamical System", fontsize=11, fontweight='bold')
        ax.set_ylabel("Observation Noise (SNR in dB)", fontsize=11, fontweight='bold')
        ax.set_title(f"Noise-Detectability Phase Diagram: {m}", fontsize=12, fontweight='bold')
        plt.tight_layout()

        out_fig = fig_dir / f"noise_detectability_phase_diagram_{m.replace('(', '').replace(')', '').replace('-', '_')}.png"
        plt.savefig(out_fig, dpi=300)
        plt.close()
        print(f"Saved heatmap to {out_fig}", flush=True)

    return df_sweep


if __name__ == '__main__':
    df_res = run_noise_detectability_sweep(n_runs=15)
