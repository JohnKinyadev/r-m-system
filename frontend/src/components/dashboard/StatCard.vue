<template>
  <div class="card flex items-center gap-3">
    <div class="w-10 h-10 rounded-xl flex-shrink-0 flex items-center justify-center" :class="bgClass">
      <span class="w-5 h-5 text-white" v-html="iconSvg" />
    </div>
    <div>
      <p class="text-2xl font-bold text-gray-800">{{ value }}</p>
      <p class="text-xs text-gray-500">{{ label }}</p>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  label: String,
  value: [String, Number],
  color: { type: String, default: 'green' },
  icon: String,
})

const bgClass = computed(() => ({
  green:  'bg-green-500',
  blue:   'bg-blue-500',
  amber:  'bg-amber-500',
  red:    'bg-red-500',
  purple: 'bg-purple-500',
}[props.color] || 'bg-gray-400'))

const icons = {
  paw: '<svg viewBox="0 0 24 24" fill="currentColor"><circle cx="6" cy="7" r="2"/><circle cx="12" cy="4" r="2"/><circle cx="18" cy="7" r="2"/><circle cx="9" cy="11" r="2"/><path d="M12 14c-3 0-6 2-6 5h12c0-3-3-5-6-5z"/></svg>',
  baby: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="8" r="4"/><path d="M8 16s1 2 4 2 4-2 4-2"/><line x1="12" y1="12" x2="12" y2="16"/></svg>',
  calendar: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="4" width="18" height="18" rx="2"/><line x1="16" y1="2" x2="16" y2="6"/><line x1="8" y1="2" x2="8" y2="6"/><line x1="3" y1="10" x2="21" y2="10"/></svg>',
  alert: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M10.29 3.86L1.82 18a2 2 0 001.71 3h16.94a2 2 0 001.71-3L13.71 3.86a2 2 0 00-3.42 0z"/><line x1="12" y1="9" x2="12" y2="13"/><line x1="12" y1="17" x2="12.01" y2="17"/></svg>',
}

const iconSvg = computed(() => icons[props.icon] || '')
</script>
