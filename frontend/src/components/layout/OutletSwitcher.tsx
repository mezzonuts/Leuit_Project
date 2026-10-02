import { useEffect } from 'react'
import { useOutletStore } from '@/stores'
import { useQuery } from '@tanstack/react-query'
import { api } from '@/services/api'
import { Store } from 'lucide-react'

export default function OutletSwitcher() {
  const { current_outlet_id, outlets, setCurrentOutlet, setOutlets } = useOutletStore()

  const { data: outletsData } = useQuery({
    queryKey: ['outlets'],
    queryFn: async () => {
      const res = await api.get('/outlets')
      return res.data
    },
  })

  useEffect(() => {
    if (outletsData?.items) {
      setOutlets(outletsData.items)
    }
  }, [outletsData, setOutlets])

  useEffect(() => {
    const saved = localStorage.getItem('leuit_current_outlet')
    if (saved) {
      setCurrentOutlet(Number(saved))
    }
  }, [setCurrentOutlet])

  if (outlets.length === 0) {
    return null
  }

  return (
    <div className="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-gray-50 border border-gray-200">
      <Store className="h-4 w-4 text-gray-500" />
      <select
        value={current_outlet_id ?? ''}
        onChange={(e) => setCurrentOutlet(e.target.value ? Number(e.target.value) : null)}
        className="text-sm font-medium text-gray-700 bg-transparent border-none focus:outline-none focus:ring-0"
        aria-label="Pilih outlet"
      >
        <option value="">Semua Outlet</option>
        {outlets.map((outlet) => (
          <option key={outlet.id} value={outlet.id}>
            {outlet.name}
          </option>
        ))}
      </select>
    </div>
  )
}
