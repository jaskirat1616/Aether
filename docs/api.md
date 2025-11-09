# API and Tooling

## CLI

- `aether range --interface simulate --target 192.168.1.10`
- `aether scan --interface simulate`
- `aether info --interface wlan0`
- `aether-calibrate --interface simulate --target 192.168.1.10 --distance 3.0`

## REST

POST `/range`

```json
{
  "interface": "simulate",
  "target": "192.168.1.10",
  "method": "auto"
}
```

Response:

```json
{
  "distance": 3.4,
  "method": "rtt",
  "variance": 0.1
}
```

## WebSocket

Connect to `/ws/scan?interface=simulate` to stream nearby device ranges.

