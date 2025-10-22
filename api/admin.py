"""Admin site registrations for API models.

Registers read-only-friendly admin views for Location, Predictions and
MLModelMetadata. Models are marked `managed = False` so admin is primarily
for inspection rather than schema management.
"""

from django.contrib import admin
from .models import (
    Location, UserPreference, LocationParameter,
    RainfallPrediction, FloodingPrediction, CyclonePrediction,
    WeatherData, MLModelMetadata
)

@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    list_display = ['country', 'region', 'city', 'latitude', 'longitude', 'is_active']
    list_filter = ['is_active', 'country']
    search_fields = ['country', 'region', 'city']


@admin.register(UserPreference)
class UserPreferenceAdmin(admin.ModelAdmin):
    list_display = ['user_id', 'default_location', 'created_at']


@admin.register(LocationParameter)
class LocationParameterAdmin(admin.ModelAdmin):
    list_display = ['location', 'infrastructure_strength', 'soil_moisture_retention', 'vegetation_density']


@admin.register(RainfallPrediction)
class RainfallPredictionAdmin(admin.ModelAdmin):
    list_display = ['location', 'prediction_date', 'predicted_rainfall_mm', 'intensity', 'is_historical']
    list_filter = ['is_historical', 'intensity']
    date_hierarchy = 'prediction_date'


@admin.register(FloodingPrediction)
class FloodingPredictionAdmin(admin.ModelAdmin):
    list_display = ['location', 'prediction_date', 'risk_score', 'risk_category', 'is_historical']
    list_filter = ['is_historical', 'risk_category']
    date_hierarchy = 'prediction_date'


@admin.register(CyclonePrediction)
class CyclonePredictionAdmin(admin.ModelAdmin):
    list_display = ['cyclone_name', 'prediction_date', 'category', 'risk_score', 'risk_category']
    list_filter = ['category', 'risk_category']
    date_hierarchy = 'prediction_date'


@admin.register(WeatherData)
class WeatherDataAdmin(admin.ModelAdmin):
    list_display = ['location', 'recorded_date', 'temperature_celsius', 'rainfall_mm', 'humidity_percent']
    date_hierarchy = 'recorded_date'


@admin.register(MLModelMetadata)
class MLModelMetadataAdmin(admin.ModelAdmin):
    list_display = ['model_type', 'version', 'accuracy_score', 'is_active', 'training_date']
    list_filter = ['model_type', 'is_active']
