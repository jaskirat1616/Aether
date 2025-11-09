from __future__ import annotations

import json
from pathlib import Path

import joblib
import numpy as np
from sklearn.ensemble import GradientBoostingRegressor


def load_dataset(path: Path) -> tuple[np.ndarray, np.ndarray]:
    records = json.loads(path.read_text())
    X = []
    y = []
    for record in records:
        X.append(record["features"])
        y.append(record["distance"])
    return np.array(X), np.array(y)


def train(input_path: str, output_path: str) -> None:
    X, y = load_dataset(Path(input_path))
    model = GradientBoostingRegressor()
    model.fit(X, y)
    joblib.dump(model, output_path)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    train(args.input, args.output)

