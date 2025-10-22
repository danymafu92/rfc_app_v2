"""Rainfall model wrapper

Wrapper around a persisted scikit-learn model (RandomForest regressor).
Provides safe `load_model()` and `predict()` methods and deterministic
fallback predictions when the persisted model is missing or fails. Used by
`api.views.RainfallPredictionViewSet` to generate rainfall forecasts.

Notes for contributors/AI agents:
- `load_model()` is best-effort: it returns False on failure but does not
    raise. This pattern keeps the API endpoints resilient when model files are
    absent in development or CI environments.
- `predict()` must return a dict with `predicted_rainfall_mm`,
    `confidence_score`, and `intensity` — the views expect these keys.
"""

import numpy as np
import os
from typing import Dict, List


class RainfallPredictionModel:
    """Wrapper for a RandomForest-based rainfall regressor.

    Notes:
    - If `model_path` does not exist or load fails, `is_loaded` remains False and
      `predict()` returns a deterministic fallback (based on humidity/pressure/cloud_cover).
    - `preprocess_data()` ensures a stable feature ordering used during training.
    """

    def __init__(self, model_path: str = None):
        self.model = None
        self.model_path = model_path
        self.is_loaded = False

    def load_model(self) -> bool:
        """Attempt to load the model from disk using joblib.

        Returns True on success, False on failure. Does not raise.
        """
        if self.model_path and os.path.exists(self.model_path):
            try:
                import joblib
                self.model = joblib.load(self.model_path)
                self.is_loaded = True
                return True
            except Exception as e:
                # Print for local debugging; production should capture this in logs
                # Keep behavior non-failing so the API can use the fallback.
                print(f"Error loading model: {e}")
                return False
        return False

    def preprocess_data(self, features: Dict) -> np.ndarray:
        """Convert a feature dict to a numpy array in a stable order.

        Missing features are filled with sensible defaults to avoid KeyError.
        """
        feature_array = np.array([
            features.get('temperature', 25.0),
            features.get('humidity', 60.0),
            features.get('pressure', 1013.0),
            features.get('wind_speed', 10.0),
            features.get('cloud_cover', 50.0),
            features.get('historical_avg_rainfall', 0.0),
        ]).reshape(1, -1)

        return feature_array

    def predict(self, features: Dict) -> Dict:
        """Return a prediction dict.

        If the model is not loaded or prediction fails, fall back to
        `_fallback_prediction()` which returns a basic heuristic.
        """
        if not self.is_loaded:
            return self._fallback_prediction(features)

        try:
            X = self.preprocess_data(features)
            prediction = self.model.predict(X)[0]

            confidence = 0.75

            return {
                'predicted_rainfall_mm': max(float(prediction), 0.0),
                'confidence_score': confidence,
                'intensity': self._calculate_intensity(prediction),
            }
        except Exception as e:
            # Any runtime error during prediction falls back to heuristic
            print(f"Prediction error: {e}")
            return self._fallback_prediction(features)

    def _fallback_prediction(self, features: Dict) -> Dict:
        """Deterministic heuristic used when model is unavailable.

        Simple rules based on humidity, pressure and cloud cover to compute a
        coarse rainfall estimate and an associated low confidence score.
        """
        humidity = features.get('humidity', 60.0)
        pressure = features.get('pressure', 1013.0)
        cloud_cover = features.get('cloud_cover', 50.0)

        rainfall = 0.0
        # Basic heuristic: only predict rainfall when conditions indicate risk
        if humidity > 70 and pressure < 1010 and cloud_cover > 60:
            rainfall = (humidity - 70) * 0.5 + (1010 - pressure) * 2 + (cloud_cover - 60) * 0.3
            rainfall = max(0, rainfall)

        return {
            'predicted_rainfall_mm': round(rainfall, 2),
            'confidence_score': 0.50,
            'intensity': self._calculate_intensity(rainfall),
        }

    def _calculate_intensity(self, rainfall_mm: float) -> str:
        """Map rainfall amount to a human-readable intensity string."""
        if rainfall_mm < 2.5:
            return 'Light'
        elif rainfall_mm < 10:
            return 'Moderate'
        elif rainfall_mm < 50:
            return 'Heavy'
        else:
            return 'Extreme'

    def train(self, training_data: List[Dict], labels: List[float]) -> Dict:
        """Train a RandomForest regressor and optionally persist it to `model_path`.

        Returns performance metrics on a hold-out test set or an error dict.
        """
        try:
            from sklearn.ensemble import RandomForestRegressor
            from sklearn.model_selection import train_test_split
            from sklearn.metrics import mean_squared_error, mean_absolute_error
            import joblib

            X = np.array([self.preprocess_data(d).flatten() for d in training_data])
            y = np.array(labels)

            X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

            self.model = RandomForestRegressor(n_estimators=100, random_state=42, n_jobs=-1)
            self.model.fit(X_train, y_train)

            predictions = self.model.predict(X_test)
            rmse = np.sqrt(mean_squared_error(y_test, predictions))
            mae = mean_absolute_error(y_test, predictions)

            if self.model_path:
                joblib.dump(self.model, self.model_path)

            self.is_loaded = True

            return {
                'rmse': float(rmse),
                'mae': float(mae),
                'accuracy_score': float(1.0 - (rmse / (np.max(y_test) - np.min(y_test) + 0.001))),
                'training_samples': len(X_train),
                'test_samples': len(X_test),
            }
        except Exception as e:
            return {'error': str(e)}

    def update_model(self, new_data: List[Dict], new_labels: List[float]) -> Dict:
        """Update (retrain) the model with new examples.

        For simplicity this implementation retrains from scratch.
        """
        if not self.is_loaded:
            return self.train(new_data, new_labels)

        return self.train(new_data, new_labels)
