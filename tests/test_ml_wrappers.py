"""Unit tests validating ML wrapper fallback behavior.

These tests exercise the wrapper `predict()` methods to ensure the code
returns structured dicts even when no persisted model is loaded. They are
fast, pure-Python checks suitable for CI smoke tests.
"""

import unittest
from ml_models.rainfall_model import RainfallPredictionModel
from ml_models.flooding_model import FloodingPredictionModel
from ml_models.cyclone_model import CyclonePredictionModel


class TestMLWrappersFallbacks(unittest.TestCase):
    def test_rainfall_fallback_low_conditions(self):
        model = RainfallPredictionModel()
        # not loading any model -> fallback
        features = {'humidity': 80.0, 'pressure': 1005.0, 'cloud_cover': 70.0}
        pred = model.predict(features)
        self.assertIn('predicted_rainfall_mm', pred)
        self.assertGreaterEqual(pred['predicted_rainfall_mm'], 0.0)
        self.assertIn(pred['intensity'], ['Light', 'Moderate', 'Heavy', 'Extreme'])

    def test_rainfall_fallback_no_rain(self):
        model = RainfallPredictionModel()
        features = {'humidity': 50.0, 'pressure': 1015.0, 'cloud_cover': 20.0}
        pred = model.predict(features)
        # conditions not met -> expect 0 rainfall
        self.assertEqual(pred['predicted_rainfall_mm'], 0.0)
        self.assertEqual(pred['intensity'], 'Light')

    def test_flooding_prediction_basic(self):
        model = FloodingPredictionModel()
        features = {
            'rainfall_mm': 30.0,
            'infrastructure_strength': 4.0,
            'soil_moisture_retention': 4.0,
            'vegetation_density': 4.0,
            'population_density': 200.0,
            'base_area_km2': 20.0,
        }
        pred = model.predict(features)
        self.assertIn('flood_probability', pred)
        self.assertIn('risk_score', pred)
        self.assertIn('affected_area_km2', pred)
        self.assertGreaterEqual(pred['affected_area_km2'], 0.0)

    def test_cyclone_prediction_basic(self):
        model = CyclonePredictionModel()
        features = {'wind_speed': 150.0, 'pressure': 980.0, 'latitude': 10.0, 'longitude': 120.0}
        pred = model.predict(features)
        self.assertIn('category', pred)
        self.assertIn('path_coordinates', pred)
        self.assertIsInstance(pred['path_coordinates'], list)
        self.assertGreaterEqual(pred['max_wind_speed_kmh'], 0.0)


if __name__ == '__main__':
    unittest.main()
