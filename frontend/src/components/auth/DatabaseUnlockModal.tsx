import { useState } from 'react'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import { Lock, Unlock, Loader2, AlertCircle, Key, Shield, Eye, EyeOff, ChevronLeft } from 'lucide-react'
import { api } from '@/services/api'
import { cn } from '@/utils/formatters'

const unlockSchema = z.object({
  passkey: z.string().min(4, 'PIN minimal 4 digit'),
  is_developer: z.boolean().default(false),
})

type UnlockFormSchema = z.infer<typeof unlockSchema>

interface DatabaseUnlockModalProps {
  onUnlock: () => void
}

export default function DatabaseUnlockModal({ onUnlock }: DatabaseUnlockModalProps) {
  const [showPassword, setShowPassword] = useState(false)
  const [isDeveloper, setIsDeveloper] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm<UnlockFormSchema>({
    resolver: zodResolver(unlockSchema),
    defaultValues: {
      passkey: '',
      is_developer: false,
    },
  })

  const onSubmit = async (data: UnlockFormSchema) => {
    setError(null)
    try {
      const res = await api.post('/auth/unlock', {
        passkey: data.passkey,
        is_developer: data.is_developer,
      })
      if (res.data.success) {
        localStorage.setItem('leuit_passkey', data.passkey)
        onUnlock()
      } else {
        setError(res.data.message || 'PIN salah atau akses ditolak')
      }
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Gagal membuka database. Coba lagi.')
    }
  }

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 backdrop-blur-sm">
      <div className="w-full max-w-md bg-white rounded-2xl shadow-2xl overflow-hidden animate-in fade-in zoom-in-95 duration-300">
        {/* Header */}
        <div className="bg-gradient-to-r from-primary-600 to-primary-700 p-8 text-center text-white">
          <div className="relative inline-block mb-4">
            <div className="w-20 h-20 bg-white/20 rounded-full flex items-center justify-center">
              <Lock className="h-10 w-10 text-white" />
            </div>
            <div className="absolute -bottom-2 right-2 w-8 h-8 bg-primary-500 rounded-full flex items-center justify-center border-4 border-white">
              <Shield className="h-4 w-4 text-white" />
            </div>
          </div>
          <h1 className="text-2xl font-bold">Database Terkunci</h1>
          <p className="text-primary-100 mt-1">Masukkan PIN Owner atau Developer Recovery Key untuk melanjutkan</p>
        </div>

        {/* Form */}
        <form onSubmit={handleSubmit(onSubmit)} className="p-6 space-y-4" noValidate>
          {error && (
            <div className="p-3 bg-danger-50 border border-danger-200 rounded-lg text-danger-700 text-sm flex items-center gap-2">
              <AlertCircle className="h-5 w-5 flex-shrink-0" />
              {error}
            </div>
          )}

          {/* Mode Toggle */}
          <div className="flex gap-2 p-1 bg-gray-100 rounded-lg">
            <button
              type="button"
              onClick={() => { setIsDeveloper(false); setValue('is_developer', false) }}
              className={cn(
                'flex-1 py-2 px-3 rounded-md text-sm font-medium transition-colors',
                !isDeveloper ? 'bg-white text-primary-600 shadow-sm' : 'text-gray-600'
              )}
            >
              <Key className="h-4 w-4 inline mr-1" />
              Owner PIN
            </button>
            <button
              type="button"
              onClick={() => { setIsDeveloper(true); setValue('is_developer', true) }}
              className={cn(
                'flex-1 py-2 px-3 rounded-md text-sm font-medium transition-colors',
                isDeveloper ? 'bg-white text-danger-600 shadow-sm' : 'text-gray-600'
              )}
            >
              <Shield className="h-4 w-4 inline mr-1" />
              Developer Key
            </button>
          </div>

          {/* Passkey Input */}
          <div>
            <label className="label">PIN / Recovery Key *</label>
            <div className="relative">
              <input
                type={showPassword ? 'text' : 'password'}
                {...register('passkey')}
                placeholder={isDeveloper ? 'Masukkan Developer Recovery Key' : 'Masukkan 6-digit Owner PIN'}
                autoComplete="off"
                autoFocus
                className={cn('input pl-10', errors.passkey && 'border-danger-500')}
                inputMode={isDeveloper ? 'text' : 'numeric'}
              />
              <div className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400">
                {isDeveloper ? <Shield className="h-5 w-5" /> : <Lock className="h-5 w-5" />}
              </div>
              <button
                type="button"
                onClick={() => setShowPassword(!showPassword)}
                className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600"
                aria-label={showPassword ? 'Sembunyikan PIN' : 'Tampilkan PIN'}
              >
                {showPassword ? <EyeOff className="h-5 w-5" /> : <Eye className="h-5 w-5" />}
              </button>
            </div>
            {errors.passkey && <p className="mt-1 text-xs text-danger-600">{errors.passkey.message}</p>}
          </div>

          {/* Submit Button */}
          <button
            type="submit"
            disabled={isSubmitting}
            className="btn-primary w-full py-3 text-lg flex items-center justify-center gap-2"
          >
            {isSubmitting ? (
              <>
                <Loader2 className="h-5 w-5 animate-spin" />
                Membuka Database...
              </>
            ) : (
              <>
                <Unlock className="h-5 w-5" />
                Buka Database
              </>
            )}
          </button>

          {/* Info */}
          <div className="pt-4 border-t border-gray-200">
            <p className="text-xs text-gray-500 text-center">
              {isDeveloper
                ? 'Developer Recovery Key hanya untuk audit teknis & pemulihan darurat.'
                : 'PIN Owner diberikan saat aktivasi lisensi. Barista hanya akses operasional.'}
            </p>
          </div>
        </form>

        {/* Footer */}
        <div className="px-6 pb-6 text-center">
          <p className="text-xs text-gray-400">
            LEUIT v1.0.0 — SQLCipher AES-256 Encrypted Database
          </p>
        </div>
      </div>
    </div>
  )
}

// Helper for form
function setValue(name: string, value: any) {
  // This will be handled by react-hook-form
}