<template>
  <header class="bg-farm-700 px-4 py-3 flex items-center justify-between lg:px-6">
    <h1 class="text-lg font-semibold text-white">{{ pageTitle }}</h1>

    <div class="flex items-center gap-3">

      <!-- PWA install button — always visible, hidden inside Capacitor native app -->
      <div v-if="!isCapacitor" class="relative" ref="installAnchor">
        <button
          @click="handleInstall"
          class="p-2 rounded-lg hover:bg-farm-600 transition-colors"
          :title="installLabel"
          aria-label="Install app"
        >
          <!-- Checkmark when already installed -->
          <svg v-if="isStandalone" class="w-5 h-5 text-farm-200" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M20 6L9 17l-5-5"/>
          </svg>
          <!-- Download icon otherwise -->
          <svg v-else class="w-5 h-5 text-white" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M21 15v4a2 2 0 01-2 2H5a2 2 0 01-2-2v-4"/>
            <polyline points="7 10 12 15 17 10"/>
            <line x1="12" y1="15" x2="12" y2="3"/>
          </svg>
        </button>

        <!-- Manual-install instructions popover -->
        <div
          v-if="showInstructions"
          class="absolute right-0 top-11 z-50 w-72 bg-white border border-gray-200 rounded-xl shadow-lg p-4 text-sm"
        >
          <div class="flex items-center justify-between mb-2">
            <span class="font-semibold text-gray-800">Install RentManager</span>
            <button @click="showInstructions = false" class="text-gray-400 hover:text-gray-600">
              <svg class="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/>
              </svg>
            </button>
          </div>
          <!-- iOS but NOT Safari — must switch browser -->
          <template v-if="isIos && !isIosSafari">
            <p class="text-amber-600 font-medium mb-2 text-xs">⚠ Chrome &amp; Firefox on iPhone/iPad cannot install PWAs.</p>
            <p class="text-gray-600 text-xs">Copy this URL, open <strong>Safari</strong>, paste it, then tap the Share button&nbsp;
              <svg class="w-3 h-3 inline" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M4 12v8a2 2 0 002 2h12a2 2 0 002-2v-8"/><polyline points="16 6 12 2 8 6"/><line x1="12" y1="2" x2="12" y2="15"/>
              </svg>
              → <strong>Add to Home Screen</strong>.
            </p>
          </template>

          <!-- iOS Safari — correct browser -->
          <template v-else-if="isIosSafari">
            <p class="text-gray-500 mb-2 text-xs">Add this app to your home screen:</p>
            <ol class="space-y-1.5 text-gray-700 text-xs list-decimal list-inside">
              <li>Tap the <strong>Share</strong> button&nbsp;
                <svg class="w-3 h-3 inline" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <path d="M4 12v8a2 2 0 002 2h12a2 2 0 002-2v-8"/><polyline points="16 6 12 2 8 6"/><line x1="12" y1="2" x2="12" y2="15"/>
                </svg>
                at the bottom of the screen.
              </li>
              <li>Scroll down and tap <strong>Add to Home Screen</strong>.</li>
              <li>Tap <strong>Add</strong> to confirm.</li>
            </ol>
          </template>

          <!-- Android / Desktop -->
          <template v-else>
            <p class="text-gray-500 mb-2 text-xs">Add this app to your home screen:</p>
            <ul class="space-y-1.5 text-gray-700 text-xs">
              <li><strong>Android Chrome:</strong> tap ⋮ → <strong>Add to Home screen</strong>.</li>
              <li><strong>Desktop Chrome/Edge:</strong> click the install icon ⊕ in the address bar.</li>
            </ul>
          </template>
        </div>
      </div>

      <!-- Notification bell -->
      <RouterLink to="/notifications" class="relative p-2 rounded-lg hover:bg-farm-600 transition-colors">
        <svg class="w-5 h-5 text-white" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M18 8A6 6 0 006 8c0 7-3 9-3 9h18s-3-2-3-9"/>
          <path d="M13.73 21a2 2 0 01-3.46 0"/>
        </svg>
        <span
          v-if="notifStore.unreadCount > 0"
          class="absolute top-1 right-1 w-4 h-4 bg-red-500 text-white text-xs font-bold rounded-full flex items-center justify-center"
        >
          {{ notifStore.unreadCount > 9 ? '9+' : notifStore.unreadCount }}
        </span>
      </RouterLink>

      <!-- Avatar (desktop) — links to profile -->
      <RouterLink to="/profile" class="hidden lg:flex items-center gap-2 rounded-full hover:ring-2 hover:ring-farm-300 transition-all">
        <div class="w-8 h-8 rounded-full bg-farm-700 text-white flex items-center justify-center text-sm font-bold">
          {{ initials }}
        </div>
      </RouterLink>
    </div>
  </header>
</template>

<script setup>
import { computed, ref, onMounted, onUnmounted } from 'vue'
import { useRoute, RouterLink } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useNotificationStore } from '@/stores/notifications'
import { usePwaInstall } from '@/composables/usePwaInstall'

const route = useRoute()
const auth = useAuthStore()
const notifStore = useNotificationStore()
const { canInstall, isStandalone, isCapacitor, install } = usePwaInstall()

const showInstructions = ref(false)
const installAnchor = ref(null)
const isIos = ref(false)
const isIosSafari = ref(false)

onMounted(() => {
  const ua = navigator.userAgent
  // iPadOS 13+ reports as Macintosh — detect via touch points
  isIos.value = /iphone|ipad|ipod/i.test(ua) ||
    (navigator.platform === 'MacIntel' && navigator.maxTouchPoints > 1)
  // Only Safari on iOS supports "Add to Home Screen"
  isIosSafari.value = isIos.value &&
    /safari/i.test(ua) && !/crios|chrome|fxios|opios/i.test(ua)

  // Close popover on outside click
  document.addEventListener('click', onOutsideClick)
})
onUnmounted(() => document.removeEventListener('click', onOutsideClick))

function onOutsideClick(e) {
  if (installAnchor.value && !installAnchor.value.contains(e.target)) {
    showInstructions.value = false
  }
}

async function handleInstall() {
  if (isStandalone.value) return   // already installed — button is decorative
  if (canInstall.value) {
    await install()
  } else {
    showInstructions.value = !showInstructions.value
  }
}

const installLabel = computed(() => {
  if (isStandalone.value) return 'App installed'
  if (canInstall.value) return 'Install app'
  return 'How to install'
})

const titles = {
  dashboard: 'Dashboard',
  properties: 'Properties',
  units: 'Units',
  tenants: 'Tenants',
  rent: 'Rent Ledger',
  payments: 'Payments',
  maintenance: 'Maintenance',
  expenses: 'Expenses',
  reports: 'Reports',
  notifications: 'Notifications',
  caretakers: 'Caretakers',
  profile: 'My Profile',
}

const pageTitle = computed(() => titles[route.name] || 'Rent Manager')
const initials = computed(() => {
  const name = auth.user?.full_name || ''
  return name.split(' ').map(w => w[0]).slice(0, 2).join('').toUpperCase()
})
</script>
