import { ref, onMounted, onUnmounted } from 'vue'

const deferredPrompt = ref(null)

function onBeforeInstall(e) {
  e.preventDefault()
  deferredPrompt.value = e
  window.__pwaPrompt = e
}

function onAppInstalled() {
  deferredPrompt.value = null
  window.__pwaPrompt = null
}

if (typeof window !== 'undefined') {
  window.addEventListener('beforeinstallprompt', onBeforeInstall)
  window.addEventListener('appinstalled', onAppInstalled)
}

export function usePwaInstall() {
  const isStandalone = ref(false)
  const isCapacitor = ref(false)

  onMounted(() => {
    isStandalone.value =
      window.matchMedia('(display-mode: standalone)').matches ||
      window.navigator.standalone === true
    isCapacitor.value = !!window.Capacitor

    // Pick up the event if it fired before this module loaded
    if (window.__pwaPrompt && !deferredPrompt.value) {
      deferredPrompt.value = window.__pwaPrompt
    }
  })

  async function install() {
    if (!deferredPrompt.value) return false
    deferredPrompt.value.prompt()
    const { outcome } = await deferredPrompt.value.userChoice
    if (outcome === 'accepted') {
      deferredPrompt.value = null
      window.__pwaPrompt = null
    }
    return outcome === 'accepted'
  }

  return {
    canInstall: deferredPrompt,
    isStandalone,
    isCapacitor,
    install,
  }
}
