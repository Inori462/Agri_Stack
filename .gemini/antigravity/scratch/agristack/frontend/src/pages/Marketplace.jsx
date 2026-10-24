import { useEffect, useState } from 'react'
import api from '../services/api'

export default function Marketplace() {
  const [listings, setListings] = useState([])
  const [projects, setProjects] = useState([])
  const [form, setForm] = useState({ project_id: '', crop_name: 'Pomegranate', quantity_kg: 1000, asking_price_per_kg: 110, description: 'Grade A harvest' })
  const [sale, setSale] = useState({ listing_id: '', buyer_name: 'APMC Buyer', buyer_contact: '+919800112233', quantity_kg: 200, sale_price_per_kg: 135, apmc_reference_price: 100 })
  const [msg, setMsg] = useState('')

  const load = () => api.get('/marketplace/listings').then((r) => setListings(r.data))
  useEffect(() => {
    load()
    api.get('/projects').then((r) => {
      setProjects(r.data)
      if (r.data[0]) setForm((f) => ({ ...f, project_id: r.data[0].id }))
    })
  }, [])

  return (
    <div className="space-y-6">
      <h1 className="text-xl font-semibold">B2B harvest marketplace</h1>
      <form
        className="bg-white rounded-2xl p-4 shadow grid md:grid-cols-2 gap-2"
        onSubmit={async (e) => {
          e.preventDefault()
          const { data } = await api.post('/marketplace/listings', { ...form, quantity_kg: Number(form.quantity_kg), asking_price_per_kg: Number(form.asking_price_per_kg) })
          setMsg(`Listed ${data.crop_name}`)
          load()
        }}
      >
        <select className="rounded-md" value={form.project_id} onChange={(e) => setForm({ ...form, project_id: e.target.value })}>
          {projects.map((p) => <option key={p.id} value={p.id}>{p.title}</option>)}
        </select>
        <input className="rounded-md" value={form.crop_name} onChange={(e) => setForm({ ...form, crop_name: e.target.value })} />
        <input type="number" className="rounded-md" value={form.quantity_kg} onChange={(e) => setForm({ ...form, quantity_kg: e.target.value })} />
        <input type="number" className="rounded-md" value={form.asking_price_per_kg} onChange={(e) => setForm({ ...form, asking_price_per_kg: e.target.value })} />
        <button className="bg-agri-700 text-white rounded-md py-2">Create listing</button>
      </form>
      <div className="grid md:grid-cols-2 gap-3">
        {listings.map((l) => (
          <div key={l.id} className="bg-white rounded-xl p-4 shadow">
            <p className="font-medium">{l.crop_name}</p>
            <p className="text-sm">{l.quantity_kg} kg @ ₹{l.asking_price_per_kg || l.price_per_kg_inr}</p>
            <p className="text-xs">{l.status}</p>
            <button className="text-xs underline mt-2" onClick={() => setSale({ ...sale, listing_id: l.id })}>Use for sale</button>
          </div>
        ))}
      </div>
      <form
        className="bg-white rounded-2xl p-4 shadow space-y-2"
        onSubmit={async (e) => {
          e.preventDefault()
          const { data } = await api.post('/marketplace/sales', { ...sale, quantity_kg: Number(sale.quantity_kg), sale_price_per_kg: Number(sale.sale_price_per_kg), apmc_reference_price: Number(sale.apmc_reference_price) })
          setMsg(`Sale ${data.id} flagged=${data.is_flagged} amount=${data.total_amount}`)
        }}
      >
        <h2 className="font-semibold">Record sale (APMC anomaly check)</h2>
        <input className="w-full rounded-md" placeholder="listing id" value={sale.listing_id} onChange={(e) => setSale({ ...sale, listing_id: e.target.value })} />
        <input className="w-full rounded-md" value={sale.buyer_name} onChange={(e) => setSale({ ...sale, buyer_name: e.target.value })} />
        <button className="bg-agri-700 text-white rounded-md px-4 py-2">Submit sale</button>
      </form>
      {msg && <p className="text-sm text-agri-800">{msg}</p>}
    </div>
  )
}
