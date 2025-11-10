# Aether API Service

FastAPI service providing REST and WebSocket endpoints for Wi-Fi ranging.

## Running the Server

### Option 1: From project root (Recommended)

```bash
# From project root
cd /Users/jaskiratsingh/Desktop/Aether
poetry run uvicorn services.api.main:app --reload --port 8000
```

### Option 2: From services/api directory

```bash
cd services/api
poetry run uvicorn main:app --reload --port 8000
```

## Endpoints

### REST API

- `POST /range` - Get distance estimate for a target device
  ```json
  {
    "interface": "simulate",
    "target": "192.168.1.10",
    "method": "auto"
  }
  ```

- `GET /docs` - Interactive API documentation (Swagger UI)
- `GET /redoc` - Alternative API documentation

### WebSocket

- `WS /ws/scan` - Stream device scan results
  ```json
  {
    "interface": "simulate",
    "csi_backend": null
  }
  ```

## Testing

```bash
# Test REST endpoint
curl -X POST "http://localhost:8000/range" \
  -H "Content-Type: application/json" \
  -d '{"interface": "simulate", "target": "192.168.1.10", "method": "auto"}'

# Test WebSocket (use the test script)
cd ../..
poetry run python scripts/test_websocket.py
```

## Troubleshooting

**Error: "Could not import module 'main'"**
- Make sure you're using `poetry run` to run uvicorn
- Or run from project root: `poetry run uvicorn services.api.main:app --reload`

**Error: "ModuleNotFoundError: No module named 'aether'"**
- The SDK path is automatically added in `main.py`
- If issues persist, install the package: `poetry install` from project root

