"""URL routing for the API app.

Registers ViewSets with a DRF DefaultRouter. The router exposes the
endpoints used by the frontend under `/api/` (the project `urls.py`
includes this module).
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    LocationViewSet, UserPreferenceViewSet,
    RainfallPredictionViewSet, FloodingPredictionViewSet,
    CyclonePredictionViewSet, WeatherDataViewSet,
    MLModelMetadataViewSet
)

router = DefaultRouter()
router.register(r'locations', LocationViewSet, basename='location')
router.register(r'user-preferences', UserPreferenceViewSet, basename='user-preference')
router.register(r'rainfall-predictions', RainfallPredictionViewSet, basename='rainfall-prediction')
router.register(r'flooding-predictions', FloodingPredictionViewSet, basename='flooding-prediction')
router.register(r'cyclone-predictions', CyclonePredictionViewSet, basename='cyclone-prediction')
router.register(r'weather-data', WeatherDataViewSet, basename='weather-data')
router.register(r'ml-models', MLModelMetadataViewSet, basename='ml-model')

urlpatterns = [
    path('', include(router.urls)),
]
