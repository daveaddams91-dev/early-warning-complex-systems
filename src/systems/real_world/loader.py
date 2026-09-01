"""
Real-World Empirical Dataset Loader.
Loads paleoclimate proxy records (GISP2 Greenland Ice Core delta18O)
across the Younger Dryas abrupt climate transition (~11.7 ka BP).
"""

from pathlib import Path
from typing import Dict, Any, Optional
import numpy as np
import pandas as pd


def get_dataset_path() -> Path:
    """Returns absolute path to the bundled real-world dataset."""
    root = Path(__file__).resolve().parent.parent.parent.parent
    return root / "data" / "real_world" / "gisp2_younger_dryas.csv"


def load_younger_dryas_proxy(detrend_window: int = 15) -> Dict[str, Any]:
    """
    Loads and preprocesses the GISP2 Younger Dryas delta18O paleoclimate time series.
    Returns:
        - time: age in years Before Present (BP), moving forward in time toward the present.
        - raw: raw delta18O values (per mil).
        - residuals: causally detrended anomalies (rolling mean subtraction).
        - transition_time: age of abrupt Preboreal warming onset (~11,700 yr BP).
        - metadata: provenance, resolution, and citation.
    """
    csv_path = get_dataset_path()
    if not csv_path.exists():
        raise FileNotFoundError(f"Empirical dataset not found at {csv_path}")

    df = pd.read_csv(csv_path)

    # Sort chronological (oldest to youngest, moving forward in time)
    df = df.sort_values('Age_yr_BP', ascending=False).reset_index(drop=True)

    # Isolate Younger Dryas stadial up to transition onset (12,900 BP to 11,600 BP)
    # The abrupt transition occurs at 11,700 BP
    yd_df = df[(df['Age_yr_BP'] <= 12900) & (df['Age_yr_BP'] >= 11600)].reset_index(drop=True)

    # Time moving forward: elapsed years from start of Younger Dryas
    age_bp = yd_df['Age_yr_BP'].values
    elapsed_years = 12900.0 - age_bp
    raw_vals = yd_df['delta18O_permil'].values

    # Causal rolling detrending to extract fluctuation residuals
    residuals = np.zeros_like(raw_vals)
    for i in range(len(raw_vals)):
        start = max(0, i - detrend_window + 1)
        mean_val = np.mean(raw_vals[start : i + 1])
        residuals[i] = raw_vals[i] - mean_val

    # Transition onset occurs at age 11,700 BP -> elapsed_years = 1200.0 yr
    t_trans_elapsed = 1200.0

    metadata = {
        'source': 'NOAA World Data Service for Paleoclimatology / GISP2 Ice Core',
        'citation': 'Grootes, P.M., and Stuiver, M. (1997). Oxygen 18/16 variability in Greenland snow and ice. J. Geophys. Res., 102(C12), 26455-26470.',
        'proxy': 'delta18O (permil) as temperature proxy',
        'resolution_yr': 20.0,
        'transition_type': 'Abrupt Dansgaard-Oeschger / Bølling-Allerød / Preboreal warming',
        'transition_age_bp': 11700.0,
        'license': 'Public Domain (U.S. Federal Government Data)'
    }

    return {
        'time': elapsed_years,
        'age_bp': age_bp,
        'raw': raw_vals,
        'residuals': residuals,
        'transition_time': t_trans_elapsed,
        'metadata': metadata
    }
