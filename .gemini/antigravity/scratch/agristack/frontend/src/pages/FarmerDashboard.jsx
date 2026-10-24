import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import api from '../services/api'
import { useAuth } from '../context/AuthContext'

export default function FarmerDashboard() {
  const { user } = useAuth()
  const [projects, setProjects] = useState([])
  const [investments, setInvestments] = useState([])
  const [listings, setListings] = useState([])

  useEffect(() => {
    api.get('/projects').then((r) => setProjects(r.data)).catch(() => setProjects([]))
    api.get('/payments/my-investments').then((r) => setInvestments(r.data)).catch(() => setInvestments([]))
    api.get('/marketplace/listings').then((r) => setListings(r.data)).catch(() => setListings([]))
  }, [])

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-semibold">Welcome, {user?.full_name}</h1>
      <div className="grid md:grid-cols-3 gap-4">
        <Stat title="Projects" value={projects.length} />
        <Stat title="Holdings / investments" value={investments.length} />
        <Stat title="Live listings" value={listings.length} />
      </div>
      <section className="bg-white rounded-2xl p-4 shadow">
        <h2 className="font-semibold mb-3">Crop cycles</h2>
        <div className="space-y-2">
          {projects.map((p) => (
            <Link key={p.id} to={`/app/projects/${p.id}`} className="flex justify-between border rounded-lg p-3 hover:bg-emerald-50">
              <span>{p.title} · {p.crop_name}</span>
              <span className="text-sm text-agri-800">{p.status} · {p.funded_shares}/{p.total_shares} shares</span>
            </Link>
          ))}
          {!projects.length && <p className="text-sm text-slate-500">No projects yet. Create one after onboarding.</p>}
        </div>
      </section>
    </div>
  )
}

function Stat({ title, value }) {
  return (
    <div className="bg-white rounded-2xl p-4 shadow">
      <p className="text-xs text-slate-500">{title}</p>
      <p className="text-2xl font-semibold text-agri-800">{value}</p>
    </div>
  )
}
