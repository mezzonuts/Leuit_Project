/**
 * WhatsApp reminder utility for AP alerts.
 * Creates wa.me deep link for supplier payment reminders.
 */

export function createWhatsAppReminderLink(
  phone: string,
  supplierName: string,
  totalUnpaid: number,
  daysUntilDue: number | null,
): string {
  // Clean phone number (remove non-digits, ensure country code)
  const cleanPhone = phone.replace(/\D/g, '').replace(/^0+/, '')
  const phoneWithCode = cleanPhone.startsWith('62') ? cleanPhone : `62${cleanPhone}`
  
  const message = [
    `Halo ${supplierName},`,
    '',
    `Ini pengingat pembayaran dari LEUIT:`,
    `Total belum bayar: Rp ${totalUnpaid.toLocaleString('id-ID')}`,
    daysUntilDue !== null ? `Jatuh tempo: ${daysUntilDue} hari lagi` : '',
    '',
    'Terima kasih.',
  ].filter(Boolean).join('\n')
  
  return `https://wa.me/${phoneWithCode}?text=${encodeURIComponent(message)}`
}

export function formatRupiah(amount: number): string {
  return `Rp ${amount.toLocaleString('id-ID')}`
}
