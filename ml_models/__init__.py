"""ML wrapper package.

Contains lightweight wrappers for model types (rainfall, flooding, cyclone).
Wrappers provide `load_model()`, `predict(features: Dict) -> Dict`, and
training helpers. They intentionally implement deterministic fallbacks so
the API can respond even if persisted model files are missing.
"""
