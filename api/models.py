"""Database model declarations used by the API.

These ORM classes mirror the Supabase/Postgres schema defined under
`supabase/migrations/`. Models are marked `managed = False` because the
database schema is owned externally (Supabase) and migrations are not
maintained inside this Django project.
"""

from django.db import models
from django.contrib.auth.models import User
import uuid

class Location(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    country = models.CharField(max_length=200)
    region = models.CharField(max_length=200, blank=True, null=True)
    city = models.CharField(max_length=200, blank=True, null=True)
    latitude = models.DecimalField(max_digits=10, decimal_places=7)
    longitude = models.DecimalField(max_digits=10, decimal_places=7)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'locations'
        managed = False

    def __str__(self):
        return f"{self.city}, {self.country}" if self.city else self.country
    # Note: `managed = False` — the DB schema lives in Supabase and is not
    # managed by Django migrations. Treat these models as read-only unless
    # you're certain the external schema will accept writes.


class UserPreference(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user_id = models.UUIDField()
    default_location = models.ForeignKey(Location, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'user_preferences'
        managed = False

    def __str__(self):
        return f"Preferences for user {self.user_id}"
    # `user_id` is stored as a UUIDField and maps to the Supabase user's id.
    # The backend uses the Supabase JWT to determine `request.user.id` and
    # filter preferences accordingly (see `api/views.py`).


class LocationParameter(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    location = models.OneToOneField(Location, on_delete=models.CASCADE, related_name='parameters')
    infrastructure_strength = models.DecimalField(max_digits=3, decimal_places=2, default=5.0)
    soil_moisture_retention = models.DecimalField(max_digits=3, decimal_places=2, default=5.0)
    soil_type = models.CharField(max_length=100, blank=True, default='')
    vegetation_density = models.DecimalField(max_digits=3, decimal_places=2, default=5.0)
    population_size = models.IntegerField(default=0)
    population_density = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'location_parameters'
        managed = False

    def __str__(self):
        return f"Parameters for {self.location}"
    # These per-location parameters provide domain-specific defaults used by
    # flooding/risk calculations when the frontend or request does not supply
    # them. Keep field names in sync with `RiskCalculationInputSerializer`.


class RainfallPrediction(models.Model):
    INTENSITY_CHOICES = [
        ('Light', 'Light'),
        ('Moderate', 'Moderate'),
        ('Heavy', 'Heavy'),
        ('Extreme', 'Extreme'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    location = models.ForeignKey(Location, on_delete=models.CASCADE, related_name='rainfall_predictions')
    prediction_date = models.DateField()
    prediction_time = models.TimeField(null=True, blank=True)
    predicted_rainfall_mm = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    intensity = models.CharField(max_length=20, choices=INTENSITY_CHOICES, default='Light')
    humidity_percent = models.DecimalField(max_digits=5, decimal_places=2, default=0.0)
    wind_speed_kmh = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    wind_direction = models.CharField(max_length=50, blank=True, default='')
    air_pressure_hpa = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    confidence_score = models.DecimalField(max_digits=3, decimal_places=2, default=0.0)
    is_historical = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'rainfall_predictions'
        managed = False
        ordering = ['-prediction_date', '-prediction_time']

    def __str__(self):
        return f"Rainfall for {self.location} on {self.prediction_date}"
    # Predictions stored here follow the wrapper contract: `predicted_rainfall_mm`,
    # `intensity`, and `confidence_score` are expected by the frontend.


class FloodingPrediction(models.Model):
    RISK_CATEGORIES = [
        ('Low', 'Low'),
        ('Medium', 'Medium'),
        ('High', 'High'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    location = models.ForeignKey(Location, on_delete=models.CASCADE, related_name='flooding_predictions')
    prediction_date = models.DateField()
    flood_probability = models.DecimalField(max_digits=3, decimal_places=2, default=0.0)
    affected_area_km2 = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    water_level_meters = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    risk_score = models.DecimalField(max_digits=4, decimal_places=2, default=0.0)
    risk_category = models.CharField(max_length=20, choices=RISK_CATEGORIES, default='Low')
    mudslide_probability = models.DecimalField(max_digits=3, decimal_places=2, default=0.0)
    affected_population = models.IntegerField(default=0)
    confidence_score = models.DecimalField(max_digits=3, decimal_places=2, default=0.0)
    is_historical = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'flooding_predictions'
        managed = False
        ordering = ['-prediction_date']

    def __str__(self):
        return f"Flooding for {self.location} on {self.prediction_date}"
    # `risk_category` uses a small set of choices (Low/Medium/High) — align
    # any UI logic or serialization with these options.


class CyclonePrediction(models.Model):
    RISK_CATEGORIES = [
        ('Low', 'Low'),
        ('Medium', 'Medium'),
        ('High', 'High'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    cyclone_name = models.CharField(max_length=200, blank=True, default='')
    prediction_date = models.DateField()
    category = models.IntegerField(default=1)
    max_wind_speed_kmh = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    central_pressure_hpa = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    path_coordinates = models.JSONField(default=list)
    affected_locations = models.JSONField(default=list)
    risk_score = models.DecimalField(max_digits=4, decimal_places=2, default=0.0)
    risk_category = models.CharField(max_length=20, choices=RISK_CATEGORIES, default='Low')
    estimated_landfall_date = models.DateTimeField(null=True, blank=True)
    confidence_score = models.DecimalField(max_digits=3, decimal_places=2, default=0.0)
    is_historical = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'cyclone_predictions'
        managed = False
        ordering = ['-prediction_date']

    def __str__(self):
        return f"Cyclone {self.cyclone_name} on {self.prediction_date}"
    # `path_coordinates` is a JSON array of {latitude, longitude, timestamp}
    # dicts. The frontend expects this structure for mapping cyclone tracks.


class WeatherData(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    location = models.ForeignKey(Location, on_delete=models.CASCADE, related_name='weather_data')
    recorded_date = models.DateField()
    recorded_time = models.TimeField(null=True, blank=True)
    temperature_celsius = models.DecimalField(max_digits=5, decimal_places=2, default=0.0)
    rainfall_mm = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    humidity_percent = models.DecimalField(max_digits=5, decimal_places=2, default=0.0)
    wind_speed_kmh = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    wind_direction = models.CharField(max_length=50, blank=True, default='')
    air_pressure_hpa = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    cloud_cover_percent = models.DecimalField(max_digits=5, decimal_places=2, default=0.0)
    visibility_km = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'weather_data'
        managed = False
        ordering = ['-recorded_date', '-recorded_time']

    def __str__(self):
        return f"Weather for {self.location} on {self.recorded_date}"
    # `WeatherData` is primarily used by the UI and by downstream risk
    # calculations; it's stored separately from predictions to allow
    # historical queries.


class MLModelMetadata(models.Model):
    MODEL_TYPES = [
        ('rainfall', 'Rainfall'),
        ('flooding', 'Flooding'),
        ('cyclone', 'Cyclone'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    model_type = models.CharField(max_length=50, choices=MODEL_TYPES)
    version = models.CharField(max_length=50)
    architecture = models.TextField(blank=True, default='')
    training_date = models.DateTimeField(auto_now_add=True)
    accuracy_score = models.DecimalField(max_digits=5, decimal_places=4, default=0.0)
    rmse = models.DecimalField(max_digits=10, decimal_places=4, default=0.0)
    mae = models.DecimalField(max_digits=10, decimal_places=4, default=0.0)
    is_active = models.BooleanField(default=False)
    model_file_path = models.CharField(max_length=500, blank=True, default='')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'ml_model_metadata'
        managed = False
        ordering = ['-training_date']

    def __str__(self):
        return f"{self.model_type} model v{self.version}"
