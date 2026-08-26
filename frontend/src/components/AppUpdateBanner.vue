<template>
  <Transition name="slide-up">
    <div
      v-if="needRefresh"
      class="fixed bottom-20 lg:bottom-4 left-4 right-4 lg:left-auto lg:right-4 lg:w-80
             bg-white border border-gray-200 rounded-2xl shadow-xl p-4 z-50
             flex items-start gap-3"
    >
      <!-- Icon -->
      <div class="flex-shrink-0 w-9 h-9 rounded-xl bg-farm-700 flex items-center justify-center">
        <svg class="w-5 h-5 text-white" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
          <path d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"/>
        </svg>
      </div>

      <!-- Text -->
      <div class="flex-1 min-w-0">
        <p class="font-semibold text-gray-900 text-sm">Update available</p>
        <p class="text-xs text-gray-500 mt-0.5">Reload to get the latest version.</p>
        <div class="flex gap-2 mt-3">
          <button
            @click="update"
            class="flex-1 py-1.5 bg-farm-700 text-white text-xs font-semibold rounded-lg
                   hover:bg-farm-600 active:bg-farm-800 transition-colors"
          >
            Reload now
          </button>
          <button
            @click="needRefresh = false"
            class="px-3 py-1.5 text-xs text-gray-500 hover:text-gray-700 transition-colors"
          >
            Later
          </button>
        </div>
      </div>

      <!-- Dismiss -->
      <button
        @click="needRefresh = false"
        class="flex-shrink-0 text-gray-400 hover:text-gray-600 transition-colors"
        aria-label="Dismiss"
      >
        <svg class="w-4 h-4" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
          <line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/>
        </svg>
      </button>
    </div>
  </Transition>
</template>

<script setup>
import { useRegisterSW } from 'virtual:pwa-register/vue'

const { needRefresh, updateServiceWorker } = useRegisterSW({
  onRegisteredSW(swUrl, r) {
    // Check for updates every 60 minutes while the app is open
    if (r) setInterval(() => r.update(), 60 * 60 * 1000)
  },
})

function update() {
  updateServiceWorker(true)
}
</script>

<style scoped>
.slide-up-enter-active,
.slide-up-leave-active {
  transition: transform 0.3s ease, opacity 0.3s ease;
}
.slide-up-enter-from,
.slide-up-leave-to {
  transform: translateY(1rem);
  opacity: 0;
}
</style>
