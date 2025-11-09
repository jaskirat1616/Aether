"""Aether command-line interface."""

from __future__ import annotations

from typing import Optional

import typer

from .api import Aether

app = typer.Typer(help="Aether Wi-Fi ranging toolkit")


@app.command()
def range(
    interface: str = typer.Option(..., help="Wi-Fi interface identifier"),
    target: str = typer.Option(..., help="Target IP or MAC address"),
    method: str = typer.Option("auto", help="Ranging method"),
) -> None:
    client = Aether(interface=interface)
    estimate = client.range(target, method=method)
    typer.echo(f"Distance to {target}: {estimate.distance:.2f} m (method={estimate.method})")
    client.close()


@app.command()
def scan(
    interface: str = typer.Option(..., help="Wi-Fi interface identifier"),
) -> None:
    client = Aether(interface=interface)
    for record in client.scan():
        distance = f"{record.distance:.2f}" if record.distance is not None else "unknown"
        typer.echo(f"{record.ip}\t{distance} m")
    client.close()


@app.command()
def info(
    interface: str = typer.Option(..., help="Wi-Fi interface identifier"),
) -> None:
    client = Aether(interface=interface)
    info = client._iface.info()  # noqa: SLF001 (exposing low-level info)
    typer.echo(f"Interface: {info.name}")
    typer.echo(f"Capabilities: {info.capabilities}")
    client.close()

