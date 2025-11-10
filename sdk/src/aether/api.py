"""High-level SDK entrypoints."""

from __future__ import annotations

from contextlib import AbstractContextManager
from dataclasses import dataclass
from typing import Any, Iterable, Optional

from .core.interface import WiFiInterface
from .sense.collectors import CollectorConfig, SignalCollector
from .sense.models import RangeEstimate


@dataclass
class DeviceRecord:
    ip: str
    distance: Optional[float]
    metadata: dict[str, Any]


class Aether:
    """Primary synchronous API surface."""

    def __init__(
        self,
        interface: str,
        collector_config: Optional[CollectorConfig] = None,
        csi_backend: Optional[str] = None,
    ) -> None:
        self._iface = WiFiInterface.open(interface, csi_backend=csi_backend)
        self._collector = SignalCollector(self._iface, collector_config)

    def range(self, target: str, method: str = "auto") -> RangeEstimate:
        """Estimate distance to ``target`` using chosen method."""
        return self._collector.estimate_range(target, method=method)

    def scan(self) -> Iterable[DeviceRecord]:
        """Discover reachable devices and provide coarse range estimates."""
        for record in self._collector.enumerate_devices():
            metadata = dict(record.metadata)
            metadata["method"] = record.estimate.method
            yield DeviceRecord(
                ip=record.ip,
                distance=record.estimate.distance,
                metadata=metadata,
            )

    def close(self) -> None:
        self._collector.close()
        self._iface.close()


class AetherSession(AbstractContextManager["AetherSession"]):
    """Context managed variant of :class:`Aether`."""

    def __init__(
        self,
        interface: str,
        collector_config: Optional[CollectorConfig] = None,
        csi_backend: Optional[str] = None,
    ) -> None:
        self._aether = Aether(interface=interface, collector_config=collector_config, csi_backend=csi_backend)

    def __enter__(self) -> "AetherSession":
        return self

    def __exit__(self, *exc: Any) -> Optional[bool]:
        self.close()
        return None

    @property
    def api(self) -> Aether:
        return self._aether

    def range(self, target: str, method: str = "auto") -> RangeEstimate:
        return self._aether.range(target, method=method)

    def scan(self) -> Iterable[DeviceRecord]:
        return self._aether.scan()

    def close(self) -> None:
        self._aether.close()

