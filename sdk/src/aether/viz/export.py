"""Export utilities for spatial data."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Iterable

from ..mesh.trilateration import Anchor
from ..sense.models import DeviceEstimate


def export_geojson(path: Path, devices: Iterable[DeviceEstimate]) -> None:
    features = []
    for device in devices:
        features.append(
            {
                "type": "Feature",
                "properties": {"ip": device.ip, "distance": device.estimate.distance},
                "geometry": {
                    "type": "Point",
                    "coordinates": [
                        device.estimate.distance,
                        0,
                        0,
                    ],
                },
            }
        )
    payload = {"type": "FeatureCollection", "features": features}
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2))

