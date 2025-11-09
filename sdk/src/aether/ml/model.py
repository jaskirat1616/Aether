"""Machine learning enhancements for range estimation."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Optional

import joblib
import numpy as np

from ..sense.models import RangeEstimate, SignalSample


@dataclass
class MLConfig:
    model_path: Optional[Path] = None


class MLRangeRefiner:
    """Apply ML regression to refine distance estimates."""

    def __init__(self, config: Optional[MLConfig] = None) -> None:
        self._config = config or MLConfig()
        self._model = None
        if self._config.model_path and self._config.model_path.exists():
            self._model = joblib.load(self._config.model_path)

    def refine(self, estimate: RangeEstimate) -> RangeEstimate:
        if self._model is None:
            return estimate
        features = self._extract_features(estimate.raw)
        distance = float(self._model.predict([features])[0])
        return RangeEstimate(
            timestamp=estimate.timestamp,
            method="ml",
            distance=distance,
            variance=estimate.variance,
            raw=estimate.raw,
        )

    def _extract_features(self, samples: Iterable[SignalSample]) -> list[float]:
        values = np.array([sample.value for sample in samples])
        return [
            float(values.mean()),
            float(values.std()),
            float(values.min()),
            float(values.max()),
        ]

