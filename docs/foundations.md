# Foundations

## Hardware Support Matrix

| Platform | RSSI | RTT | CSI | Notes |
|----------|------|-----|-----|-------|
| Linux (iw + ping) | ✅ | ✅ | ⚠️ (requires Intel 5300 or Nexmon) | Default backend |
| macOS (CoreWLAN) | ✅ | ⚠️ (limited precision) | ❌ | Planned Phase 1.2 |
| Windows (Native Wi-Fi) | ✅ | ⚠️ (needs admin) | ❌ | Planned Phase 1.3 |
| Simulation (`interface=\"simulate\"`) | ✅ | ✅ | ✅ | Deterministic dev mode |

## Success Metrics

- Mean absolute ranging error ≤ 1.0 m at 5 m line-of-sight.
- P95 error ≤ 2.5 m in multipath indoor testbed.
- Topology reconstruction accuracy ≥ 90% when compared to ground truth meshes.
- SDK API latency ≤ 200 ms per range query in standard mode.

## Repository Scaffolding

- `sdk/` source tree with modular packages (`core`, `sense`, `mesh`, `ml`, `viz`).
- `services/` placeholder for FastAPI gateway.
- `ml/`, `viz/`, `docs/`, `tests/`, `scripts/`, `data/` directories prepared.
- `pyproject.toml` configured with Poetry and lint/test tooling.

