import axios from 'axios'
import { isOnline } from '@/composables/useOnlineStatus'
import { enqueueMutation, getCached, kvGet } from '@/db/offlineDb'

const MUTATION_METHODS = new Set(['post', 'patch', 'put', 'delete'])

// These endpoints must NEVER be queued — they require a live server response.
const NO_QUEUE_PREFIXES = ['/api/auth/']

const OFFLINE_CACHE_SENTINEL = '__offline_cache__'

/**
 * Map of URL patterns → how to serve them from the local cache when offline.
 *
 * Each entry is either:
 *  • { test, store, single }  – read from an IDB object-store (keyPath:'id')
 *  • { test, kvKey, isArray } – read from the KV store using a computed key
 */
const OFFLINE_GET_MAP = [
  // ── Animals ──────────────────────────────────────────────────────────────
  { test: (u) => u === '/api/animals',                    store: 'animals',         single: false },
  { test: (u) => /^\/api\/animals\/\d+$/.test(u),         store: 'animals',         single: true  },

  // ── Livestock types ───────────────────────────────────────────────────────
  { test: (u) => u.startsWith('/api/livestock-types'),     store: 'livestock_types', single: false },

  // ── Feed ─────────────────────────────────────────────────────────────────
  { test: (u) => u.startsWith('/api/feed/types'),          store: 'feed_types',      single: false },

  // ── Mating & births ───────────────────────────────────────────────────────
  { test: (u) => u === '/api/mating',                      store: 'mating_events',   single: false },
  { test: (u) => u.startsWith('/api/mating/births'),       store: 'births',          single: false },

  // ── Notifications ─────────────────────────────────────────────────────────
  { test: (u) => u.startsWith('/api/notifications'),       store: 'notifications',   single: false },

  // ── Health logs per animal (lazy-cached in AnimalDetailView) ─────────────
  {
    test:    (u) => /^\/api\/health\/animal\/\d+$/.test(u),
    kvKey:   (u) => `health_logs_${u.split('/').pop()}`,
    isArray: true,
  },

  // ── Reports (cached in refreshCaches) ────────────────────────────────────
  { test: (u) => u === '/api/reports/dashboard',           kvKey: () => 'reports_dashboard',         isArray: false },
  { test: (u) => u === '/api/reports/herd-health',         kvKey: () => 'reports_herd_health',       isArray: false },
  { test: (u) => u === '/api/reports/birth-mortality',     kvKey: () => 'reports_birth_mortality',   isArray: false },
  { test: (u) => u === '/api/reports/feed-consumption',    kvKey: () => 'reports_feed_consumption',  isArray: true  },
]

async function serveFromCache(urlPath) {
  const entry = OFFLINE_GET_MAP.find(e => e.test(urlPath))
  if (!entry) return []   // No mapping → empty response; page shows "no data"

  if (entry.kvKey) {
    const val = await kvGet(entry.kvKey(urlPath))
    return val ?? (entry.isArray ? [] : null)
  }

  const all = await getCached(entry.store)
  if (entry.single) {
    const id = parseInt(urlPath.split('/').pop(), 10)
    return all.find(item => item.id === id) ?? null
  }
  return all
}

// ── Axios instance ────────────────────────────────────────────────────────────

const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || '',
  timeout: 15000,
})

api.interceptors.request.use(async (config) => {
  const token = localStorage.getItem('token')
  if (token) config.headers.Authorization = `Bearer ${token}`

  if (!isOnline.value) {
    const method = config.method?.toLowerCase()
    const urlPath = (config.url ?? '').split('?')[0]

    if (MUTATION_METHODS.has(method)) {
      const isExempt = NO_QUEUE_PREFIXES.some(p => urlPath.startsWith(p))
      if (isExempt) {
        const err = new Error('offline'); err.isOffline = true
        return Promise.reject(err)
      }
      await enqueueMutation({
        method: config.method,
        url: config.url,
        data: config.data ? JSON.parse(JSON.stringify(config.data)) : undefined,
      })
      const err = new Error('offline'); err.isOfflineQueued = true
      return Promise.reject(err)
    }

    if (method === 'get') {
      const cached = await serveFromCache(urlPath)
      const err = new Error(OFFLINE_CACHE_SENTINEL)
      err[OFFLINE_CACHE_SENTINEL] = cached
      return Promise.reject(err)
    }
  }

  return config
})

api.interceptors.response.use(
  (res) => res,
  (err) => {
    if (err.isOfflineQueued) return Promise.reject(err)
    if (err.isOffline)       return Promise.reject(err)

    if (err[OFFLINE_CACHE_SENTINEL] !== undefined) {
      return Promise.resolve({ data: err[OFFLINE_CACHE_SENTINEL], status: 200, offline: true })
    }

    if (err.response?.status === 401) {
      localStorage.removeItem('token')
      localStorage.removeItem('user')
      window.location.href = '/login'
    }
    return Promise.reject(err)
  }
)

export default api
