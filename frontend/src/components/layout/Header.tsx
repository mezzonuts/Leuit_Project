import { Menu } from 'lucide-react'
import { useUIStore } from '@/stores'
import OutletSwitcher from './OutletSwitcher'
import LanguageSwitcher from '../ui/LanguageSwitcher'

interface HeaderProps {
  onMenuClick: () => void
  title: string
}

export default function Header({ onMenuClick, title }: HeaderProps) {
  const { licenseGraceDays } = useUIStore()

  return (
    <header role="banner" className="sticky top-0 z-30 h-16 bg-white border-b border-gray-200">
      <div className="flex h-full items-center justify-between px-4 lg:px-6">
        <div className="flex items-center gap-4">
          <button
            onClick={onMenuClick}
            className="lg:hidden p-2 rounded-lg text-gray-500 hover:bg-gray-100"
            aria-label="Buka menu"
          >
            <Menu className="h-6 w-6" />
          </button>
          <h1 className="text-lg font-semibold text-gray-900" aria-label={title}>{title}</h1>
        </div>

        <div className="flex items-center gap-4">
          <OutletSwitcher />
          <LanguageSwitcher />
          {licenseGraceDays !== null && licenseGraceDays > 0 && licenseGraceDays <= 3 && (
            <div className="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-warning-50 text-warning-700 text-sm font-medium">
              <span className="relative flex h-2 w-2">
                <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-warning-400 opacity-75" />
                <span className="relative inline-flex rounded-full h-2 w-2 bg-warning-500" />
              </span>
              Lisensi berakhir dalam {licenseGraceDays} hari
            </div>
          )}
          <div className="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-green-50 text-green-700 text-sm font-medium">
            <span className="relative flex h-2 w-2">
              <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-green-400 opacity-75" />
              <span className="relative inline-flex rounded-full h-2 w-2 bg-green-500" />
            </span>
            Database Terbuka
          </div>
        </div>
      </div>
    </header>
  )
}