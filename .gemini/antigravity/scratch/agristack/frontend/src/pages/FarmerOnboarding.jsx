import { useState } from 'react'
import api from '../services/api'

const STEPS = ['Personal KYC', '7/12 Satbara', 'DigiLocker']

export default function FarmerOnboarding() {
  const [step, setStep] = useState(0)
  const [kyc, setKyc] = useState({ aadhaar_number: '', pan_number: '', satbara_document_url: '', survey_number_claimed: '' })
  const [farm, setFarm] = useState({ farm_name: '', district: 'Pune', taluka: '', village: '', pincode: '', total_area_acres: 5 })
  const [msg, setMsg] = useState('')

  const submitKyc = async () => {
    const { data } = await api.post('/kyc/submit', kyc)
    setMsg(`KYC ${data.verification_status}, Aadhaar last4 ${data.aadhaar_last4}`)
    setStep(1)
  }

  const createFarm = async () => {
    const { data } = await api.post('/farms', { ...farm, state: 'Maharashtra', total_area_acres: Number(farm.total_area_acres) })
    setMsg(`Farm registered: ${data.farm_name}`)
    setStep(2)
  }

  const pullDigilocker = async () => {
    const { data } = await api.post('/kyc/digilocker-pull')
    setMsg(`DigiLocker URI: ${data.digilocker_uri || 'linked'}`)
  }

  return (
    <div className="max-w-xl bg-white rounded-2xl p-6 shadow space-y-4">
      <h1 className="text-xl font-semibold">Farmer onboarding wizard</h1>
      <p className="text-sm text-slate-500">Step {step + 1} / 3 — {STEPS[step]}</p>
      {step === 0 && (
        <div className="space-y-2">
          <input className="w-full rounded-md" placeholder="Aadhaar 12 digits" value={kyc.aadhaar_number} onChange={(e) => setKyc({ ...kyc, aadhaar_number: e.target.value })} />
          <input className="w-full rounded-md" placeholder="PAN" value={kyc.pan_number} onChange={(e) => setKyc({ ...kyc, pan_number: e.target.value })} />
          <input className="w-full rounded-md" placeholder="7/12 URL" value={kyc.satbara_document_url} onChange={(e) => setKyc({ ...kyc, satbara_document_url: e.target.value })} />
          <input className="w-full rounded-md" placeholder="Survey number" value={kyc.survey_number_claimed} onChange={(e) => setKyc({ ...kyc, survey_number_claimed: e.target.value })} />
          <button className="bg-agri-700 text-white rounded-md px-4 py-2" onClick={submitKyc}>Submit KYC</button>
        </div>
      )}
      {step === 1 && (
        <div className="space-y-2">
          {Object.keys(farm).map((k) => (
            <input key={k} className="w-full rounded-md" placeholder={k} value={farm[k]} onChange={(e) => setFarm({ ...farm, [k]: e.target.value })} />
          ))}
          <button className="bg-agri-700 text-white rounded-md px-4 py-2" onClick={createFarm}>Save farm</button>
        </div>
      )}
      {step === 2 && (
        <button className="bg-agri-700 text-white rounded-md px-4 py-2" onClick={pullDigilocker}>Pull DigiLocker (sandbox)</button>
      )}
      {msg && <p className="text-sm text-agri-800">{msg}</p>}
    </div>
  )
}
