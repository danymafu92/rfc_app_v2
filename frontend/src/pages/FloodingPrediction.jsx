// Flooding prediction page: allows calculating flooding risk using
// deterministic inputs and fetching stored predictions from the backend.
import { useState, useEffect } from 'react'
import { getLocations, getFloodingPredictions, predictFlooding } from '../services/api'
import Map from '../components/Map'
import { formatRiskScore, getRiskColor } from '../utils/riskUtils'
import './Prediction.css'

function FloodingPrediction() {
  const [locations, setLocations] = useState([])
  const [selectedLocation, setSelectedLocation] = useState(null)
  const [predictions, setPredictions] = useState([])
  const [selectedYear, setSelectedYear] = useState(new Date().getFullYear())
  const [loading, setLoading] = useState(false)
  const [predicting, setPredicting] = useState(false)
  const [riskInputs, setRiskInputs] = useState({
    infrastructure_strength: 5.0,
    soil_moisture_retention: 5.0,
    soil_type: 'Clay',
    vegetation_density: 5.0,
    population_size: 100000,
    population_density: 1000,
    predicted_rainfall_mm: 50
  })

  useEffect(() => {
    fetchLocations()
  }, [])

  useEffect(() => {
    if (selectedLocation) {
      fetchPredictions()
    }
  }, [selectedLocation, selectedYear])

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
      const startDate = `${selectedYear}-01-01`
      const endDate = `${selectedYear}-12-31`

      const response = await getFloodingPredictions({
        location_id: selectedLocation.id,
        start_date: startDate,
        end_date: endDate
      })
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
      await predictFlooding({
        location_id: selectedLocation.id,
        ...riskInputs
      })
      alert('Prediction generated successfully!')
      fetchPredictions()
    } catch (error) {
      console.error('Error predicting:', error)
      alert('Failed to generate prediction')
    } finally {
      setPredicting(false)
    }
  }

  const getMapMarkers = () => {
    if (!selectedLocation || predictions.length === 0) return []

    return predictions.slice(0, 10).map(pred => ({
      lat: parseFloat(selectedLocation.latitude),
      lng: parseFloat(selectedLocation.longitude),
      type: 'circle',
      radius: Math.min(pred.affected_area_km2 / 5, 30) || 10,
      riskScore: pred.risk_score,
      popup: {
        title: selectedLocation.city || selectedLocation.country,
        content: (
          <div>
            <p>Date: {pred.prediction_date}</p>
            <p>Risk: {pred.risk_category}</p>
            <p>Flood Probability: {(pred.flood_probability * 100).toFixed(0)}%</p>
            <p>Affected Area: {pred.affected_area_km2} km²</p>
          </div>
        )
      }
    }))
  }

  return (
    <div className="prediction-page">
      <div className="page-header">
        <h1>Flooding Predictions</h1>
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
          <select value={selectedYear} onChange={(e) => setSelectedYear(Number(e.target.value))}>
            {[...Array(5)].map((_, i) => {
              const year = new Date().getFullYear() - i
              return <option key={year} value={year}>{year}</option>
            })}
          </select>
        </div>
      </div>

      <div className="risk-calculator">
        <h2>Calculate Flooding Risk</h2>
        <div className="input-grid">
          <div className="input-group">
            <label>Infrastructure Strength (0-10)</label>
            <input
              type="number"
              min="0"
              max="10"
              step="0.1"
              value={riskInputs.infrastructure_strength}
              onChange={(e) => setRiskInputs({...riskInputs, infrastructure_strength: parseFloat(e.target.value)})}
            />
          </div>
          <div className="input-group">
            <label>Soil Moisture Retention (0-10)</label>
            <input
              type="number"
              min="0"
              max="10"
              step="0.1"
              value={riskInputs.soil_moisture_retention}
              onChange={(e) => setRiskInputs({...riskInputs, soil_moisture_retention: parseFloat(e.target.value)})}
            />
          </div>
          <div className="input-group">
            <label>Vegetation Density (0-10)</label>
            <input
              type="number"
              min="0"
              max="10"
              step="0.1"
              value={riskInputs.vegetation_density}
              onChange={(e) => setRiskInputs({...riskInputs, vegetation_density: parseFloat(e.target.value)})}
            />
          </div>
          <div className="input-group">
            <label>Population Size</label>
            <input
              type="number"
              min="0"
              value={riskInputs.population_size}
              onChange={(e) => setRiskInputs({...riskInputs, population_size: parseInt(e.target.value)})}
            />
          </div>
          <div className="input-group">
            <label>Population Density (per km²)</label>
            <input
              type="number"
              min="0"
              step="0.1"
              value={riskInputs.population_density}
              onChange={(e) => setRiskInputs({...riskInputs, population_density: parseFloat(e.target.value)})}
            />
          </div>
          <div className="input-group">
            <label>Predicted Rainfall (mm)</label>
            <input
              type="number"
              min="0"
              step="0.1"
              value={riskInputs.predicted_rainfall_mm}
              onChange={(e) => setRiskInputs({...riskInputs, predicted_rainfall_mm: parseFloat(e.target.value)})}
            />
          </div>
        </div>
        <button onClick={handlePredict} disabled={predicting || !selectedLocation} className="btn-predict">
          {predicting ? 'Calculating...' : 'Calculate Risk'}
        </button>
      </div>

      {loading ? (
        <div className="loading">Loading predictions...</div>
      ) : (
        <>
          {selectedLocation && (
            <div className="map-container-section">
              <Map
                center={[parseFloat(selectedLocation.latitude), parseFloat(selectedLocation.longitude)]}
                zoom={8}
                markers={getMapMarkers()}
              />
            </div>
          )}

          <div className="predictions-list">
            <h2>Historical Predictions</h2>
            {predictions.length === 0 ? (
              <p className="no-data">No predictions available for {selectedYear}</p>
            ) : (
              <div className="predictions-grid">
                {predictions.map((pred) => (
                  <div key={pred.id} className="prediction-card">
                    <h3>{pred.prediction_date}</h3>
                    <div className="prediction-details">
                      <p>
                        <strong>Risk Score:</strong>{' '}
                        <span
                          className="risk-badge"
                          style={{ backgroundColor: getRiskColor(pred.risk_score) }}
                        >
                          {formatRiskScore(pred.risk_score)}
                        </span>
                      </p>
                      <p><strong>Category:</strong> {pred.risk_category}</p>
                      <p><strong>Flood Probability:</strong> {(pred.flood_probability * 100).toFixed(0)}%</p>
                      <p><strong>Mudslide Probability:</strong> {(pred.mudslide_probability * 100).toFixed(0)}%</p>
                      <p><strong>Water Level:</strong> {pred.water_level_meters} m</p>
                      <p><strong>Affected Area:</strong> {pred.affected_area_km2} km²</p>
                      <p><strong>Affected Population:</strong> {pred.affected_population.toLocaleString()}</p>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </>
      )}
    </div>
  )
}

export default FloodingPrediction
