import numpy as np
import pytest
from experiments.scripts.ablate_amoc_failure import apply_transform, run_amoc_ablation


class TestAMOCAblation:
    def test_apply_transform_shapes_and_values(self):
        rng = np.random.default_rng(42)
        x_1d = rng.normal(1.0, 0.1, size=100)
        x_2d = rng.normal(1.0, 0.1, size=(100, 2))

        # 1D tests
        for t_name in ["raw", "log_transform", "first_difference", "local_detrend", "linearizing_reparam"]:
            res = apply_transform(x_1d, t_name)
            assert len(res) == 100, f"Failed length for 1D {t_name}"
            assert not np.isnan(res).any(), f"NaN found in 1D {t_name}"

        # 2D tests
        for t_name in ["raw", "log_transform", "first_difference", "local_detrend", "linearizing_reparam"]:
            res_2d = apply_transform(x_2d, t_name)
            assert len(res_2d) == 100, f"Failed length for 2D {t_name}"
            assert not np.isnan(res_2d).any(), f"NaN found in 2D {t_name}"

    def test_run_amoc_ablation_fast(self):
        # Run minimal 2-run ablation to verify end-to-end execution and columns
        df = run_amoc_ablation(n_runs=2, dt_obs=0.1)
        assert not df.empty
        assert 'ROC_AUC' in df.columns
        assert 'Transform' in df.columns
        assert 'Indicator' in df.columns
