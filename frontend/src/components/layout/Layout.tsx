import { Outlet, NavLink, useLocation } from 'react-router-dom'
import { useState } from 'react'
import { Menu, X, ChevronLeft, ChevronRight, Shield, Package, ChefHat, ShoppingCart, RefreshCw, BarChart2, Settings } from 'lucide-react'
import { useUIStore } from '@/stores'
import './Layout.css'

const navigation = [
  { name: 'Dashboard', href: '/dashboard', icon: BarChart2 },
  { name: 'Kelola Stok', href: '/inventory', icon: Package },
  { name: 'Resep & Menu', href: '/bom', icon: ChefHat },
  { name: 'Pembelian', href: '/purchases', icon: ShoppingCart },
  { name: 'Sinkronisasi', href: '/sync', icon: RefreshCw },
]

export default function Layout() {
  const location = useLocation()
  const [sidebarOpen, setSidebarOpen] = useState(true)
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false)
  const { activeDrawer, closeDrawer, isMobileMenuOpen: storeMobileOpen, toggleMobileMenu } = useUIStore()

  const isDrawerOpen = activeDrawer !== null

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Mobile overlay */}
      {(mobileMenuOpen || storeMobileOpen) && (
        <div
          className="fixed inset-0 z-40 bg-black/50 lg:hidden"
          onClick={() => { setMobileMenuOpen(false); toggleMobileMenu() }}
          aria-hidden="true"
        />
      )}

      {/* Sidebar */}
      <aside
        className={`fixed top-0 left-0 z-50 h-screen bg-white border-r border-gray-200 transition-all duration-300 ease-in-out lg:translate-x-0 ${
          sidebarOpen ? 'w-64' : 'w-20'
        } ${mobileMenuOpen || storeMobileOpen ? 'translate-x-0' : '-translate-x-full lg:translate-x-0'}`}
        aria-label="Navigasi utama"
      >
        <div className="flex h-full flex-col">
          {/* Logo & Toggle */}
          <div className="flex h-16 items-center justify-between border-b border-gray-200 px-4">
            <div className="flex items-center gap-3">
              <Shield className="h-8 w-8 text-primary-600" aria-hidden="true" />
              {sidebarOpen && (
                <span className="text-xl font-bold text-gray-900">LEUIT</span>
              )}
            </div>
            <button
              onClick={() => setSidebarOpen(!sidebarOpen)}
              className="p-2 rounded-lg text-gray-500 hover:bg-gray-100 hover:text-gray-700 lg:hidden"
              aria-label={sidebarOpen ? 'Tutup sidebar' : 'Buka sidebar'}
              aria-expanded={sidebarOpen}
            >
              {sidebarOpen ? <ChevronLeft className="h-5 w-5" /> : <ChevronRight className="h-5 w-5" />}
            </button>
          </div>

          {/* Navigation */}
          <nav className="flex-1 space-y-1 p-3 overflow-y-auto" aria-label="Menu navigasi">
            {navigation.map((item) => {
              const isActive = location.pathname === item.href || location.pathname.startsWith(item.href + '/')
              return (
                <NavLink
                  key={item.name}
                  to={item.href}
                  className={({ isActive }) => `
                    flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-medium transition-colors
                    ${isActive
                      ? 'bg-primary-50 text-primary-700'
                      : 'text-gray-600 hover:bg-gray-100 hover:text-gray-900'
                    }
                    ${!sidebarOpen ? 'justify-center' : ''}
                  `}
                  title={sidebarOpen ? undefined : item.name}
                  aria-current={isActive ? 'page' : undefined}
                >
                  <item.icon className="h-5 w-5 flex-shrink-0" aria-hidden="true" />
                  {sidebarOpen && <span>{item.name}</span>}
                </NavLink>
              )
            })}
          </nav>

          {/* Footer */}
          <div className="border-t border-gray-200 p-3" aria-hidden={!sidebarOpen}>
            {sidebarOpen && (
              <div className="text-xs text-gray-500 text-center">
                LEUIT v1.0.0
              </div>
            )}
          </div>
        </div>
      </aside>

      {/* Main Content */}
      <main
        className={`lg:pl-64 transition-all duration-300 min-h-screen ${
          sidebarOpen ? 'pl-64' : 'pl-20'
        } ${isDrawerOpen ? 'pr-96' : 'pr-0'}`}
      >
        {/* Header */}
        <header className="sticky top-0 z-30 h-16 bg-white border-b border-gray-200">
          <div className="flex h-full items-center justify-between px-4 lg:px-6">
            <div className="flex items-center gap-4">
              <button
                onClick={() => { setMobileMenuOpen(true); toggleMobileMenu() }}
                className="lg:hidden p-2 rounded-lg text-gray-500 hover:bg-gray-100"
                aria-label="Buka menu"
              >
                <Menu className="h-6 w-6" />
              </button>
              <h1 className="text-lg font-semibold text-gray-900 hidden sm:block">
                {navigation.find(n => location.pathname === n.href || location.pathname.startsWith(n.href + '/'))?.name || 'LEUIT'}
              </h1>
            </div>
            <div className="flex items-center gap-4">
              <div className="hidden sm:flex items-center gap-2 px-3 py-1.5 rounded-lg bg-green-50 text-green-700 text-sm font-medium">
                <span className="relative flex h-2 w-2">
                  <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-green-400 opacity-75" />
                  <span className="relative inline-flex rounded-full h-2 w-2 bg-green-500" />
                </span>
                Database Terkunci
              </div>
            </div>
          </div>
        </header>

        {/* Page Content */}
        <div className="p-4 lg:p-6 pb-16">
          <Outlet />
        </div>
      </main>

      {/* Slide-over Drawer */}
      {isDrawerOpen && (
        <div className="fixed inset-y-0 right-0 z-50 w-96 bg-white border-l border-gray-200 shadow-xl lg:static lg:shadow-none lg:border-0" aria-hidden="false">
          <Outlet context={activeDrawer} />
        </div>
      )}
    </div>
  )
}