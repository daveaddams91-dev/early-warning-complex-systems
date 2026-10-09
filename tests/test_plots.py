import os
import tempfile
import numpy as np

from unittest.mock import patch
from src.visualization.plots import (
    plot_trajectory_and_indicators,
    plot_roc_curves_comparison,
    plot_lead_time_distributions
)


def test_plot_trajectory_and_indicators():
    time = np.linspace(0, 100, 100)
    state = np.sin(time)
    mu = np.linspace(1, 2, 100)
    indicators = {
        'Variance': np.random.rand(100),
        'Autocorrelation': np.random.rand(100)
    }

    with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp:
        save_path = tmp.name

    try:
        plot_trajectory_and_indicators(
            time=time,
            state=state,
            mu=mu,
            indicators_dict=indicators,
            t_crit=80.0,
            system_name="Test System",
            save_path=save_path
        )
        assert os.path.exists(save_path)
        assert os.path.getsize(save_path) > 0
    finally:
        if os.path.exists(save_path):
            os.remove(save_path)


def test_plot_trajectory_and_indicators_multidim():
    time = np.linspace(0, 100, 100)
    state = np.random.rand(100, 3)  # 3 dimensions
    mu = np.linspace(1, 2, 100)
    indicators = {
        'Variance': np.random.rand(100)
    }

    with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp:
        save_path = tmp.name

    try:
        plot_trajectory_and_indicators(
            time=time,
            state=state,
            mu=mu,
            indicators_dict=indicators,
            save_path=save_path
        )
        assert os.path.exists(save_path)
        assert os.path.getsize(save_path) > 0
    finally:
        if os.path.exists(save_path):
            os.remove(save_path)


def test_plot_roc_curves_comparison():
    roc_results = {
        'Indicator 1': {
            'fpr': np.linspace(0, 1, 10),
            'tpr': np.linspace(0, 1, 10),
            'roc_auc': 0.85
        },
        'Indicator 2': {
            'fpr': np.linspace(0, 1, 10),
            'tpr': np.linspace(0.1, 1, 10),
            'roc_auc': 0.90
        }
    }

    with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp:
        save_path = tmp.name

    try:
        plot_roc_curves_comparison(
            roc_results=roc_results,
            title="Test ROC",
            save_path=save_path
        )
        assert os.path.exists(save_path)
        assert os.path.getsize(save_path) > 0
    finally:
        if os.path.exists(save_path):
            os.remove(save_path)


@patch('matplotlib.pyplot.boxplot')
def test_plot_lead_time_distributions(mock_boxplot):
    lead_time_data = {
        'Method A': np.random.normal(10, 2, 50),
        'Method B': np.random.normal(15, 3, 50),
        'Method C': np.array([])  # Empty array test case
    }

    with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp:
        save_path = tmp.name

    try:
        plot_lead_time_distributions(
            lead_time_data=lead_time_data,
            title="Test Lead Time",
            save_path=save_path
        )
        assert os.path.exists(save_path)
        assert os.path.getsize(save_path) > 0
    finally:
        if os.path.exists(save_path):
            os.remove(save_path)
