import { useEffect, useState } from 'react'
import { CircleMarker, MapContainer, Popup, TileLayer } from 'react-leaflet'
import api from '../services/api'

export default function GovSocietyDashboard() {
  const [data, setData] = useState(null)
  useEffect(() => {
    api.get('/gov/heatmap').then((r) => setData(r.data)).catch(() => setData(null))
  }, [])

  return (
    <div className="space-y-4">
      <h1 className="text-xl font-semibold">Government / society heatmap</h1>
      <p className="text-xs text-slate-600">{data?.disclaimer}</p>
      <MapContainer center={[19.5, 75.5]} zoom={6} style={{ height: 420 }}>
        <TileLayer url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png" />
        {(data?.points || []).map((p) => (
          <CircleMarker key={p.district} center={[p.lat, p.lng]} radius={8 + p.project_count} color={p.risk_band === 'HIGH' ? '#b91c1c' : p.risk_band === 'MEDIUM' ? '#ca8a04' : '#166534'}>
            <Popup>
              {p.district}: {p.project_count} projects, risk {p.avg_risk} ({p.risk_band})
            </Popup>
          </CircleMarker>
        ))}
      </MapContainer>
    </div>
  )
}
