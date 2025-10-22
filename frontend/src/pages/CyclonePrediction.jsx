// Cyclone prediction page: view historical cyclone tracks and generate new
// deterministic predictions. Uses `/api/cyclone-predictions/` endpoints.
import { useState, useEffect } from 'react'
import { getCyclonePredictions, predictCyclone } from '../services/api'
import Map from '../components/Map'
import { formatRiskScore } from '../utils/riskUtils'
import './Prediction.css'

function CyclonePrediction() {
  const [predictions, setPredictions] = useState([])
  const [selectedYear, setSelectedYear] = useState(new Date().getFullYear())
  const [loading, setLoading] = useState(false)
  const [predicting, setPredicting] = useState(false)

  useEffect(() => {
    fetchPredictions()
  }, [selectedYear])

  const fetchPredictions = async () => {
    setLoading(true)
    try {
      const startDate = `${selectedYear}-01-01`
      const endDate = `${selectedYear}-12-31`

      const response = await getCyclonePredictions({ start_date: startDate, end_date: endDate })
      setPredictions(response.data.results || response.data || [])
    } catch (error) {
      console.error('Error fetching predictions:', error)
    } finally {
      setLoading(false)
    }
  }

  const handlePredict = async () => {
    setPredicting(true)
    try {
      const response = await predictCyclone({
        latitude: 15.0,
        longitude: 120.0,
        wind_speed: 150,
        pressure: 960,
        name: 'Prediction Test'
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

  const getMapData = () => {
    if (predictions.length === 0) return { center: [20, 100], markers: [], paths: [] }

    const mostRecent = predictions[0]
    const paths = []

    if (mostRecent.path_coordinates && mostRecent.path_coordinates.length > 0) {
      paths.push({
        coordinates: mostRecent.path_coordinates.map(coord => [coord.latitude, coord.longitude]),
        color: '#ef4444',
        weight: 4
      })
    }

    const center = mostRecent.path_coordinates?.[0]
      ? [mostRecent.path_coordinates[0].latitude, mostRecent.path_coordinates[0].longitude]
      : [20, 100]

    return { center, markers: [], paths }
  }

  const mapData = getMapData()

  return (
    <div className="prediction-page">
      <div className="page-header">
        <h1>Cyclone Predictions</h1>
        <div className="controls">
          <select value={selectedYear} onChange={(e) => setSelectedYear(Number(e.target.value))}>
            {[...Array(5)].map((_, i) => {
              const year = new Date().getFullYear() - i
              return <option key={year} value={year}>{year}</option>
            })}
          </select>
          <button onClick={handlePredict} disabled={predicting} className="btn-predict">
            {predicting ? 'Predicting...' : 'Generate New Prediction'}
          </button>
        </div>
      </div>

      {loading ? (
        <div className="loading">Loading predictions...</div>
      ) : (
        <>
          <div className="map-container-section">
            <Map center={mapData.center} zoom={5} paths={mapData.paths} markers={mapData.markers} />
          </div>

          <div className="predictions-list">
            <h2>Historical Predictions</h2>
            {predictions.length === 0 ? (
              <p className="no-data">No predictions available for {selectedYear}</p>
            ) : (
              <div className="predictions-grid">
                {predictions.map((pred) => (
                  <div key={pred.id} className="prediction-card">
                    <h3>{pred.cyclone_name || 'Unnamed'}</h3>
                    <div className="prediction-details">
                      <p><strong>Date:</strong> {pred.prediction_date}</p>
                      <p><strong>Category:</strong> {pred.category}</p>
                      <p><strong>Max Wind Speed:</strong> {pred.max_wind_speed_kmh} km/h</p>
                      <p><strong>Central Pressure:</strong> {pred.central_pressure_hpa} hPa</p>
                      <p>
                        <strong>Risk Score:</strong>{' '}
                        <span className={`risk-badge risk-${pred.risk_category.toLowerCase()}`}>
                          {formatRiskScore(pred.risk_score)}
                        </span>
                      </p>
                      <p><strong>Risk Category:</strong> {pred.risk_category}</p>
                      <p><strong>Confidence:</strong> {(pred.confidence_score * 100).toFixed(0)}%</p>
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

export default CyclonePrediction
