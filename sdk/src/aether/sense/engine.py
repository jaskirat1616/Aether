"""Ranging engine combining multiple signal-derived estimates."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

import numpy as np

from .models import RangeEstimate


@dataclass
class EnvironmentPreset:
    name: str
    path_loss_exponent: float
    variance: float


ENVIRONMENTS: dict[str, EnvironmentPreset] = {
    "default": EnvironmentPreset("default", path_loss_exponent=2.2, variance=0.5),
    "home": EnvironmentPreset("home", path_loss_exponent=2.0, variance=0.4),
    "industrial": EnvironmentPreset("industrial", path_loss_exponent=2.6, variance=0.8),
    "hospital": EnvironmentPreset("hospital", path_loss_exponent=2.4, variance=0.6),
}


class RangingEngine:
    """Fuse multiple range estimates into a calibrated prediction."""

    def __init__(self, environment: str = "default") -> None:
        self._environment = ENVIRONMENTS.get(environment, ENVIRONMENTS["default"])
        self._state_mean = None
        self._state_var = None

    def reset(self) -> None:
        self._state_mean = None
        self._state_var = None

    def calibrate(self, measured_distance: float) -> None:
        self._state_mean = measured_distance
        self._state_var = self._environment.variance

    def fuse(self, estimates: Iterable[RangeEstimate]) -> RangeEstimate:
        estimates = list(estimates)
        if not estimates:
            raise ValueError("No estimates provided")

        distances = np.array([estimate.distance for estimate in estimates])
        variances = np.array([max(estimate.variance, 1e-6) for estimate in estimates])

        weights = 1 / variances
        fused_distance = float(np.average(distances, weights=weights))
        fused_variance = float(1 / weights.sum())

        if self._state_mean is None:
            self._state_mean = fused_distance
            self._state_var = fused_variance
        else:
            kalman_gain = self._state_var / (self._state_var + fused_variance)
            self._state_mean = self._state_mean + kalman_gain * (fused_distance - self._state_mean)
            self._state_var = (1 - kalman_gain) * self._state_var

        best_estimate = estimates[0]
        return RangeEstimate(
            timestamp=best_estimate.timestamp,
            method="fusion",
            distance=self._state_mean,
            variance=self._state_var,
            raw=sum((estimate.raw for estimate in estimates), start=[]),
        )

