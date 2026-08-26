<template>
  <nav class="fixed bottom-0 left-0 right-0 bg-farm-700 flex z-50"
       style="padding-bottom: env(safe-area-inset-bottom)">
    <RouterLink
      v-for="item in tabs"
      :key="item.to"
      :to="item.to"
      class="flex-1 flex flex-col items-center justify-center py-2 text-xs transition-colors"
      :class="isActive(item.to) ? 'text-white' : 'text-farm-300'"
    >
      <span class="w-6 h-6 mb-0.5 relative">
        <span v-html="item.svg" />
        <span
          v-if="item.badge && notifStore.unreadCount > 0"
          class="absolute -top-1 -right-1 w-4 h-4 bg-red-500 text-white text-xs font-bold rounded-full flex items-center justify-center"
        >{{ notifStore.unreadCount > 9 ? '9+' : notifStore.unreadCount }}</span>
      </span>
      <span>{{ item.label }}</span>
    </RouterLink>
  </nav>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute, RouterLink } from 'vue-router'
import { useNotificationStore } from '@/stores/notifications'
import { useAuthStore } from '@/stores/auth'

const route = useRoute()
const notifStore = useNotificationStore()
const auth = useAuthStore()

const isActive = (to) => route.path.startsWith(to)

const ALL_TABS = [
  { to: '/dashboard', label: 'Home',     module: null, svg: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="w-6 h-6"><rect x="3" y="3" width="7" height="7"/><rect x="14" y="3" width="7" height="7"/><rect x="14" y="14" width="7" height="7"/><rect x="3" y="14" width="7" height="7"/></svg>' },
  { to: '/properties', label: 'Property', module: 'properties', svg: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="w-6 h-6"><path d="M3 21h18"/><path d="M5 21V5a2 2 0 012-2h7a2 2 0 012 2v16"/><path d="M9 7h1M9 11h1M9 15h1M14 21v-5h3v5"/></svg>' },
  { to: '/units', label: 'Units', module: 'units', svg: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="w-6 h-6"><path d="M3 11l9-8 9 8"/><path d="M5 10v11h14V10"/><path d="M9 21v-6h6v6"/></svg>' },
  { to: '/rent', label: 'Rent', module: 'rent', svg: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="w-6 h-6"><path d="M4 2v20l2-1 2 1 2-1 2 1 2-1 2 1 2-1 2 1V2z"/><path d="M8 7h8M8 11h8M8 15h5"/></svg>' },
  { to: '/notifications', label: 'Alerts', module: null, badge: true, svg: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="w-6 h-6"><path d="M18 8A6 6 0 006 8c0 7-3 9-3 9h18s-3-2-3-9"/><path d="M13.73 21a2 2 0 01-3.46 0"/></svg>' },
  { to: '/profile',   label: 'Profile',  module: null, svg: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="w-6 h-6"><path d="M20 21v-2a4 4 0 00-4-4H8a4 4 0 00-4 4v2"/><circle cx="12" cy="7" r="4"/></svg>' },
]

const tabs = computed(() =>
  ALL_TABS.filter(t => !t.module || auth.hasModule(t.module))
)
</script>
