export function exportToCSV<T extends Record<string, any>>(
  data: T[],
  filename: string,
  columnMap?: Record<keyof T, string>
): void {
  if (data.length === 0) return

  const headers = columnMap
    ? Object.keys(data[0]).map(key => columnMap[key as keyof T] || key)
    : Object.keys(data[0])

  const rows = data.map(item =>
    Object.keys(item).map(key => {
      const value = item[key]
      if (value === null || value === undefined) return ''
      if (typeof value === 'object') return JSON.stringify(value)
      if (typeof value === 'string' && (value.includes(',') || value.includes('"') || value.includes('\n'))) {
        return `"${value.replace(/"/g, '""')}"`
      }
      return String(value)
    }).join(',')
  )

  const csvContent = [headers.join(','), ...rows].join('\n')
  const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' })
  downloadBlob(blob, filename)
}

function downloadBlob(blob: Blob, filename: string): void {
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = filename
  document.body.appendChild(a)
  a.click()
  document.body.removeChild(a)
  URL.revokeObjectURL(url)
}

export function generateValuationCSV(ingredients: any[]): string {
  const headers = [
    'ID',
    'Nama Bahan',
    'Barcode/SKU',
    'Sisa Stok',
    'Satuan',
    'HPP per Satuan',
    'Total Valuasi',
    'Masa Simpan (Hari)',
    'Minimum Threshold',
  ]

  const rows = ingredients.map(ing => [
    ing.id,
    ing.name,
    ing.barcode_sku || '',
    ing.current_stock,
    ing.unit,
    ing.cost_per_unit,
    ing.current_stock * ing.cost_per_unit,
    ing.shelf_life_days,
    ing.min_stock_threshold,
  ])

  return [headers.join(','), ...rows.map(r => r.join(','))].join('\n')
}

export function downloadValuationCSV(ingredients: any[]): void {
  const csv = generateValuationCSV(ingredients)
  const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' })
  const date = new Date().toISOString().split('T')[0]
  downloadBlob(blob, `valuasi-aset-${date}.csv`)
}