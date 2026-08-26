import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { listNotifications, markAllRead } from '@/api/notifications'

export const useNotificationStore = defineStore('notifications', () => {
  const items = ref([])

  const unreadCount = computed(() => items.value.filter(n => !n.is_read).length)

  async function fetch() {
    items.value = await listNotifications()
  }

  async function markAll() {
    await markAllRead()
    items.value = items.value.map(n => ({ ...n, is_read: true }))
  }

  return { items, unreadCount, fetch, markAll }
})
