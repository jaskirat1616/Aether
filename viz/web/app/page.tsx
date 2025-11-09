"use client";

import useSWR from "swr";

const fetcher = (url: string) => fetch(url).then((res) => res.json());

export default function Dashboard() {
  const { data } = useSWR("/api/sample-devices", fetcher, { refreshInterval: 2000 });
  return (
    <main style={{ padding: "2rem" }}>
      <h1>Aether Live Ranging</h1>
      <table>
        <thead>
          <tr>
            <th>Device</th>
            <th>Distance (m)</th>
          </tr>
        </thead>
        <tbody>
          {(data?.devices ?? []).map((device: any) => (
            <tr key={device.ip}>
              <td>{device.ip}</td>
              <td>{device.distance?.toFixed(2) ?? "N/A"}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </main>
  );
}

