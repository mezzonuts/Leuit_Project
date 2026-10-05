import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { api } from '@/services/api'
import { X, Plus, Trash2 } from 'lucide-react'

interface CategoryManagerProps {
  onClose: () => void
}

export default function CategoryManager({ onClose }: CategoryManagerProps) {
  const queryClient = useQueryClient()
  const [newName, setNewName] = useState('')
  const [newColor, setNewColor] = useState('#16a34a')

  const { data } = useQuery({
    queryKey: ['categories'],
    queryFn: () => api.get('/categories').then(res => res.data),
  })

  const createMutation = useMutation({
    mutationFn: (data: { name: string; color: string }) => api.post('/categories', data),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['categories'] }),
  })

  const deleteMutation = useMutation({
    mutationFn: (id: number) => api.delete(`/categories/${id}`),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['categories'] }),
  })

  const categories = data?.items || []

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/50">
      <div className="w-full max-w-md bg-white rounded-xl shadow-xl">
        <div className="flex items-center justify-between p-4 border-b">
          <h2 className="text-lg font-semibold">Kelola Kategori</h2>
          <button onClick={onClose} aria-label="Tutup" className="p-2 hover:bg-gray-100 rounded">
            <X className="h-5 w-5" />
          </button>
        </div>

        <div className="p-4 space-y-4">
          {/* Add new category */}
          <div className="flex gap-2">
            <input
              type="text"
              value={newName}
              onChange={e => setNewName(e.target.value)}
              placeholder="Nama kategori baru"
              className="form-input flex-1"
            />
            <input
              type="color"
              value={newColor}
              onChange={e => setNewColor(e.target.value)}
              className="w-10 h-10 rounded cursor-pointer"
              aria-label="Warna kategori"
            />
            <button
              onClick={() => {
                if (newName.trim()) {
                  createMutation.mutate({ name: newName.trim(), color: newColor })
                  setNewName('')
                }
              }}
              className="btn-primary flex items-center gap-1"
              disabled={!newName.trim() || createMutation.isPending}
            >
              <Plus className="h-4 w-4" />
            </button>
          </div>

          {/* Category list */}
          <div className="space-y-2 max-h-60 overflow-y-auto">
            {categories.map((cat: any) => (
              <div key={cat.id} className="flex items-center justify-between p-2 bg-gray-50 rounded-lg">
                <div className="flex items-center gap-2">
                  <div className="w-4 h-4 rounded" style={{ backgroundColor: cat.color }} />
                  <span className="text-sm font-medium">{cat.name}</span>
                </div>
                <button
                  onClick={() => deleteMutation.mutate(cat.id)}
                  className="p-1 text-red-500 hover:bg-red-50 rounded"
                  aria-label={`Hapus ${cat.name}`}
                >
                  <Trash2 className="h-4 w-4" />
                </button>
              </div>
            ))}
            {categories.length === 0 && (
              <div className="text-center py-4 text-gray-500 text-sm">
                Belum ada kategori
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}
