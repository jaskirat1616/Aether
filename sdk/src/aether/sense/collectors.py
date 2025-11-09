"""Signal collectors coordinating measurements."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from statistics import mean, variance
from typing import Iterable, Optional

from ..core.interface import WiFiInterface
from .models import DeviceEstimate, RangeEstimate, SignalSample


@dataclass
class CollectorConfig:
    rssi_samples: int = 5
    rtt_samples: int = 5
    csi_frames: int = 3
    smoothing: float = 0.5


class SignalCollector:
    """Gather signals from a Wi-Fi interface and produce range estimates."""

    def __init__(self, interface: WiFiInterface, config: Optional[CollectorConfig] = None) -> None:
        self._iface = interface
        self._config = config or CollectorConfig()

    def estimate_range(self, target: str, method: str = "auto") -> RangeEstimate:
        if method == "auto":
            capabilities = self._iface.info().capabilities or {}
            if capabilities.get("csi"):
                method = "csi"
            elif capabilities.get("rtt"):
                method = "rtt"
            else:
                method = "rssi"

        samples: list[SignalSample]
        if method == "rssi":
            samples = self._collect_rssi(target)
            distance = self._distance_from_rssi(samples)
        elif method == "rtt":
            samples = self._collect_rtt(target)
            distance = self._distance_from_rtt(samples)
        elif method == "csi":
            samples = self._collect_csi(target)
            distance = self._distance_from_csi(samples)
        else:
            raise ValueError(f"Unknown method '{method}'")

        variance_value = variance([sample.value for sample in samples]) if len(samples) > 1 else 0.0
        return RangeEstimate(
            timestamp=datetime.utcnow(),
            method=method,
            distance=distance,
            variance=variance_value,
            raw=samples,
        )

    def enumerate_devices(self) -> Iterable[DeviceEstimate]:
        for ip in self._iface.enumerate_devices():
            try:
                estimate = self.estimate_range(ip, method="auto")
            except Exception:
                continue
            yield DeviceEstimate(ip=ip, estimate=estimate, metadata={})

    def close(self) -> None:
        return None

    # --- internal helpers ---

    def _collect_rssi(self, target: str) -> list[SignalSample]:
        return [
            SignalSample(
                timestamp=datetime.utcnow(),
                method="rssi",
                value=self._iface.measure_rssi(target),
                metadata={},
            )
            for _ in range(self._config.rssi_samples)
        ]

    def _collect_rtt(self, target: str) -> list[SignalSample]:
        return [
            SignalSample(
                timestamp=datetime.utcnow(),
                method="rtt",
                value=self._iface.measure_rtt(target),
                metadata={},
            )
            for _ in range(self._config.rtt_samples)
        ]

    def _collect_csi(self, target: str) -> list[SignalSample]:
        frames = []
        for frame in self._iface.capture_csi(target):
            frames.append(frame)
            if len(frames) >= self._config.csi_frames:
                break
        magnitudes = [abs(value) for frame in frames for value in frame]
        return [
            SignalSample(
                timestamp=datetime.utcnow(),
                method="csi",
                value=value,
                metadata={},
            )
            for value in magnitudes
        ]

    def _distance_from_rssi(self, samples: list[SignalSample]) -> float:
        # Placeholder log-distance formula
        avg_rssi = mean(sample.value for sample in samples)
        tx_power = -40  # assumed dBm
        path_loss_exponent = 2.2
        return 10 ** ((tx_power - avg_rssi) / (10 * path_loss_exponent))

    def _distance_from_rtt(self, samples: list[SignalSample]) -> float:
        speed_of_light = 299_792_458.0
        avg_time = mean(sample.value for sample in samples)
        return (avg_time * speed_of_light) / 2

    def _distance_from_csi(self, samples: list[SignalSample]) -> float:
        avg_mag = mean(sample.value for sample in samples)
        return 1.0 / max(avg_mag, 1e-6)

