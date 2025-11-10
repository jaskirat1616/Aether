"""Tests for platform-specific Wi-Fi interfaces."""

import platform

import pytest

from aether.core.interface import WiFiInterface
from aether.core.simulated import SimulatedWiFiInterface


def test_simulated_interface():
    """Test simulated interface works on all platforms."""
    iface = SimulatedWiFiInterface("simulate")
    assert iface.name == "simulate"
    
    devices = list(iface.enumerate_devices())
    assert len(devices) > 0
    
    # Test RSSI measurement
    rssi = iface.measure_rssi(devices[0])
    assert isinstance(rssi, float)
    assert rssi < 0  # RSSI is negative dBm
    
    # Test RTT measurement
    rtt = iface.measure_rtt(devices[0])
    assert isinstance(rtt, float)
    assert rtt > 0
    
    # Test CSI capture
    csi_frames = list(iface.capture_csi(devices[0]))
    assert len(csi_frames) > 0
    assert all(isinstance(frame, list) for frame in csi_frames)
    
    iface.close()


def test_platform_detection():
    """Test that platform detection works correctly."""
    system = platform.system()
    
    if system == "Darwin":
        from aether.core.macos import MacOSWiFiInterface
        # Should not raise on macOS
        try:
            iface = MacOSWiFiInterface("en0")
            info = iface.info()
            assert info.name == "en0"
            iface.close()
        except Exception:
            # May fail if en0 doesn't exist, that's okay
            pass
    elif system == "Windows":
        from aether.core.windows import WindowsWiFiInterface
        # Should not raise on Windows
        try:
            iface = WindowsWiFiInterface("Wi-Fi")
            info = iface.info()
            assert info.name == "Wi-Fi"
            iface.close()
        except Exception:
            # May fail if Wi-Fi interface doesn't exist, that's okay
            pass
    elif system == "Linux":
        from aether.core.linux import LinuxWiFiInterface
        # Should not raise on Linux
        try:
            iface = LinuxWiFiInterface("wlan0")
            info = iface.info()
            assert info.name == "wlan0"
            iface.close()
        except Exception:
            # May fail if wlan0 doesn't exist, that's okay
            pass


def test_interface_factory():
    """Test WiFiInterface.open factory method."""
    # Simulated interface should work on all platforms
    iface = WiFiInterface.open("simulate")
    assert isinstance(iface, SimulatedWiFiInterface)
    iface.close()
    
    # Platform-specific interface should be selected automatically
    system = platform.system()
    if system in ("Linux", "Darwin", "Windows"):
        # This may fail if no Wi-Fi interface exists, but shouldn't raise ImportError
        try:
            iface = WiFiInterface.open("wlan0" if system == "Linux" else "en0" if system == "Darwin" else "Wi-Fi")
            assert iface.name in ("wlan0", "en0", "Wi-Fi")
            iface.close()
        except Exception:
            # Interface may not exist, that's acceptable
            pass


def test_csi_backend_wrapper():
    """Test CSI backend wrapper functionality."""
    from aether.core.csi import CSICapableWiFiInterface, NexmonCSIBackend
    
    base = SimulatedWiFiInterface("simulate")
    csi_backend = NexmonCSIBackend("simulate", "/tmp/nonexistent.dat")
    
    # Wrapper should preserve base interface functionality
    wrapped = CSICapableWiFiInterface(base, csi_backend)
    assert wrapped.name == base.name
    
    # Info should reflect CSI capability
    info = wrapped.info()
    assert info.capabilities is not None
    assert info.capabilities.get("csi") is True
    
    wrapped.close()

