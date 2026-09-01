"""
Lead-Time vs False Alarm Rate Benchmark.
Runs Monte Carlo evaluations on all 5 canonical systems, generates lead-time distributions
at FAR = 1%, 5%, 10%, and plots Lead-Time vs FAR curves.
"""

import sys
from pathlib import Path
from typing import Dict, Any, List
import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from src.systems.may_harvesting import MayHarvestingSystem
from src.systems.fitzhugh_nagumo import FitzHughNagumoSystem
from src.systems.subcritical_pitchfork import SubcriticalPitchforkSystem
from src.systems.stommel_box import StommelBoxSystem
from src.systems.coupled_network import CoupledNetworkSystem
from src.simulation.integrator import SDEIntegrator
from src.indicators.univariate import VarianceIndicator, AutocorrelationLag1Indicator
from src.models.mahalanobis_composite import MultiIndicatorMahalanobisModel
from src.advancements.adaptive_inference_framework import AdaptiveInferenceFramework
from src.evaluation.lead_time import compute_lead_time_distribution, generate_lead_time_vs_far_curve


def run_full_lead_time_benchmark(n_runs: int = 25, dt_obs: float = 0.05) -> Tuple[pd.DataFrame, pd.DataFrame]:
    print("=" * 70, flush=True)
    print("RUNNING OPERATIONAL LEAD-TIME VS. FALSE ALARM RATE BENCHMARK", flush=True)
    print("=" * 70, flush=True)

    fig_dir = Path("experiments/results/figures")
    table_dir = Path("experiments/results/tables")
    fig_dir.mkdir(parents=True, exist_ok=True)
    table_dir.mkdir(parents=True, exist_ok=True)

    systems = [
        ("SYS1_May_Fold", MayHarvestingSystem(), lambda t: 1.5 + (3.2 - 1.5)*(t/120.0), 120.0, lambda t: 1.5, 20.0),
        ("SYS2_FitzHughNagumo_Hopf", FitzHughNagumoSystem(), lambda t: -0.5 + (0.45 - (-0.5))*(t/150.0), 150.0, lambda t: -0.5, 20.0),
        ("SYS3_Subcritical_Pitchfork", SubcriticalPitchforkSystem(), lambda t: -0.6 + (0.1 - (-0.6))*(t/100.0), 100.0, lambda t: -0.6, 20.0),
        ("SYS4_Stommel_AMOC", StommelBoxSystem(), lambda t: 0.8 + (1.4 - 0.8)*(t/120.0), 120.0, lambda t: 0.8, 20.0),
        ("SYS5_Coupled_Network", CoupledNetworkSystem(n_nodes=10, network_type='erdos_renyi', seed=42), lambda t: 1.5 + (5.2 - 1.5)*(t/120.0), 120.0, lambda t: 1.5, 20.0)
    ]

    operating_records = []
    all_curve_dfs = []

    for sys_name, sys_obj, ramp_fn, t_max, null_fn, safe_t in systems:
        print(f"\n>>> Benchmarking System: {sys_name} ...", flush=True)
        integrator = SDEIntegrator(sys_obj, dt_sim=0.01, dt_obs=dt_obs)

        null_trajs = [integrator.simulate(t_max=t_max, mu_func=null_fn, seed=1000 + r) for r in range(n_runs)]
        ramp_trajs = [integrator.simulate(t_max=t_max, mu_func=ramp_fn, seed=2000 + r, stop_on_collapse=True) for r in range(n_runs)]

        r_times = [tr['t'] for tr in ramp_trajs]
        c_times = [tr['t_crit'] for tr in ramp_trajs]
        n_times = [tr['t'] for tr in null_trajs]

        r_xs = [tr['x'] for tr in ramp_trajs]
        n_xs = [tr['x'] for tr in null_trajs]

        r_1d = [tr['x'][:, 0] if tr['x'].ndim > 1 else tr['x'] for tr in ramp_trajs]
        n_1d = [tr['x'][:, 0] if tr['x'].ndim > 1 else tr['x'] for tr in null_trajs]

        # 1. Variance
        var_ind = VarianceIndicator()
        var_r = [var_ind.compute_rolling(x, window_size=50, step=4) for x in r_1d]
        var_n = [var_ind.compute_rolling(x, window_size=50, step=4) for x in n_1d]

        # 2. AR(1)
        ar1_ind = AutocorrelationLag1Indicator()
        ar1_r = [ar1_ind.compute_rolling(x, window_size=50, step=4) for x in r_1d]
        ar1_n = [ar1_ind.compute_rolling(x, window_size=50, step=4) for x in n_1d]

        # 3. CEWF-Mahalanobis
        core_subset = [VarianceIndicator(), AutocorrelationLag1Indicator()]
        mah_model = MultiIndicatorMahalanobisModel(indicators=core_subset, regularization=1e-3)
        mah_model.fit(n_xs, window_size=50, step=4)
        mah_r = [mah_model.predict_score(x, window_size=50, step=4) for x in r_xs]
        mah_n = [mah_model.predict_score(x, window_size=50, step=4) for x in n_xs]

        # 4. AEWIF
        aewif = AdaptiveInferenceFramework(window_size=50, trend_window=30, reliability_threshold=0.25)
        aewif.calibrate_baseline(n_xs)
        aewif_r = [aewif.predict_trajectory(x)['warning_score'] for x in r_xs]
        aewif_n = [aewif.predict_trajectory(x)['warning_score'] for x in n_xs]

        method_data = {
            'Variance': {'ramp_scores': var_r, 'null_scores': var_n, 'time_ramp': r_times, 't_crit': c_times, 'time_null': n_times},
            'AR(1)': {'ramp_scores': ar1_r, 'null_scores': ar1_n, 'time_ramp': r_times, 't_crit': c_times, 'time_null': n_times},
            'CEWF-Mahalanobis': {'ramp_scores': mah_r, 'null_scores': mah_n, 'time_ramp': r_times, 't_crit': c_times, 'time_null': n_times},
            'AEWIF': {'ramp_scores': aewif_r, 'null_scores': aewif_n, 'time_ramp': r_times, 't_crit': c_times, 'time_null': n_times}
        }

        # Compute point metrics at 1%, 5%, 10% FAR
        for m_name, m_dict in method_data.items():
            dist_res = compute_lead_time_distribution(
                m_dict['ramp_scores'], m_dict['null_scores'],
                m_dict['time_ramp'], m_dict['t_crit'], m_dict['time_null'],
                safe_baseline_time=safe_t, min_lead_time=2.0, far_points=(0.01, 0.05, 0.10)
            )
            for far_val in [0.01, 0.05, 0.10]:
                d = dist_res[far_val]
                operating_records.append({
                    'System': sys_name,
                    'Method': m_name,
                    'FAR_Operating_Point': far_val,
                    'Threshold': d['threshold'],
                    'Detection_Rate': d['detection_rate'],
                    'Lead_Time_Mean': d['lead_time_mean'],
                    'Lead_Time_Std': d['lead_time_std'],
                    'Lead_Time_Median': d['lead_time_median'],
                    'Lead_Time_IQR': d['lead_time_q75'] - d['lead_time_q25']
                })
                print(f"  {m_name:<18} @ FAR={far_val*100:4.1f}% | DetRate: {d['detection_rate']:4.2f} | MeanLead: {d['lead_time_mean']:5.2f}s | MedianLead: {d['lead_time_median']:5.2f}s", flush=True)

        # Generate curve figure
        fig_path = fig_dir / f"lead_time_vs_far_{sys_name}.png"
        df_curve = generate_lead_time_vs_far_curve(
            sys_name, method_data, fig_path, far_grid=np.linspace(0.01, 0.20, 20),
            safe_baseline_time=safe_t, min_lead_time=2.0
        )
        all_curve_dfs.append(df_curve)
        print(f"  Saved curve figure to {fig_path}", flush=True)

    df_operating = pd.DataFrame(operating_records)
    out_table_csv = table_dir / "lead_time_benchmark.csv"
    df_operating.to_csv(out_table_csv, index=False)
    print(f"\nSaved lead time operating points table to {out_table_csv}", flush=True)

    return df_operating, pd.concat(all_curve_dfs, ignore_index=True)


if __name__ == '__main__':
    df_op, df_curves = run_full_lead_time_benchmark(n_runs=25)
