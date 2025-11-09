import networkx as nx

from aether.mesh.tracking import ConstantVelocityFilter
from aether.mesh.trilateration import Anchor, build_mesh_graph, shortest_path, trilaterate
from aether.sense.models import RangeEstimate, SignalSample
from datetime import datetime


def make_range(distance: float) -> RangeEstimate:
    sample = SignalSample(timestamp=datetime.utcnow(), method="rssi", value=distance, metadata={})
    return RangeEstimate(timestamp=datetime.utcnow(), method="rssi", distance=distance, variance=0.1, raw=[sample])


def test_trilateration_three_anchors():
    anchors = [
        Anchor("a", (0.0, 0.0, 0.0)),
        Anchor("b", (5.0, 0.0, 0.0)),
        Anchor("c", (0.0, 5.0, 0.0)),
    ]
    ranges = {"a": make_range(3.0), "b": make_range(4.0), "c": make_range(4.0)}
    position = trilaterate(anchors, ranges)
    assert len(position) == 3


def test_build_mesh_and_shortest_path():
    graph = build_mesh_graph(
        ["a", "b", "c"],
        {("a", "b"): 2.0, ("b", "c"): 2.0, ("a", "c"): 5.0},
    )
    path = shortest_path("a", "c", graph)
    assert path == ["a", "b", "c"]


def test_constant_velocity_filter():
    filter = ConstantVelocityFilter()
    filter.initialize((0.0, 0.0, 0.0))
    filter.predict()
    filter.update((1.0, 0.0, 0.0))
    state = filter.get_state()
    assert state is not None
    assert state.position[0] >= 0.0

