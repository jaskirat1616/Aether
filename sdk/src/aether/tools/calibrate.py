"""Calibration helper CLI."""

from __future__ import annotations

import json
from pathlib import Path

import typer

from ..api import Aether

app = typer.Typer()


@app.command()
def calibrate(
    interface: str = typer.Option(..., help="Interface name"),
    target: str = typer.Option(..., help="Target IP or MAC"),
    distance: float = typer.Option(..., help="Reference distance in meters"),
    environment: str = typer.Option("default", help="Environment profile name"),
    output: Path = typer.Option(Path("data/calibration/profile.json"), help="Output profile path"),
) -> None:
    client = Aether(interface)
    estimate = client.range(target)
    client.close()
    profile = {
        "environment": environment,
        "reference_distance": distance,
        "observed_distance": estimate.distance,
        "method": estimate.method,
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(profile, indent=2))
    typer.echo(f"Wrote calibration profile to {output}")


def main() -> None:
    app()


if __name__ == "__main__":
    main()

