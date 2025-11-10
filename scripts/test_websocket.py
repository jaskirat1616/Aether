#!/usr/bin/env python3
"""Test script for WebSocket endpoint."""

import asyncio
import json
import sys
from typing import Optional

try:
    import websockets
except ImportError:
    print("Error: websockets package not installed")
    print("Install with: poetry add websockets")
    sys.exit(1)


async def test_websocket(uri: str = "ws://localhost:8000/ws/scan", interface: str = "simulate"):
    """Test WebSocket connection and data streaming."""
    print(f"Connecting to {uri}...")
    
    try:
        async with websockets.connect(uri) as websocket:
            print("✅ Connected!")
            
            # Send configuration
            config = {
                "interface": interface,
                "csi_backend": None
            }
            print(f"Sending config: {json.dumps(config)}")
            await websocket.send(json.dumps(config))
            
            # Receive updates
            print("\nReceiving device updates (press Ctrl+C to stop):\n")
            count = 0
            devices_seen = set()
            
            try:
                async for message in websocket:
                    data = json.loads(message)
                    
                    if "error" in data:
                        print(f"❌ Error: {data['error']}")
                        break
                    
                    ip = data.get("ip")
                    distance = data.get("distance")
                    method = data.get("method", "unknown")
                    timestamp = data.get("timestamp", "")
                    
                    if ip not in devices_seen:
                        devices_seen.add(ip)
                        print(f"📡 New device: {ip}")
                    
                    print(f"  {ip}: {distance:.2f}m ({method}) - {timestamp}")
                    count += 1
                    
                    # Stop after 20 updates
                    if count >= 20:
                        print(f"\n✅ Received {count} updates from {len(devices_seen)} devices")
                        break
                        
            except KeyboardInterrupt:
                print(f"\n\n✅ Test completed. Received {count} updates from {len(devices_seen)} devices")
                
    except websockets.exceptions.ConnectionRefused:
        print("❌ Connection refused. Is the FastAPI server running?")
        print("   Start with: cd services/api && poetry run uvicorn main:app --reload")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Test Aether WebSocket endpoint")
    parser.add_argument("--url", default="ws://localhost:8000/ws/scan", help="WebSocket URL")
    parser.add_argument("--interface", default="simulate", help="Wi-Fi interface name")
    
    args = parser.parse_args()
    
    asyncio.run(test_websocket(args.url, args.interface))

