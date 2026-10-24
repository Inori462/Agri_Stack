import { useState } from 'react'
import api from '../services/api'

export default function AIInsights() {
  const [yieldRes, setYieldRes] = useState(null)
  const [price, setPrice] = useState(null)
  const [risk, setRisk] = useState(null)

  const run = async () => {
    const y = await api.post('/predictions/yield', { crop: 'Soybean', acres: 5, soil_type: 'Black Cotton', irrigation_source: 'Drip', season: 'Kharif' })
    const p = await api.post('/predictions/market-price', { crop: 'Soybean', harvest_month: 10 })
    const r = await api.post('/predictions/risk-score', {})
    setYieldRes(y.data)
    setPrice(p.data)
    setRisk(r.data)
  }

  return (
    <div className="space-y-4">
      <h1 className="text-xl font-semibold">AI insights</h1>
      <button className="bg-agri-700 text-white rounded-md px-4 py-2" onClick={run}>Run yield, APMC price & risk models</button>
      <div className="grid md:grid-cols-3 gap-4">
        <Card title="Yield predictor" data={yieldRes} />
        <Card title="APMC price" data={price} />
        <Card title="Explainable risk 0–100" data={risk} />
      </div>
    </div>
  )
}

function Card({ title, data }) {
  return (
    <div className="bg-white rounded-2xl p-4 shadow">
      <h2 className="font-semibold mb-2">{title}</h2>
      <pre className="text-xs whitespace-pre-wrap">{data ? JSON.stringify(data, null, 2) : 'Run models to view.'}</pre>
    </div>
  )
}
