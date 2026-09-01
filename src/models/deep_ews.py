"""
Deep Learning Early-Warning Baseline (Bury et al. 2021 PNAS style).
Implements a 1D Convolutional Neural Network (1D-CNN) trained on rolling windows
of raw time series data to classify impending critical transitions.
"""

from typing import Dict, Any, List, Optional
import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim

from src.models.base_model import BaseEarlyWarningModel


class BuryCNN(nn.Module):
    """
    Lightweight 1D-CNN classifier inspired by Bury et al. (2021, PNAS).
    Processes rolling window of raw scalar time series (batch, 1, window_size)
    and predicts probability of impending transition P in [0, 1].
    """
    def __init__(self, in_channels: int = 1):
        super().__init__()
        self.conv1 = nn.Conv1d(in_channels=in_channels, out_channels=16, kernel_size=5, padding=2)
        self.bn1 = nn.BatchNorm1d(16)
        self.relu = nn.ReLU()
        self.pool = nn.MaxPool1d(kernel_size=2)
        self.conv2 = nn.Conv1d(in_channels=16, out_channels=32, kernel_size=3, padding=1)
        self.bn2 = nn.BatchNorm1d(32)
        self.gap = nn.AdaptiveAvgPool1d(1)
        self.fc1 = nn.Linear(32, 16)
        self.fc2 = nn.Linear(16, 1)
        self.sigmoid = nn.Sigmoid()

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        # x: (batch, in_channels, window_size)
        h = self.pool(self.relu(self.bn1(self.conv1(x))))
        h = self.relu(self.bn2(self.conv2(h)))
        h = self.gap(h).squeeze(-1)
        h = self.relu(self.fc1(h))
        out = self.sigmoid(self.fc2(h))
        return out.squeeze(-1)


class DeepEWSModel(BaseEarlyWarningModel):
    """
    Deep Learning Early-Warning Baseline Model wrapper adhering to BaseEarlyWarningModel.
    """
    def __init__(self, name: str = "DeepEWS-Bury2021", in_channels: int = 1, seed: int = 42):
        super().__init__(name=name, indicators=[])
        torch.manual_seed(seed)
        np.random.seed(seed)
        self.in_channels = in_channels
        self.network = BuryCNN(in_channels=in_channels)
        self.is_fitted = False

    def fit_supervised(
        self,
        null_trajectories: List[np.ndarray],
        ramp_trajectories: List[np.ndarray],
        window_size: int = 50,
        step: int = 4,
        epochs: int = 15,
        lr: float = 0.003,
        batch_size: int = 64
    ) -> 'DeepEWSModel':
        """
        Trains the network in a strictly supervised manner on historical training runs.
        Extracts causal rolling windows from null (class 0) and ramp (class 1) trajectories.
        """
        windows = []
        labels = []

        # 1. Null windows -> Class 0
        for x in null_trajectories:
            x_1d = x[:, 0] if x.ndim > 1 else x
            n_obs = len(x_1d)
            for k in range(window_size, n_obs, step * 2):
                win = x_1d[k - window_size : k]
                # Causal z-score normalization
                mean_w = np.mean(win)
                std_w = np.std(win) + 1e-6
                norm_win = (win - mean_w) / std_w
                windows.append(norm_win)
                labels.append(0.0)

        # 2. Ramp windows -> Class 1 (sample closer to collapse)
        for x in ramp_trajectories:
            x_1d = x[:, 0] if x.ndim > 1 else x
            n_obs = len(x_1d)
            # Only sample latter half of ramp trajectory where transition is imminent
            start_k = max(window_size, int(0.5 * n_obs))
            for k in range(start_k, n_obs, step):
                win = x_1d[k - window_size : k]
                mean_w = np.mean(win)
                std_w = np.std(win) + 1e-6
                norm_win = (win - mean_w) / std_w
                windows.append(norm_win)
                labels.append(1.0)

        X = torch.tensor(np.array(windows), dtype=torch.float32).unsqueeze(1)  # (N, 1, W)
        y = torch.tensor(np.array(labels), dtype=torch.float32)

        dataset = torch.utils.data.TensorDataset(X, y)
        loader = torch.utils.data.DataLoader(dataset, batch_size=batch_size, shuffle=True)

        optimizer = optim.Adam(self.network.parameters(), lr=lr, weight_decay=1e-4)
        criterion = nn.BCELoss()

        self.network.train()
        for epoch in range(epochs):
            for batch_x, batch_y in loader:
                optimizer.zero_grad()
                pred = self.network(batch_x)
                loss = criterion(pred, batch_y)
                loss.backward()
                optimizer.step()

        self.network.eval()
        self.is_fitted = True
        return self

    def fit(self, baseline_trajectories: List[np.ndarray], window_size: int = 50, step: int = 1) -> 'DeepEWSModel':
        """
        Fallback fit: If only baseline null trajectories are provided, synthetic contrastive
        tipping windows are generated via variance scaling to train the discriminator.
        """
        null_windows = []
        ramp_windows = []

        for x in baseline_trajectories:
            x_1d = x[:, 0] if x.ndim > 1 else x
            n_obs = len(x_1d)
            for k in range(window_size, n_obs, step * 4):
                win = x_1d[k - window_size : k]
                null_windows.append(win)
                # Synthetic contrastive transition: inject escalating trend and variance
                t_ramp = np.linspace(0, 1, window_size)
                synthetic_ramp = win * (1.0 + 1.5 * t_ramp) + 0.5 * t_ramp**2
                ramp_windows.append(synthetic_ramp)

        return self.fit_supervised(
            [np.array(null_windows)], [np.array(ramp_windows)],
            window_size=window_size, step=step, epochs=10
        )

    def predict_score(
        self,
        x: np.ndarray,
        window_size: int = 50,
        step: int = 1,
        features: Optional[np.ndarray] = None
    ) -> np.ndarray:
        """
        Computes rolling warning probabilities causally along time series x.
        """
        n_obs = len(x)
        scores = np.zeros(n_obs, dtype=np.float64)
        x_1d = x[:, 0] if x.ndim > 1 else x

        if not self.is_fitted:
            # Self-fit on early trajectory baseline
            init_win = [x_1d[:max(window_size * 2, int(0.3 * n_obs))]]
            self.fit(init_win, window_size=window_size, step=step)

        self.network.eval()
        batch_windows = []
        batch_indices = []

        for k in range(window_size, n_obs, step):
            win = x_1d[k - window_size : k]
            mean_w = np.mean(win)
            std_w = np.std(win) + 1e-6
            norm_win = (win - mean_w) / std_w
            batch_windows.append(norm_win)
            batch_indices.append(k)

        if not batch_windows:
            return scores

        X = torch.tensor(np.array(batch_windows), dtype=torch.float32).unsqueeze(1)
        with torch.no_grad():
            preds = self.network(X).cpu().numpy()

        for idx, k in enumerate(batch_indices):
            scores[k : k + step] = float(preds[idx])

        return scores
