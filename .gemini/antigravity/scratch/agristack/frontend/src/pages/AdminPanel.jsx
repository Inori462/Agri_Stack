import { useEffect, useState } from 'react'
import api from '../services/api'

export default function AdminPanel() {
  const [overview, setOverview] = useState(null)
  const [kyc, setKyc] = useState([])
  const [claims, setClaims] = useState([])
  const [disputes, setDisputes] = useState([])
  const [projects, setProjects] = useState([])
  const [msg, setMsg] = useState('')

  const load = () => {
    api.get('/admin/overview').then((r) => setOverview(r.data))
    api.get('/kyc/admin/queue').then((r) => setKyc(r.data)).catch(() => [])
    api.get('/disputes/crop-failure/pending').then((r) => setClaims(r.data)).catch(() => [])
    api.get('/disputes/open').then((r) => setDisputes(r.data)).catch(() => [])
    api.get('/projects').then((r) => setProjects(r.data))
  }
  useEffect(load, [])

  return (
    <div className="space-y-6">
      <h1 className="text-xl font-semibold">Admin panel</h1>
      {overview && <pre className="bg-white rounded-2xl p-4 text-xs">{JSON.stringify(overview, null, 2)}</pre>}
      <section className="bg-white rounded-2xl p-4 shadow">
        <h2 className="font-semibold mb-2">KYC queue</h2>
        {kyc.map((k) => (
          <div key={k.id} className="flex justify-between text-sm border-b py-2">
            <span>{k.aadhaar_last4} · {k.verification_status}</span>
            <button className="text-agri-700" onClick={async () => {
              await api.post(`/kyc/admin/${k.id}/decision`, { decision: 'VERIFIED' })
              load()
            }}>Verify</button>
          </div>
        ))}
      </section>
      <section className="bg-white rounded-2xl p-4 shadow">
        <h2 className="font-semibold mb-2">Insurance claims</h2>
        {claims.map((c) => (
          <div key={c.id} className="text-sm flex justify-between py-2">
            <span>{c.failure_reason} · {c.affected_area_pct}%</span>
            <button onClick={async () => {
              await api.patch(`/disputes/crop-failure/${c.id}/review`, { decision: 'APPROVED', insurance_approved_amount: 100000 })
              load()
            }}>Approve</button>
          </div>
        ))}
      </section>
      <section className="bg-white rounded-2xl p-4 shadow">
        <h2 className="font-semibold mb-2">Open disputes</h2>
        {disputes.map((d) => <p key={d.id} className="text-sm">{d.dispute_type}: {d.description}</p>)}
      </section>
      <section className="bg-white rounded-2xl p-4 shadow space-y-2">
        <h2 className="font-semibold">Advance project / settle</h2>
        {projects.slice(0, 8).map((p) => (
          <div key={p.id} className="text-sm flex gap-2 items-center">
            <span className="flex-1">{p.title} ({p.status})</span>
            <button className="underline" onClick={async () => {
              const order = ['SUBMITTED', 'UNDER_VERIFICATION', 'VERIFIED', 'OPEN_FOR_FUNDING', 'FUNDED', 'IN_PROGRESS', 'HARVESTED', 'SOLD']
              const next = order[order.indexOf(p.status) + 1]
              if (!next) return
              await api.post(`/projects/${p.id}/transition`, { next_state: next, remarks: `Admin to ${next}` })
              load()
            }}>Next state</button>
            <button className="underline" onClick={async () => {
              const { data } = await api.post('/settlements/', { project_id: p.id, gross_revenue: 1000000, total_expenses: 300000, insurance_recovered: 0 })
              setMsg(`Settled net ${data.net_distributable}`)
            }}>Settle</button>
          </div>
        ))}
        {msg && <p className="text-agri-800 text-sm">{msg}</p>}
      </section>
    </div>
  )
}
