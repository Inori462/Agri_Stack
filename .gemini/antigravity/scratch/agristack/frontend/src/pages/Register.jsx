import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useTranslation } from 'react-i18next'
import { useAuth } from '../context/AuthContext'

export default function Register() {
  const { t } = useTranslation()
  const { register } = useAuth()
  const navigate = useNavigate()
  const [form, setForm] = useState({
    email: '',
    phone_number: '+91',
    password: '',
    full_name: '',
    primary_role: 'FARMER',
    preferred_language: 'en',
  })
  const [error, setError] = useState('')
  const set = (k, v) => setForm((f) => ({ ...f, [k]: v }))

  const onSubmit = async (e) => {
    e.preventDefault()
    setError('')
    try {
      await register(form)
      navigate('/app/dashboard')
    } catch (err) {
      setError(err.response?.data?.error?.message || 'Registration failed')
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-emerald-50 p-4">
      <form onSubmit={onSubmit} className="bg-white w-full max-w-md rounded-2xl shadow p-6 space-y-3">
        <h1 className="text-xl font-semibold">{t('register')}</h1>
        {['full_name', 'email', 'phone_number', 'password'].map((k) => (
          <input
            key={k}
            type={k === 'password' ? 'password' : 'text'}
            className="w-full rounded-md"
            placeholder={k}
            value={form[k]}
            onChange={(e) => set(k, e.target.value)}
          />
        ))}
        <select className="w-full rounded-md" value={form.primary_role} onChange={(e) => set('primary_role', e.target.value)}>
          <option value="FARMER">Farmer</option>
          <option value="INVESTOR">Investor</option>
          <option value="GOV_OFFICER">Gov officer</option>
        </select>
        {error && <p className="text-red-600 text-sm">{error}</p>}
        <button className="w-full bg-agri-700 text-white rounded-md py-2">{t('register')}</button>
      </form>
    </div>
  )
}
