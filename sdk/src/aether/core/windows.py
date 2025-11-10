"""Windows Wi-Fi interface using netsh and ping utilities."""

from __future__ import annotations

import platform
import subprocess
import re
from typing import Iterable

from .interface import InterfaceError, InterfaceInfo, WiFiInterface


class WindowsWiFiInterface(WiFiInterface):
    """Windows backend using netsh and system commands."""

    def __init__(self, name: str) -> None:
        super().__init__(name)
        if platform.system() != "Windows":
            raise InterfaceError("WindowsWiFiInterface requires Windows")

    def measure_rssi(self, target: str) -> float:
        """Extract RSSI using netsh wlan show interfaces."""
        try:
            result = subprocess.run(
                ["netsh", "wlan", "show", "interfaces"],
                capture_output=True,
                text=True,
                check=True,
                shell=True,
            )
            for line in result.stdout.splitlines():
                if "Signal" in line and "%" in line:
                    # Extract percentage and convert to dBm approximation
                    match = re.search(r"(\d+)%", line)
                    if match:
                        percentage = int(match.group(1))
                        # Rough conversion: 100% = -30 dBm, 0% = -100 dBm
                        return -30.0 - (100 - percentage) * 0.7
        except (FileNotFoundError, subprocess.CalledProcessError) as exc:
            raise InterfaceError(f"Failed to query RSSI: {exc}") from exc

        # Fallback placeholder
        return -70.0

    def measure_rtt(self, target: str) -> float:
        """Measure RTT using ping."""
        try:
            result = subprocess.run(
                ["ping", "-n", "1", target],
                capture_output=True,
                text=True,
                check=True,
                shell=True,
            )
        except FileNotFoundError as exc:
            raise InterfaceError("ping command not available") from exc
        except subprocess.CalledProcessError as exc:
            raise InterfaceError(f"Failed to query RTT: {exc.stderr}") from exc

        # Windows ping output format: "time=XXms" or "time<1ms"
        match = re.search(r"time[<=](\d+)ms", result.stdout)
        if match:
            millis = float(match.group(1))
            return millis / 1000.0
        raise InterfaceError("RTT not found in ping output")

    def capture_csi(self, target: str) -> Iterable[list[complex]]:
        """CSI capture not natively supported on Windows without specialized hardware."""
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
                shell=True,
            )
        except subprocess.CalledProcessError as exc:
            raise InterfaceError(f"Failed to list devices: {exc.stderr}") from exc

        # Windows arp format: "192.168.1.1    00-11-22-33-44-55    dynamic"
        for line in result.stdout.splitlines():
            parts = line.split()
            if len(parts) >= 1:
                ip = parts[0]
                # Validate IP format
                if re.match(r"^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$", ip):
                    yield ip

    def info(self) -> InterfaceInfo:
        return InterfaceInfo(
            name=self.name,
            mac_address=self._get_mac_address(),
            capabilities={"rssi": True, "rtt": True, "csi": False},
        )

    def _get_mac_address(self) -> str | None:
        """Extract MAC address using ipconfig."""
        try:
            result = subprocess.run(
                ["ipconfig", "/all"],
                capture_output=True,
                text=True,
                check=True,
                shell=True,
            )
            # Look for the interface name and extract Physical Address
            in_interface = False
            for line in result.stdout.splitlines():
                if self.name.lower() in line.lower() or "Wireless" in line:
                    in_interface = True
                if in_interface and "Physical Address" in line:
                    match = re.search(r":\s*([0-9A-Fa-f-]{17})", line)
                    if match:
                        return match.group(1)
                    if ":" in line:
                        parts = line.split(":")
                        if len(parts) > 1:
                            return parts[1].strip()
        except (FileNotFoundError, subprocess.CalledProcessError):
            return None
        return None

    def close(self) -> None:
        return None

