import { useState, useEffect } from 'react'

interface OfflineItem {
  id: number
  endpoint: string
  method: string
  data: any
  timestamp: number
  status: 'pending' | 'syncing' | 'synced' | 'failed'
}

const OFFLINE_QUEUE_KEY = 'leuit_offline_queue'

function getQueue(): OfflineItem[] {
  try {
    const raw = localStorage.getItem(OFFLINE_QUEUE_KEY)
    return raw ? JSON.parse(raw) : []
  } catch {
    return []
  }
}

function saveQueue(queue: OfflineItem[]) {
  localStorage.setItem(OFFLINE_QUEUE_KEY, JSON.stringify(queue))
}

export function useOfflineSync() {
  const [isOnline, setIsOnline] = useState(navigator.onLine)
  const [pendingCount, setPendingCount] = useState(0)

  useEffect(() => {
    const updateOnline = () => setIsOnline(navigator.onLine)
    window.addEventListener('online', updateOnline)
    window.addEventListener('offline', updateOnline)
    return () => {
      window.removeEventListener('online', updateOnline)
      window.removeEventListener('offline', updateOnline)
    }
  }, [])

  useEffect(() => {
    const queue = getQueue()
    setPendingCount(queue.filter(item => item.status === 'pending').length)
  }, [])

  const enqueue = (endpoint: string, method: string, data: any) => {
    const queue = getQueue()
    const item: OfflineItem = {
      id: Date.now(),
      endpoint,
      method,
      data,
      timestamp: Date.now(),
      status: 'pending',
    }
    queue.push(item)
    saveQueue(queue)
    setPendingCount(queue.filter(i => i.status === 'pending').length)
    return item.id
  }

  const syncQueue = async (apiCall: (item: OfflineItem) => Promise<void>) => {
    if (!navigator.onLine) return false

    const queue = getQueue()
    const pending = queue.filter(item => item.status === 'pending')

    for (const item of pending) {
      item.status = 'syncing'
      saveQueue(queue)

      try {
        await apiCall(item)
        item.status = 'synced'
      } catch {
        item.status = 'failed'
      }
      saveQueue(queue)
    }

    setPendingCount(getQueue().filter(i => i.status === 'pending').length)
    return true
  }

  const clearSynced = () => {
    const queue = getQueue().filter(item => item.status !== 'synced')
    saveQueue(queue)
    setPendingCount(queue.filter(i => i.status === 'pending').length)
  }

  return {
    isOnline,
    pendingCount,
    enqueue,
    syncQueue,
    clearSynced,
  }
}
