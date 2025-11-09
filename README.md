# Aether

Aether is a Python SDK and research framework for Wi-Fi-based ranging, spatial awareness, and mesh intelligence. It measures distances and relative device positions without extra sensors by leveraging RSSI, RTT, and CSI metrics.

## Repository Layout

- `sdk/` – Core Python SDK source (`AetherCore`, `AetherSense`, `AetherMesh`, `AetherML`, `AetherViz`)
- `services/` – FastAPI gateway, WebSocket relay, and backend jobs
- `ml/` – Training pipelines, datasets, and exported models
- `viz/` – Visualization components, dashboards, and web client
- `docs/` – Technical documentation, calibration guides, architecture notes
- `tests/` – Unit, integration, and hardware-in-the-loop suites
- `scripts/` – Developer utilities and data conversion helpers
- `data/` – Sample capture logs and synthetic datasets

## Getting Started

```bash
poetry install
poetry run pytest
```

See `docs/` for detailed usage, architecture, and deployment instructions.

