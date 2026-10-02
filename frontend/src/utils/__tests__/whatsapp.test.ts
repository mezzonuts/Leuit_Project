import { describe, it, expect } from 'vitest'
import { createWhatsAppReminderLink } from '../whatsapp'

describe('createWhatsAppReminderLink', () => {
  it('creates wa.me link with formatted message', () => {
    const link = createWhatsAppReminderLink(
      '08123456789',
      'PT ABC',
      500000,
      3,
    )
    expect(link).toContain('https://wa.me/628123456789')
    expect(link).toContain('text=')
  })

  it('handles phone with country code', () => {
    const link = createWhatsAppReminderLink('628123456789', 'PT ABC', 100000, null)
    expect(link).toContain('628123456789')
  })

  it('omits due date when null', () => {
    const link = createWhatsAppReminderLink('0812', 'PT ABC', 50000, null)
    const decoded = decodeURIComponent(link.split('text=')[1])
    expect(decoded).not.toContain('Jatuh tempo')
  })

  it('includes due date when present', () => {
    const link = createWhatsAppReminderLink('0812', 'PT ABC', 50000, 5)
    const decoded = decodeURIComponent(link.split('text=')[1])
    expect(decoded).toContain('Jatuh tempo: 5 hari lagi')
  })
})
