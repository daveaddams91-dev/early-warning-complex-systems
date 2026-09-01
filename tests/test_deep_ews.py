import numpy as np
import pytest
import torch
from src.models.deep_ews import BuryCNN, DeepEWSModel


class TestDeepEWS:
    def test_bury_cnn_forward(self):
        model = BuryCNN(in_channels=1)
        x = torch.randn(8, 1, 50)
        out = model(x)
        assert out.shape == (8,)
        assert torch.all(out >= 0.0) and torch.all(out <= 1.0)

    def test_deep_ews_fit_and_predict(self):
        rng = np.random.default_rng(42)
        null_runs = [rng.normal(0.0, 0.1, size=200) for _ in range(5)]
        ramp_runs = [rng.normal(0.0, 0.1, size=200) + np.linspace(0, 2.0, 200) for _ in range(5)]

        model = DeepEWSModel(seed=42)
        model.fit_supervised(null_runs, ramp_runs, window_size=30, step=4, epochs=5)

        test_traj = rng.normal(0.0, 0.1, size=200)
        scores = model.predict_score(test_traj, window_size=30, step=4)

        assert len(scores) == 200
        assert np.all(scores >= 0.0) and np.all(scores <= 1.0)
        assert np.all(scores[:30] == 0.0)  # Causal initial window
