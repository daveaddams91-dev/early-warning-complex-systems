import numpy as np
import pytest
from src.systems.real_world.loader import load_younger_dryas_proxy, get_dataset_path


class TestRealWorldLoader:
    def test_file_exists(self):
        path = get_dataset_path()
        assert path.exists(), f"Dataset not found at {path}"

    def test_load_younger_dryas_proxy(self):
        data = load_younger_dryas_proxy(detrend_window=15)
        assert 'time' in data
        assert 'raw' in data
        assert 'residuals' in data
        assert 'transition_time' in data
        assert 'metadata' in data

        assert len(data['time']) > 50
        assert len(data['raw']) == len(data['time'])
        assert len(data['residuals']) == len(data['time'])
        assert not np.isnan(data['raw']).any()
        assert not np.isnan(data['residuals']).any()
        assert data['transition_time'] > 0.0
