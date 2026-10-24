import { useEffect, useState } from 'react'
import { Doughnut } from 'react-chartjs-2'
import { Chart as ChartJS, ArcElement, Tooltip, Legend } from 'chart.js'
import api from '../services/api'

ChartJS.register(ArcElement, Tooltip, Legend)

export default function OwnershipShares() {
  const [projects, setProjects] = useState([])
  const [holdings, setHoldings] = useState([])
  const [projectId, setProjectId] = useState('')

  useEffect(() => {
    api.get('/projects').then((r) => {
      setProjects(r.data)
      if (r.data[0]) setProjectId(r.data[0].id)
    })
  }, [])

  useEffect(() => {
    if (projectId) api.get(`/projects/${projectId}/shares`).then((r) => setHoldings(r.data)).catch(() => setHoldings([]))
  }, [projectId])

  const data = {
    labels: holdings.map((h) => h.holding_type),
    datasets: [{ data: holdings.map((h) => h.share_count), backgroundColor: ['#166534', '#22c55e', '#86efac', '#facc15'] }],
  }

  return (
    <div className="grid md:grid-cols-2 gap-6">
      <div className="bg-white rounded-2xl p-4 shadow">
        <h1 className="font-semibold mb-3">Ownership donut</h1>
        <select className="w-full rounded-md mb-4" value={projectId} onChange={(e) => setProjectId(e.target.value)}>
          {projects.map((p) => <option key={p.id} value={p.id}>{p.title}</option>)}
        </select>
        {holdings.length ? <Doughnut data={data} /> : <p className="text-sm text-slate-500">No cap table yet.</p>}
      </div>
      <div className="bg-white rounded-2xl p-4 shadow">
        <h2 className="font-semibold mb-2">Cap table</h2>
        {holdings.map((h) => (
          <p key={h.id} className="text-sm">{h.holding_type}: {h.share_count} ({h.share_percentage}%)</p>
        ))}
      </div>
    </div>
  )
}
