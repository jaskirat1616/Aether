"""Simulated Wi-Fi interface for development and testing."""

from __future__ import annotations

import math
import random
from dataclasses import dataclass
from typing import Iterable

from .interface import InterfaceInfo, WiFiInterface


@dataclass
class SimulatedDevice:
    ip: str
    position: tuple[float, float, float]


class SimulatedWiFiInterface(WiFiInterface):
    def __init__(self, name: str) -> None:
        super().__init__(name)
        self._devices = [
            SimulatedDevice("192.168.1.10", (0.0, 0.0, 0.0)),
            SimulatedDevice("192.168.1.11", (2.5, 1.0, 0.0)),
            SimulatedDevice("192.168.1.12", (4.0, -1.0, 1.0)),
        ]
        self._self = SimulatedDevice("192.168.1.2", (0.0, 0.0, 0.5))

    def _distance(self, target: str) -> float:
        device = next((d for d in self._devices if d.ip == target), None)
        if not device:
            raise ValueError(f"Unknown target {target}")
        dx = device.position[0] - self._self.position[0]
        dy = device.position[1] - self._self.position[1]
        dz = device.position[2] - self._self.position[2]
        return math.sqrt(dx * dx + dy * dy + dz * dz)

    def measure_rssi(self, target: str) -> float:
        distance = self._distance(target)
        # Log-distance path loss model placeholder
        path_loss = 27.55 + 20 * math.log10(2400) - 20 * math.log10(max(distance, 0.1))
        noise = random.gauss(0, 2)
        return -(path_loss + noise)

    def measure_rtt(self, target: str) -> float:
        distance = self._distance(target)
        speed_of_light = 299_792_458.0
        base = (distance * 2) / speed_of_light
        jitter = random.gauss(0, 1e-7)
        return base + jitter

    def capture_csi(self, target: str) -> Iterable[list[complex]]:
        distance = self._distance(target)
        subcarriers = 30
        # Phase offset proportional to distance (wavelength ~ 0.125m at 2.4GHz)
        phase_offset = (distance / 0.125) * 2 * math.pi
        # Magnitude decreases with distance (inverse square law approximation)
        magnitude = 1.0 / max(distance, 0.1)
        noise_scale = 0.1
        
        for _ in range(5):
            yield [
                complex(
                    magnitude * math.cos(phase_offset + i * 0.1 + random.gauss(0, noise_scale)),
                    magnitude * math.sin(phase_offset + i * 0.1 + random.gauss(0, noise_scale))
                )
                for i in range(subcarriers)
            ]

    def enumerate_devices(self) -> Iterable[str]:
        return [device.ip for device in self._devices]

    def info(self) -> InterfaceInfo:
        return InterfaceInfo(
            name=self.name,
            capabilities={"rssi": True, "rtt": True, "csi": True},
        )

    def close(self) -> None:
        return None

