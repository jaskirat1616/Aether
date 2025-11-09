from datetime import datetime

from aether.ml.model import MLRangeRefiner, MLConfig
from aether.sense.engine import RangingEngine
from aether.sense.models import RangeEstimate, SignalSample


def make_estimate(distance: float, variance: float) -> RangeEstimate:
    sample = SignalSample(timestamp=datetime.utcnow(), method="rssi", value=distance, metadata={})
    return RangeEstimate(
        timestamp=datetime.utcnow(),
        method="rssi",
        distance=distance,
        variance=variance,
        raw=[sample],
    )


def test_engine_fuses_estimates():
    engine = RangingEngine(environment="home")
    fused = engine.fuse([make_estimate(3.0, 0.2), make_estimate(4.0, 0.3)])
    assert 3.0 < fused.distance < 4.0
    assert fused.method == "fusion"


def test_engine_calibration_updates_state():
    engine = RangingEngine()
    engine.calibrate(2.5)
    fused = engine.fuse([make_estimate(3.0, 0.5)])
    assert abs(fused.distance - 2.5) < 1.0


def test_ml_refiner_falls_back(tmp_path):
    estimate = make_estimate(3.0, 0.2)
    refiner = MLRangeRefiner()
    refined = refiner.refine(estimate)
    assert refined.distance == estimate.distance

