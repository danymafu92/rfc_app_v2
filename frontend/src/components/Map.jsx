// Map component using react-leaflet. Renders markers, circle markers and
// polylines and uses `utils/riskUtils.js` to style risk-based markers.
import { MapContainer, TileLayer, Marker, Popup, CircleMarker, Polyline } from 'react-leaflet'
import { getRiskColor, formatRiskScore } from '../utils/riskUtils'
import 'leaflet/dist/leaflet.css'
import './Map.css'

function Map({ center = [20, 0], zoom = 2, markers = [], paths = [], className = '' }) {
  return (
    <MapContainer center={center} zoom={zoom} className={`map-container ${className}`}>
      <TileLayer
        attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
        url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
      />

      {markers.map((marker, idx) => (
        marker.type === 'circle' ? (
          <CircleMarker
            key={idx}
            center={[marker.lat, marker.lng]}
            radius={marker.radius || 10}
            fillColor={marker.riskScore ? getRiskColor(marker.riskScore) : '#3b82f6'}
            color={marker.riskScore ? getRiskColor(marker.riskScore) : '#3b82f6'}
            fillOpacity={0.6}
          >
            {marker.popup && (
              <Popup>
                <div className="map-popup">
                  <h3>{marker.popup.title}</h3>
                  {marker.popup.content}
                  {marker.riskScore && (
                    <div className="risk-badge" style={{ backgroundColor: getRiskColor(marker.riskScore) }}>
                      Risk Score: {formatRiskScore(marker.riskScore)}
                    </div>
                  )}
                </div>
              </Popup>
            )}
          </CircleMarker>
        ) : (
          <Marker key={idx} position={[marker.lat, marker.lng]}>
            {marker.popup && (
              <Popup>
                <div className="map-popup">
                  <h3>{marker.popup.title}</h3>
                  {marker.popup.content}
                </div>
              </Popup>
            )}
          </Marker>
        )
      ))}

      {paths.map((path, idx) => (
        <Polyline
          key={idx}
          positions={path.coordinates}
          color={path.color || '#3b82f6'}
          weight={path.weight || 3}
          opacity={0.7}
        />
      ))}
    </MapContainer>
  )
}

export default Map
