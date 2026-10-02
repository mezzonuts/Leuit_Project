import { Routes, Route, Navigate } from 'react-router-dom'
import { useEffect } from 'react'
import { QueryClientProvider } from '@tanstack/react-query'
import { queryClient } from './main'
import { useSecurityStore, useUIStore } from '@/stores'
import { authApi } from '@/services/api'
import Layout from '@/components/layout/Layout'
import { LazyDashboard, LazyInventory, LazyBOM, LazyPurchases, LazySync } from '@/utils/lazyLoad'
import DatabaseUnlockModal from '@/components/auth/DatabaseUnlockModal'
import i18n from './i18n'

const Dashboard = LazyDashboard
const Inventory = LazyInventory
const BOM = LazyBOM
const Purchases = LazyPurchases
const Sync = LazySync
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
  const { language } = useUIStore()

  useEffect(() => {
    const savedLang = localStorage.getItem('leuit_locale') || language || 'id'
    i18n.changeLanguage(savedLang)
  }, [language])

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