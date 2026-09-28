import { NavLink, useLocation } from 'react-router-dom'
import { useState } from 'react'
import { Menu, X, ChevronLeft, ChevronRight, Shield, Package, ChefHat, ShoppingCart, RefreshCw, BarChart2 } from 'lucide-react'

const navigation = [
  { name: 'Dashboard', href: '/dashboard', icon: BarChart2 },
  { name: 'Kelola Stok', href: '/inventory', icon: Package },
  { name: 'Resep & Menu', href: '/bom', icon: ChefHat },
  { name: 'Pembelian', href: '/purchases', icon: ShoppingCart },
  { name: 'Sinkronisasi', href: '/sync', icon: RefreshCw },
]

interface SidebarProps {
  isOpen: boolean
  onToggle: () => void
  mobileOpen: boolean
  onMobileClose: () => void
}

export default function Sidebar({ isOpen, onToggle, mobileOpen, onMobileClose }: SidebarProps) {
  const location = useLocation()

  return (
    <aside
      className={`fixed top-0 left-0 z-50 h-screen bg-white border-r border-gray-200 transition-all duration-300 ease-in-out ${
        isOpen ? 'w-64' : 'w-20'
      } ${mobileOpen ? 'translate-x-0' : '-translate-x-full lg:translate-x-0'}`}
      aria-label="Navigasi utama"
    >
      <div className="flex h-full flex-col">
        <div className="flex h-16 items-center justify-between border-b border-gray-200 px-4">
          <div className="flex items-center gap-3">
            <Shield className="h-8 w-8 text-primary-600" aria-hidden="true" />
            {isOpen && <span className="text-xl font-bold text-gray-900">LEUIT</span>}
          </div>
          <button
            onClick={onToggle}
            className="p-2 rounded-lg text-gray-500 hover:bg-gray-100 hover:text-gray-700 lg:hidden"
            aria-label={isOpen ? 'Tutup sidebar' : 'Buka sidebar'}
            aria-expanded={isOpen}
          >
            {isOpen ? <ChevronLeft className="h-5 w-5" /> : <ChevronRight className="h-5 w-5" />}
          </button>
        </div>

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
                  ${!isOpen ? 'justify-center' : ''}
                `}
                title={isOpen ? undefined : item.name}
                aria-current={isActive ? 'page' : undefined}
                onClick={onMobileClose}
              >
                <item.icon className="h-5 w-5 flex-shrink-0" aria-hidden="true" />
                {isOpen && <span>{item.name}</span>}
              </NavLink>
            )
          })}
        </nav>

        <div className="border-t border-gray-200 p-3" aria-hidden={!isOpen}>
          {isOpen && (
            <div className="text-xs text-gray-500 text-center">
              LEUIT v1.0.0
            </div>
          )}
        </div>
      </div>
    </aside>
  )
}