<template>
  <Transition name="slide-down">
    <div v-if="!isOnline || pendingCount > 0"
         :class="[
           'flex items-center justify-between px-4 py-2 text-sm font-medium z-50',
           !isOnline ? 'bg-amber-500 text-white' : 'bg-farm-600 text-white',
         ]">
      <div class="flex items-center gap-2">
        <!-- Offline icon -->
        <svg v-if="!isOnline" class="w-4 h-4 flex-shrink-0" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
          <line x1="1" y1="1" x2="23" y2="23"/>
          <path d="M16.72 11.06A10.94 10.94 0 0119 12.55M5 12.55a10.94 10.94 0 015.17-2.39M10.71 5.05A16 16 0 0122.56 9M1.42 9a15.91 15.91 0 014.7-2.88M8.53 16.11a6 6 0 016.95 0M12 20h.01"/>
        </svg>
        <!-- Sync icon -->
        <svg v-else class="w-4 h-4 flex-shrink-0 animate-spin" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
          <polyline points="23 4 23 10 17 10"/>
          <path d="M20.49 15a9 9 0 1 1-2.12-9.36L23 10"/>
        </svg>

        <span v-if="!isOnline">
          You're offline — changes will sync when reconnected
          <span v-if="pendingCount > 0">({{ pendingCount }} pending)</span>
        </span>
        <span v-else>
          {{ syncStore.syncing ? 'Syncing changes…' : `${pendingCount} change(s) queued — syncing now` }}
        </span>
      </div>

      <button
        v-if="isOnline && !syncStore.syncing"
        @click="syncStore.syncNow()"
        class="text-xs underline hover:no-underline"
      >Sync now</button>
    </div>
  </Transition>
</template>

<script setup>
import { useOnlineStatus } from '@/composables/useOnlineStatus'
import { useSyncStore } from '@/stores/sync'
import { computed, onMounted } from 'vue'

const { isOnline } = useOnlineStatus()
const syncStore = useSyncStore()

const pendingCount = computed(() => syncStore.pendingCount)

onMounted(() => syncStore.refreshPendingCount())
</script>

<style scoped>
.slide-down-enter-active,
.slide-down-leave-active {
  transition: all 0.25s ease;
}
.slide-down-enter-from,
.slide-down-leave-to {
  transform: translateY(-100%);
  opacity: 0;
}
</style>
