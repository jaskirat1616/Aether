from __future__ import annotations

from typing import Optional

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from pydantic import BaseModel

from aether.api import Aether

app = FastAPI(title="Aether API")


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
async def websocket_scan(ws: WebSocket, interface: str) -> None:
    await ws.accept()
    client: Optional[Aether] = None
    try:
        client = Aether(interface=interface)
        for record in client.scan():
            await ws.send_json({"ip": record.ip, "distance": record.distance})
    except WebSocketDisconnect:
        pass
    finally:
        if client:
            client.close()
        await ws.close()

