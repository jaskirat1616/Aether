# Testing Guide

This guide covers how to test all components of the Aether Wi-Fi ranging system.

## Prerequisites

1. Python 3.10+ with Poetry installed
2. Node.js 18+ and npm (for dashboard testing)
3. Git repository cloned

## 1. Unit Tests (Python SDK)

### Run All Tests

```bash
# From project root
poetry run pytest tests/ -v
```

### Run Specific Test Suites

```bash
# Test signal collection and ranging
poetry run pytest tests/test_sense.py -v

# Test ranging engine and fusion
poetry run pytest tests/test_engine.py -v

# Test spatial mapping
poetry run pytest tests/test_mesh.py -v

# Test visualization
poetry run pytest tests/test_viz.py -v

# Test platform backends
poetry run pytest tests/test_platforms.py -v
```

### Run with Coverage

```bash
poetry run pytest tests/ --cov=sdk/src/aether --cov-report=html
```

## 2. Testing the Python SDK Directly

### Basic Usage Test

```python
from aether import Aether

# Use simulated interface (works on all platforms)
a = Aether(interface="simulate")

# Measure distance to a device
estimate = a.range("192.168.1.10")
print(f"Distance: {estimate.distance:.2f}m")
print(f"Method: {estimate.method}")
print(f"Variance: {estimate.variance:.4f}")

# Scan all devices
for device in a.scan():
    print(f"{device.ip}: {device.distance:.2f}m")

a.close()
```

### Test Different Methods

```python
from aether import Aether

a = Aether(interface="simulate")

# Test RSSI method
rssi_estimate = a.range("192.168.1.10", method="rssi")
print(f"RSSI: {rssi_estimate.distance:.2f}m")

# Test RTT method
rtt_estimate = a.range("192.168.1.10", method="rtt")
print(f"RTT: {rtt_estimate.distance:.2f}m")

# Test CSI method (simulated)
csi_estimate = a.range("192.168.1.10", method="csi")
print(f"CSI: {csi_estimate.distance:.2f}m")

a.close()
```

### Test Platform-Specific Backends

#### macOS
```python
from aether import Aether

# Auto-detects macOS and uses MacOSWiFiInterface
a = Aether(interface="en0")  # or your Wi-Fi interface name
info = a._iface.info()
print(f"Interface: {info.name}")
print(f"Capabilities: {info.capabilities}")

# Test scanning
for device in a.scan():
    print(f"{device.ip}: {device.distance}m")

a.close()
```

#### Windows
```python
from aether import Aether

# Auto-detects Windows and uses WindowsWiFiInterface
a = Aether(interface="Wi-Fi")  # or your Wi-Fi interface name
info = a._iface.info()
print(f"Interface: {info.name}")

for device in a.scan():
    print(f"{device.ip}: {device.distance}m")

a.close()
```

#### Linux
```python
from aether import Aether

# Auto-detects Linux and uses LinuxWiFiInterface
a = Aether(interface="wlan0")  # or your Wi-Fi interface name
info = a._iface.info()
print(f"Interface: {info.name}")

for device in a.scan():
    print(f"{device.ip}: {device.distance}m")

a.close()
```

## 3. Testing the CLI

### Install CLI

```bash
poetry install
```

### Test CLI Commands

```bash
# Range a specific device
poetry run aether range --interface simulate --target 192.168.1.10

# Scan all devices
poetry run aether scan --interface simulate

# Get interface info
poetry run aether info --interface simulate
```

## 4. Testing the FastAPI Service

### Start the API Server

```bash
# From project root
cd services/api
poetry run uvicorn main:app --reload --port 8000
```

The API will be available at `http://localhost:8000`

### Test REST Endpoint

```bash
# Test range endpoint
curl -X POST "http://localhost:8000/range" \
  -H "Content-Type: application/json" \
  -d '{
    "interface": "simulate",
    "target": "192.168.1.10",
    "method": "auto"
  }'
```

Expected response:
```json
{
  "distance": 2.5,
  "method": "rssi",
  "variance": 0.1
}
```

### Test WebSocket Endpoint

#### Using Python

```python
import asyncio
import websockets
import json

async def test_websocket():
    uri = "ws://localhost:8000/ws/scan"
    async with websockets.connect(uri) as websocket:
        # Send configuration
        await websocket.send(json.dumps({
            "interface": "simulate",
            "csi_backend": None
        }))
        
        # Receive updates
        for i in range(10):
            message = await websocket.recv()
            data = json.loads(message)
            print(f"Device {data['ip']}: {data['distance']:.2f}m")

asyncio.run(test_websocket())
```

#### Using JavaScript (Node.js)

```javascript
const WebSocket = require('ws');

const ws = new WebSocket('ws://localhost:8000/ws/scan');

ws.on('open', () => {
  console.log('Connected');
  ws.send(JSON.stringify({
    interface: 'simulate',
    csi_backend: null
  }));
});

ws.on('message', (data) => {
  const message = JSON.parse(data.toString());
  console.log(`Device ${message.ip}: ${message.distance}m`);
});

ws.on('error', (error) => {
  console.error('Error:', error);
});
```

#### Using Browser Console

```javascript
const ws = new WebSocket('ws://localhost:8000/ws/scan');

ws.onopen = () => {
  ws.send(JSON.stringify({
    interface: 'simulate',
    csi_backend: null
  }));
};

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log(`Device ${data.ip}: ${data.distance}m`);
};
```

## 5. Testing the Next.js Dashboard

### Install Dependencies

```bash
cd viz/web
npm install
```

### Start Development Server

```bash
npm run dev
```

The dashboard will be available at `http://localhost:3000`

### Test Dashboard Features

1. **Connection Status**: Check the green/red indicator in the top-left
2. **Live Updates**: Devices should appear and update every 2 seconds
3. **Reconnection**: Disconnect the FastAPI server and watch it reconnect
4. **Error Handling**: Stop the API server to see error messages

### Configure WebSocket URL

Create `.env.local` file:

```bash
NEXT_PUBLIC_WS_URL=ws://localhost:8000/ws/scan
```

## 6. End-to-End Testing

### Full Stack Test

1. **Terminal 1**: Start FastAPI service
```bash
cd services/api
poetry run uvicorn main:app --reload --port 8000
```

2. **Terminal 2**: Start Next.js dashboard
```bash
cd viz/web
npm run dev
```

3. **Terminal 3**: Run Python tests
```bash
poetry run pytest tests/ -v
```

4. **Browser**: Open `http://localhost:3000` and verify:
   - Connection indicator is green
   - Devices appear in the table
   - Distances update in real-time
   - Method and timestamp columns populate

## 7. Testing with Real Hardware

### Find Your Wi-Fi Interface

#### macOS
```bash
ifconfig | grep "inet " | grep -v 127.0.0.1
networksetup -listallhardwareports | grep -A 1 "Wi-Fi"
```

#### Linux
```bash
iwconfig
ip link show
```

#### Windows
```powershell
netsh wlan show interfaces
```

### Test with Real Interface

```python
from aether import Aether

# Replace with your actual interface name
a = Aether(interface="wlan0")  # Linux
# a = Aether(interface="en0")   # macOS
# a = Aether(interface="Wi-Fi") # Windows

# Scan real devices on your network
for device in a.scan():
    print(f"{device.ip}: {device.distance:.2f}m (method: {device.metadata.get('method')})")

a.close()
```

### Test CSI Capture (Requires Special Hardware)

```python
from aether import Aether

# For nexmon (Linux with Broadcom chipset)
a = Aether(interface="wlan0", csi_backend="nexmon")

# For Intel 5300 (Linux with modified driver)
# a = Aether(interface="wlan0", csi_backend="intel5300")

estimate = a.range("192.168.1.10", method="csi")
print(f"CSI Distance: {estimate.distance:.2f}m")

a.close()
```

## 8. Performance Testing

### Benchmark Range Operations

```python
import time
from aether import Aether

a = Aether(interface="simulate")

methods = ["rssi", "rtt", "csi"]
target = "192.168.1.10"

for method in methods:
    times = []
    for _ in range(100):
        start = time.time()
        estimate = a.range(target, method=method)
        times.append(time.time() - start)
    
    avg_time = sum(times) / len(times)
    print(f"{method}: {avg_time*1000:.2f}ms average")

a.close()
```

## 9. Troubleshooting

### Common Issues

1. **"iw command not available"** (Linux)
   - Install: `sudo apt-get install iw` (Debian/Ubuntu)
   - Or use simulated interface: `interface="simulate"`

2. **"ping command not available"**
   - Ensure ping is installed and in PATH
   - On Windows, ping should be available by default

3. **WebSocket connection fails**
   - Ensure FastAPI server is running on port 8000
   - Check CORS settings in `services/api/main.py`
   - Verify firewall isn't blocking port 8000

4. **No devices found**
   - Check network connectivity
   - Verify interface name is correct
   - Try simulated interface first: `interface="simulate"`

5. **CSI capture fails**
   - CSI requires specialized hardware (nexmon or Intel 5300)
   - Use simulated interface for testing: `interface="simulate"`

### Debug Mode

Enable verbose logging:

```python
import logging
logging.basicConfig(level=logging.DEBUG)

from aether import Aether
a = Aether(interface="simulate")
```

## 10. Continuous Integration

Run all tests in CI:

```bash
# Install dependencies
poetry install

# Run tests
poetry run pytest tests/ -v --cov=sdk/src/aether

# Check code quality
poetry run ruff check sdk/
poetry run mypy sdk/
```

## Quick Test Checklist

- [ ] Python tests pass: `poetry run pytest tests/ -v`
- [ ] CLI works: `poetry run aether scan --interface simulate`
- [ ] FastAPI starts: `poetry run uvicorn services.api.main:app`
- [ ] REST endpoint responds: `curl http://localhost:8000/docs`
- [ ] WebSocket connects: Use Python/JavaScript test script
- [ ] Dashboard loads: `npm run dev` and open `http://localhost:3000`
- [ ] Dashboard shows devices: Check table updates
- [ ] Reconnection works: Stop/start API server

