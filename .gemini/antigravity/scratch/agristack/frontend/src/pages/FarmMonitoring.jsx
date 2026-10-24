import { useEffect, useState } from 'react'
import { MapContainer, TileLayer, GeoJSON } from 'react-leaflet'
import api from '../services/api'

export default function FarmMonitoring() {
  const [farms, setFarms] = useState([])
  const [ndvi, setNdvi] = useState(null)
  const [records, setRecords] = useState([])
  const [projects, setProjects] = useState([])

  useEffect(() => {
    api.get('/farms').then((r) => setFarms(r.data)).catch(() => setFarms([]))
    api.get('/projects').then((r) => {
      setProjects(r.data)
      if (r.data[0]) api.get(`/monitoring/records/${r.data[0].id}`).then((x) => setRecords(x.data)).catch(() => {})
    })
  }, [])

  const parcel = farms[0]?.parcels?.[0]
  useEffect(() => {
    if (parcel) api.get(`/monitoring/satellite-ndvi/${parcel.id}`).then((r) => setNdvi(r.data)).catch(() => {})
  }, [parcel])

  const center = parcel ? [Number(parcel.center_latitude), Number(parcel.center_longitude)] : [18.52, 73.85]

  return (
    <div className="space-y-4">
      <h1 className="text-xl font-semibold">Farm monitoring</h1>
      <MapContainer center={center} zoom={14}>
        <TileLayer url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png" />
        {parcel?.boundary_geojson && <GeoJSON data={parcel.boundary_geojson} />}
      </MapContainer>
      {ndvi && (
        <div className="bg-white rounded-2xl p-4 shadow text-sm">
          <p>NDVI: {ndvi.ndvi ?? ndvi.current_ndvi ?? JSON.stringify(ndvi).slice(0, 180)}</p>
        </div>
      )}
      <div className="bg-white rounded-2xl p-4 shadow">
        <h2 className="font-semibold mb-2">Activity records</h2>
        {records.map((r) => (
          <p key={r.id} className="text-sm">{r.activity_type} · {r.activity_date} · {r.verification_status}</p>
        ))}
        {!records.length && <p className="text-sm text-slate-500">No geotagged records yet.</p>}
      </div>
      <p className="text-xs text-slate-500">{projects.length} linked crop cycles</p>
    </div>
  )
}
