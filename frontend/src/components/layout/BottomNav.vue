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
  { to: '/animals',   label: 'Animals',  module: 'animals', svg: '<svg viewBox="0 0 24 24" fill="currentColor" class="w-6 h-6"><circle cx="6" cy="7" r="2"/><circle cx="12" cy="4" r="2"/><circle cx="18" cy="7" r="2"/><circle cx="9" cy="11" r="2"/><path d="M12 14c-3 0-6 2-6 5h12c0-3-3-5-6-5z"/></svg>' },
  { to: '/feed',      label: 'Feed',     module: 'feed', svg: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="w-6 h-6"><path d="M21 16V8a2 2 0 00-1-1.73l-7-4a2 2 0 00-2 0l-7 4A2 2 0 003 8v8a2 2 0 001 1.73l7 4a2 2 0 002 0l7-4A2 2 0 0021 16z"/></svg>' },
  { to: '/health',    label: 'Health',   module: 'health', svg: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="w-6 h-6"><path d="M20.84 4.61a5.5 5.5 0 00-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 00-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 000-7.78z"/></svg>' },
  { to: '/notifications', label: 'Alerts', module: null, badge: true, svg: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="w-6 h-6"><path d="M18 8A6 6 0 006 8c0 7-3 9-3 9h18s-3-2-3-9"/><path d="M13.73 21a2 2 0 01-3.46 0"/></svg>' },
  { to: '/profile',   label: 'Profile',  module: null, svg: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="w-6 h-6"><path d="M20 21v-2a4 4 0 00-4-4H8a4 4 0 00-4 4v2"/><circle cx="12" cy="7" r="4"/></svg>' },
]

const tabs = computed(() =>
  ALL_TABS.filter(t => !t.module || auth.hasModule(t.module))
)
</script>
