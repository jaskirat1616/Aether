"""Spatial mapping utilities."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Iterable, List, Tuple

import networkx as nx
import numpy as np

from ..sense.models import RangeEstimate


@dataclass
class Anchor:
    device_id: str
    position: Tuple[float, float, float]


def trilaterate(anchors: Iterable[Anchor], ranges: Dict[str, RangeEstimate]) -> Tuple[float, float, float]:
    anchors = list(anchors)
    if len(anchors) < 3:
        raise ValueError("Need at least three anchors for trilateration")

    positions = np.array([anchor.position for anchor in anchors])
    distances = np.array([ranges[anchor.device_id].distance for anchor in anchors])

    A = []
    b = []
    for i in range(1, len(anchors)):
        p0 = positions[0]
        pi = positions[i]
        di = distances[i]
        d0 = distances[0]
        A.append(2 * (pi - p0))
        b.append(di**2 - d0**2 - np.dot(pi, pi) + np.dot(p0, p0))
    A = np.array(A)
    b = np.array(b)
    solution, *_ = np.linalg.lstsq(A, b, rcond=None)
    return tuple(solution.tolist())


def build_mesh_graph(devices: Iterable[str], pairwise_ranges: Dict[tuple[str, str], float]) -> nx.Graph:
    graph = nx.Graph()
    for device in devices:
        graph.add_node(device)
    for (a, b), distance in pairwise_ranges.items():
        graph.add_edge(a, b, weight=distance)
    return graph


def shortest_path(device_a: str, device_b: str, graph: nx.Graph) -> List[str]:
    return nx.shortest_path(graph, device_a, device_b, weight="weight")

