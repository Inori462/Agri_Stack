import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useTranslation } from 'react-i18next'
import { useAuth } from '../context/AuthContext'

const DEMOS = [
  { label: 'Farmer', email: 'farmer@agristack.org', password: 'AgriStack@Farmer2026' },
  { label: 'Investor', email: 'investor@agristack.org', password: 'AgriStack@Investor2026' },
  { label: 'Admin', email: 'admin@agristack.org', password: 'AgriStack@Admin2026' },
  { label: 'Gov officer', email: 'gov@agristack.org', password: 'AgriStack@Gov2026' },
]

export default function Login() {
  const { t } = useTranslation()
  const { login } = useAuth()
  const navigate = useNavigate()
  const [email, setEmail] = useState('farmer@agristack.org')
  const [password, setPassword] = useState('AgriStack@Farmer2026')
  const [error, setError] = useState('')

  const onSubmit = async (e) => {
    e.preventDefault()
    setError('')
    try {
      await login(email, password)
      navigate('/app/dashboard')
    } catch (err) {
      setError(err.response?.data?.error?.message || 'Login failed')
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-emerald-50 p-4">
      <form onSubmit={onSubmit} className="bg-white w-full max-w-md rounded-2xl shadow p-6 space-y-4">
        <h1 className="text-xl font-semibold text-agri-900">{t('login')}</h1>
        <input className="w-full rounded-md" value={email} onChange={(e) => setEmail(e.target.value)} placeholder={t('email')} />
        <input type="password" className="w-full rounded-md" value={password} onChange={(e) => setPassword(e.target.value)} placeholder={t('password')} />
        {error && <p className="text-red-600 text-sm">{error}</p>}
        <button className="w-full bg-agri-700 text-white rounded-md py-2">{t('login')}</button>
        <p className="text-xs text-slate-500">Demo accounts</p>
        <div className="grid grid-cols-2 gap-2">
          {DEMOS.map((d) => (
            <button
              type="button"
              key={d.email}
              className="text-xs border rounded-md py-2"
              onClick={() => {
                setEmail(d.email)
                setPassword(d.password)
              }}
            >
              {d.label}
            </button>
          ))}
        </div>
        <Link className="block text-center text-sm text-agri-700" to="/register">{t('register')}</Link>
      </form>
    </div>
  )
}
