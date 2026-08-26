<template>
  <div class="flex flex-col h-full bg-gray-50">
    <!-- Offline / pending-sync banner — always on top -->
    <OfflineBanner />

    <div class="flex flex-1 min-h-0 overflow-hidden">
      <!-- Sidebar — desktop only -->
      <AppSidebar class="hidden lg:flex" />

      <div class="flex-1 flex flex-col min-w-0 overflow-hidden">
        <AppHeader />

        <main class="flex-1 overflow-y-auto p-4 pb-24 lg:pb-6">
          <RouterView />
        </main>
      </div>
    </div>

    <!-- Bottom nav — mobile only -->
    <BottomNav class="lg:hidden" />
  </div>
</template>

<script setup>
import { RouterView } from 'vue-router'
import AppSidebar from './AppSidebar.vue'
import AppHeader from './AppHeader.vue'
import BottomNav from './BottomNav.vue'
import OfflineBanner from '@/components/OfflineBanner.vue'
import { onMounted } from 'vue'
import { useNotificationStore } from '@/stores/notifications'
import { useAuthStore } from '@/stores/auth'
import { useSyncStore } from '@/stores/sync'

const notifStore = useNotificationStore()
const auth = useAuthStore()
const syncStore = useSyncStore()

onMounted(async () => {
  if (auth.isLoggedIn) {
    await notifStore.fetch()
    await syncStore.refreshPendingCount()
    // Prime local caches on first mount
    syncStore.refreshCaches()
  }
})
</script>
