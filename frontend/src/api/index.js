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
  { test: (u) => u === '/api/properties', store: 'properties', single: false },
  { test: (u) => /^\/api\/properties\/\d+$/.test(u), store: 'properties', single: true },
  { test: (u) => u === '/api/units', store: 'units', single: false },
  { test: (u) => /^\/api\/units\/\d+$/.test(u), store: 'units', single: true },
  { test: (u) => u === '/api/tenants', store: 'tenants', single: false },
  { test: (u) => /^\/api\/tenants\/\d+$/.test(u), store: 'tenants', single: true },
  { test: (u) => u === '/api/tenancies', store: 'tenancies', single: false },
  { test: (u) => u === '/api/payments', store: 'payments', single: false },
  { test: (u) => u === '/api/maintenance', store: 'maintenance', single: false },
  { test: (u) => u === '/api/expenses', store: 'expenses', single: false },
  { test: (u) => u.startsWith('/api/notifications'), store: 'notifications', single: false },
  { test: (u) => u === '/api/reports/dashboard', kvKey: () => 'reports_dashboard', isArray: false },
  { test: (u) => u === '/api/reports/arrears', kvKey: () => 'reports_arrears', isArray: true },
  { test: (u) => u === '/api/reports/property-performance', kvKey: () => 'reports_property_performance', isArray: true },
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
