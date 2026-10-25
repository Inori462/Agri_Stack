
import { Link } from 'react-router-dom'
import { useTranslation } from 'react-i18next'

export default function Landing() {
  const { t } = useTranslation()

  return (
    <div className="min-h-screen bg-gradient-to-b from-emerald-900 to-emerald-700 text-white">
      <header className="flex justify-between items-center px-6 py-4">
        <strong className="text-xl font-bold tracking-wide">
          AgriStack
        </strong>

        <div className="space-x-3 text-sm">
          <Link to="/login" className="underline">
            {t('login')}
          </Link>

          <Link
            to="/register"
            className="bg-white text-emerald-800 rounded-md px-3 py-2 font-medium"
          >
            {t('register')}
          </Link>
        </div>
      </header>

      <section className="max-w-4xl mx-auto px-6 py-20">
        <p className="text-emerald-200 font-medium mb-3">
          SMART FARMING · SHARED GROWTH
        </p>

        <h1 className="text-4xl md:text-5xl font-semibold mb-6 leading-tight">
          Growing Together, Sharing Prosperity
        </h1>

        <p className="text-emerald-100 text-lg max-w-2xl mb-10 leading-relaxed">
          AgriStack connects farmers and investors to create new agricultural
          opportunities through shared ownership, transparent crop monitoring,
          and sustainable farming practices.
        </p>

        <div className="grid md:grid-cols-3 gap-4 text-sm">
          <div className="bg-white/10 border border-white/10 rounded-xl p-5">
            <h2 className="text-lg font-semibold mb-2">
              Farmer Empowerment
            </h2>
            <p className="text-emerald-100 leading-relaxed">
              Help farmers access investment opportunities and manage their
              agricultural projects with confidence.
            </p>
          </div>

          <div className="bg-white/10 border border-white/10 rounded-xl p-5">
            <h2 className="text-lg font-semibold mb-2">
              Smart Investment
            </h2>
            <p className="text-emerald-100 leading-relaxed">
              Connect investors with agricultural projects and provide
              transparent information about crop-cycle progress.
            </p>
          </div>

          <div className="bg-white/10 border border-white/10 rounded-xl p-5">
            <h2 className="text-lg font-semibold mb-2">
              Sustainable Agriculture
            </h2>
            <p className="text-emerald-100 leading-relaxed">
              Support informed farming decisions, responsible resource use,
              and long-term agricultural growth.
            </p>
          </div>
        </div>
      </section>

      <footer className="px-6 py-5 text-center text-sm text-emerald-200 border-t border-white/10">
        AgriStack — Growing a better future for agriculture.
      </footer>
    </div>
  )
}
