/*
  # Weather Prediction Platform - Initial Schema

  ## Overview
  This migration creates the core database structure for the weather prediction platform,
  including tables for locations, predictions, historical data, and risk assessments.

  ## New Tables

  ### 1. `locations`
  Stores geographic locations with coordinates and metadata
  - `id` (uuid, primary key)
  - `country` (text) - Country name
  - `region` (text) - State/province/region name
  - `city` (text) - City name
  - `latitude` (decimal) - Latitude coordinate
  - `longitude` (decimal) - Longitude coordinate
  - `is_active` (boolean) - Whether location is available for selection
  - `created_at` (timestamptz) - Record creation timestamp
  - `updated_at` (timestamptz) - Record update timestamp

  ### 2. `user_preferences`
  Stores user preferences and default location settings
  - `id` (uuid, primary key)
  - `user_id` (uuid) - References auth.users
  - `default_location_id` (uuid) - References locations table
  - `created_at` (timestamptz)
  - `updated_at` (timestamptz)

  ### 3. `location_parameters`
  Stores location-specific parameters for risk calculations
  - `id` (uuid, primary key)
  - `location_id` (uuid) - References locations table
  - `infrastructure_strength` (decimal) - Scale 0-10
  - `soil_moisture_retention` (decimal) - Scale 0-10
  - `soil_type` (text) - Classification of soil type
  - `vegetation_density` (decimal) - Scale 0-10
  - `population_size` (integer) - Total population
  - `population_density` (decimal) - People per square km
  - `created_at` (timestamptz)
  - `updated_at` (timestamptz)

  ### 4. `rainfall_predictions`
  Stores rainfall prediction data and results
  - `id` (uuid, primary key)
  - `location_id` (uuid) - References locations
  - `prediction_date` (date) - Date of prediction
  - `prediction_time` (time) - Time of prediction
  - `predicted_rainfall_mm` (decimal) - Predicted rainfall in mm
  - `intensity` (text) - Light/Moderate/Heavy/Extreme
  - `humidity_percent` (decimal) - Humidity percentage
  - `wind_speed_kmh` (decimal) - Wind speed in km/h
  - `wind_direction` (text) - Wind direction
  - `air_pressure_hpa` (decimal) - Air pressure in hPa
  - `confidence_score` (decimal) - Model confidence 0-1
  - `is_historical` (boolean) - Whether this is actual recorded data
  - `created_at` (timestamptz)

  ### 5. `flooding_predictions`
  Stores flooding occurrence and risk predictions
  - `id` (uuid, primary key)
  - `location_id` (uuid) - References locations
  - `prediction_date` (date)
  - `flood_probability` (decimal) - 0-1 probability
  - `affected_area_km2` (decimal) - Estimated affected area
  - `water_level_meters` (decimal) - Predicted water level
  - `risk_score` (decimal) - Risk score 0-10
  - `risk_category` (text) - Low/Medium/High
  - `mudslide_probability` (decimal) - 0-1 probability
  - `affected_population` (integer) - Estimated affected population
  - `confidence_score` (decimal) - Model confidence 0-1
  - `is_historical` (boolean)
  - `created_at` (timestamptz)

  ### 6. `cyclone_predictions`
  Stores cyclone/hurricane/typhoon predictions and path data
  - `id` (uuid, primary key)
  - `cyclone_name` (text) - Name of the cyclone
  - `prediction_date` (date)
  - `category` (integer) - Saffir-Simpson scale 1-5
  - `max_wind_speed_kmh` (decimal) - Maximum sustained wind speed
  - `central_pressure_hpa` (decimal) - Central pressure
  - `path_coordinates` (jsonb) - Array of lat/lng coordinates
  - `affected_locations` (jsonb) - Array of location IDs
  - `risk_score` (decimal) - Risk score 0-10
  - `risk_category` (text) - Low/Medium/High
  - `estimated_landfall_date` (timestamptz) - Predicted landfall time
  - `confidence_score` (decimal) - Model confidence 0-1
  - `is_historical` (boolean)
  - `created_at` (timestamptz)

  ### 7. `weather_data`
  Stores historical weather data from Open-Meteo API
  - `id` (uuid, primary key)
  - `location_id` (uuid) - References locations
  - `recorded_date` (date)
  - `recorded_time` (time)
  - `temperature_celsius` (decimal)
  - `rainfall_mm` (decimal)
  - `humidity_percent` (decimal)
  - `wind_speed_kmh` (decimal)
  - `wind_direction` (text)
  - `air_pressure_hpa` (decimal)
  - `cloud_cover_percent` (decimal)
  - `visibility_km` (decimal)
  - `created_at` (timestamptz)

  ### 8. `ml_model_metadata`
  Tracks ML model versions and performance metrics
  - `id` (uuid, primary key)
  - `model_type` (text) - rainfall/flooding/cyclone
  - `version` (text) - Model version identifier
  - `architecture` (text) - Model architecture description
  - `training_date` (timestamptz) - When model was trained
  - `accuracy_score` (decimal) - Model accuracy
  - `rmse` (decimal) - Root mean square error
  - `mae` (decimal) - Mean absolute error
  - `is_active` (boolean) - Whether model is currently in use
  - `model_file_path` (text) - Path to saved model file
  - `created_at` (timestamptz)

  ## Security
  - Enable RLS on all tables
  - Add policies for authenticated users to read their own data
  - Add policies for authenticated users to access location and prediction data
  - Admin-only policies for writing predictions and model metadata
*/

-- Create locations table
CREATE TABLE IF NOT EXISTS locations (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  country text NOT NULL,
  region text,
  city text,
  latitude decimal(10, 7) NOT NULL,
  longitude decimal(10, 7) NOT NULL,
  is_active boolean DEFAULT true,
  created_at timestamptz DEFAULT now(),
  updated_at timestamptz DEFAULT now()
);

-- Create user_preferences table
CREATE TABLE IF NOT EXISTS user_preferences (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id uuid NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
  default_location_id uuid REFERENCES locations(id) ON DELETE SET NULL,
  created_at timestamptz DEFAULT now(),
  updated_at timestamptz DEFAULT now(),
  UNIQUE(user_id)
);

-- Create location_parameters table
CREATE TABLE IF NOT EXISTS location_parameters (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  location_id uuid NOT NULL REFERENCES locations(id) ON DELETE CASCADE,
  infrastructure_strength decimal(3, 2) DEFAULT 5.0,
  soil_moisture_retention decimal(3, 2) DEFAULT 5.0,
  soil_type text DEFAULT '',
  vegetation_density decimal(3, 2) DEFAULT 5.0,
  population_size integer DEFAULT 0,
  population_density decimal(10, 2) DEFAULT 0.0,
  created_at timestamptz DEFAULT now(),
  updated_at timestamptz DEFAULT now(),
  UNIQUE(location_id)
);

-- Create rainfall_predictions table
CREATE TABLE IF NOT EXISTS rainfall_predictions (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  location_id uuid NOT NULL REFERENCES locations(id) ON DELETE CASCADE,
  prediction_date date NOT NULL,
  prediction_time time,
  predicted_rainfall_mm decimal(10, 2) DEFAULT 0.0,
  intensity text DEFAULT 'Light',
  humidity_percent decimal(5, 2) DEFAULT 0.0,
  wind_speed_kmh decimal(10, 2) DEFAULT 0.0,
  wind_direction text DEFAULT '',
  air_pressure_hpa decimal(10, 2) DEFAULT 0.0,
  confidence_score decimal(3, 2) DEFAULT 0.0,
  is_historical boolean DEFAULT false,
  created_at timestamptz DEFAULT now()
);

-- Create flooding_predictions table
CREATE TABLE IF NOT EXISTS flooding_predictions (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  location_id uuid NOT NULL REFERENCES locations(id) ON DELETE CASCADE,
  prediction_date date NOT NULL,
  flood_probability decimal(3, 2) DEFAULT 0.0,
  affected_area_km2 decimal(10, 2) DEFAULT 0.0,
  water_level_meters decimal(10, 2) DEFAULT 0.0,
  risk_score decimal(4, 2) DEFAULT 0.0,
  risk_category text DEFAULT 'Low',
  mudslide_probability decimal(3, 2) DEFAULT 0.0,
  affected_population integer DEFAULT 0,
  confidence_score decimal(3, 2) DEFAULT 0.0,
  is_historical boolean DEFAULT false,
  created_at timestamptz DEFAULT now()
);

-- Create cyclone_predictions table
CREATE TABLE IF NOT EXISTS cyclone_predictions (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  cyclone_name text DEFAULT '',
  prediction_date date NOT NULL,
  category integer DEFAULT 1,
  max_wind_speed_kmh decimal(10, 2) DEFAULT 0.0,
  central_pressure_hpa decimal(10, 2) DEFAULT 0.0,
  path_coordinates jsonb DEFAULT '[]'::jsonb,
  affected_locations jsonb DEFAULT '[]'::jsonb,
  risk_score decimal(4, 2) DEFAULT 0.0,
  risk_category text DEFAULT 'Low',
  estimated_landfall_date timestamptz,
  confidence_score decimal(3, 2) DEFAULT 0.0,
  is_historical boolean DEFAULT false,
  created_at timestamptz DEFAULT now()
);

-- Create weather_data table
CREATE TABLE IF NOT EXISTS weather_data (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  location_id uuid NOT NULL REFERENCES locations(id) ON DELETE CASCADE,
  recorded_date date NOT NULL,
  recorded_time time,
  temperature_celsius decimal(5, 2) DEFAULT 0.0,
  rainfall_mm decimal(10, 2) DEFAULT 0.0,
  humidity_percent decimal(5, 2) DEFAULT 0.0,
  wind_speed_kmh decimal(10, 2) DEFAULT 0.0,
  wind_direction text DEFAULT '',
  air_pressure_hpa decimal(10, 2) DEFAULT 0.0,
  cloud_cover_percent decimal(5, 2) DEFAULT 0.0,
  visibility_km decimal(10, 2) DEFAULT 0.0,
  created_at timestamptz DEFAULT now()
);

-- Create ml_model_metadata table
CREATE TABLE IF NOT EXISTS ml_model_metadata (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  model_type text NOT NULL,
  version text NOT NULL,
  architecture text DEFAULT '',
  training_date timestamptz DEFAULT now(),
  accuracy_score decimal(5, 4) DEFAULT 0.0,
  rmse decimal(10, 4) DEFAULT 0.0,
  mae decimal(10, 4) DEFAULT 0.0,
  is_active boolean DEFAULT false,
  model_file_path text DEFAULT '',
  created_at timestamptz DEFAULT now()
);

-- Create indexes for better query performance
CREATE INDEX IF NOT EXISTS idx_locations_country ON locations(country);
CREATE INDEX IF NOT EXISTS idx_locations_coordinates ON locations(latitude, longitude);
CREATE INDEX IF NOT EXISTS idx_rainfall_location_date ON rainfall_predictions(location_id, prediction_date);
CREATE INDEX IF NOT EXISTS idx_flooding_location_date ON flooding_predictions(location_id, prediction_date);
CREATE INDEX IF NOT EXISTS idx_cyclone_date ON cyclone_predictions(prediction_date);
CREATE INDEX IF NOT EXISTS idx_weather_location_date ON weather_data(location_id, recorded_date);

-- Enable Row Level Security
ALTER TABLE locations ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_preferences ENABLE ROW LEVEL SECURITY;
ALTER TABLE location_parameters ENABLE ROW LEVEL SECURITY;
ALTER TABLE rainfall_predictions ENABLE ROW LEVEL SECURITY;
ALTER TABLE flooding_predictions ENABLE ROW LEVEL SECURITY;
ALTER TABLE cyclone_predictions ENABLE ROW LEVEL SECURITY;
ALTER TABLE weather_data ENABLE ROW LEVEL SECURITY;
ALTER TABLE ml_model_metadata ENABLE ROW LEVEL SECURITY;

-- RLS Policies for locations (public read access)
CREATE POLICY "Anyone can view active locations"
  ON locations FOR SELECT
  TO authenticated
  USING (is_active = true);

CREATE POLICY "Admins can manage locations"
  ON locations FOR ALL
  TO authenticated
  USING (auth.jwt()->>'role' = 'admin')
  WITH CHECK (auth.jwt()->>'role' = 'admin');

-- RLS Policies for user_preferences
CREATE POLICY "Users can view own preferences"
  ON user_preferences FOR SELECT
  TO authenticated
  USING (auth.uid() = user_id);

CREATE POLICY "Users can insert own preferences"
  ON user_preferences FOR INSERT
  TO authenticated
  WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update own preferences"
  ON user_preferences FOR UPDATE
  TO authenticated
  USING (auth.uid() = user_id)
  WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can delete own preferences"
  ON user_preferences FOR DELETE
  TO authenticated
  USING (auth.uid() = user_id);

-- RLS Policies for location_parameters (read for all, write for admins)
CREATE POLICY "Authenticated users can view location parameters"
  ON location_parameters FOR SELECT
  TO authenticated
  USING (true);

CREATE POLICY "Admins can manage location parameters"
  ON location_parameters FOR ALL
  TO authenticated
  USING (auth.jwt()->>'role' = 'admin')
  WITH CHECK (auth.jwt()->>'role' = 'admin');

-- RLS Policies for rainfall_predictions (read for all, write for admins)
CREATE POLICY "Authenticated users can view rainfall predictions"
  ON rainfall_predictions FOR SELECT
  TO authenticated
  USING (true);

CREATE POLICY "Admins can manage rainfall predictions"
  ON rainfall_predictions FOR ALL
  TO authenticated
  USING (auth.jwt()->>'role' = 'admin')
  WITH CHECK (auth.jwt()->>'role' = 'admin');

-- RLS Policies for flooding_predictions (read for all, write for admins)
CREATE POLICY "Authenticated users can view flooding predictions"
  ON flooding_predictions FOR SELECT
  TO authenticated
  USING (true);

CREATE POLICY "Admins can manage flooding predictions"
  ON flooding_predictions FOR ALL
  TO authenticated
  USING (auth.jwt()->>'role' = 'admin')
  WITH CHECK (auth.jwt()->>'role' = 'admin');

-- RLS Policies for cyclone_predictions (read for all, write for admins)
CREATE POLICY "Authenticated users can view cyclone predictions"
  ON cyclone_predictions FOR SELECT
  TO authenticated
  USING (true);

CREATE POLICY "Admins can manage cyclone predictions"
  ON cyclone_predictions FOR ALL
  TO authenticated
  USING (auth.jwt()->>'role' = 'admin')
  WITH CHECK (auth.jwt()->>'role' = 'admin');

-- RLS Policies for weather_data (read for all, write for admins)
CREATE POLICY "Authenticated users can view weather data"
  ON weather_data FOR SELECT
  TO authenticated
  USING (true);

CREATE POLICY "Admins can manage weather data"
  ON weather_data FOR ALL
  TO authenticated
  USING (auth.jwt()->>'role' = 'admin')
  WITH CHECK (auth.jwt()->>'role' = 'admin');

-- RLS Policies for ml_model_metadata (read for all, write for admins)
CREATE POLICY "Authenticated users can view ml model metadata"
  ON ml_model_metadata FOR SELECT
  TO authenticated
  USING (true);

CREATE POLICY "Admins can manage ml model metadata"
  ON ml_model_metadata FOR ALL
  TO authenticated
  USING (auth.jwt()->>'role' = 'admin')
  WITH CHECK (auth.jwt()->>'role' = 'admin');

-- Insert some initial location data
INSERT INTO locations (country, region, city, latitude, longitude, is_active) VALUES
  ('United States', 'Florida', 'Miami', 25.7617, -80.1918, true),
  ('United States', 'Louisiana', 'New Orleans', 29.9511, -90.0715, true),
  ('United States', 'Texas', 'Houston', 29.7604, -95.3698, true),
  ('Japan', 'Tokyo', 'Tokyo', 35.6762, 139.6503, true),
  ('Philippines', 'Metro Manila', 'Manila', 14.5995, 120.9842, true),
  ('India', 'West Bengal', 'Kolkata', 22.5726, 88.3639, true),
  ('Bangladesh', 'Dhaka', 'Dhaka', 23.8103, 90.4125, true),
  ('Australia', 'Queensland', 'Brisbane', -27.4698, 153.0251, true),
  ('China', 'Guangdong', 'Guangzhou', 23.1291, 113.2644, true),
  ('Mexico', 'Quintana Roo', 'Cancun', 21.1619, -86.8515, true)
ON CONFLICT DO NOTHING;
