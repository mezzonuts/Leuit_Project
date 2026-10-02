import { useState } from 'react'
import { Calendar } from 'lucide-react'

interface DateRangePickerProps {
  startDate: string
  endDate: string
  onChange: (start: string, end: string) => void
}

const PRESETS = [
  { label: '7 Hari', days: 7 },
  { label: '30 Hari', days: 30 },
  { label: '90 Hari', days: 90 },
  { label: '1 Tahun', days: 365 },
]

export default function DateRangePicker({ startDate, endDate, onChange }: DateRangePickerProps) {
  const [showPresets, setShowPresets] = useState(false)

  const applyPreset = (days: number) => {
    const end = new Date()
    const start = new Date()
    start.setDate(start.getDate() - days)

    onChange(
      start.toISOString().split('T')[0],
      end.toISOString().split('T')[0]
    )
    setShowPresets(false)
  }

  return (
    <div className="relative">
      <button
        type="button"
        onClick={() => setShowPresets(!showPresets)}
        className="btn-secondary flex items-center gap-2 text-sm"
        aria-label="Pilih rentang tanggal"
      >
        <Calendar className="h-4 w-4" />
        {startDate} — {endDate}
      </button>

      {showPresets && (
        <div className="absolute z-10 mt-1 w-48 bg-white border border-gray-200 rounded-lg shadow-lg p-2">
          {PRESETS.map((preset) => (
            <button
              key={preset.label}
              type="button"
              onClick={() => applyPreset(preset.days)}
              className="block w-full text-left px-3 py-2 text-sm hover:bg-gray-50 rounded"
            >
              {preset.label}
            </button>
          ))}
        </div>
      )}

      <div className="flex items-center gap-2 mt-2">
        <input
          type="date"
          value={startDate}
          onChange={(e) => onChange(e.target.value, endDate)}
          className="form-input text-sm"
          aria-label="Tanggal mulai"
        />
        <span className="text-gray-400">—</span>
        <input
          type="date"
          value={endDate}
          onChange={(e) => onChange(startDate, e.target.value)}
          className="form-input text-sm"
          aria-label="Tanggal selesai"
        />
      </div>
    </div>
  )
}
