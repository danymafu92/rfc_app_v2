# Weather Prediction Platform

A comprehensive weather prediction application that predicts rainfall occurrence and intensity, flooding and mudslide risk, and cyclone paths with affected areas. The application uses machine learning models that continuously learn from real-time data to improve predictions.

## Features

### Core Prediction Capabilities
- **Rainfall Prediction**: Predicts rainfall occurrence, intensity, humidity levels, wind speed/direction, and air pressure
- **Flooding Risk Assessment**: Calculates flooding and mudslide occurrence, affected areas, and severity with categorized risk (0-10 scale)
- **Cyclone Path Tracking**: Predicts cyclone/hurricane/typhoon occurrence, path, affected areas, and severity

### Risk Assessment System
- Risk scoring from 0-10 using decimal points
- Color-coded risk categories:
  - Green (0-3.5): Low risk
  - Yellow (3.6-7.4): Medium risk
  - Red (7.5-10): High risk
- Risk calculation based on:
  - Infrastructure strength
  - Soil moisture retention and type
  - Vegetation density
  - Population size and density
  - Predicted rainfall amount and intensity

### User Interface
- **Dashboard**: Shows most recent predictions based on historical data for preset location
- **Cyclone Prediction Page**: View cyclone predictions with path visualization on map, filter by year and location
- **Flooding Prediction Page**: View flooding predictions with affected areas on map, calculate custom risk scenarios
- **Rainfall Data Page**: View historical and predicted rainfall with filters (location, year, date range, time range), switch between map and table views

### Technical Features
- Real-time weather data from Open-Meteo API
- Machine learning models with continuous learning capabilities
- Offline mode using cached predictions from PostgreSQL database
- Interactive maps showing affected areas and risk levels
- Authentication with Supabase
- RESTful API built with Django REST Framework

## Tech Stack

### Backend
- Python 3.x
- Django 4.2.7
- Django REST Framework 3.14.0
- PostgreSQL (Supabase)
- Machine Learning: scikit-learn, NumPy, pandas

### Frontend
- React 18.2.0
- React Router 6.20.0
- Leaflet (for maps)
- Recharts (for data visualization)
- Axios (API calls)
- Vite (build tool)

### External Services
- Supabase (database and authentication)
- Open-Meteo API (weather data)

## Installation

### Prerequisites
- Python 3.8 or higher
- Node.js 16 or higher
- npm or yarn

### Backend Setup

1. Install Python dependencies:
```bash
pip install -r requirements.txt
```

2. Set up environment variables in `.env`:
```
VITE_SUPABASE_URL=your_supabase_url
VITE_SUPABASE_ANON_KEY=your_supabase_anon_key
DJANGO_SECRET_KEY=your_django_secret_key
DEBUG=True
```

3. The database is already set up in Supabase with all required tables and initial location data.

### Frontend Setup

1. Install Node dependencies:
```bash
npm install
```

2. The frontend uses the same `.env` file for Supabase configuration.

## Running the Application

### Development Mode

1. Start the Django backend:
```bash
python manage.py runserver
```
The backend will run on http://localhost:8000

2. Start the Vite frontend (in a separate terminal):
```bash
npm run dev
```
The frontend will run on http://localhost:5173

### Production Build

Build the frontend for production:
```bash
npm run build
```

## Database Schema

The application uses the following main tables:

- **locations**: Geographic locations with coordinates
- **user_preferences**: User settings and default locations
- **location_parameters**: Location-specific parameters for risk calculations
- **rainfall_predictions**: Rainfall prediction data and historical records
- **flooding_predictions**: Flooding risk predictions and historical data
- **cyclone_predictions**: Cyclone/hurricane/typhoon predictions with path data
- **weather_data**: Historical weather data from Open-Meteo API
- **ml_model_metadata**: ML model versions and performance metrics

## API Endpoints

### Locations
- `GET /api/locations/` - List all active locations
- `GET /api/locations/{id}/parameters/` - Get location parameters

### Predictions
- `GET /api/rainfall-predictions/` - List rainfall predictions
- `POST /api/rainfall-predictions/predict/` - Generate new rainfall predictions
- `GET /api/flooding-predictions/` - List flooding predictions
- `POST /api/flooding-predictions/predict/` - Calculate flooding risk
- `GET /api/cyclone-predictions/` - List cyclone predictions
- `POST /api/cyclone-predictions/predict/` - Generate cyclone prediction

### Weather Data
- `GET /api/weather-data/` - Get historical weather data
- `POST /api/weather-data/fetch/` - Fetch weather data from Open-Meteo API

## Machine Learning Models

### Rainfall Prediction Model
- Uses Random Forest Regressor
- Features: temperature, humidity, pressure, wind speed, cloud cover
- Outputs: predicted rainfall amount, intensity, confidence score

### Flooding Prediction Model
- Uses Gradient Boosting Classifier
- Features: rainfall, infrastructure, soil properties, vegetation, population
- Outputs: flood probability, risk score, affected area, affected population

### Cyclone Prediction Model
- Uses Random Forest Classifier
- Features: sea surface temperature, wind speed, pressure, humidity, wind shear
- Outputs: category, wind speed, path coordinates, risk score

### Continuous Learning
- Models can be retrained with new data
- Performance metrics tracked in database
- Supports incremental learning with new real-time data

## Usage

1. **Sign Up/Sign In**: Create an account or sign in with existing credentials
2. **Dashboard**: View recent predictions for your default location
3. **Change Location**: Select different locations from the dropdown menu
4. **View Predictions**: Navigate to specific prediction pages (Cyclone, Flooding, Rainfall)
5. **Filter Data**: Use filters to view historical data by year, date range, or location
6. **Calculate Custom Risk**: Enter custom parameters to calculate flooding risk
7. **Generate Predictions**: Use the "Generate Predictions" button to create new forecasts
8. **Toggle Views**: Switch between map and table views for rainfall data

## Risk Calculation

The risk score (0-10) is calculated based on:

**Flooding Risk Formula:**
- Rainfall factor × 4.0
- (10 - infrastructure strength) × 0.3
- (10 - soil moisture retention) × 0.25
- (10 - vegetation density) × 0.2
- Flood probability × 2.5

**Cyclone Risk Formula:**
- Wind factor × 3.0
- Category weight × 3.5
- Distance factor × 2.0
- Infrastructure vulnerability × 1.0
- Population factor × 0.5

## Contributing

This is a comprehensive weather prediction system. Future enhancements could include:
- Deep learning models (LSTM, CNN) for improved accuracy
- Real-time alerts and notifications
- Mobile application
- Multi-language support
- Historical trend analysis and reporting
- Integration with additional weather data sources

## License

MIT License

## Support

For issues or questions, please contact the development team.

## Development helper scripts

Two convenience scripts are provided to start the backend and frontend together:

- `scripts/start-dev.sh` (Linux / macOS / Git Bash):
  - Usage: `./scripts/start-dev.sh [--no-install] [--build]`
    - `--no-install` skips dependency installation
    - `--build` runs a frontend production build before starting dev servers
  - This script installs Python and Node dependencies (unless skipped), optionally builds the frontend, then starts the Django dev server and the Vite dev server and tails their logs in `.dev_logs/`.

- `scripts/start-dev.ps1` (Windows PowerShell):
  - Usage: `.	emplates\start-dev.ps1 [-NoInstall] [-Build]` (run from repo root or provide full path)
    - `-NoInstall` skips dependency installation
    - `-Build` runs a frontend production build before starting dev servers
  - The PowerShell script starts both servers and redirects logs to `.dev_logs\`.

Examples (Linux/macOS/Git Bash):
```bash
# install deps and start servers
./scripts/start-dev.sh

# skip installs and build frontend before starting
./scripts/start-dev.sh --no-install --build
```

Examples (PowerShell):
```powershell
# install deps and start servers
.\scripts\start-dev.ps1

# skip installs and build frontend before starting
.\scripts\start-dev.ps1 -NoInstall -Build
```

Note: The scripts assume you have Python, pip, Node.js and npm available on your PATH. The Vite dev server is proxied to the Django backend at `http://localhost:8000` as configured in `vite.config.js`.

## Production deployment

The repository includes helper scripts to build and run the app in production. The recommended production stack is:
- Build frontend with Vite and place static files in `frontend/build` (the Django `collectstatic` step picks them up).
- Serve Django with a WSGI server (Gunicorn) behind a process manager (systemd) or reverse proxy (nginx).

Use the production script (Linux):
```bash
./scripts/start-prod.sh
```
Options:
- `--no-install` : skip dependency installation

Windows: use PowerShell script; the script suggests using Waitress or deploying to a Linux host for Gunicorn.

Example `systemd` unit (adjust paths and user):
```ini
[Unit]
Description=Weather Prediction Gunicorn
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/path/to/rfc_app_v2
Environment="PATH=/path/to/venv/bin"
ExecStart=/path/to/venv/bin/gunicorn -c /path/to/rfc_app_v2/gunicorn.conf.py weather_prediction.wsgi:application

[Install]
WantedBy=multi-user.target
```

Notes:
- The `start-prod.sh` script installs dependencies, builds the frontend, runs `collectstatic`, applies migrations, and starts Gunicorn.
- In production you should also configure an HTTP reverse proxy (nginx) to serve static files, terminate TLS, and forward requests to Gunicorn.
- Consider using a process manager such as systemd, supervisor, or similar, and set up log rotation and monitoring.
