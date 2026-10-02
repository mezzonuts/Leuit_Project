import { useState } from 'react'
import { X } from 'lucide-react'
import { useMutation, useQueryClient } from '@tanstack/react-query'
import { api } from '@/services/api'
import { useUIStore } from '@/stores'

interface SupplierDrawerProps {
  onClose: () => void
}

export default function SupplierDrawer({ onClose }: SupplierDrawerProps) {
  const { drawerData } = useUIStore()
  const queryClient = useQueryClient()
  const isEdit = drawerData?.mode === 'edit'
  
  const [form, setForm] = useState({
    name: drawerData?.supplier?.name || '',
    phone_whatsapp: drawerData?.supplier?.phone_whatsapp || '',
    payment_terms_days: drawerData?.supplier?.payment_terms_days || 0,
  })

  const mutation = useMutation({
    mutationFn: async () => {
      if (isEdit) {
        return api.put(`/purchases/suppliers/${drawerData?.supplier?.id}`, form)
      }
      return api.post('/purchases/suppliers', form)
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['suppliers'] })
      onClose()
    },
  })

  return (
    <div className="fixed inset-0 z-50 flex justify-end bg-black/50">
      <div className="w-full max-w-md bg-white h-full overflow-y-auto">
        <div className="flex items-center justify-between p-4 border-b">
          <h2 className="text-lg font-semibold">
            {isEdit ? 'Edit Suplier' : 'Tambah Suplier'}
          </h2>
          <button onClick={onClose} aria-label="Tutup" className="p-2 hover:bg-gray-100 rounded">
            <X className="h-5 w-5" />
          </button>
        </div>
        
        <div className="p-4 space-y-4">
          <div>
            <label className="form-label">Nama Suplier *</label>
            <input
              type="text"
              value={form.name}
              onChange={(e) => setForm({ ...form, name: e.target.value })}
              className="form-input"
              placeholder="PT ABC"
            />
          </div>
          
          <div>
            <label className="form-label">WhatsApp</label>
            <input
              type="text"
              value={form.phone_whatsapp}
              onChange={(e) => setForm({ ...form, phone_whatsapp: e.target.value })}
              className="form-input"
              placeholder="08123456789"
            />
          </div>
          
          <div>
            <label className="form-label">Tempo Pembayaran (Hari)</label>
            <input
              type="number"
              value={form.payment_terms_days}
              onChange={(e) => setForm({ ...form, payment_terms_days: Number(e.target.value) })}
              className="form-input"
              min={0}
            />
            <p className="text-xs text-gray-500 mt-1">0 = Cash</p>
          </div>
          
          <div className="flex gap-2 pt-4">
            <button onClick={onClose} className="btn-secondary flex-1">
              Batal
            </button>
            <button
              onClick={() => mutation.mutate()}
              disabled={mutation.isPending || !form.name}
              className="btn-primary flex-1"
            >
              {mutation.isPending ? 'Menyimpan...' : isEdit ? 'Update' : 'Simpan'}
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}
