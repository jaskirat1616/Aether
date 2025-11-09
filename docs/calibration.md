# Calibration Workflow

1. Place reference device at known distances (1 m, 3 m, 5 m).
2. Run:

```bash
poetry run aether-calibrate --interface simulate --distance 3.0 --target 192.168.1.10
```

3. Engine updates internal baseline via `RangingEngine.calibrate`.
4. Export calibration profiles to `data/calibration/<environment>.json`.
5. Load profile with `Aether(environment="home")` (planned).

