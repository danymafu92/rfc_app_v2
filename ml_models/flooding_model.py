"""Flooding model wrapper

This module exposes a `predict(features)` function that combines a small
machine-learning model (optional) with deterministic domain logic implemented
in `services.risk_calculator.RiskCalculator`.

Behavior notes for contributors/AI agents:
- The wrapper uses `RiskCalculator` to derive core risk metrics. Even when a
    persisted ML model is missing the API receives structured output because the
    deterministic calculator fills in values.
- The `predict()` method always returns a dict with keys:
    `flood_probability`, `risk_score`, `risk_category`, `mudslide_probability`,
    `water_level_meters`, `affected_area_km2`, `affected_population`, and
    `confidence_score` — keep this shape when modifying behavior.
"""

import numpy as np
import os
from typing import Dict, List
from services.risk_calculator import RiskCalculator


class FloodingPredictionModel:
    """Wrapper for flooding risk prediction.

    The model blends a separate RiskCalculator (deterministic) with an
    optional persisted ML classifier. The deterministic calculator is used to
    derive `flood_probability` and related metrics even when a trained model
    is not available.
    """

    def __init__(self, model_path: str = None):
        self.model = None
        self.model_path = model_path
        self.is_loaded = False
        self.risk_calculator = RiskCalculator()

    def load_model(self) -> bool:
        """Attempt to load a persisted classifier. Returns True on success."""
        if self.model_path and os.path.exists(self.model_path):
            try:
                import joblib
                self.model = joblib.load(self.model_path)
                self.is_loaded = True
                return True
            except Exception as e:
                print(f"Error loading model: {e}")
                return False
        return False

    def preprocess_data(self, features: Dict) -> np.ndarray:
        """Stable feature ordering for training/prediction."""
        feature_array = np.array([
            features.get('rainfall_mm', 0.0),
            features.get('infrastructure_strength', 5.0),
            features.get('soil_moisture_retention', 5.0),
            features.get('vegetation_density', 5.0),
            features.get('population_density', 100.0),
            features.get('elevation', 0.0),
            features.get('drainage_capacity', 5.0),
            features.get('historical_flood_count', 0.0),
        ]).reshape(1, -1)

        return feature_array

    def predict(self, features: Dict) -> Dict:
        """Return structured flooding prediction derived from risk calculator

        The method applies deterministic calculations for water level and
        affected area; if a persisted model exists it can be used (not required).
        """
        risk_result = self.risk_calculator.calculate_flooding_risk(
            predicted_rainfall_mm=features.get('rainfall_mm', 0.0),
            infrastructure_strength=features.get('infrastructure_strength', 5.0),
            soil_moisture_retention=features.get('soil_moisture_retention', 5.0),
            vegetation_density=features.get('vegetation_density', 5.0),
            population_density=features.get('population_density', 100.0)
        )

        # Simple domain rule: water level grows when rainfall exceeds threshold
        water_level = 0.0
        rainfall = features.get('rainfall_mm', 0.0)
        if rainfall > 25:
            drainage = features.get('drainage_capacity', 5.0)
            water_level = (rainfall - 25) * 0.05 * (10 - drainage) / 10

        # Compute affected area from flood probability
        affected_area = 0.0
        if risk_result['flood_probability'] > 0.3:
            base_area = features.get('base_area_km2', 10.0)
            affected_area = base_area * risk_result['flood_probability']

        affected_population = int(
            affected_area * features.get('population_density', 100.0)
        )

        confidence = 0.70 if self.is_loaded else 0.55

        return {
            'flood_probability': risk_result['flood_probability'],
            'risk_score': risk_result['risk_score'],
            'risk_category': risk_result['risk_category'],
            'mudslide_probability': risk_result['mudslide_probability'],
            'water_level_meters': round(water_level, 2),
            'affected_area_km2': round(affected_area, 2),
            'affected_population': affected_population,
            'confidence_score': confidence,
        }

    def train(self, training_data: List[Dict], labels: List[float]) -> Dict:
        """Train a classifier and optionally save it to `model_path`.

        Returns training metrics or an error dict.
        """
        try:
            from sklearn.ensemble import GradientBoostingClassifier
            from sklearn.model_selection import train_test_split
            from sklearn.metrics import accuracy_score
            import joblib

            X = np.array([self.preprocess_data(d).flatten() for d in training_data])
            y = np.array(labels)

            X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

            self.model = GradientBoostingClassifier(n_estimators=100, random_state=42)
            self.model.fit(X_train, y_train)

            predictions = self.model.predict(X_test)
            accuracy = accuracy_score(y_test, predictions)

            if self.model_path:
                joblib.dump(self.model, self.model_path)

            self.is_loaded = True

            return {
                'accuracy_score': float(accuracy),
                'training_samples': len(X_train),
                'test_samples': len(X_test),
            }
        except Exception as e:
            return {'error': str(e)}

    def update_model(self, new_data: List[Dict], new_labels: List[float]) -> Dict:
        """Retrain the model with new data (simple retrain implementation)."""
        if not self.is_loaded:
            return self.train(new_data, new_labels)

        return self.train(new_data, new_labels)
