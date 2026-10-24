import { useEffect, useState } from 'react'
import api from '../services/api'

export default function Reports() {
  const [projects, setProjects] = useState([])
  const [report, setReport] = useState(null)
  const [payouts, setPayouts] = useState([])

  useEffect(() => {
    api.get('/projects').then((r) => setProjects(r.data))
    api.get('/settlements/my-payouts').then((r) => setPayouts(r.data)).catch(() => [])
  }, [])

  return (
    <div className="space-y-4">
      <h1 className="text-xl font-semibold">P&L and payouts</h1>
      <select className="rounded-md" onChange={async (e) => {
        if (e.target.value) setReport((await api.get(`/reports/project/${e.target.value}`)).data)
      }}>
        <option value="">Select project</option>
        {projects.map((p) => <option key={p.id} value={p.id}>{p.title}</option>)}
      </select>
      {report && <pre className="bg-white rounded-2xl p-4 text-xs overflow-auto">{JSON.stringify(report, null, 2)}</pre>}
      <div className="bg-white rounded-2xl p-4 shadow">
        <h2 className="font-semibold mb-2">My payouts</h2>
        {payouts.map((p) => (
          <p key={p.id} className="text-sm">{p.shares_held} shares · ₹{p.payout_amount || p.payout_amount_inr} · {p.status}</p>
        ))}
        {!payouts.length && <p className="text-sm text-slate-500">No investor payouts yet.</p>}
      </div>
    </div>
  )
}
