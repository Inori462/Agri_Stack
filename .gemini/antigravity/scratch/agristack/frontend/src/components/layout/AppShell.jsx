import { NavLink, Outlet, useNavigate } from 'react-router-dom'
import { useTranslation } from 'react-i18next'
import { useAuth } from '../../context/AuthContext'
import AssistantDrawer from '../ai/AssistantDrawer'

const NAV = [
  { to: '/app/dashboard', key: 'dashboard', roles: ['FARMER', 'INVESTOR', 'ADMIN', 'GOV_OFFICER'] },
  { to: '/app/onboarding', key: 'onboarding', roles: ['FARMER'] },
  { to: '/app/projects/new', key: 'projects', roles: ['FARMER', 'ADMIN'] },
  { to: '/app/monitoring', key: 'monitoring', roles: ['FARMER', 'ADMIN'] },
  { to: '/app/insights', key: 'insights', roles: ['FARMER', 'INVESTOR', 'ADMIN'] },
  { to: '/app/ownership', key: 'ownership', roles: ['FARMER', 'INVESTOR', 'ADMIN'] },
  { to: '/app/marketplace', key: 'marketplace', roles: ['FARMER', 'INVESTOR', 'ADMIN'] },
  { to: '/app/discover', key: 'discover', roles: ['INVESTOR', 'ADMIN'] },
  { to: '/app/ledger', key: 'ledger', roles: ['FARMER', 'INVESTOR', 'ADMIN'] },
  { to: '/app/reports', key: 'reports', roles: ['FARMER', 'INVESTOR', 'ADMIN'] },
  { to: '/app/admin', key: 'admin', roles: ['ADMIN'] },
  { to: '/app/gov', key: 'gov', roles: ['GOV_OFFICER', 'ADMIN'] },
]

export default function AppShell() {
  const { t, i18n } = useTranslation()
  const { user, logout } = useAuth()
  const navigate = useNavigate()

  return (
    <div className="min-h-screen grid md:grid-cols-[240px_1fr] bg-emerald-50">
      <aside className="bg-agri-900 text-white p-4 space-y-4">
        <div>
          <p className="text-lg font-semibold">{t('brand')}</p>
          <p className="text-xs text-emerald-200">{t('tagline')}</p>
        </div>
        <nav className="space-y-1 text-sm">
          {NAV.filter((item) => !user || item.roles.includes(user.primary_role)).map((item) => (
            <NavLink
              key={item.to}
              to={item.to}
              className={({ isActive }) =>
                `block rounded-md px-3 py-2 ${isActive ? 'bg-agri-700' : 'hover:bg-agri-800'}`
              }
            >
              {t(item.key)}
            </NavLink>
          ))}
        </nav>
      </aside>
      <div className="flex flex-col min-h-screen">
        <header className="flex flex-wrap items-center justify-between gap-3 bg-white border-b px-4 py-3">
          <p className="text-sm text-agri-800 font-medium">{user?.full_name} · {user?.primary_role}</p>
          <div className="flex items-center gap-2">
            <select
              className="rounded-md border-emerald-200 text-sm"
              value={i18n.language.slice(0, 2)}
              onChange={(e) => i18n.changeLanguage(e.target.value)}
            >
              <option value="en">English</option>
              <option value="hi">हिंदी</option>
              <option value="mr">मराठी</option>
            </select>
            <button
              className="text-sm text-red-700"
              onClick={() => {
                logout()
                navigate('/')
              }}
            >
              {t('logout')}
            </button>
          </div>
        </header>
        <main className="p-4 md:p-6 flex-1">
          <p className="mb-4 text-xs bg-amber-50 border border-amber-200 text-amber-800 rounded-lg px-3 py-2">{t('pilot')}</p>
          <Outlet />
        </main>
      </div>
      <AssistantDrawer />
    </div>
  )
}
