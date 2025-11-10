"""Abstractions for platform Wi-Fi interfaces."""

from __future__ import annotations

import abc
from dataclasses import dataclass
from typing import Iterable, Optional


@dataclass
class InterfaceInfo:
    name: str
    mac_address: Optional[str] = None
    driver: Optional[str] = None
    capabilities: dict[str, bool] | None = None


class InterfaceError(RuntimeError):
    """Base error for Wi-Fi interface issues."""


class WiFiInterface(abc.ABC):
    """Abstract Wi-Fi interface handle."""

    def __init__(self, name: str) -> None:
        self._name = name

    @property
    def name(self) -> str:
        return self._name

    @abc.abstractmethod
    def measure_rssi(self, target: str) -> float:
        """Return RSSI (dBm) for ``target``."""

    @abc.abstractmethod
    def measure_rtt(self, target: str) -> float:
        """Return round trip time in seconds."""

    @abc.abstractmethod
    def capture_csi(self, target: str) -> Iterable[list[complex]]:
        """Stream CSI matrices if supported."""

    @abc.abstractmethod
    def enumerate_devices(self) -> Iterable[str]:
        """Return reachable device identifiers."""

    @abc.abstractmethod
    def info(self) -> InterfaceInfo:
        """Return interface metadata."""

    @abc.abstractmethod
    def close(self) -> None:
        """Release resources."""

    @staticmethod
    def open(name: str, csi_backend: str | None = None) -> "WiFiInterface":
        """Factory selecting correct backend implementation."""
        import platform

        from .linux import LinuxWiFiInterface
        from .macos import MacOSWiFiInterface
        from .simulated import SimulatedWiFiInterface
        from .windows import WindowsWiFiInterface

        if name == "simulate":
            return SimulatedWiFiInterface(name)

        system = platform.system()
        if system == "Linux":
            interface = LinuxWiFiInterface(name)
        elif system == "Darwin":
            interface = MacOSWiFiInterface(name)
        elif system == "Windows":
            interface = WindowsWiFiInterface(name)
        else:
            raise InterfaceError(f"Unsupported platform: {system}")

        # Add CSI capture if backend specified
        if csi_backend:
            from .csi import CSICapableWiFiInterface, NexmonCSIBackend, Intel5300CSIBackend

            if csi_backend == "nexmon":
                csi = NexmonCSIBackend(name)
            elif csi_backend == "intel5300":
                csi = Intel5300CSIBackend(name)
            else:
                raise InterfaceError(f"Unknown CSI backend: {csi_backend}")
            return CSICapableWiFiInterface(interface, csi)

        return interface

