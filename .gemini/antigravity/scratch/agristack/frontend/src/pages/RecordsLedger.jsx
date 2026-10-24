import { useEffect, useState } from 'react'
import api from '../services/api'

export default function RecordsLedger() {
  const [projects, setProjects] = useState([])
  const [projectId, setProjectId] = useState('')
  const [entries, setEntries] = useState([])
  const [integrity, setIntegrity] = useState(null)

  useEffect(() => {
    api.get('/projects').then((r) => {
      setProjects(r.data)
      if (r.data[0]) setProjectId(r.data[0].id)
    })
  }, [])

  useEffect(() => {
    if (!projectId) return
    api.get(`/ledger/project/${projectId}`).then((r) => setEntries(r.data)).catch(() => setEntries([]))
    api.get(`/ledger/verify-integrity/${projectId}`).then((r) => setIntegrity(r.data)).catch(() => setIntegrity(null))
  }, [projectId])

  return (
    <div className="space-y-4">
      <h1 className="text-xl font-semibold">SHA-256 ownership ledger</h1>
      <select className="rounded-md" value={projectId} onChange={(e) => setProjectId(e.target.value)}>
        {projects.map((p) => <option key={p.id} value={p.id}>{p.title}</option>)}
      </select>
      {integrity && <p className="text-sm">Chain valid: {String(integrity.is_valid)} · {integrity.entries_audited} entries</p>}
      <div className="bg-white rounded-2xl p-4 shadow overflow-x-auto">
        <table className="w-full text-xs">
          <thead><tr><th>seq</th><th>type</th><th>shares</th><th>hash</th></tr></thead>
          <tbody>
            {entries.map((e) => (
              <tr key={e.entry_id} className="border-t">
                <td>{e.sequence_id}</td>
                <td>{e.transaction_type}</td>
                <td>{e.shares_count}</td>
                <td className="font-mono">{e.entry_hash?.slice(0, 16)}…</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}
