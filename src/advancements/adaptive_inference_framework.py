"""
Adaptive Early-Warning Inference Framework (AEWIF).
Implements:
1. Online Indicator Informativeness Estimator: P(indicator i is informative | X_{1:t}).
2. Dynamic, state-dependent indicator weighting: w_i(t) = f(X_{1:t}).
3. System-Level Reliability Score: R(t) in [0, 1].
4. Explicit Abstention State: W(t) = UNRELIABLE when R(t) < threshold.
5. Causal Multi-Step Persistence Filter.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from typing import Dict, Any, List, Optional, Tuple
import numpy as np
import pandas as pd
from scipy.stats import kendalltau
from src.systems.may_harvesting import MayHarvestingSystem
from src.simulation.integrator import SDEIntegrator, ObservationCorrupter
from src.indicators.base_indicator import BaseIndicator
from src.indicators.univariate import VarianceIndicator, AutocorrelationLag1Indicator, PermutationEntropyIndicator, SpectralReddeningIndicator
from src.indicators.multivariate import PCA1VarianceIndicator
from src.evaluation.metrics import compute_trajectory_level_roc_pr


class AdaptiveInferenceFramework:
    """
    AEWIF: Adaptive Early-Warning Inference Framework.
    Dynamically assesses the reliability and informativeness of multiple competing indicators,
    weights them state-dependently, and declares UNRELIABLE when evidence is contradictory or noisy.
    """

    def __init__(
        self,
        indicators: Optional[List[BaseIndicator]] = None,
        window_size: int = 50,
        trend_window: int = 30,
        reliability_threshold: float = 0.25,
        alarm_threshold: float = 2.0,
        persistence_steps: int = 4
    ):
        if indicators is None:
            self.indicators = [
                VarianceIndicator(),
                AutocorrelationLag1Indicator(),
                PermutationEntropyIndicator(m=3, tau=1),
                SpectralReddeningIndicator(low_freq_fraction=0.15),
                PCA1VarianceIndicator()
            ]
        else:
            self.indicators = indicators

        self.window_size = window_size
        self.trend_window = trend_window
        self.reliability_threshold = reliability_threshold
        self.alarm_threshold = alarm_threshold
        self.persistence_steps = persistence_steps

        # Baseline empirical calibration
        self.baseline_means: Optional[np.ndarray] = None
        self.baseline_stds: Optional[np.ndarray] = None
        self.expected_directions: Optional[np.ndarray] = None
        self.is_calibrated = False

    def calibrate_baseline(self, baseline_runs: List[np.ndarray], step: int = 4):
        """
        Calibrates stationary null baseline statistics and expected sign of response.
        """
        all_feats = []
        for x in baseline_runs:
            feats = self._extract_raw_features(x, step=step)
            all_feats.append(feats)

        flat_feats = np.concatenate(all_feats, axis=0)
        # Remove NaNs
        valid_mask = ~np.isnan(flat_feats).any(axis=1)
        valid_feats = flat_feats[valid_mask]

        if len(valid_feats) < 10:
            self.baseline_means = np.nanmean(flat_feats, axis=0)
            self.baseline_stds = np.nanstd(flat_feats, axis=0) + 1e-4
        else:
            self.baseline_means = np.mean(valid_feats, axis=0)
            self.baseline_stds = np.std(valid_feats, axis=0) + 1e-4

        # Expected directionality:
        # Variance (+1), AR1 (+1), PermutationEntropy (-1: drops as regularity increases),
        # SpectralReddening (+1), PCA1 (+1)
        directions = []
        for ind in self.indicators:
            if 'PermutationEntropy' in ind.name or 'RecoveryRate' in ind.name:
                directions.append(-1.0)
            else:
                directions.append(1.0)
        self.expected_directions = np.array(directions, dtype=np.float64)
        self.is_calibrated = True

    def _extract_raw_features(self, x: np.ndarray, step: int = 4) -> np.ndarray:
        n_obs = len(x)
        K = len(self.indicators)
        feats = np.full((n_obs, K), np.nan)
        x_1d = x[:, 0] if x.ndim > 1 else x

        for j, ind in enumerate(self.indicators):
            if ind.is_multivariate:
                feats[:, j] = ind.compute_rolling(x, window_size=self.window_size, step=step)
            else:
                feats[:, j] = ind.compute_rolling(x_1d, window_size=self.window_size, step=step)
        return feats

    def predict_trajectory(self, x: np.ndarray, step: int = 4) -> Dict[str, Any]:
        """
        Runs online adaptive inference over trajectory x.
        Returns:
            - warning_score: W(t)
            - reliability_score: R(t)
            - weights: w_i(t)
            - is_reliable: bool
            - alarm_active: bool (after persistence filter)
        """
        n_obs = len(x)
        K = len(self.indicators)
        raw_feats = self._extract_raw_features(x, step=step)

        if not self.is_calibrated:
            # Fallback self-calibration on first 25% of trajectory if uncalibrated
            init_idx = max(self.window_size + 10, int(0.25 * n_obs))
            init_data = raw_feats[:init_idx]
            self.baseline_means = np.nanmean(init_data, axis=0)
            self.baseline_stds = np.nanstd(init_data, axis=0) + 1e-4
            self.expected_directions = np.array([
                -1.0 if ('PermutationEntropy' in ind.name or 'RecoveryRate' in ind.name) else 1.0
                for ind in self.indicators
            ])
            self.is_calibrated = True

        warning_score = np.zeros(n_obs)
        reliability_score = np.zeros(n_obs)
        weights_history = np.zeros((n_obs, K))
        is_reliable_history = np.ones(n_obs, dtype=bool)

        x_1d = x[:, 0] if x.ndim > 1 else x

        # Process each evaluation step
        for k in range(self.window_size, n_obs, step):
            f_k = raw_feats[k]
            if np.isnan(f_k).any():
                continue

            # 1. Causal Direction-Aligned Z-scores
            z_k = self.expected_directions * (f_k - self.baseline_means) / self.baseline_stds
            # Rectify: only positive anomalies represent slowing down / tipping precursors
            z_rect = np.maximum(z_k, 0.0)

            # 2. Local Observation Noise Estimation (differencing ratio)
            w_start = max(0, k - self.window_size + 1)
            x_win = x_1d[w_start : k + 1]
            diff_var = np.var(np.diff(x_win))
            tot_var = np.var(x_win) + 1e-8
            noise_ratio = diff_var / tot_var  # ~2.0 for pure white noise, << 1 for smooth signal

            # 3. Individual Indicator Trend & Informativeness Assessment
            t_start = max(0, k - self.trend_window + 1)
            alpha = np.zeros(K)

            for j in range(K):
                feat_series = raw_feats[t_start : k + 1 : step, j]
                valid_series = feat_series[~np.isnan(feat_series)]
                if len(valid_series) >= 4:
                    tau_val, _ = kendalltau(np.arange(len(valid_series)), valid_series)
                    trend_score = self.expected_directions[j] * (0.0 if np.isnan(tau_val) else tau_val)
                else:
                    trend_score = 0.0

                # SNR factor
                snr_factor = np.clip(z_rect[j] / 3.0, 0.0, 3.0)
                # High-frequency noise penalty (AR1 and higher moments suffer heavily)
                noise_penalty = 1.0 if ('AR(1)' in self.indicators[j].name and noise_ratio > 1.2) else 0.0

                # Informativeness weight
                raw_alpha = max(0.0, trend_score) * snr_factor * (1.0 - 0.7 * noise_penalty)
                alpha[j] = raw_alpha

            # 4. Normalize Weights or Abstain
            sum_alpha = np.sum(alpha)
            if sum_alpha > 1e-4:
                w_k = alpha / sum_alpha
                has_informative_signal = True
            else:
                # Strict abstention semantics: when no indicator is informative,
                # do NOT fall back to equal weights. Assign zero weights and declare uninformative.
                w_k = np.zeros(K)
                has_informative_signal = False

            # 5. Calculate Reliability Score R(t)
            # Higher when:
            # - average SNR is high
            # - noise_ratio is low
            # - active indicators agree
            mean_snr = np.mean(z_rect)
            consensus = 1.0 / (1.0 + np.var(z_rect) + 1e-4)
            snr_sig = 1.0 / (1.0 + np.exp(-(mean_snr - 1.5)))
            clean_sig = np.clip(1.0 - 0.4 * max(0.0, noise_ratio - 0.5), 0.0, 1.0)
            
            r_t = float(snr_sig * consensus * clean_sig)
            reliability_score[k : k + step] = r_t

            # 6. None-of-the-Above / Abstention Check
            if (r_t < self.reliability_threshold) or (not has_informative_signal):
                is_reliable_history[k : k + step] = False
                # Downweight or reject warning score when unreliable
                w_score = 0.0
            else:
                is_reliable_history[k : k + step] = True
                w_score = float(np.sum(w_k * z_rect))

            warning_score[k : k + step] = w_score
            weights_history[k : k + step] = w_k

        # 7. Causal Multi-Step Persistence Filter
        # An operational alarm is active if and only if warning_score >= alarm_threshold and is_reliable
        # for at least persistence_steps consecutive evaluation steps.
        alarm_active = np.zeros(n_obs, dtype=bool)
        consecutive_count = 0
        for k in range(self.window_size, n_obs, step):
            if is_reliable_history[k] and warning_score[k] >= self.alarm_threshold:
                consecutive_count += 1
                if consecutive_count >= self.persistence_steps:
                    alarm_active[k : k + step] = True
            else:
                consecutive_count = 0

        return {
            'warning_score': warning_score,
            'reliability_score': reliability_score,
            'weights': weights_history,
            'is_reliable': is_reliable_history,
            'alarm_active': alarm_active
        }


def evaluate_adaptive_vs_static_framework(n_runs: int = 20, dt_obs: float = 0.05) -> pd.DataFrame:
    """
    Directly compares the Adaptive Inference Framework (AEWIF) against static baselines
    across clean and corrupted regimes on May Fold and Stommel AMOC.
    """
    print("=" * 70, flush=True)
    print("EVALUATING ADAPTIVE INFERENCE FRAMEWORK (AEWIF) VS STATIC BASELINES", flush=True)
    print("=" * 70, flush=True)

    out_dir = Path("results/validated/tables")
    out_dir.mkdir(parents=True, exist_ok=True)

    sys_may = MayHarvestingSystem()
    integrator_may = SDEIntegrator(sys_may, dt_sim=0.01, dt_obs=dt_obs)

    null_may = [integrator_may.simulate(t_max=120.0, mu_func=lambda t: 1.5, seed=1000 + r) for r in range(n_runs)]
    ramp_may = [integrator_may.simulate(t_max=120.0, mu_func=lambda t: 1.5 + (3.2 - 1.5)*(t/120.0), seed=2000 + r, stop_on_collapse=True) for r in range(n_runs)]
    c_times = [tr['t_crit'] for tr in ramp_may]
    r_times = [tr['t'] for tr in ramp_may]
    n_times = [tr['t'] for tr in null_may]

    aewif = AdaptiveInferenceFramework(window_size=50, trend_window=30, reliability_threshold=0.25)
    aewif.calibrate_baseline([tr['x'] for tr in null_may])

    scenarios = [
        ('Clean_Reference', lambda x, s: x),
        ('Severe_Noise_0dB', lambda x, s: ObservationCorrupter.add_gaussian_noise(x, snr_db=0.0, seed=s)),
        ('Colored_Red_Noise', lambda x, s: ObservationCorrupter.add_colored_red_noise(x, dt=dt_obs, gamma=0.7, sigma_eta=0.04, seed=s)),
        ('20_Distractors', lambda x, s: ObservationCorrupter.append_distractors(x, n_distractors=20, dt=dt_obs, seed=s))
    ]

    records = []

    for scen_name, corrupter in scenarios:
        r_xs = [corrupter(tr['x'], 3000 + i) for i, tr in enumerate(ramp_may)]
        n_xs = [corrupter(tr['x'], 4000 + i) for i, tr in enumerate(null_may)]

        # 1. Evaluate AEWIF
        aewif_r = [aewif.predict_trajectory(x)['warning_score'] for x in r_xs]
        aewif_n = [aewif.predict_trajectory(x)['warning_score'] for x in n_xs]
        aewif_rel_r = [aewif.predict_trajectory(x)['reliability_score'] for x in r_xs]

        roc_aewif = compute_trajectory_level_roc_pr(
            aewif_r, aewif_n, r_times, c_times, n_times, safe_baseline_time=20.0, min_lead_time=2.0
        )

        # 2. Evaluate Pure Variance
        var_ind = VarianceIndicator()
        v_r = [var_ind.compute_rolling(x[:, 0] if x.ndim > 1 else x, window_size=50, step=4) for x in r_xs]
        v_n = [var_ind.compute_rolling(x[:, 0] if x.ndim > 1 else x, window_size=50, step=4) for x in n_xs]
        roc_var = compute_trajectory_level_roc_pr(v_r, v_n, r_times, c_times, n_times, safe_baseline_time=20.0, min_lead_time=2.0)

        # 3. Evaluate Pure AR(1)
        ar1_ind = AutocorrelationLag1Indicator()
        ar_r = [ar1_ind.compute_rolling(x[:, 0] if x.ndim > 1 else x, window_size=50, step=4) for x in r_xs]
        ar_n = [ar1_ind.compute_rolling(x[:, 0] if x.ndim > 1 else x, window_size=50, step=4) for x in n_xs]
        roc_ar = compute_trajectory_level_roc_pr(ar_r, ar_n, r_times, c_times, n_times, safe_baseline_time=20.0, min_lead_time=2.0)

        mean_rel = float(np.mean([np.mean(r_sc[400:]) for r_sc in aewif_rel_r]))

        records.append({
            'Scenario': scen_name,
            'AEWIF_Trajectory_ROC_AUC': roc_aewif['roc_auc'],
            'Variance_Trajectory_ROC_AUC': roc_var['roc_auc'],
            'AR1_Trajectory_ROC_AUC': roc_ar['roc_auc'],
            'Mean_Reliability_Score_R': mean_rel,
            'AEWIF_vs_Variance_Delta': roc_aewif['roc_auc'] - roc_var['roc_auc'],
            'AEWIF_vs_AR1_Delta': roc_aewif['roc_auc'] - roc_ar['roc_auc']
        })

    df_comp = pd.DataFrame(records)
    df_comp.to_csv(out_dir / "phase4_aewif_benchmark_comparison.csv", index=False)
    print("  AEWIF comparison saved to results/validated/tables/phase4_aewif_benchmark_comparison.csv", flush=True)
    return df_comp


if __name__ == '__main__':
    df = evaluate_adaptive_vs_static_framework(n_runs=15)
    print(df.to_string())
