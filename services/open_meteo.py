import requests
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from django.conf import settings

class OpenMeteoService:
    def __init__(self):
        self.base_url = settings.OPEN_METEO_API_URL

    # Notes for contributors/AI agents:
    # - Methods return a dict with the upstream API JSON or {'error': str}
    #   when the HTTP request fails. Callers should check for 'error' before
    #   using the payload.
    # - `fetch_forecast()` requests both `daily` and `hourly` fields; the
    #   `api.views` code expects `hourly` to include `time`, `temperature_2m`,
    #   `relative_humidity_2m`, and `pressure_msl` arrays.

    def fetch_weather_data(
        self,
        latitude: float,
        longitude: float,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
    ) -> Dict:
        if not start_date:
            start_date = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
        if not end_date:
            end_date = datetime.now().strftime('%Y-%m-%d')

        url = f"{self.base_url}/forecast"
        params = {
            'latitude': latitude,
            'longitude': longitude,
            'start_date': start_date,
            'end_date': end_date,
            'hourly': 'temperature_2m,relative_humidity_2m,precipitation,pressure_msl,wind_speed_10m,wind_direction_10m,cloud_cover',
            'timezone': 'auto'
        }

        try:
            response = requests.get(url, params=params, timeout=30)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            return {'error': str(e)}


    def fetch_historical_weather(
        self,
        latitude: float,
        longitude: float,
        start_date: str,
        end_date: str
    ) -> Dict:
        url = f"{self.base_url}/archive"
        params = {
            'latitude': latitude,
            'longitude': longitude,
            'start_date': start_date,
            'end_date': end_date,
            'hourly': 'temperature_2m,relative_humidity_2m,precipitation,pressure_msl,wind_speed_10m,wind_direction_10m,cloud_cover',
            'timezone': 'auto'
        }

        try:
            response = requests.get(url, params=params, timeout=30)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            return {'error': str(e)}

    def fetch_forecast(
        self,
        latitude: float,
        longitude: float,
        days: int = 7
    ) -> Dict:
        url = f"{self.base_url}/forecast"
        params = {
            'latitude': latitude,
            'longitude': longitude,
            'daily': 'temperature_2m_max,temperature_2m_min,precipitation_sum,precipitation_probability_mean,wind_speed_10m_max',
            'hourly': 'temperature_2m,relative_humidity_2m,precipitation_probability,precipitation,pressure_msl,wind_speed_10m,wind_direction_10m',
            'forecast_days': days,
            'timezone': 'auto'
        }

        try:
            response = requests.get(url, params=params, timeout=30)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            return {'error': str(e)}

    def parse_weather_data(self, raw_data: Dict) -> List[Dict]:
        # If upstream returns an error or the expected hourly payload is
        # missing, return an empty list. Callers should handle empty lists as
        # "no data" rather than an exception.
        if 'error' in raw_data or 'hourly' not in raw_data:
            return []

        hourly = raw_data['hourly']
        parsed_data = []

        for i in range(len(hourly.get('time', []))):
            data_point = {
                'timestamp': hourly['time'][i],
                'temperature_celsius': hourly.get('temperature_2m', [])[i] if i < len(hourly.get('temperature_2m', [])) else None,
                'humidity_percent': hourly.get('relative_humidity_2m', [])[i] if i < len(hourly.get('relative_humidity_2m', [])) else None,
                'rainfall_mm': hourly.get('precipitation', [])[i] if i < len(hourly.get('precipitation', [])) else None,
                'air_pressure_hpa': hourly.get('pressure_msl', [])[i] if i < len(hourly.get('pressure_msl', [])) else None,
                'wind_speed_kmh': hourly.get('wind_speed_10m', [])[i] if i < len(hourly.get('wind_speed_10m', [])) else None,
                'wind_direction': hourly.get('wind_direction_10m', [])[i] if i < len(hourly.get('wind_direction_10m', [])) else None,
                'cloud_cover_percent': hourly.get('cloud_cover', [])[i] if i < len(hourly.get('cloud_cover', [])) else None,
            }
            parsed_data.append(data_point)

        return parsed_data
