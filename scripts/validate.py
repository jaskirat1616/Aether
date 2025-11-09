from __future__ import annotations

import argparse
import json
from pathlib import Path

import duckdb

from aether.api import Aether
from aether.sense.storage import register_estimate


def main() -> None:
    parser = argparse.ArgumentParser(description="Validation harness")
    parser.add_argument("--interface", required=True)
    parser.add_argument("--targets", required=True, help="JSON file with target list")
    parser.add_argument("--database", default="data/validation/runs.duckdb")
    args = parser.parse_args()

    targets = json.loads(Path(args.targets).read_text())
    client = Aether(interface=args.interface)

    db_path = Path(args.database)
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = duckdb.connect(str(db_path))

    for target in targets:
        estimate = client.range(target["ip"], method=target.get("method", "auto"))
        register_estimate(conn, estimate)

    client.close()
    conn.close()


if __name__ == "__main__":
    main()

