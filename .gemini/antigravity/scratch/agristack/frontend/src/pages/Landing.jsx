import { Link } from 'react-router-dom'
import { useTranslation } from 'react-i18next'

export default function Landing() {
  const { t } = useTranslation()
  return (
    <div className="min-h-screen bg-gradient-to-b from-emerald-900 to-emerald-700 text-white">
      <header className="flex justify-between items-center px-6 py-4">
        <strong>{t('brand')}</strong>
        <div className="space-x-3 text-sm">
          <Link to="/login" className="underline">{t('login')}</Link>
          <Link to="/register" className="bg-white text-emerald-800 rounded-md px-3 py-1">{t('register')}</Link>
        </div>
      </header>
      <section className="max-w-4xl mx-auto px-6 py-20">
        <h1 className="text-4xl md:text-5xl font-semibold mb-4">{t('tagline')}</h1>
        <p className="text-emerald-100 max-w-2xl mb-8">
          Fractional crop-cycle enterprises with 100 digital shares, SHA-256 ownership ledger,
          Razorpay sandbox escrow, Sentinel-2 NDVI, and multilingual AI.
        </p>
        <p className="text-amber-200 text-sm mb-8">{t('pilot')}</p>
        <div className="grid md:grid-cols-3 gap-4 text-sm">
          <div className="bg-white/10 rounded-xl p-4">Farmer onboarding with Aadhaar masking & 7/12 Satbara</div>
          <div className="bg-white/10 rounded-xl p-4">Investor checkout, marketplace, pro-rata settlement</div>
          <div className="bg-white/10 rounded-xl p-4">Admin KYC queue, insurance claims, gov heatmap</div>
        </div>
      </section>
    </div>
  )
}
