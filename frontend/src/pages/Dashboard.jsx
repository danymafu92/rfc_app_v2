// Dashboard aggregates recent predictions (rainfall, flooding, cyclone) and
// exposes a map overview. Fetches multiple endpoints in parallel for speed.
import { useState, useEffect } from 'react'
import { getLocations, getRainfallPredictions, getFloodingPredictions, getCyclonePredictions } from '../services/api'
import Map from '../components/Map'
import { getRiskColor, formatRiskScore } from '../utils/riskUtils'
import './Dashboard.css'

function Dashboard() {
  const [locations, setLocations] = useState([])
  const [selectedLocation, setSelectedLocation] = useState(null)
  const [recentData, setRecentData] = useState({
    rainfall: null,
    flooding: null,
    cyclone: null,
  })
  const [loading, setLoading] = useState(true)
  const [showLocationPrompt, setShowLocationPrompt] = useState(false)

  useEffect(() => {
    fetchLocations()
  }, [])

  useEffect(() => {
    if (selectedLocation) {
      fetchRecentData()
    }
  }, [selectedLocation])

  const fetchLocations = async () => {
    try {
      const response = await getLocations()
      setLocations(response.data.results || response.data)
      if (response.data.results?.length > 0 || response.data.length > 0) {
        setSelectedLocation((response.data.results || response.data)[0])
      } else {
        setShowLocationPrompt(true)
      }
    } catch (error) {
      console.error('Error fetching locations:', error)
      setShowLocationPrompt(true)
    } finally {
      setLoading(false)
    }
  }

  const fetchRecentData = async () => {
    if (!selectedLocation) return

    try {
      const oneYearAgo = new Date()
      oneYearAgo.setFullYear(oneYearAgo.getFullYear() - 1)

      const [rainfall, flooding, cyclone] = await Promise.all([
        getRainfallPredictions({
          location_id: selectedLocation.id,
          start_date: oneYearAgo.toISOString().split('T')[0],
          is_historical: true
        }),
        getFloodingPredictions({
          location_id: selectedLocation.id,
          start_date: oneYearAgo.toISOString().split('T')[0],
          is_historical: true
        }),
        getCyclonePredictions({
          start_date: oneYearAgo.toISOString().split('T')[0],
          is_historical: true
        })
      ])

      setRecentData({
        rainfall: rainfall.data.results?.[0] || null,
        flooding: flooding.data.results?.[0] || null,
        cyclone: cyclone.data.results?.[0] || null,
      })
    } catch (error) {
      console.error('Error fetching recent data:', error)
    }
  }

  const getMapMarkers = () => {
    const markers = []

    if (selectedLocation && recentData.flooding) {
      markers.push({
        lat: parseFloat(selectedLocation.latitude),
        lng: parseFloat(selectedLocation.longitude),
        type: 'circle',
        radius: 15,
        riskScore: recentData.flooding.risk_score,
        popup: {
          title: selectedLocation.city || selectedLocation.country,
          content: (
            <div>
              <p>Flooding Risk: {recentData.flooding.risk_category}</p>
              <p>Probability: {(recentData.flooding.flood_probability * 100).toFixed(0)}%</p>
            </div>
          )
        }
      })
    }

    return markers
  }

  if (loading) {
    return <div className="loading">Loading dashboard...</div>
  }

  if (showLocationPrompt) {
    return (
      <div className="dashboard">
        <div className="location-prompt">
          <h2>No Recent Data Available</h2>
          <p>Please select a different location to view predictions.</p>
          <select
            onChange={(e) => {
              const location = locations.find(l => l.id === e.target.value)
              setSelectedLocation(location)
              setShowLocationPrompt(false)
            }}
            className="location-select"
          >
            <option value="">Select a location</option>
            {locations.map(loc => (
              <option key={loc.id} value={loc.id}>
                {loc.city ? `${loc.city}, ${loc.country}` : loc.country}
              </option>
            ))}
          </select>
        </div>
      </div>
    )
  }

  return (
    <div className="dashboard">
      <div className="dashboard-header">
        <h1>Dashboard</h1>
        <div className="location-selector">
          <label>Location:</label>
          <select
            value={selectedLocation?.id || ''}
            onChange={(e) => {
              const location = locations.find(l => l.id === e.target.value)
              setSelectedLocation(location)
            }}
          >
            {locations.map(loc => (
              <option key={loc.id} value={loc.id}>
                {loc.city ? `${loc.city}, ${loc.country}` : loc.country}
              </option>
            ))}
          </select>
        </div>
      </div>

      <div className="dashboard-cards">
        <div className="card">
          <h3>Recent Rainfall</h3>
          {recentData.rainfall ? (
            <div>
              <p className="big-number">{recentData.rainfall.predicted_rainfall_mm} mm</p>
              <p className="label">Intensity: {recentData.rainfall.intensity}</p>
              <p className="label">Date: {recentData.rainfall.prediction_date}</p>
            </div>
          ) : (
            <p className="no-data">No recent data available</p>
          )}
        </div>

        <div className="card">
          <h3>Flooding Risk</h3>
          {recentData.flooding ? (
            <div>
              <div
                className="risk-badge"
                style={{ backgroundColor: getRiskColor(recentData.flooding.risk_score) }}
              >
                {formatRiskScore(recentData.flooding.risk_score)}
              </div>
              <p className="label">Category: {recentData.flooding.risk_category}</p>
              <p className="label">Probability: {(recentData.flooding.flood_probability * 100).toFixed(0)}%</p>
            </div>
          ) : (
            <p className="no-data">No recent data available</p>
          )}
        </div>

        <div className="card">
          <h3>Cyclone Activity</h3>
          {recentData.cyclone ? (
            <div>
              <p className="big-number">Category {recentData.cyclone.category}</p>
              <p className="label">Name: {recentData.cyclone.cyclone_name}</p>
              <div
                className="risk-badge"
                style={{ backgroundColor: getRiskColor(recentData.cyclone.risk_score) }}
              >
                Risk: {formatRiskScore(recentData.cyclone.risk_score)}
              </div>
            </div>
          ) : (
            <p className="no-data">No recent cyclone activity</p>
          )}
        </div>
      </div>

      <div className="map-section">
        <h2>Recent Events Map</h2>
        {selectedLocation && (
          <Map
            center={[parseFloat(selectedLocation.latitude), parseFloat(selectedLocation.longitude)]}
            zoom={8}
            markers={getMapMarkers()}
          />
        )}
      </div>
    </div>
  )
}

export default Dashboard
