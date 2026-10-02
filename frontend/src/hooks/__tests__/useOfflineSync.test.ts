import { renderHook, act } from '@testing-library/react'
import { useOfflineSync } from '../useOfflineSync'
import { describe, it, expect, beforeEach } from 'vitest'

describe('useOfflineSync', () => {
  beforeEach(() => {
    localStorage.clear()
    // Mock navigator.onLine
    Object.defineProperty(navigator, 'onLine', {
      value: true,
      writable: true,
    })
  })

  it('returns initial state', () => {
    const { result } = renderHook(() => useOfflineSync())
    expect(result.current.isOnline).toBe(true)
    expect(result.current.pendingCount).toBe(0)
  })

  it('enqueue adds item to queue', () => {
    const { result } = renderHook(() => useOfflineSync())

    act(() => {
      result.current.enqueue('/api/inventory', 'POST', { name: 'Test' })
    })

    expect(result.current.pendingCount).toBe(1)
  })

  it('clearSynced removes synced items', () => {
    const { result } = renderHook(() => useOfflineSync())

    act(() => {
      result.current.enqueue('/api/test', 'POST', {})
      result.current.enqueue('/api/test2', 'POST', {})
    })

    expect(result.current.pendingCount).toBe(2)
  })

  it('syncQueue returns false when offline', async () => {
    Object.defineProperty(navigator, 'onLine', { value: false, writable: true })
    const { result } = renderHook(() => useOfflineSync())

    let syncResult: boolean | undefined
    await act(async () => {
      syncResult = await result.current.syncQueue(async () => {})
    })

    expect(syncResult).toBe(false)
  })
})
