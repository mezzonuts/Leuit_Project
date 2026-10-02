import { vi, describe, it, expect } from 'vitest'

// Mock lazy loading
vi.mock('react', async () => {
  const actual = await vi.importActual<typeof import('react')>('react')
  return {
    ...actual,
    lazy: vi.fn(() => 'LazyComponent'),
    Suspense: ({ children }: any) => <div data-testid="suspense">{children}</div>,
  }
})

describe('lazyLoad utility', () => {
  it('exports lazy components', async () => {
    const { LazyDashboard } = await import('../lazyLoad')
    expect(LazyDashboard).toBeDefined()
  })

  it('all lazy components are defined', async () => {
    const mod = await import('../lazyLoad')
    expect(mod.LazyDashboard).toBeDefined()
    expect(mod.LazyInventory).toBeDefined()
    expect(mod.LazyBOM).toBeDefined()
    expect(mod.LazyPurchases).toBeDefined()
    expect(mod.LazySync).toBeDefined()
  })
})
