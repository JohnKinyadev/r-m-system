import { defineStore } from 'pinia'
import { ref, watch } from 'vue'
import { isOnline } from '@/composables/useOnlineStatus'
import { getPendingMutations, deleteMutation, cacheAll, upsertCached, kvSet } from '@/db/offlineDb'
import api from '@/api/index'

const CACHE_TTL_MS = 5 * 60 * 1000  // don't re-fetch if refreshed within last 5 min

export const useSyncStore = defineStore('sync', () => {
  const syncing       = ref(false)
  const pendingCount  = ref(0)
  const lastSynced    = ref(null)
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
          // 4xx = permanent failure — discard. 5xx / network = keep for next cycle.
          if (err.response?.status >= 400 && err.response?.status < 500) {
            await deleteMutation(m.id)
          }
        }
      }
      await refreshCaches(true) // force after sync to pick up server-created records
      lastSynced.value = new Date()

      if (replayed > 0) {
        try {
          const { useToastStore } = await import('@/stores/toast')
          useToastStore().success(
            'Changes synced!',
            `${replayed} offline change${replayed !== 1 ? 's' : ''} saved to the server.`,
            '☁️',
          )
        } catch { /* */ }
      }
    } finally {
      syncing.value = false
      await refreshPendingCount()
    }
  }

  /**
   * Pre-populate every IndexedDB store used by the offline GET map.
   * Throttled to once per CACHE_TTL_MS unless `force` is true.
   */
  async function refreshCaches(force = false) {
    if (!isOnline.value) return
    const now = Date.now()
    if (!force && lastCacheTime.value && now - lastCacheTime.value < CACHE_TTL_MS) return

    try {
      const [
        animals, feedTypes, livestockTypes, notifications,
        matingEvents, births,
        dashboard, herdHealth, birthMortality, feedConsumption,
      ] = await Promise.all([
        api.get('/api/animals').then(r => r.data),
        api.get('/api/feed/types').then(r => r.data),
        api.get('/api/livestock-types').then(r => r.data),
        api.get('/api/notifications').then(r => r.data),
        api.get('/api/mating').then(r => r.data),
        api.get('/api/mating/births').then(r => r.data),
        api.get('/api/reports/dashboard').then(r => r.data),
        api.get('/api/reports/herd-health').then(r => r.data),
        api.get('/api/reports/birth-mortality').then(r => r.data),
        api.get('/api/reports/feed-consumption').then(r => r.data),
      ])

      await Promise.all([
        cacheAll('animals',         animals),
        cacheAll('feed_types',      feedTypes),
        cacheAll('livestock_types', livestockTypes),
        cacheAll('notifications',   notifications),
        cacheAll('mating_events',   matingEvents),
        cacheAll('births',          births),
        kvSet('reports_dashboard',        dashboard),
        kvSet('reports_herd_health',      herdHealth),
        kvSet('reports_birth_mortality',  birthMortality),
        kvSet('reports_feed_consumption', feedConsumption),
      ])

      lastCacheTime.value = Date.now()
    } catch {
      // Stale cache is better than crashing — fail silently
    }
  }

  async function updateAnimalCache(animal) {
    await upsertCached('animals', animal)
  }

  watch(isOnline, async (online) => {
    if (online) {
      syncNow()
    } else {
      try {
        const { useToastStore } = await import('@/stores/toast')
        useToastStore().warning("You're offline", 'Changes will sync automatically when reconnected.', '📶')
      } catch { /* */ }
    }
  })

  return { syncing, pendingCount, lastSynced, syncNow, refreshCaches, refreshPendingCount, updateAnimalCache }
})
