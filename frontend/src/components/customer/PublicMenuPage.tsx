import { useQuery } from '@tanstack/react-query'
import { api } from '@/services/api'
import { formatRupiah } from '@/utils/formatters'

export default function PublicMenuPage() {
  const { data: menuData, isLoading } = useQuery({
    queryKey: ['public-menu'],
    queryFn: async () => {
      const res = await api.get('/public/menu')
      return res.data
    },
  })

  if (isLoading) {
    return <div className="text-center py-8 text-gray-500">Memuat menu...</div>
  }

  return (
    <div className="max-w-lg mx-auto">
      <div className="text-center mb-6">
        <h1 className="text-2xl font-bold">Menu Kami</h1>
        <p className="text-gray-600">Pilihan minuman & makanan favorit</p>
      </div>
      
      <div className="space-y-3">
        {menuData?.items?.map((item: any) => (
          <div key={item.id} className="card flex justify-between items-center">
            <div>
              <h3 className="font-medium">{item.name}</h3>
              <p className="text-sm text-gray-500">{item.ingredient_count} bahan</p>
            </div>
            <span className="text-lg font-semibold text-primary-600">
              {formatRupiah(item.sale_price)}
            </span>
          </div>
        ))}
      </div>
      
      {menuData?.items?.length === 0 && (
        <div className="text-center py-8 text-gray-500">
          Menu belum tersedia
        </div>
      )}
    </div>
  )
}
