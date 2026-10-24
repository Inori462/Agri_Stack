import { useEffect, useState } from 'react'
import { useParams } from 'react-router-dom'
import { MapContainer, TileLayer } from 'react-leaflet'
import api from '../services/api'

export default function ProjectDetail() {
  const { id } = useParams()
  const [project, setProject] = useState(null)
  const [shares, setShares] = useState(5)
  const [msg, setMsg] = useState('')
  const [milestones, setMilestones] = useState([])

  useEffect(() => {
    api.get(`/projects/${id}`).then((r) => setProject(r.data))
    api.get(`/projects/${id}/milestones`).then((r) => setMilestones(r.data)).catch(() => [])
  }, [id])

  const checkout = async () => {
    const order = await api.post('/payments/orders', { project_id: id, num_shares: Number(shares) })
    const verify = await api.post('/payments/verify', {
      razorpay_order_id: order.data.razorpay_order_id,
      razorpay_payment_id: `pay_ui_${Date.now()}`,
      razorpay_signature: 'test_sig_checkout',
    })
    setMsg(`Allocated ${verify.data.shares_purchased} shares. Ledger ${verify.data.ledger_entry_hash?.slice(0, 16)}…`)
  }

  if (!project) return <p>Loading…</p>

  return (
    <div className="space-y-4">
      <h1 className="text-2xl font-semibold">{project.title}</h1>
      <p className="text-sm">{project.crop_name} · {project.status} · ₹{project.share_price_inr} / share</p>
      <MapContainer center={[18.52, 73.85]} zoom={12}>
        <TileLayer url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png" />
      </MapContainer>
      <div className="bg-white rounded-2xl p-4 shadow">
        <h2 className="font-semibold mb-2">Escrow 40 / 40 / 20</h2>
        {milestones.map((m) => (
          <p key={m.id} className="text-sm">{m.name}: ₹{m.amount_inr} ({m.status})</p>
        ))}
      </div>
      <div className="bg-white rounded-2xl p-4 shadow space-y-2">
        <h2 className="font-semibold">Investor checkout (Razorpay sandbox)</h2>
        <input type="number" className="rounded-md" value={shares} onChange={(e) => setShares(e.target.value)} />
        <button className="bg-agri-700 text-white rounded-md px-4 py-2" onClick={checkout}>Pay & allocate shares</button>
        {msg && <p className="text-sm text-agri-800">{msg}</p>}
      </div>
    </div>
  )
}
