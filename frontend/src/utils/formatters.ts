export function formatRupiah(value: number): string {
  return new Intl.NumberFormat('id-ID', {
    style: 'currency',
    currency: 'IDR',
    minimumFractionDigits: 0,
    maximumFractionDigits: 0,
  }).format(value)
}

export function formatNumber(value: number, decimals = 0): string {
  return new Intl.NumberFormat('id-ID', {
    minimumFractionDigits: decimals,
    maximumFractionDigits: decimals,
  }).format(value)
}

export function formatDate(dateString: string, options?: Intl.DateTimeFormatOptions): string {
  const defaultOptions: Intl.DateTimeFormatOptions = {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric',
  }
  return new Date(dateString).toLocaleDateString('id-ID', options || defaultOptions)
}

export function formatDateTime(dateString: string): string {
  return new Date(dateString).toLocaleString('id-ID', {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  })
}

export function formatRelativeTime(dateString: string): string {
  const date = new Date(dateString)
  const now = new Date()
  const diffMs = now.getTime() - date.getTime()
  const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24))
  const diffHours = Math.floor(diffMs / (1000 * 60 * 60))
  const diffMinutes = Math.floor(diffMs / (1000 * 60))

  if (diffDays > 0) return `${diffDays} hari lalu`
  if (diffHours > 0) return `${diffHours} jam lalu`
  if (diffMinutes > 0) return `${diffMinutes} menit lalu`
  return 'Baru saja'
}

export function getStockRatio(current: number, threshold: number): number {
  if (threshold <= 0) return 100
  return Math.round((current / threshold) * 100)
}

export function getStockStatus(ratio: number): 'safe' | 'warning' | 'danger' {
  if (ratio >= 150) return 'safe'
  if (ratio >= 100) return 'warning'
  return 'danger'
}

export function getStockStatusColor(status: 'safe' | 'warning' | 'danger'): string {
  switch (status) {
    case 'safe': return 'text-green-700 bg-green-100'
    case 'warning': return 'text-warning-700 bg-warning-100'
    case 'danger': return 'text-danger-700 bg-danger-100'
  }
}

export function getStockProgressColor(ratio: number): string {
  if (ratio >= 150) return 'bg-green-500'
  if (ratio >= 100) return 'bg-warning-500'
  return 'bg-danger-500'
}

export function daysUntilExpiry(shelfLifeDays: number, createdAt?: string): number {
  const baseDate = createdAt ? new Date(createdAt) : new Date()
  const expiryDate = new Date(baseDate)
  expiryDate.setDate(expiryDate.getDate() + shelfLifeDays)
  const now = new Date()
  const diffMs = expiryDate.getTime() - now.getTime()
  return Math.ceil(diffMs / (1000 * 60 * 60 * 24))
}

export function cn(...classes: (string | undefined | null | false)[]): string {
  return classes.filter(Boolean).join(' ')
}

export function downloadBlob(blob: Blob, filename: string): void {
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = filename
  document.body.appendChild(a)
  a.click()
  document.body.removeChild(a)
  URL.revokeObjectURL(url)
}

export function parseCSV(csvText: string): string[][] {
  const lines = csvText.trim().split('\n')
  return lines.map(line => {
    const result = []
    let current = ''
    let inQuotes = false
    for (let i = 0; i < line.length; i++) {
      const char = line[i]
      if (char === '"') {
        if (inQuotes && line[i + 1] === '"') {
          current += '"'
          i++
        } else {
          inQuotes = !inQuotes
        }
      } else if (char === ',' && !inQuotes) {
        result.push(current)
        current = ''
      } else {
        current += char
      }
    }
    result.push(current)
    return result
  })
}

export function csvToObjects(csvText: string): Record<string, string>[] {
  const rows = parseCSV(csvText)
  if (rows.length < 2) return []
  const headers = rows[0]
  return rows.slice(1).map(row => {
    const obj: Record<string, string> = {}
    headers.forEach((header, i) => {
      obj[header] = row[i] || ''
    })
    return obj
  })
}