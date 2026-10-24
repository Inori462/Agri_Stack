import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import api from '../services/api'

export default function InvestorDiscovery() {
  const [projects, setProjects] = useState([])
  const [crop, setCrop] = useState('')

  useEffect(() => {
    const params = { status: 'OPEN_FOR_FUNDING' }
    if (crop) params.crop = crop
    api.get('/projects', { params }).then((r) => setProjects(r.data)).catch(() => setProjects([]))
  }, [crop])

  const band = (score) => (score < 35 ? 'Low' : score < 65 ? 'Medium' : 'High')

  return (
    <div className="space-y-4">
      <h1 className="text-xl font-semibold">Investor discovery</h1>
      <input className="rounded-md" placeholder="Filter crop" value={crop} onChange={(e) => setCrop(e.target.value)} />
      <div className="grid md:grid-cols-2 gap-4">
        {projects.map((p) => (
          <Link key={p.id} to={`/app/projects/${p.id}`} className="bg-white rounded-2xl p-4 shadow block">
            <p className="font-semibold">{p.title}</p>
            <p className="text-sm">{p.crop_name} · ₹{p.share_price_inr}/share</p>
            <p className="text-xs">Risk {p.risk_score} ({band(p.risk_score)}) · funded {p.funded_shares}/{p.total_shares}</p>
          </Link>
        ))}
        {!projects.length && <p className="text-sm text-slate-500">No open projects. Ask admin to move a cycle to OPEN_FOR_FUNDING.</p>}
      </div>
    </div>
  )
}
