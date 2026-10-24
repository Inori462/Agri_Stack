import { Navigate, Route, Routes } from 'react-router-dom'
import { useAuth } from './context/AuthContext'
import AppShell from './components/layout/AppShell'
import Landing from './pages/Landing'
import Login from './pages/Login'
import Register from './pages/Register'
import FarmerDashboard from './pages/FarmerDashboard'
import FarmerOnboarding from './pages/FarmerOnboarding'
import CreateProject from './pages/CreateProject'
import FarmMonitoring from './pages/FarmMonitoring'
import AIInsights from './pages/AIInsights'
import OwnershipShares from './pages/OwnershipShares'
import Marketplace from './pages/Marketplace'
import InvestorDiscovery from './pages/InvestorDiscovery'
import ProjectDetail from './pages/ProjectDetail'
import RecordsLedger from './pages/RecordsLedger'
import Reports from './pages/Reports'
import AdminPanel from './pages/AdminPanel'
import GovSocietyDashboard from './pages/GovSocietyDashboard'

function Protected({ children }) {
  const { user, loading } = useAuth()
  if (loading) return <p className="p-8">Loading…</p>
  if (!user) return <Navigate to="/login" replace />
  return children
}

export default function App() {
  return (
    <Routes>
      <Route path="/" element={<Landing />} />
      <Route path="/login" element={<Login />} />
      <Route path="/register" element={<Register />} />
      <Route
        path="/app"
        element={
          <Protected>
            <AppShell />
          </Protected>
        }
      >
        <Route path="dashboard" element={<FarmerDashboard />} />
        <Route path="onboarding" element={<FarmerOnboarding />} />
        <Route path="projects/new" element={<CreateProject />} />
        <Route path="projects/:id" element={<ProjectDetail />} />
        <Route path="monitoring" element={<FarmMonitoring />} />
        <Route path="insights" element={<AIInsights />} />
        <Route path="ownership" element={<OwnershipShares />} />
        <Route path="marketplace" element={<Marketplace />} />
        <Route path="discover" element={<InvestorDiscovery />} />
        <Route path="ledger" element={<RecordsLedger />} />
        <Route path="reports" element={<Reports />} />
        <Route path="admin" element={<AdminPanel />} />
        <Route path="gov" element={<GovSocietyDashboard />} />
      </Route>
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  )
}
