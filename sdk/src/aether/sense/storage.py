"""Persistence utilities for signal samples."""

from __future__ import annotations

from pathlib import Path
from typing import Iterable

import duckdb
import pyarrow as pa
import pyarrow.parquet as pq

from .models import RangeEstimate, SignalSample


def samples_to_table(samples: Iterable[SignalSample]) -> pa.Table:
    rows = [
        {
            "timestamp": sample.timestamp,
            "method": sample.method,
            "value": sample.value,
            "metadata": sample.metadata,
        }
        for sample in samples
    ]
    return pa.Table.from_pylist(rows)


def write_samples_parquet(path: Path, samples: Iterable[SignalSample]) -> None:
    table = samples_to_table(samples)
    path.parent.mkdir(parents=True, exist_ok=True)
    pq.write_table(table, path)


def register_estimate(connection: duckdb.DuckDBPyConnection, estimate: RangeEstimate) -> None:
    connection.execute(
        """
        CREATE TABLE IF NOT EXISTS range_estimates (
            timestamp TIMESTAMP,
            method TEXT,
            distance DOUBLE,
            variance DOUBLE
        )
        """
    )
    connection.execute(
        "INSERT INTO range_estimates VALUES (?, ?, ?, ?)",
        [estimate.timestamp, estimate.method, estimate.distance, estimate.variance],
    )

