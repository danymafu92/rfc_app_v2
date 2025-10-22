from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from api.models import Location, RainfallPrediction, WeatherData
from django.db import connections
from types import SimpleNamespace
from datetime import date, timedelta
from unittest.mock import patch


class FakeUser:
    """Small user-like object used for DRF force_authenticate in tests."""
    def __init__(self, id):
        self.id = id
        self.is_authenticated = True

# Mock the third-party API call (Open-Meteo) to ensure tests are fast and reliable
# We are only testing our API's structure and handling, not the external service.
WEATHER_DATA_MOCK_RESPONSE = {
    "latitude": 0.0, "longitude": 0.0, "timezone": "GMT", "daily_units": {},
    "daily": {
        "time": [str(date.today())],
        "temperature_2m_max": [25.0],
        "temperature_2m_min": [15.0],
        "rain_sum": [10.5],
        "precipitation_sum": [10.5],
        "wind_speed_10m_max": [20.5],
    }
}


class APISmokeTests(APITestCase):
    """
    A collection of smoke tests to ensure API endpoints are running and returning
    the expected status codes and basic data structures.
    """

    def setUp(self):
        # Create minimal unmanaged model tables in the test DB using raw SQL.
        # This avoids schema_editor transaction limitations on SQLite and keeps
        # the DDL simple and portable for test runs.
        with connections['default'].cursor() as cur:
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS locations (
                    id TEXT PRIMARY KEY,
                    country TEXT NOT NULL,
                    region TEXT,
                    city TEXT,
                    latitude REAL NOT NULL,
                    longitude REAL NOT NULL,
                    is_active INTEGER DEFAULT 1,
                    created_at DATETIME,
                    updated_at DATETIME
                );
                """
            )

            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS rainfall_predictions (
                    id TEXT PRIMARY KEY,
                    location_id TEXT,
                    prediction_date DATE,
                    prediction_time TIME,
                    predicted_rainfall_mm REAL,
                    intensity TEXT,
                    humidity_percent REAL,
                    wind_speed_kmh REAL,
                    wind_direction TEXT,
                    air_pressure_hpa REAL,
                    confidence_score REAL,
                    is_historical INTEGER DEFAULT 0,
                    created_at DATETIME
                );
                """
            )

            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS weather_data (
                    id TEXT PRIMARY KEY,
                    location_id TEXT,
                    recorded_date DATE,
                    recorded_time TIME,
                    temperature_celsius REAL,
                    rainfall_mm REAL,
                    humidity_percent REAL,
                    wind_speed_kmh REAL,
                    wind_direction TEXT,
                    air_pressure_hpa REAL,
                    cloud_cover_percent REAL,
                    visibility_km REAL,
                    created_at DATETIME
                );
                """
            )
        
        # Create a test location object for database-dependent tests
        self.location = Location.objects.create(
            country='TestCountry', 
            city='TestCity', 
            latitude=0.0, 
            longitude=0.0
        )

        # Create a test rainfall prediction object
        self.prediction = RainfallPrediction.objects.create(
            location=self.location,
            prediction_date=date.today() + timedelta(days=1),
            predicted_rainfall_mm=10.0,
            intensity='Moderate',
            humidity_percent=70.0,
            wind_speed_kmh=15.0,
            confidence_score=0.95
        )

        # Create a test weather data object
        self.weather_data = WeatherData.objects.create(
            location=self.location,
            recorded_date=date.today(),
            temperature_celsius=20.0,
            rainfall_mm=5.0,
            humidity_percent=80.0,
            wind_speed_kmh=10.0,
            air_pressure_hpa=1010.0
        )

        # URLs for the tests (use DRF router-generated names)
        # rainfall-prediction-list is the correct URL name for the list view.
        self.rainfall_predict_url = reverse('rainfall-prediction-list') 
        # The weather data 'fetch' action is exposed as a POST on the list route
        # named 'weather-data-fetch'. The tests POST to that URL to trigger fetch.
        self.weather_data_fetch_url = reverse('weather-data-fetch')
        self.locations_url = reverse('location-list')

        # Force-authenticate the test client so endpoints using IsAuthenticated
        # permission class return 200 in tests. Use a Small FakeUser object
        # that exposes `id` and `is_authenticated` attributes.
        self.client.force_authenticate(user=FakeUser(str(self.location.id)))


    def tearDown(self):
        # Drop the temporary tables created for unmanaged models to keep the
        # test database clean between test runs.
        with connections['default'].cursor() as cur:
            cur.execute('DROP TABLE IF EXISTS weather_data;')
            cur.execute('DROP TABLE IF EXISTS rainfall_predictions;')
            cur.execute('DROP TABLE IF EXISTS locations;')


    def test_locations_list_endpoint(self):
        """Ensure the location list endpoint returns a 200 OK."""
        response = self.client.get(self.locations_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # DRF may apply pagination; normalize to a list of items
        data = response.data
        if isinstance(data, dict) and 'results' in data:
            items = data['results']
        else:
            items = data

        # Check that the test location is included
        self.assertEqual(len(items), 1)
        self.assertEqual(items[0]['country'], 'TestCountry')


    def test_rainfall_predict_endpoint(self):
        """Ensure the rainfall prediction endpoint returns a 200 OK."""
        response = self.client.get(self.rainfall_predict_url, {'location_id': self.location.id})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.data
        if isinstance(data, dict) and 'results' in data:
            items = data['results']
        else:
            items = data

        # Check that the test prediction is included
        self.assertEqual(len(items), 1)
        self.assertEqual(items[0]['intensity'], 'Moderate')


    @patch('services.open_meteo.OpenMeteoService.parse_weather_data')
    @patch('services.open_meteo.OpenMeteoService.fetch_weather_data')
    def test_weather_data_fetch_endpoint(self, mock_fetch, mock_parse):
        """
        Ensure the weather data fetch endpoint returns a 200 OK and mock data structure.
        Uses a mock to avoid making a real external API call.
        """
        # Return the mocked weather payload directly from the service method
        mock_fetch.return_value = WEATHER_DATA_MOCK_RESPONSE
        # Ensure parse_weather_data returns a friendly parsed structure
        mock_parse.return_value = [
            {"date": str(date.today()), "rainfall_mm": 10.5}
        ]

        # Test with location ID
        response = self.client.post(
            self.weather_data_fetch_url,
            {'location_id': self.location.id},
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Check that the mocked service method and parser were called
        mock_fetch.assert_called_once()
        mock_parse.assert_called_once()

        # Check the response structure
        self.assertIn('data', response.data)
        self.assertEqual(response.data['count'], 1)
        self.assertEqual(response.data['data'][0]['rainfall_mm'], 10.5)
