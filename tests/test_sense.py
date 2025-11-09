from datetime import datetime

import duckdb

from aether.api import Aether
from aether.sense.storage import register_estimate, samples_to_table


def test_simulated_range_outputs():
    client = Aether(interface="simulate")
    estimate = client.range("192.168.1.10")
    assert estimate.distance > 0
    assert estimate.method in {"csi", "rtt", "rssi"}
    client.close()


def test_samples_to_table_roundtrip():
    client = Aether(interface="simulate")
    estimate = client.range("192.168.1.10", method="rssi")
    table = samples_to_table(estimate.raw)
    assert table.num_rows == len(estimate.raw)
    client.close()


def test_register_estimate_duckdb(tmp_path):
    client = Aether(interface="simulate")
    estimate = client.range("192.168.1.10", method="rtt")
    conn = duckdb.connect(str(tmp_path / "ranges.db"))
    register_estimate(conn, estimate)
    result = conn.execute("SELECT COUNT(*) FROM range_estimates").fetchone()
    assert result[0] == 1
    client.close()

