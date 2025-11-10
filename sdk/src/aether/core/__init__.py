"""Wi-Fi interface backends for different platforms."""

from .interface import InterfaceError, InterfaceInfo, WiFiInterface
from .linux import LinuxWiFiInterface
from .macos import MacOSWiFiInterface
from .simulated import SimulatedWiFiInterface
from .windows import WindowsWiFiInterface

__all__ = [
    "WiFiInterface",
    "InterfaceError",
    "InterfaceInfo",
    "LinuxWiFiInterface",
    "MacOSWiFiInterface",
    "WindowsWiFiInterface",
    "SimulatedWiFiInterface",
]

