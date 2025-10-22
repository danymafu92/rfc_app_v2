// Rainfall data page: fetches locations, displays rainfall predictions from
// the backend and can request generation of new predictions.
// Uses `services/api.js` which injects the Supabase access token.
import { useState, useEffect } from 'react'
import { getLocations, getRainfallPredictions, predictRainfall } from '../services/api'
import Map from '../components/Map'
import './Prediction.css'

function RainfallData() {
  const [locations, setLocations] = useState([])
  const [selectedLocation, setSelectedLocation] = useState(null)
  const [predictions, setPredictions] = useState([])
  const [viewMode, setViewMode] = useState('map')
  const [filters, setFilters] = useState({
    year: new Date().getFullYear(),
    startDate: '',
    endDate: '',
  })
  const [loading, setLoading] = useState(false)
  const [predicting, setPredicting] = useState(false)

  useEffect(() => {
    fetchLocations()
  }, [])

  useEffect(() => {
    if (selectedLocation) {
      fetchPredictions()
    }
  }, [selectedLocation, filters.year, filters.startDate, filters.endDate])

  const fetchLocations = async () => {
    try {
      const response = await getLocations()
      const locs = response.data.results || response.data
      setLocations(locs)
      if (locs.length > 0) {
        setSelectedLocation(locs[0])
      }
    } catch (error) {
      console.error('Error fetching locations:', error)
    }
  }

  const fetchPredictions = async () => {
    if (!selectedLocation) return

    setLoading(true)
    try {
      const params = {
        location_id: selectedLocation.id,
        start_date: filters.startDate || `${filters.year}-01-01`,
        end_date: filters.endDate || `${filters.year}-12-31`,
      }

      const response = await getRainfallPredictions(params)
      setPredictions(response.data.results || response.data || [])
    } catch (error) {
      console.error('Error fetching predictions:', error)
    } finally {
      setLoading(false)
    }
  }

  const handlePredict = async () => {
    if (!selectedLocation) return

    setPredicting(true)
    try {
      await predictRainfall(selectedLocation.id)
      alert('Predictions generated successfully!')
      fetchPredictions()
    } catch (error) {
      console.error('Error predicting:', error)
      alert('Failed to generate predictions')
    } finally {
      setPredicting(false)
    }
  }

  const getMapMarkers = () => {
    if (!selectedLocation || predictions.length === 0) return []

    return predictions.slice(0, 20).map((pred, idx) => ({
      lat: parseFloat(selectedLocation.latitude) + (Math.random() - 0.5) * 0.1,
      lng: parseFloat(selectedLocation.longitude) + (Math.random() - 0.5) * 0.1,
      type: 'circle',
      radius: Math.min(pred.predicted_rainfall_mm / 5, 15) || 5,
      riskScore: null,
      popup: {
        title: `${pred.prediction_date} ${pred.prediction_time || ''}`,
        content: (
          <div>
            <p>Rainfall: {pred.predicted_rainfall_mm} mm</p>
            <p>Intensity: {pred.intensity}</p>
            <p>Humidity: {pred.humidity_percent}%</p>
            <p>Wind: {pred.wind_speed_kmh} km/h {pred.wind_direction}</p>
            <p>Pressure: {pred.air_pressure_hpa} hPa</p>
          </div>
        )
      }
    }))
  }

  return (
    <div className="prediction-page">
      <div className="page-header">
        <h1>Rainfall Data & Predictions</h1>
        <div className="controls">
          <select
            value={selectedLocation?.id || ''}
            onChange={(e) => {
              const loc = locations.find(l => l.id === e.target.value)
              setSelectedLocation(loc)
            }}
          >
            {locations.map(loc => (
              <option key={loc.id} value={loc.id}>
                {loc.city ? `${loc.city}, ${loc.country}` : loc.country}
              </option>
            ))}
          </select>
          <button onClick={handlePredict} disabled={predicting || !selectedLocation} className="btn-predict">
            {predicting ? 'Predicting...' : 'Generate Predictions'}
          </button>
        </div>
      </div>

      <div className="filters">
        <div className="input-group">
          <label>Year</label>
          <select value={filters.year} onChange={(e) => setFilters({...filters, year: Number(e.target.value)})}>
            {[...Array(5)].map((_, i) => {
              const year = new Date().getFullYear() - i
              return <option key={year} value={year}>{year}</option>
            })}
          </select>
        </div>
        <div className="input-group">
          <label>Start Date</label>
          <input
            type="date"
            value={filters.startDate}
            onChange={(e) => setFilters({...filters, startDate: e.target.value})}
          />
        </div>
        <div className="input-group">
          <label>End Date</label>
          <input
            type="date"
            value={filters.endDate}
            onChange={(e) => setFilters({...filters, endDate: e.target.value})}
          />
        </div>
        <div className="view-toggle">
          <button
            className={viewMode === 'map' ? 'active' : ''}
            onClick={() => setViewMode('map')}
          >
            Map View
          </button>
          <button
            className={viewMode === 'table' ? 'active' : ''}
            onClick={() => setViewMode('table')}
          >
            Table View
          </button>
        </div>
      </div>

      {loading ? (
        <div className="loading">Loading data...</div>
      ) : (
        <>
          {viewMode === 'map' && selectedLocation && (
            <div className="map-container-section">
              <Map
                center={[parseFloat(selectedLocation.latitude), parseFloat(selectedLocation.longitude)]}
                zoom={8}
                markers={getMapMarkers()}
              />
            </div>
          )}

          {viewMode === 'table' && (
            <div className="table-container">
              <table className="data-table">
                <thead>
                  <tr>
                    <th>Date</th>
                    <th>Time</th>
                    <th>Rainfall (mm)</th>
                    <th>Intensity</th>
                    <th>Humidity (%)</th>
                    <th>Wind Speed (km/h)</th>
                    <th>Wind Direction</th>
                    <th>Air Pressure (hPa)</th>
                    <th>Confidence</th>
                  </tr>
                </thead>
                <tbody>
                  {predictions.length === 0 ? (
                    <tr>
                      <td colSpan="9" className="no-data">No data available</td>
                    </tr>
                  ) : (
                    predictions.map((pred) => (
                      <tr key={pred.id}>
                        <td>{pred.prediction_date}</td>
                        <td>{pred.prediction_time || 'N/A'}</td>
                        <td>{pred.predicted_rainfall_mm}</td>
                        <td>
                          <span className={`intensity-badge intensity-${pred.intensity.toLowerCase()}`}>
                            {pred.intensity}
                          </span>
                        </td>
                        <td>{pred.humidity_percent}</td>
                        <td>{pred.wind_speed_kmh}</td>
                        <td>{pred.wind_direction || 'N/A'}</td>
                        <td>{pred.air_pressure_hpa}</td>
                        <td>{(pred.confidence_score * 100).toFixed(0)}%</td>
                      </tr>
                    ))
                  )}
                </tbody>
              </table>
            </div>
          )}
        </>
      )}
    </div>
  )
}

export default RainfallData
