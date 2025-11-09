"""Linux Wi-Fi interface using iw and ping utilities."""

from __future__ import annotations

import subprocess
from typing import Iterable

from .interface import InterfaceError, InterfaceInfo, WiFiInterface


class LinuxWiFiInterface(WiFiInterface):
    """Basic Linux backend relying on system commands."""

    def measure_rssi(self, target: str) -> float:
        try:
            result = subprocess.run(
                ["iw", "dev", self.name, "station", "get", target],
                capture_output=True,
                text=True,
                check=True,
            )
        except FileNotFoundError as exc:
            raise InterfaceError("iw command not available") from exc
        except subprocess.CalledProcessError as exc:
            raise InterfaceError(f"Failed to query RSSI: {exc.stderr}") from exc

        for line in result.stdout.splitlines():
            line = line.strip()
            if line.startswith("signal:"):
                return float(line.split()[1])
        raise InterfaceError("RSSI signal not found in iw output")

    def measure_rtt(self, target: str) -> float:
        try:
            result = subprocess.run(
                ["ping", "-c", "1", "-n", target],
                capture_output=True,
                text=True,
                check=True,
            )
        except FileNotFoundError as exc:
            raise InterfaceError("ping command not available") from exc
        except subprocess.CalledProcessError as exc:
            raise InterfaceError(f"Failed to query RTT: {exc.stderr}") from exc

        for part in result.stdout.split():
            if part.startswith("time="):
                millis = float(part.removeprefix("time=").replace("ms", ""))
                return millis / 1000.0
        raise InterfaceError("RTT not found in ping output")

    def capture_csi(self, target: str) -> Iterable[list[complex]]:
        raise InterfaceError("CSI capture not supported on generic Linux backend")

    def enumerate_devices(self) -> Iterable[str]:
        try:
            result = subprocess.run(
                ["arp", "-a"],
                capture_output=True,
                text=True,
                check=True,
            )
        except subprocess.CalledProcessError as exc:
            raise InterfaceError(f"Failed to list devices: {exc.stderr}") from exc

        for line in result.stdout.splitlines():
            parts = line.split()
            if parts:
                yield parts[1].strip("()")

    def info(self) -> InterfaceInfo:
        return InterfaceInfo(name=self.name, capabilities={"rssi": True, "rtt": True, "csi": False})

    def close(self) -> None:
        return None

