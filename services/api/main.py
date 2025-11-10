from __future__ import annotations

import sys
from datetime import datetime
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# Add SDK to path if running from services/api directory
sdk_path = Path(__file__).parent.parent.parent / "sdk" / "src"
if str(sdk_path) not in sys.path:
    sys.path.insert(0, str(sdk_path))

from aether.api import Aether

app = FastAPI(title="Aether API")

# Enable CORS for Next.js frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class RangeRequest(BaseModel):
    interface: str
    target: str
    method: str = "auto"


class RangeResponse(BaseModel):
    distance: float
    method: str
    variance: float


@app.post("/range", response_model=RangeResponse)
def range_endpoint(payload: RangeRequest) -> RangeResponse:
    client = Aether(interface=payload.interface)
    estimate = client.range(payload.target, method=payload.method)
    client.close()
    return RangeResponse(distance=estimate.distance, method=estimate.method, variance=estimate.variance)


@app.websocket("/ws/scan")
async def websocket_scan(ws: WebSocket) -> None:
    await ws.accept()
    client: Optional[Aether] = None
    try:
        # Receive initial configuration
        config = await ws.receive_json()
        interface = config.get("interface", "simulate")
        csi_backend = config.get("csi_backend")
        
        client = Aether(interface=interface, csi_backend=csi_backend)
        
        # Continuously scan and send updates
        import asyncio
        while True:
            for record in client.scan():
                await ws.send_json({
                    "ip": record.ip,
                    "distance": record.distance,
                    "method": record.metadata.get("method", "unknown"),
                    "timestamp": datetime.utcnow().isoformat(),
                })
            await asyncio.sleep(2)  # Scan interval
    except WebSocketDisconnect:
        pass
    except Exception as e:
        await ws.send_json({"error": str(e)})
    finally:
        if client:
            client.close()
        try:
            await ws.close()
        except Exception:
            pass

