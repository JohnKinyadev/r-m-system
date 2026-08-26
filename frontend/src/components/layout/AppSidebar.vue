<template>
  <aside class="w-64 flex-shrink-0 bg-farm-700 text-white flex flex-col h-full">
    <!-- Logo -->
    <div class="flex items-center gap-3 px-6 py-5 border-b border-farm-600">
      <svg class="w-8 h-8 text-farm-200" fill="currentColor" viewBox="0 0 24 24">
        <path d="M12 2L2 7l10 5 10-5-10-5zm0 7L2 14l10 5 10-5-10-5z"/>
      </svg>
      <div>
        <p class="font-bold text-sm leading-tight">FarmManager</p>
        <p class="text-farm-300 text-xs">Ranch & Livestock</p>
      </div>
    </div>

    <!-- Nav -->
    <nav class="flex-1 px-3 py-4 space-y-1 overflow-y-auto">
      <SidebarLink v-for="link in navLinks" :key="link.to" v-bind="link" />
    </nav>

    <!-- User footer -->
    <div class="px-4 py-4 border-t border-farm-600">
      <div class="flex items-center gap-3 mb-3">
        <div class="w-8 h-8 rounded-full bg-farm-500 flex items-center justify-center text-sm font-bold">
          {{ initials }}
        </div>
        <div class="min-w-0">
          <p class="text-sm font-medium truncate">{{ auth.user?.full_name }}</p>
          <p class="text-xs text-farm-300 truncate">{{ auth.isOwner ? 'Farm Owner' : 'Farm Worker' }}</p>
        </div>
      </div>
      <button @click="auth.logout()" class="w-full text-left text-xs text-farm-300 hover:text-white transition-colors py-1">
        Sign out
      </button>
    </div>
  </aside>
</template>

<script setup>
import { computed } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { useNotificationStore } from '@/stores/notifications'
import SidebarLink from './SidebarLink.vue'

const auth = useAuthStore()
const notifStore = useNotificationStore()

const initials = computed(() => {
  const name = auth.user?.full_name || ''
  return name.split(' ').map(w => w[0]).slice(0, 2).join('').toUpperCase()
})

const ALL_LINKS = [
  { to: '/dashboard',       icon: 'grid',       label: 'Dashboard',        module: null },
  { to: '/animals',         icon: 'paw',        label: 'Animals',          module: 'animals' },
  { to: '/livestock-types', icon: 'tag',        label: 'Livestock Types',  module: 'livestock_types' },
  { to: '/feed',            icon: 'box',        label: 'Feed',             module: 'feed' },
  { to: '/health',          icon: 'heart',      label: 'Health',           module: 'health' },
  { to: '/mating',          icon: 'link',       label: 'Mating & Births',  module: 'mating' },
  { to: '/reports',         icon: 'bar-chart',  label: 'Reports',          module: 'reports' },
  { to: '/notifications',   icon: 'bell',       label: 'Notifications',    module: null, badge: notifStore.unreadCount },
]

const navLinks = computed(() => {
  const links = ALL_LINKS.filter(l => !l.module || auth.hasModule(l.module))
  if (auth.isOwner) links.push({ to: '/workers', icon: 'users', label: 'Workers', module: null })
  links.push({ to: '/profile', icon: 'user', label: 'My Profile', module: null })
  return links
})
</script>
