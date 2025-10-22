"""API viewsets and actions for prediction and data endpoints.

This module defines the Django REST Framework ViewSets used under `/api`:
- LocationViewSet (read-only + parameters action)
- UserPreferenceViewSet (CRUD for user prefs)
- RainfallPredictionViewSet / FloodingPredictionViewSet / CyclonePredictionViewSet
- WeatherDataViewSet, MLModelMetadataViewSet

ViewSets rely on ML wrapper classes in `ml_models/` and helper services in
`services/` to fetch weather data and compute predictions.
"""

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.conf import settings
from datetime import datetime

from .models import (
    Location, UserPreference, LocationParameter,
    RainfallPrediction, FloodingPrediction, CyclonePrediction,
    WeatherData, MLModelMetadata
)
from .serializers import (
    LocationSerializer, UserPreferenceSerializer, LocationParameterSerializer,
    RainfallPredictionSerializer, FloodingPredictionSerializer, CyclonePredictionSerializer,
    WeatherDataSerializer, MLModelMetadataSerializer, RiskCalculationInputSerializer
)
from services.open_meteo import OpenMeteoService
from ml_models.rainfall_model import RainfallPredictionModel
from ml_models.flooding_model import FloodingPredictionModel
from ml_models.cyclone_model import CyclonePredictionModel


class LocationViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Location.objects.filter(is_active=True)
    serializer_class = LocationSerializer
    # Locations are public (default locations stored in the DB). AllowAny
    # makes it possible for the frontend to fetch the list without a
    # logged-in Supabase session. Individual parameter details remain
    # accessible to anonymous users as well; tighten if needed.
    permission_classes = [AllowAny]

    @action(detail=True, methods=['get'])
    def parameters(self, request, pk=None):
        location = self.get_object()
        try:
            params = LocationParameter.objects.get(location=location)
            serializer = LocationParameterSerializer(params)
            return Response(serializer.data)
        except LocationParameter.DoesNotExist:
            return Response({'error': 'Parameters not found'}, status=status.HTTP_404_NOT_FOUND)


class UserPreferenceViewSet(viewsets.ModelViewSet):
    serializer_class = UserPreferenceSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return UserPreference.objects.filter(user_id=self.request.user.id)

    def perform_create(self, serializer):
        serializer.save(user_id=self.request.user.id)


class RainfallPredictionViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = RainfallPredictionSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = RainfallPrediction.objects.all()
        location_id = self.request.query_params.get('location_id')
        start_date = self.request.query_params.get('start_date')
        end_date = self.request.query_params.get('end_date')
        is_historical = self.request.query_params.get('is_historical')

        if location_id:
            queryset = queryset.filter(location_id=location_id)
        if start_date:
            queryset = queryset.filter(prediction_date__gte=start_date)
        if end_date:
            queryset = queryset.filter(prediction_date__lte=end_date)
        if is_historical is not None:
            queryset = queryset.filter(is_historical=is_historical.lower() == 'true')

        return queryset

    @action(detail=False, methods=['post'])
    def predict(self, request):
        location_id = request.data.get('location_id')

        try:
            location = Location.objects.get(id=location_id)
        except Location.DoesNotExist:
            return Response({'error': 'Location not found'}, status=status.HTTP_404_NOT_FOUND)

        # Fetch forecast data from the external Open-Meteo service. This is
        # used as input features for the rainfall ML wrapper.
        weather_service = OpenMeteoService()
        weather_data = weather_service.fetch_forecast(
            latitude=float(location.latitude),
            longitude=float(location.longitude),
            days=7
        )

        if 'error' in weather_data:
            return Response({'error': 'Failed to fetch weather data'}, status=status.HTTP_503_SERVICE_UNAVAILABLE)

        # Initialize the ML wrapper. The wrapper will attempt to load a
        # persisted model from `ML_MODELS_DIR`; if it fails, the wrapper
        # provides a deterministic fallback so the API still returns results.
        model_path = f"{settings.ML_MODELS_DIR}/rainfall_model.pkl"
        model = RainfallPredictionModel(model_path)
        model.load_model()

        # Build per-hour feature vectors and call the model wrapper for each
        # timestep. The code defensively fills missing hourly arrays with
        # sensible defaults to avoid IndexError.
        predictions = []
        if 'hourly' in weather_data:
            hourly = weather_data['hourly']
            for i in range(min(len(hourly.get('time', [])), 48)):
                features = {
                    'temperature': hourly.get('temperature_2m', [])[i] if i < len(hourly.get('temperature_2m', [])) else 25.0,
                    'humidity': hourly.get('relative_humidity_2m', [])[i] if i < len(hourly.get('relative_humidity_2m', [])) else 60.0,
                    'pressure': hourly.get('pressure_msl', [])[i] if i < len(hourly.get('pressure_msl', [])) else 1013.0,
                    'wind_speed': hourly.get('wind_speed_10m', [])[i] if i < len(hourly.get('wind_speed_10m', [])) else 10.0,
                    'cloud_cover': 0.0,
                }

                # The wrapper returns a dict with keys: predicted_rainfall_mm,
                # intensity, confidence_score. If the persisted model isn't
                # present, a deterministic heuristic is returned instead.
                prediction = model.predict(features)

                timestamp = hourly['time'][i]
                dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))

                predictions.append({
                    'location': location.id,
                    'prediction_date': dt.date(),
                    'prediction_time': dt.time(),
                    'predicted_rainfall_mm': prediction['predicted_rainfall_mm'],
                    'intensity': prediction['intensity'],
                    'confidence_score': prediction['confidence_score'],
                })

        return Response({'predictions': predictions})


class FloodingPredictionViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = FloodingPredictionSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = FloodingPrediction.objects.all()
        location_id = self.request.query_params.get('location_id')
        start_date = self.request.query_params.get('start_date')
        end_date = self.request.query_params.get('end_date')

        if location_id:
            queryset = queryset.filter(location_id=location_id)
        if start_date:
            queryset = queryset.filter(prediction_date__gte=start_date)
        if end_date:
            queryset = queryset.filter(prediction_date__lte=end_date)

        return queryset

    @action(detail=False, methods=['post'])
    def predict(self, request):
        serializer = RiskCalculationInputSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        data = serializer.validated_data
        location_id = data['location_id']

        try:
            location = Location.objects.get(id=location_id)
        except Location.DoesNotExist:
            return Response({'error': 'Location not found'}, status=status.HTTP_404_NOT_FOUND)

        model_path = f"{settings.ML_MODELS_DIR}/flooding_model.pkl"
        model = FloodingPredictionModel(model_path)
        model.load_model()

        features = {
            'rainfall_mm': float(data['predicted_rainfall_mm']),
            'infrastructure_strength': float(data['infrastructure_strength']),
            'soil_moisture_retention': float(data['soil_moisture_retention']),
            'vegetation_density': float(data['vegetation_density']),
            'population_density': float(data['population_density']),
            'drainage_capacity': 5.0,
            'base_area_km2': 50.0,
        }

        prediction = model.predict(features)

        result = {
            'location': str(location.id),
            'prediction_date': datetime.now().date(),
            'flood_probability': prediction['flood_probability'],
            'risk_score': prediction['risk_score'],
            'risk_category': prediction['risk_category'],
            'mudslide_probability': prediction['mudslide_probability'],
            'water_level_meters': prediction['water_level_meters'],
            'affected_area_km2': prediction['affected_area_km2'],
            'affected_population': prediction['affected_population'],
            'confidence_score': prediction['confidence_score'],
        }

        return Response(result)


class CyclonePredictionViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = CyclonePredictionSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = CyclonePrediction.objects.all()
        start_date = self.request.query_params.get('start_date')
        end_date = self.request.query_params.get('end_date')

        if start_date:
            queryset = queryset.filter(prediction_date__gte=start_date)
        if end_date:
            queryset = queryset.filter(prediction_date__lte=end_date)

        return queryset

    @action(detail=False, methods=['post'])
    def predict(self, request):
        latitude = request.data.get('latitude')
        longitude = request.data.get('longitude')
        wind_speed = request.data.get('wind_speed', 100.0)
        pressure = request.data.get('pressure', 980.0)

        model_path = f"{settings.ML_MODELS_DIR}/cyclone_model.pkl"
        model = CyclonePredictionModel(model_path)
        model.load_model()

        features = {
            'sea_surface_temp': 28.0,
            'wind_speed': float(wind_speed),
            'pressure': float(pressure),
            'humidity': 85.0,
            'wind_shear': 5.0,
            'latitude': float(latitude),
            'longitude': float(longitude),
            'direction': 270.0,
            'speed_kmh': 25.0,
        }

        prediction = model.predict(features)

        result = {
            'cyclone_name': request.data.get('name', 'Unnamed'),
            'prediction_date': datetime.now().date(),
            'category': prediction['category'],
            'max_wind_speed_kmh': prediction['max_wind_speed_kmh'],
            'central_pressure_hpa': prediction['central_pressure_hpa'],
            'path_coordinates': prediction['path_coordinates'],
            'affected_locations': prediction['affected_locations'],
            'risk_score': prediction['risk_score'],
            'risk_category': prediction['risk_category'],
            'confidence_score': prediction['confidence_score'],
        }

        return Response(result)


class WeatherDataViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = WeatherDataSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = WeatherData.objects.all()
        location_id = self.request.query_params.get('location_id')
        start_date = self.request.query_params.get('start_date')
        end_date = self.request.query_params.get('end_date')

        if location_id:
            queryset = queryset.filter(location_id=location_id)
        if start_date:
            queryset = queryset.filter(recorded_date__gte=start_date)
        if end_date:
            queryset = queryset.filter(recorded_date__lte=end_date)

        return queryset

    @action(detail=False, methods=['post'])
    def fetch(self, request):
        location_id = request.data.get('location_id')
        start_date = request.data.get('start_date')
        end_date = request.data.get('end_date')

        try:
            location = Location.objects.get(id=location_id)
        except Location.DoesNotExist:
            return Response({'error': 'Location not found'}, status=status.HTTP_404_NOT_FOUND)

        weather_service = OpenMeteoService()
        weather_data = weather_service.fetch_weather_data(
            latitude=float(location.latitude),
            longitude=float(location.longitude),
            start_date=start_date,
            end_date=end_date
        )

        if 'error' in weather_data:
            return Response({'error': 'Failed to fetch weather data'}, status=status.HTTP_503_SERVICE_UNAVAILABLE)

        parsed_data = weather_service.parse_weather_data(weather_data)

        return Response({'data': parsed_data, 'count': len(parsed_data)})


class MLModelMetadataViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = MLModelMetadata.objects.all()
    serializer_class = MLModelMetadataSerializer
    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=['get'])
    def active(self, request):
        model_type = request.query_params.get('type')
        if model_type:
            models = MLModelMetadata.objects.filter(model_type=model_type, is_active=True)
        else:
            models = MLModelMetadata.objects.filter(is_active=True)

        serializer = self.get_serializer(models, many=True)
        return Response(serializer.data)
