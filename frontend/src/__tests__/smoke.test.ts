import { describe, it, expect } from 'vitest'

describe('Smoke Tests', () => {
  it('formatters: formatRupiah', async () => {
    const { formatRupiah } = await import('../utils/formatters')
    expect(formatRupiah(10000)).toContain('10')
    expect(formatRupiah(0)).toContain('0')
  })

  it('formatters: getStockRatio', async () => {
    const { getStockRatio } = await import('../utils/formatters')
    expect(getStockRatio(50, 100)).toBe(50)
    expect(getStockRatio(100, 100)).toBe(100)
    expect(getStockRatio(50, 0)).toBe(100)
  })

  it('formatters: getStockStatus', async () => {
    const { getStockStatus } = await import('../utils/formatters')
    expect(getStockStatus(200)).toBe('safe')
    expect(getStockStatus(120)).toBe('warning')
    expect(getStockStatus(80)).toBe('danger')
  })

  it('formatters: daysUntilExpiry', async () => {
    const { daysUntilExpiry } = await import('../utils/formatters')
    expect(daysUntilExpiry(30)).toBeGreaterThanOrEqual(29)
    expect(daysUntilExpiry(1)).toBeGreaterThanOrEqual(0)
  })
})