"use client";

import { useEffect, useState, useRef } from "react";

interface DeviceData {
  ip: string;
  distance: number | null;
  method?: string;
  timestamp?: string;
}

export default function Dashboard() {
  const [devices, setDevices] = useState<Map<string, DeviceData>>(new Map());
  const [connected, setConnected] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const wsRef = useRef<WebSocket | null>(null);
  const reconnectTimeoutRef = useRef<NodeJS.Timeout | null>(null);

  useEffect(() => {
    const connectWebSocket = () => {
      // Default to simulate interface for demo
      const wsUrl = process.env.NEXT_PUBLIC_WS_URL || "ws://localhost:8000/ws/scan";
      const ws = new WebSocket(wsUrl);

      ws.onopen = () => {
        console.log("WebSocket connected");
        setConnected(true);
        setError(null);
        // Send initial configuration
        ws.send(JSON.stringify({
          interface: "simulate",
          csi_backend: null,
        }));
      };

      ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          
          if (data.error) {
            setError(data.error);
            return;
          }

          // Update device data
          setDevices((prev) => {
            const updated = new Map(prev);
            updated.set(data.ip, {
              ip: data.ip,
              distance: data.distance,
              method: data.method,
              timestamp: data.timestamp,
            });
            return updated;
          });
        } catch (err) {
          console.error("Failed to parse WebSocket message:", err);
        }
      };

      ws.onerror = (err) => {
        console.error("WebSocket error:", err);
        setError("WebSocket connection error");
        setConnected(false);
      };

      ws.onclose = () => {
        console.log("WebSocket disconnected");
        setConnected(false);
        // Attempt to reconnect after 3 seconds
        reconnectTimeoutRef.current = setTimeout(() => {
          connectWebSocket();
        }, 3000);
      };

      wsRef.current = ws;
    };

    connectWebSocket();

    return () => {
      if (reconnectTimeoutRef.current) {
        clearTimeout(reconnectTimeoutRef.current);
      }
      if (wsRef.current) {
        wsRef.current.close();
      }
    };
  }, []);

  const deviceArray = Array.from(devices.values());

  return (
    <main style={{ padding: "2rem", fontFamily: "system-ui, sans-serif" }}>
      <div style={{ marginBottom: "2rem" }}>
        <h1 style={{ margin: 0, marginBottom: "0.5rem" }}>Aether Live Ranging</h1>
        <div style={{ display: "flex", gap: "1rem", alignItems: "center" }}>
          <span
            style={{
              display: "inline-block",
              width: "12px",
              height: "12px",
              borderRadius: "50%",
              backgroundColor: connected ? "#22c55e" : "#ef4444",
            }}
          />
          <span style={{ color: connected ? "#22c55e" : "#ef4444", fontWeight: 500 }}>
            {connected ? "Connected" : "Disconnected"}
          </span>
        </div>
        {error && (
          <div style={{ marginTop: "1rem", padding: "0.75rem", backgroundColor: "#fee2e2", color: "#991b1b", borderRadius: "0.5rem" }}>
            Error: {error}
          </div>
        )}
      </div>

      {deviceArray.length === 0 ? (
        <div style={{ padding: "2rem", textAlign: "center", color: "#6b7280" }}>
          {connected ? "Scanning for devices..." : "Connecting to Aether API..."}
        </div>
      ) : (
        <div style={{ overflowX: "auto" }}>
          <table
            style={{
              width: "100%",
              borderCollapse: "collapse",
              backgroundColor: "white",
              borderRadius: "0.5rem",
              overflow: "hidden",
              boxShadow: "0 1px 3px rgba(0,0,0,0.1)",
            }}
          >
            <thead>
              <tr style={{ backgroundColor: "#f3f4f6" }}>
                <th style={{ padding: "0.75rem", textAlign: "left", fontWeight: 600 }}>Device IP</th>
                <th style={{ padding: "0.75rem", textAlign: "left", fontWeight: 600 }}>Distance (m)</th>
                <th style={{ padding: "0.75rem", textAlign: "left", fontWeight: 600 }}>Method</th>
                <th style={{ padding: "0.75rem", textAlign: "left", fontWeight: 600 }}>Last Update</th>
              </tr>
            </thead>
            <tbody>
              {deviceArray.map((device) => (
                <tr
                  key={device.ip}
                  style={{
                    borderTop: "1px solid #e5e7eb",
                    transition: "background-color 0.2s",
                  }}
                  onMouseEnter={(e) => {
                    e.currentTarget.style.backgroundColor = "#f9fafb";
                  }}
                  onMouseLeave={(e) => {
                    e.currentTarget.style.backgroundColor = "white";
                  }}
                >
                  <td style={{ padding: "0.75rem", fontFamily: "monospace" }}>{device.ip}</td>
                  <td style={{ padding: "0.75rem", fontWeight: 500 }}>
                    {device.distance !== null ? device.distance.toFixed(2) : "N/A"}
                  </td>
                  <td style={{ padding: "0.75rem", textTransform: "uppercase", fontSize: "0.875rem", color: "#6b7280" }}>
                    {device.method || "unknown"}
                  </td>
                  <td style={{ padding: "0.75rem", fontSize: "0.875rem", color: "#6b7280" }}>
                    {device.timestamp
                      ? new Date(device.timestamp).toLocaleTimeString()
                      : "—"}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      <div style={{ marginTop: "2rem", padding: "1rem", backgroundColor: "#f9fafb", borderRadius: "0.5rem", fontSize: "0.875rem", color: "#6b7280" }}>
        <strong>Total devices:</strong> {deviceArray.length} |{" "}
        <strong>Status:</strong> {connected ? "Streaming live data" : "Waiting for connection"}
      </div>
    </main>
  );
}
