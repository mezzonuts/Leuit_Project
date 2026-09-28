import { Lock, Unlock, Shield, AlertTriangle, Clock } from 'lucide-react'
import { useSecurityStore } from '@/stores'

export default function KeyStatusIndicator() {
  const { is_locked, role, last_unlocked_at } = useSecurityStore()

  if (is_locked) {
    return (
      <div className="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-danger-50 text-danger-700 text-sm font-medium">
        <Lock className="h-4 w-4" />
        Database Terkunci
      </div>
    )
  }

  const isDeveloper = role === 'DEVELOPER'
  const timeAgo = last_unlocked_at ? new Date(last_unlocked_at).toLocaleTimeString('id-ID', { hour: '2-digit', minute: '2-digit' }) : ''

  return (
    <div className="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-green-50 text-green-700 text-sm font-medium">
      <Unlock className="h-4 w-4" />
      <span>Database Terbuka</span>
      <span className="px-2 py-0.5 rounded-full text-xs font-medium bg-white/50">
        {isDeveloper ? <Shield className="h-3 w-3 inline" /> : 'Owner'}
      </span>
      {timeAgo && (
        <span className="px-2 py-0.5 rounded-full text-xs bg-white/50">
          <Clock className="h-3 w-3 inline" />
          {timeAgo}
        </span>
      )}
    </div>
  )
}