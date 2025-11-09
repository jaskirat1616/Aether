"""Visualization helpers."""

from __future__ import annotations

from typing import Iterable

import plotly.graph_objects as go

from ..sense.models import DeviceEstimate


def range_bar_chart(estimates: Iterable[DeviceEstimate]) -> go.Figure:
    ips = []
    distances = []
    for record in estimates:
        ips.append(record.ip)
        distances.append(record.estimate.distance)
    fig = go.Figure(go.Bar(x=ips, y=distances))
    fig.update_layout(title="Device Distances", xaxis_title="Device", yaxis_title="Distance (m)")
    return fig

