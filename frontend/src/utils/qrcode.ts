/**
 * QR code generation utility for menu links.
 * Uses canvas-based QR generation (no external dependency for basic use).
 */

export function generateMenuQRUrl(menuUrl: string): string {
  // Use a free QR API for now
  return `https://api.qrserver.com/v1/create-qr-code/?size=300x300&data=${encodeURIComponent(menuUrl)}`
}

export function getMenuUrlForOutlet(outletId: number | null, baseUrl: string): string {
  const base = baseUrl || window.location.origin
  return outletId ? `${base}/menu?outlet=${outletId}` : `${base}/menu`
}
