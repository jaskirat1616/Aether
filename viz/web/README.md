# Aether Dashboard

Real-time Wi-Fi ranging visualization dashboard built with Next.js.

## Features

- Live WebSocket streaming of device distances
- Real-time connection status monitoring
- Automatic reconnection on disconnect
- Device method tracking (RSSI, RTT, CSI)
- Timestamp tracking for each measurement

## Setup

1. Install dependencies:
```bash
npm install
```

2. Configure WebSocket URL (optional):
```bash
cp .env.example .env.local
# Edit .env.local to set NEXT_PUBLIC_WS_URL if needed
```

3. Start the development server:
```bash
npm run dev
```

4. Ensure the Aether FastAPI service is running on port 8000:
```bash
cd ../../services/api
uvicorn main:app --reload
```

## Usage

Open [http://localhost:3000](http://localhost:3000) in your browser. The dashboard will automatically connect to the WebSocket endpoint and start streaming device distance data.

## Configuration

The dashboard connects to the WebSocket endpoint specified in `NEXT_PUBLIC_WS_URL` (defaults to `ws://localhost:8000/ws/scan`). It sends an initial configuration message:

```json
{
  "interface": "simulate",
  "csi_backend": null
}
```

You can modify the interface name or CSI backend as needed for your setup.

