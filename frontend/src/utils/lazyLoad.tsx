import React, { lazy } from 'react'
import { Loader2 } from 'lucide-react'

/**
 * Create a lazy-loaded component with loading fallback.
 */
export function createLazyComponent<T extends React.ComponentType<any>>(
  importFunc: () => Promise<{ default: T }>,
  fallback?: React.ReactNode,
) {
  const LazyComponent = lazy(importFunc)

  const WrappedComponent = (props: any) => (
    <React.Suspense
      fallback={fallback || (
        <div className="flex items-center justify-center h-64">
          <Loader2 className="h-8 w-8 animate-spin text-primary-600" />
        </div>
      )}
    >
      <LazyComponent {...props} />
    </React.Suspense>
  )

  return WrappedComponent
}

// Lazy-loaded page components
export const LazyDashboard = createLazyComponent(
  () => import('@/components/dashboard/Dashboard')
)

export const LazyInventory = createLazyComponent(
  () => import('@/components/inventory/Inventory')
)

export const LazyBOM = createLazyComponent(
  () => import('@/components/bom/BOM')
)

export const LazyPurchases = createLazyComponent(
  () => import('@/components/purchases/Purchases')
)

export const LazySync = createLazyComponent(
  () => import('@/components/sync/Sync')
)
