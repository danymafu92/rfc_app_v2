"""Deterministic risk calculation utilities used by ML wrappers and views.

This module provides small, explainable heuristics used when ML models are
absent or to augment model outputs with domain metrics. The functions return
compact dicts with `risk_score`, `risk_category` and display helpers used by
the frontend.

Keep these heuristics stable: tests and ML wrapper fallbacks rely on their
return shapes and ranges.
"""

from typing import Dict

class RiskCalculator:
    @staticmethod
    def calculate_risk_category(risk_score: float) -> str:
        if risk_score <= 3.5:
            return 'Low'
        elif risk_score <= 7.4:
            return 'Medium'
        else:
            return 'High'

    @staticmethod
    def get_risk_color(risk_score: float) -> str:
        if risk_score <= 3.5:
            return '#22c55e'
        elif risk_score <= 7.4:
            return '#f59e0b'
        else:
            return '#ef4444'

    @staticmethod
    def calculate_flooding_risk(
        predicted_rainfall_mm: float,
        infrastructure_strength: float,
        soil_moisture_retention: float,
        vegetation_density: float,
        population_density: float
    ) -> Dict:
        # Normalize rainfall to [0,1] relative to a 100mm baseline; heavy
        # rainfall above the baseline is saturated at 1.0 for these heuristics.
        rainfall_factor = min(predicted_rainfall_mm / 100.0, 1.0)

        # Compute a vulnerability score from local parameters. The weights are
        # tuned heuristically and expected to be consistent with the ML wrapper
        # fallbacks used in `ml_models/flooding_model.py`.
        vulnerability_score = (
            (10 - infrastructure_strength) * 0.3 +
            (10 - soil_moisture_retention) * 0.25 +
            (10 - vegetation_density) * 0.2 +
            min(population_density / 1000, 10) * 0.25
        )
        # Flood probability blends intensity (rainfall) with vulnerability.
        flood_probability = min(rainfall_factor * (vulnerability_score / 10), 1.0)

        # Composite risk score that includes rainfall, vulnerability and
        # flood probability. The returned `risk_score` is clamped to [0,10].
        risk_score = (
            rainfall_factor * 4.0 +
            (10 - infrastructure_strength) * 0.3 +
            (10 - soil_moisture_retention) * 0.25 +
            (10 - vegetation_density) * 0.2 +
            flood_probability * 2.5
        )

        risk_score = min(risk_score, 10.0)

        # Mudslide probability is only modeled when rainfall exceeds 50mm; the
        # formula uses terrain and vegetation (inverted) to estimate likelihood.
        mudslide_probability = 0.0
        if predicted_rainfall_mm > 50:
            mudslide_probability = min(
                (predicted_rainfall_mm - 50) / 150.0 *
                (10 - soil_moisture_retention) / 10.0 *
                (10 - vegetation_density) / 10.0,
                1.0
            )

        return {
            'risk_score': round(risk_score, 2),
            'risk_category': RiskCalculator.calculate_risk_category(risk_score),
            'flood_probability': round(flood_probability, 2),
            'mudslide_probability': round(mudslide_probability, 2),
            'risk_color': RiskCalculator.get_risk_color(risk_score)
        }

    @staticmethod
    def calculate_cyclone_risk(
        wind_speed_kmh: float,
        category: int,
        distance_km: float,
        infrastructure_strength: float,
        population_size: int
    ) -> Dict:
        wind_factor = min(wind_speed_kmh / 250.0, 1.0)

        category_weight = category / 5.0

        distance_factor = max(1.0 - (distance_km / 500.0), 0.0)

        infrastructure_vulnerability = (10 - infrastructure_strength) / 10.0

        population_factor = min(population_size / 1000000, 1.0)

        risk_score = (
            wind_factor * 3.0 +
            category_weight * 3.5 +
            distance_factor * 2.0 +
            infrastructure_vulnerability * 1.0 +
            population_factor * 0.5
        )

        risk_score = min(risk_score, 10.0)

        return {
            'risk_score': round(risk_score, 2),
            'risk_category': RiskCalculator.calculate_risk_category(risk_score),
            'risk_color': RiskCalculator.get_risk_color(risk_score)
        }

    @staticmethod
    def calculate_rainfall_intensity(rainfall_mm: float) -> str:
        if rainfall_mm < 2.5:
            return 'Light'
        elif rainfall_mm < 10:
            return 'Moderate'
        elif rainfall_mm < 50:
            return 'Heavy'
        else:
            return 'Extreme'
