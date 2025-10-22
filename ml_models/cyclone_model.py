"""Cyclone model wrapper

Provides a deterministic prediction interface for cyclone characteristics
and risk estimates. The wrapper uses a RiskCalculator for risk scoring and
generates a synthetic track if no model exists.

Important contributor notes:
- `_generate_path()` creates a simple linearized path (6-hour steps) used as
    a placeholder when no trained model is loaded. Tests and UI expect a list
    of coordinate dicts with `latitude`, `longitude`, and `timestamp` keys.
- `predict()` must include `risk_score` and `risk_category` computed via
    `services.risk_calculator.RiskCalculator` to integrate with the UI.
"""

import numpy as np
import os
from typing import Dict, List
from services.risk_calculator import RiskCalculator


class CyclonePredictionModel:
    """Wrapper for cyclone/hurricane prediction logic.

    The implementation intentionally produces a plausible, deterministic
    result even without a trained model: it calculates category from wind
    speed, generates a simple forward path and delegates risk scoring to the
    RiskCalculator used across the project.
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
            features.get('sea_surface_temp', 27.0),
            features.get('wind_speed', 50.0),
            features.get('pressure', 1000.0),
            features.get('humidity', 80.0),
            features.get('wind_shear', 5.0),
            features.get('latitude', 15.0),
            features.get('longitude', 120.0),
        ]).reshape(1, -1)

        return feature_array

    def predict(self, features: Dict) -> Dict:
        """Return a dictionary describing cyclone characteristics and risk."""
        wind_speed = features.get('wind_speed', 50.0)
        pressure = features.get('pressure', 1000.0)

        # Simple deterministic category mapping (using mph thresholds)
        category = self._calculate_category(wind_speed)

        # Generate a synthetic path: every 6 hours for 72 hours
        path_coords = self._generate_path(
            features.get('latitude', 15.0),
            features.get('longitude', 120.0),
            features.get('direction', 270.0),
            features.get('speed_kmh', 20.0)
        )

        affected_locations = features.get('affected_location_ids', [])

        risk_result = self.risk_calculator.calculate_cyclone_risk(
            wind_speed_kmh=wind_speed,
            category=category,
            distance_km=features.get('distance_km', 100.0),
            infrastructure_strength=features.get('infrastructure_strength', 5.0),
            population_size=features.get('population_size', 100000)
        )

        confidence = 0.65 if self.is_loaded else 0.50

        return {
            'category': category,
            'max_wind_speed_kmh': round(wind_speed, 2),
            'central_pressure_hpa': round(pressure, 2),
            'path_coordinates': path_coords,
            'affected_locations': affected_locations,
            'risk_score': risk_result['risk_score'],
            'risk_category': risk_result['risk_category'],
            'confidence_score': confidence,
        }

    def _calculate_category(self, wind_speed_kmh: float) -> int:
        """Map wind speed (km/h) to an integer category (0-5) using mph cutoffs."""
        wind_speed_mph = wind_speed_kmh * 0.621371

        if wind_speed_mph < 74:
            return 0
        elif wind_speed_mph < 96:
            return 1
        elif wind_speed_mph < 111:
            return 2
        elif wind_speed_mph < 130:
            return 3
        elif wind_speed_mph < 157:
            return 4
        else:
            return 5

    def _generate_path(
        self,
        start_lat: float,
        start_lon: float,
        direction: float,
        speed_kmh: float,
        hours: int = 72
    ) -> List[Dict]:
        """Generate a simple linearly propagated path for the cyclone.

        This is a lightweight deterministic approximation used when no model
        is available; each step is 6 hours apart.
        """
        path = []
        current_lat = start_lat
        current_lon = start_lon

        for hour in range(0, hours, 6):
            path.append({
                'latitude': round(current_lat, 4),
                'longitude': round(current_lon, 4),
                'timestamp': hour
            })

            # Convert travel distance to degrees (approx): 1 degree ~= 111 km
            distance_km = speed_kmh * 6
            distance_deg = distance_km / 111.0

            current_lat += distance_deg * np.cos(np.radians(direction))
            current_lon += distance_deg * np.sin(np.radians(direction))

            # Slight random walk to mimic natural path variation
            direction += np.random.uniform(-15, 15)

        return path

    def train(self, training_data: List[Dict], labels: List[int]) -> Dict:
        """Train a RandomForest classifier and optionally persist it to disk."""
        try:
            from sklearn.ensemble import RandomForestClassifier
            from sklearn.model_selection import train_test_split
            from sklearn.metrics import accuracy_score
            import joblib

            X = np.array([self.preprocess_data(d).flatten() for d in training_data])
            y = np.array(labels)

            X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

            self.model = RandomForestClassifier(n_estimators=100, random_state=42, n_jobs=-1)
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

    def update_model(self, new_data: List[Dict], new_labels: List[int]) -> Dict:
        if not self.is_loaded:
            return self.train(new_data, new_labels)

        return self.train(new_data, new_labels)
