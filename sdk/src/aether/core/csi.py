"""CSI capture backend for specialized hardware (nexmon, Intel 5300, etc.)."""

from __future__ import annotations

import os
import struct
from typing import Iterable

from .interface import InterfaceError, WiFiInterface


class CSICaptureInterface:
    """Base class for CSI capture backends."""

    def capture_csi_raw(self, target: str) -> Iterable[bytes]:
        """Yield raw CSI data frames."""
        raise NotImplementedError


class NexmonCSIBackend(CSICaptureInterface):
    """Nexmon-based CSI capture for Broadcom chipsets."""

    def __init__(self, interface: str, csi_path: str = "/tmp/csi.dat") -> None:
        self._interface = interface
        self._csi_path = csi_path
        self._file_handle = None

    def capture_csi_raw(self, target: str) -> Iterable[bytes]:
        """Read CSI data from nexmon log file."""
        if not os.path.exists(self._csi_path):
            raise InterfaceError(f"CSI log file not found: {self._csi_path}. Ensure nexmon is running.")

        try:
            with open(self._csi_path, "rb") as f:
                while True:
                    # Read nexmon CSI frame format (simplified)
                    # Actual format depends on nexmon version
                    header = f.read(8)
                    if len(header) < 8:
                        break
                    frame_len = struct.unpack("<I", header[4:8])[0]
                    frame_data = f.read(frame_len)
                    if len(frame_data) < frame_len:
                        break
                    yield header + frame_data
        except IOError as exc:
            raise InterfaceError(f"Failed to read CSI data: {exc}") from exc


class Intel5300CSIBackend(CSICaptureInterface):
    """Intel 5300 CSI capture backend (requires modified driver)."""

    def __init__(self, interface: str, log_path: str = "/tmp/csi.log") -> None:
        self._interface = interface
        self._log_path = log_path

    def capture_csi_raw(self, target: str) -> Iterable[bytes]:
        """Read CSI data from Intel 5300 log file."""
        if not os.path.exists(self._log_path):
            raise InterfaceError(f"CSI log file not found: {self._log_path}. Ensure Intel 5300 CSI tools are running.")

        try:
            with open(self._log_path, "rb") as f:
                while True:
                    # Intel 5300 CSI format (simplified)
                    header = f.read(12)
                    if len(header) < 12:
                        break
                    csi_len = struct.unpack("<I", header[8:12])[0]
                    csi_data = f.read(csi_len)
                    if len(csi_data) < csi_len:
                        break
                    yield header + csi_data
        except IOError as exc:
            raise InterfaceError(f"Failed to read CSI data: {exc}") from exc


def parse_csi_frame(frame_data: bytes) -> list[complex]:
    """Parse raw CSI frame into complex subcarrier values."""
    # Placeholder implementation - actual parsing depends on hardware format
    # This would need to be customized for each CSI backend
    subcarriers = 30
    result = []
    offset = 0
    for i in range(subcarriers):
        if offset + 8 <= len(frame_data):
            real = struct.unpack("<f", frame_data[offset : offset + 4])[0]
            imag = struct.unpack("<f", frame_data[offset + 4 : offset + 8])[0]
            result.append(complex(real, imag))
            offset += 8
        else:
            break
    return result if result else [complex(0, 0) for _ in range(subcarriers)]


class CSICapableWiFiInterface(WiFiInterface):
    """Wrapper that adds CSI capture to an existing WiFiInterface."""

    def __init__(self, base_interface: WiFiInterface, csi_backend: CSICaptureInterface | None = None) -> None:
        super().__init__(base_interface.name)
        self._base = base_interface
        self._csi_backend = csi_backend

    def measure_rssi(self, target: str) -> float:
        return self._base.measure_rssi(target)

    def measure_rtt(self, target: str) -> float:
        return self._base.measure_rtt(target)

    def capture_csi(self, target: str) -> Iterable[list[complex]]:
        if self._csi_backend is None:
            raise InterfaceError("CSI backend not configured")
        for frame in self._csi_backend.capture_csi_raw(target):
            yield parse_csi_frame(frame)

    def enumerate_devices(self) -> Iterable[str]:
        return self._base.enumerate_devices()

    def info(self) -> InterfaceInfo:
        info = self._base.info()
        if info.capabilities:
            info.capabilities["csi"] = self._csi_backend is not None
        return info

    def close(self) -> None:
        self._base.close()

