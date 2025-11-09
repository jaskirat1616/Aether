"""Temporal tracking for moving devices."""

from __future__ import annotations

from dataclasses import dataclass
from typing import List, Tuple

import numpy as np


@dataclass
class TrackState:
    position: np.ndarray
    velocity: np.ndarray
    covariance: np.ndarray


class ConstantVelocityFilter:
    def __init__(self, dt: float = 1.0, process_noise: float = 1e-2, measurement_noise: float = 1e-1) -> None:
        self._dt = dt
        self._q = process_noise
        self._r = measurement_noise
        self._state: TrackState | None = None

    def initialize(self, position: Tuple[float, float, float]) -> None:
        z = np.array(position)
        self._state = TrackState(
            position=z,
            velocity=np.zeros_like(z),
            covariance=np.eye(6),
        )

    def predict(self) -> None:
        if self._state is None:
            return
        F = np.block(
            [
                [np.eye(3), self._dt * np.eye(3)],
                [np.zeros((3, 3)), np.eye(3)],
            ]
        )
        Q = self._q * np.eye(6)
        x = np.concatenate([self._state.position, self._state.velocity])
        x = F @ x
        P = F @ self._state.covariance @ F.T + Q
        self._state = TrackState(position=x[:3], velocity=x[3:], covariance=P)

    def update(self, measurement: Tuple[float, float, float]) -> None:
        if self._state is None:
            self.initialize(measurement)
            return
        H = np.block([np.eye(3), np.zeros((3, 3))])
        R = self._r * np.eye(3)
        x = np.concatenate([self._state.position, self._state.velocity])
        P = self._state.covariance
        y = np.array(measurement) - H @ x
        S = H @ P @ H.T + R
        K = P @ H.T @ np.linalg.inv(S)
        x = x + K @ y
        P = (np.eye(6) - K @ H) @ P
        self._state = TrackState(position=x[:3], velocity=x[3:], covariance=P)

    def get_state(self) -> TrackState | None:
        return self._state

