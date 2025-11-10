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

### Quick Start

```bash
# Install dependencies
poetry install

# Run tests
poetry run pytest tests/ -v

# Or use the test script
./scripts/test_all.sh
```

### Test the SDK

```python
from aether import Aether

# Use simulated interface (works everywhere)
a = Aether(interface="simulate")
estimate = a.range("192.168.1.10")
print(f"Distance: {estimate.distance:.2f}m")
a.close()
```

### Test the API

```bash
# Terminal 1: Start API server
cd services/api
poetry run uvicorn main:app --reload --port 8000

# Terminal 2: Test WebSocket
cd ../..
poetry run python scripts/test_websocket.py
```

### Test the Dashboard

```bash
# Terminal 1: Start API (as above)

# Terminal 2: Start dashboard
cd viz/web
npm install
npm run dev

# Open http://localhost:3000 in your browser
```

## Testing

See [`docs/testing.md`](docs/testing.md) for comprehensive testing guide covering:
- Unit tests
- Platform-specific backends
- WebSocket streaming
- End-to-end testing
- Real hardware testing

