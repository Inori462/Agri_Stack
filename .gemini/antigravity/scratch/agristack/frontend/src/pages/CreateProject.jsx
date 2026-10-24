import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import api from '../services/api'

export default function CreateProject() {
  const navigate = useNavigate()
  const [farms, setFarms] = useState([])
  const [form, setForm] = useState({
    farm_id: '',
    parcel_id: '',
    title: 'Kharif Soybean Cycle',
    crop_name: 'Soybean',
    crop_variety: 'JS 335',
    season: 'Kharif',
    sowing_date: '2026-06-15',
    estimated_harvest_date: '2026-10-20',
    total_valuation_inr: 500000,
    farmer_equity_percent: 30,
    total_shares: 100,
    expected_yield_quintals: 80,
    expected_revenue_inr: 720000,
  })
  const [error, setError] = useState('')
  const set = (k, v) => setForm((f) => ({ ...f, [k]: v }))

  useEffect(() => {
    api.get('/farms').then((r) => {
      setFarms(r.data)
      if (r.data[0]) {
        set('farm_id', r.data[0].id)
        set('parcel_id', r.data[0].parcels?.[0]?.id || '')
      }
    }).catch(() => setFarms([]))
  }, [])

  const selected = farms.find((f) => f.id === form.farm_id)

  const submit = async (e) => {
    e.preventDefault()
    setError('')
    try {
      const { data } = await api.post('/projects', {
        ...form,
        total_valuation_inr: Number(form.total_valuation_inr),
        farmer_equity_percent: Number(form.farmer_equity_percent),
        total_shares: Number(form.total_shares),
        expected_yield_quintals: Number(form.expected_yield_quintals),
        expected_revenue_inr: Number(form.expected_revenue_inr),
      })
      navigate(`/app/projects/${data.id}`)
    } catch (err) {
      setError(err.response?.data?.error?.message || 'Could not create project')
    }
  }

  return (
    <form onSubmit={submit} className="max-w-2xl bg-white rounded-2xl p-6 shadow space-y-3">
      <h1 className="text-xl font-semibold">Create crop cycle (100 shares)</h1>
      <select className="w-full rounded-md" value={form.farm_id} onChange={(e) => set('farm_id', e.target.value)}>
        {farms.map((f) => <option key={f.id} value={f.id}>{f.farm_name}</option>)}
      </select>
      <select className="w-full rounded-md" value={form.parcel_id} onChange={(e) => set('parcel_id', e.target.value)}>
        {(selected?.parcels || []).map((p) => <option key={p.id} value={p.id}>{p.survey_number}</option>)}
      </select>
      {['title', 'crop_name', 'crop_variety', 'season', 'sowing_date', 'estimated_harvest_date'].map((k) => (
        <input key={k} className="w-full rounded-md" value={form[k]} onChange={(e) => set(k, e.target.value)} />
      ))}
      <input type="number" className="w-full rounded-md" value={form.total_valuation_inr} onChange={(e) => set('total_valuation_inr', e.target.value)} />
      {error && <p className="text-red-600 text-sm">{error}</p>}
      <button className="bg-agri-700 text-white rounded-md px-4 py-2">Create project</button>
    </form>
  )
}
