from pathlib import Path

from aether.sense.models import DeviceEstimate, RangeEstimate, SignalSample
from aether.viz.export import export_geojson
from aether.viz.plots import range_bar_chart
from datetime import datetime


def make_device(ip: str, distance: float) -> DeviceEstimate:
    sample = SignalSample(timestamp=datetime.utcnow(), method="rssi", value=distance, metadata={})
    estimate = RangeEstimate(
        timestamp=datetime.utcnow(), method="rssi", distance=distance, variance=0.1, raw=[sample]
    )
    return DeviceEstimate(ip=ip, estimate=estimate, metadata={})


def test_range_bar_chart_generates_figure():
    fig = range_bar_chart([make_device("192.168.1.10", 3.0)])
    assert fig.data


def test_export_geojson(tmp_path: Path):
    export_geojson(tmp_path / "devices.geojson", [make_device("192.168.1.10", 3.0)])
    assert (tmp_path / "devices.geojson").exists()

