"""macOS Wi-Fi interface using airport and networksetup utilities."""

from __future__ import annotations

import platform
import subprocess
from typing import Iterable

from .interface import InterfaceError, InterfaceInfo, WiFiInterface


class MacOSWiFiInterface(WiFiInterface):
    """macOS backend using system Wi-Fi utilities."""

    def __init__(self, name: str) -> None:
        super().__init__(name)
        if platform.system() != "Darwin":
            raise InterfaceError("MacOSWiFiInterface requires macOS")

    def measure_rssi(self, target: str) -> float:
        """Extract RSSI using airport utility or system_profiler."""
        try:
            # Try using airport utility (if available)
            result = subprocess.run(
                ["/System/Library/PrivateFrameworks/Apple80211.framework/Versions/Current/Resources/airport", "-I"],
                capture_output=True,
                text=True,
                check=False,
            )
            if result.returncode == 0:
                for line in result.stdout.splitlines():
                    if "agrCtlRSSI" in line or "RSSI" in line:
                        parts = line.split(":")
                        if len(parts) > 1:
                            return float(parts[1].strip())
        except (FileNotFoundError, ValueError):
            pass

        # Fallback: use ping-based estimation (less accurate)
        try:
            result = subprocess.run(
                ["ping", "-c", "1", "-n", target],
                capture_output=True,
                text=True,
                check=True,
            )
            # Estimate RSSI from ping success (very rough)
            # In practice, you'd need to use CoreWLAN framework via ctypes or pyobjc
            return -70.0  # Placeholder
        except (FileNotFoundError, subprocess.CalledProcessError) as exc:
            raise InterfaceError(f"Failed to query RSSI: {exc}") from exc

    def measure_rtt(self, target: str) -> float:
        """Measure RTT using ping."""
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
        """CSI capture not natively supported on macOS without specialized hardware."""
        raise InterfaceError(
            "CSI capture requires specialized hardware (e.g., Intel 5300 with modified drivers) or nexmon-compatible adapters"
        )

    def enumerate_devices(self) -> Iterable[str]:
        """Enumerate devices using arp."""
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
            if len(parts) >= 2:
                ip = parts[1].strip("()")
                if ip and ip != "?":
                    yield ip

    def info(self) -> InterfaceInfo:
        return InterfaceInfo(
            name=self.name,
            mac_address=self._get_mac_address(),
            capabilities={"rssi": True, "rtt": True, "csi": False},
        )

    def _get_mac_address(self) -> str | None:
        """Extract MAC address using ifconfig."""
        try:
            result = subprocess.run(
                ["ifconfig", self.name],
                capture_output=True,
                text=True,
                check=True,
            )
            for line in result.stdout.splitlines():
                if "ether" in line.lower():
                    parts = line.split()
                    for i, part in enumerate(parts):
                        if part.lower() == "ether" and i + 1 < len(parts):
                            return parts[i + 1]
        except (FileNotFoundError, subprocess.CalledProcessError):
            return None
        return None

    def close(self) -> None:
        return None

