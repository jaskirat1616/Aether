# Machine Learning Enhancements

- Synthetic dataset stored at `data/ml/synthetic.json`.
- Training pipeline: `python ml/pipelines/train_regressor.py --input data/ml/synthetic.json --output ml/models/range_gbm.joblib`.
- Runtime refinement via `aether.ml.model.MLRangeRefiner`.
- Deterministic fallback when model unavailable.

