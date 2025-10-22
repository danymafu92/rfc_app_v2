"""Serializers for API models and input validation.

Contains ModelSerializers for DB-backed models (Location, Predictions, etc.)
and a small `RiskCalculationInputSerializer` used by flooding prediction POSTs.
"""

from rest_framework import serializers
from .models import (
    Location, UserPreference, LocationParameter,
    RainfallPrediction, FloodingPrediction, CyclonePrediction,
    WeatherData, MLModelMetadata
)

class LocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Location
        fields = '__all__'


class LocationParameterSerializer(serializers.ModelSerializer):
    class Meta:
        model = LocationParameter
        fields = '__all__'


class UserPreferenceSerializer(serializers.ModelSerializer):
    default_location_details = LocationSerializer(source='default_location', read_only=True)

    class Meta:
        model = UserPreference
        fields = '__all__'


class RainfallPredictionSerializer(serializers.ModelSerializer):
    location_details = LocationSerializer(source='location', read_only=True)

    class Meta:
        model = RainfallPrediction
        fields = '__all__'


class FloodingPredictionSerializer(serializers.ModelSerializer):
    location_details = LocationSerializer(source='location', read_only=True)

    class Meta:
        model = FloodingPrediction
        fields = '__all__'


class CyclonePredictionSerializer(serializers.ModelSerializer):
    class Meta:
        model = CyclonePrediction
        fields = '__all__'


class WeatherDataSerializer(serializers.ModelSerializer):
    location_details = LocationSerializer(source='location', read_only=True)

    class Meta:
        model = WeatherData
        fields = '__all__'


class MLModelMetadataSerializer(serializers.ModelSerializer):
    class Meta:
        model = MLModelMetadata
        fields = '__all__'


class RiskCalculationInputSerializer(serializers.Serializer):
    location_id = serializers.UUIDField()
    infrastructure_strength = serializers.DecimalField(max_digits=3, decimal_places=2, min_value=0, max_value=10)
    soil_moisture_retention = serializers.DecimalField(max_digits=3, decimal_places=2, min_value=0, max_value=10)
    soil_type = serializers.CharField(max_length=100)
    vegetation_density = serializers.DecimalField(max_digits=3, decimal_places=2, min_value=0, max_value=10)
    population_size = serializers.IntegerField(min_value=0)
    population_density = serializers.DecimalField(max_digits=10, decimal_places=2, min_value=0)
    predicted_rainfall_mm = serializers.DecimalField(max_digits=10, decimal_places=2)

# This serializer validates the flooding prediction input payload accepted
# by `FloodingPredictionViewSet.predict`. Keep the field names and types in
# sync with the view's features mapping.
