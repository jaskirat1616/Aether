"""Data models for signal processing."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class SignalSample:
    timestamp: datetime
    method: str
    value: float
    metadata: dict[str, float]


@dataclass
class RangeEstimate:
    timestamp: datetime
    method: str
    distance: float
    variance: float
    raw: list[SignalSample]


@dataclass
class DeviceEstimate:
    ip: str
    estimate: RangeEstimate
    metadata: dict[str, float]

