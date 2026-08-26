import { defineStore } from 'pinia'
import { ref, watch } from 'vue'
import { isOnline } from '@/composables/useOnlineStatus'
import { getPendingMutations, deleteMutation, cacheAll, upsertCached, kvSet } from '@/db/offlineDb'
import api from '@/api/index'

const CACHE_TTL_MS = 5 * 60 * 1000

export const useSyncStore = defineStore('sync', () => {
  const syncing = ref(false)
  const pendingCount = ref(0)
  const lastSynced = ref(null)
  const lastCacheTime = ref(null)

  async function refreshPendingCount() {
    const mutations = await getPendingMutations()
    pendingCount.value = mutations.length
  }

  async function syncNow() {
    if (syncing.value || !isOnline.value) return
    syncing.value = true
    let replayed = 0
    try {
      const mutations = await getPendingMutations()
      for (const m of mutations) {
        try {
          await api.request({ method: m.method, url: m.url, data: m.data })
          await deleteMutation(m.id)
          replayed++
        } catch (err) {
          if (err.response?.status >= 400 && err.response?.status < 500) {
            await deleteMutation(m.id)
          }
        }
      }
      await refreshCaches(true)
      lastSynced.value = new Date()

      if (replayed > 0) {
        try {
          const { useToastStore } = await import('@/stores/toast')
          useToastStore().success(
            'Changes synced',
            `${replayed} offline change${replayed !== 1 ? 's' : ''} saved to the server.`,
            'OK',
          )
        } catch { /* empty */ }
      }
    } finally {
      syncing.value = false
      await refreshPendingCount()
    }
  }

  async function refreshCaches(force = false) {
    if (!isOnline.value) return
    const now = Date.now()
    if (!force && lastCacheTime.value && now - lastCacheTime.value < CACHE_TTL_MS) return

    try {
      const [
        properties, units, tenants, tenancies,
        payments, maintenance, expenses, notifications,
        dashboard, arrears, propertyPerformance,
      ] = await Promise.all([
        api.get('/api/properties').then(r => r.data),
        api.get('/api/units').then(r => r.data),
        api.get('/api/tenants').then(r => r.data),
        api.get('/api/tenancies').then(r => r.data),
        api.get('/api/payments').then(r => r.data),
        api.get('/api/maintenance').then(r => r.data),
        api.get('/api/expenses').then(r => r.data),
        api.get('/api/notifications').then(r => r.data),
        api.get('/api/reports/dashboard').then(r => r.data),
        api.get('/api/reports/arrears').then(r => r.data),
        api.get('/api/reports/property-performance').then(r => r.data),
      ])

      await Promise.all([
        cacheAll('properties', properties),
        cacheAll('units', units),
        cacheAll('tenants', tenants),
        cacheAll('tenancies', tenancies),
        cacheAll('payments', payments),
        cacheAll('maintenance', maintenance),
        cacheAll('expenses', expenses),
        cacheAll('notifications', notifications),
        kvSet('reports_dashboard', dashboard),
        kvSet('reports_arrears', arrears),
        kvSet('reports_property_performance', propertyPerformance),
      ])

      lastCacheTime.value = Date.now()
    } catch {
      // Existing cached data is preferable to crashing the app while offline.
    }
  }

  async function updateUnitCache(unit) {
    await upsertCached('units', unit)
  }

  watch(isOnline, async (online) => {
    if (online) {
      syncNow()
    } else {
      try {
        const { useToastStore } = await import('@/stores/toast')
        useToastStore().warning("You're offline", 'Changes will sync automatically when reconnected.', 'OFF')
      } catch { /* empty */ }
    }
  })

  return { syncing, pendingCount, lastSynced, syncNow, refreshCaches, refreshPendingCount, updateUnitCache }
})
