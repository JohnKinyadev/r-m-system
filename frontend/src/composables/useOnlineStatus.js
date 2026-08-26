import { ref, onMounted, onUnmounted } from 'vue'

// Singleton — safe to use in stores and interceptors outside components
export const isOnline = ref(typeof navigator !== 'undefined' ? navigator.onLine : true)

function handleOnline()  { isOnline.value = true  }
function handleOffline() { isOnline.value = false }

// Register global listeners once at module load (browser only)
if (typeof window !== 'undefined') {
  window.addEventListener('online',  handleOnline)
  window.addEventListener('offline', handleOffline)
}

export function useOnlineStatus() {
  // For components that want reactivity and (optionally) cleanup
  onUnmounted(() => {
    // Global listeners intentionally persist — don't remove them here
  })
  return { isOnline }
}
