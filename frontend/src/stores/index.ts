import { create } from 'zustand'
import { persist } from 'zustand/middleware'
import type { DatabaseSecurityState, UIState, DrawerType } from '@/types'

interface SecurityStore extends DatabaseSecurityState {
  setSecurityState: (state: Partial<DatabaseSecurityState>) => void
  unlock: (role: 'OWNER' | 'DEVELOPER', timestamp?: string) => void
  lock: () => void
}

export const useSecurityStore = create<SecurityStore>()(
  persist(
    (set) => ({
      is_locked: true,
      role: 'UNAUTHENTICATED',
      last_unlocked_at: undefined,
      setSecurityState: (state) => set((prev) => ({ ...prev, ...state })),
      unlock: (role, timestamp) => set({ is_locked: false, role, last_unlocked_at: timestamp || new Date().toISOString() }),
      lock: () => set({ is_locked: true, role: 'UNAUTHENTICATED', last_unlocked_at: undefined }),
    }),
    {
      name: 'leuit-security',
      partialize: (state) => ({ role: state.role, last_unlocked_at: state.last_unlocked_at }),
    }
  )
)

interface UIStoreState extends UIState {
  openDrawer: (type: DrawerType, data?: Record<string, any> | null) => void
  closeDrawer: () => void
  toggleMobileMenu: () => void
  setLicenseGraceDays: (days: number | null) => void
}

export const useUIStore = create<UIStoreState>()(
  persist(
    (set) => ({
      activeDrawer: null,
      drawerData: null as Record<string, any> | null,
      isMobileMenuOpen: false,
      licenseGraceDays: null,
      openDrawer: (type, data = null) => set({ activeDrawer: type, drawerData: data }),
      closeDrawer: () => set({ activeDrawer: null, drawerData: null }),
      toggleMobileMenu: () => set((state) => ({ isMobileMenuOpen: !state.isMobileMenuOpen })),
      setLicenseGraceDays: (days) => set({ licenseGraceDays: days }),
    }),
    {
      name: 'leuit-ui',
      partialize: (state) => ({ licenseGraceDays: state.licenseGraceDays }),
    }
  )
)