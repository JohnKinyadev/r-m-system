import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { login as apiLogin } from '@/api/auth'
import router from '@/router'

const INACTIVITY_MS = 6 * 60 * 60 * 1000
const ACTIVITY_EVENTS = ['mousemove', 'keydown', 'touchstart', 'click', 'scroll', 'visibilitychange']

export const useAuthStore = defineStore('auth', () => {
  const token = ref(null)
  const user  = ref(null)

  const isLoggedIn    = computed(() => !!token.value)
  const isOwner       = computed(() => user.value?.role?.name === 'farm_owner')
  // modules the current user may access (owners get everything from the API response)
  const permissions   = computed(() => user.value?.permissions ?? [])

  function hasModule(module) {
    if (isOwner.value) return true
    return permissions.value.includes(module)
  }

  // ── Inactivity timer ────────────────────────────────────────────────────────
  let inactivityTimer = null

  function resetTimer() {
    clearTimeout(inactivityTimer)
    inactivityTimer = setTimeout(() => logout(), INACTIVITY_MS)
  }

  function startWatching() {
    ACTIVITY_EVENTS.forEach(e => window.addEventListener(e, resetTimer, { passive: true }))
    resetTimer()
  }

  function stopWatching() {
    clearTimeout(inactivityTimer)
    ACTIVITY_EVENTS.forEach(e => window.removeEventListener(e, resetTimer))
  }

  // ── Auth actions ─────────────────────────────────────────────────────────────
  function initFromStorage() {
    token.value = localStorage.getItem('token') || null
    const raw   = localStorage.getItem('user')
    user.value  = raw ? JSON.parse(raw) : null
    if (token.value) startWatching()
  }

  async function login(email, password) {
    const data  = await apiLogin(email, password)
    token.value = data.access_token
    user.value  = data.user   // includes permissions[] from the API
    localStorage.setItem('token', data.access_token)
    localStorage.setItem('user', JSON.stringify(data.user))
    startWatching()
  }

  function logout() {
    stopWatching()
    token.value = null
    user.value  = null
    localStorage.removeItem('token')
    localStorage.removeItem('user')
    router.push('/login')
  }

  return { token, user, isLoggedIn, isOwner, permissions, hasModule, initFromStorage, login, logout }
})
