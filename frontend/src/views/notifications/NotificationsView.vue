<template>
  <div class="space-y-3">
    <div class="flex items-center justify-between">
      <p class="text-sm text-gray-500">{{ store.items.length }} notification(s)</p>
      <BaseButton v-if="store.unreadCount > 0" variant="secondary" class="text-sm" @click="store.markAll()">
        Mark all read
      </BaseButton>
    </div>

    <div v-if="store.items.length === 0" class="card text-center py-12 text-gray-400">
      No notifications.
    </div>

    <div
      v-for="n in store.items"
      :key="n.id"
      class="card flex gap-3 transition-all"
      :class="n.is_read ? 'opacity-70' : 'border-l-4 border-farm-500'"
    >
      <div class="w-8 h-8 rounded-full flex-shrink-0 flex items-center justify-center" :class="typeColor(n.type)">
        <span class="text-sm">{{ typeEmoji(n.type) }}</span>
      </div>
      <div class="flex-1 min-w-0">
        <div class="flex items-start justify-between gap-2">
          <p class="text-sm font-semibold text-gray-800">{{ n.title }}</p>
          <span class="text-xs text-gray-400 flex-shrink-0">{{ formatDate(n.created_at) }}</span>
        </div>
        <p class="text-sm text-gray-600 mt-0.5">{{ n.message }}</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { onMounted } from 'vue'
import { useNotificationStore } from '@/stores/notifications'
import BaseButton from '@/components/ui/BaseButton.vue'

const store = useNotificationStore()

const typeColor = (type) => ({
  birth_alert:     'bg-green-100',
  vaccination_due: 'bg-blue-100',
  feed_stock_low:  'bg-red-100',
  missed_feeding:  'bg-amber-100',
  general:         'bg-gray-100',
}[type] || 'bg-gray-100')

const typeEmoji = (type) => ({
  birth_alert:     '🐣',
  vaccination_due: '💉',
  feed_stock_low:  '⚠️',
  missed_feeding:  '📋',
  general:         '📢',
}[type] || '📢')

const formatDate = (d) => d ? new Date(d).toLocaleDateString() : ''

onMounted(() => store.fetch())
</script>
