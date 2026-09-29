import { Routes, Route, Navigate } from 'react-router-dom'
import { useEffect } from 'react'
import { QueryClientProvider } from '@tanstack/react-query'
import { queryClient } from './main'
import { useSecurityStore } from '@/stores'
import { authApi } from '@/services/api'
import Layout from '@/components/layout/Layout'
import Dashboard from '@/components/dashboard/Dashboard'
import Inventory from '@/components/inventory/Inventory'
import BOM from '@/components/bom/BOM'
import Purchases from '@/components/purchases/Purchases'
import Sync from '@/components/sync/Sync'
import DatabaseUnlockModal from '@/components/auth/DatabaseUnlockModal'
import LicenseGraceBanner from '@/components/layout/LicenseGraceBanner'

function PrivateRoute({ children }: { children: React.ReactNode }) {
  const { is_locked, unlock, setSecurityState } = useSecurityStore()

  useEffect(() => {
    const checkAuth = async () => {
      try {
        const res = await authApi.status()
        if (res.data.status === 'ACTIVE' || res.data.status === 'GRACE_PERIOD') {
          unlock(res.data.role as 'OWNER' | 'DEVELOPER', res.data.last_unlocked_at)
          if (res.data.grace_days_left !== undefined) {
            setSecurityState({ is_locked: false })
          }
        } else if (res.data.status === 'LOCKED') {
          setSecurityState({ is_locked: true })
        }
      } catch {
        setSecurityState({ is_locked: true })
      }
    }
    checkAuth()
  }, [unlock, setSecurityState])

  if (is_locked) {
    return <DatabaseUnlockModal onUnlock={() => window.location.reload()} />
  }

  return <>{children}</>
}

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <Routes>
        <Route path="/unlock" element={<DatabaseUnlockModal onUnlock={() => window.location.href = '/'} />} />
        <Route
          path="/*"
          element={
            <PrivateRoute>
              <Layout>
                <LicenseGraceBanner />
                <Routes>
                  <Route path="/" element={<Navigate to="/dashboard" replace />} />
                  <Route path="/dashboard" element={<Dashboard />} />
                  <Route path="/inventory" element={<Inventory />} />
                  <Route path="/bom" element={<BOM />} />
                  <Route path="/purchases" element={<Purchases />} />
                  <Route path="/sync" element={<Sync />} />
                </Routes>
              </Layout>
            </PrivateRoute>
          }
        />
      </Routes>
    </QueryClientProvider>
  )
}

export default App