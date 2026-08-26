import { defineStore } from 'pinia'
import { ref } from 'vue'

let nextId = 1

export const useToastStore = defineStore('toast', () => {
  const toasts = ref([])

  function add({ type = 'info', title, message, icon = null, duration = 4000 }) {
    const id = nextId++
    toasts.value.push({ id, type, title, message, icon, duration })
    if (duration > 0) {
      setTimeout(() => remove(id), duration)
    }
    return id
  }

  function remove(id) {
    toasts.value = toasts.value.filter(t => t.id !== id)
  }

  // Convenience helpers
  const success = (title, message, icon) => add({ type: 'success', title, message, icon })
  const info    = (title, message, icon) => add({ type: 'info',    title, message, icon })
  const warning = (title, message, icon) => add({ type: 'warning', title, message, icon })
  const celebrate = (title, message, icon) => add({ type: 'celebrate', title, message, icon, duration: 5000 })

  return { toasts, add, remove, success, info, warning, celebrate }
})
