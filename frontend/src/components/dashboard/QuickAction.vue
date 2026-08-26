<template>
  <RouterLink
    :to="to"
    class="flex flex-col items-center justify-center p-3 rounded-xl border-2 border-dashed text-center transition-all hover:scale-105 hover:shadow-sm"
    :class="borderClass"
  >
    <span class="text-2xl mb-1 block">{{ emoji }}</span>
    <span class="text-xs font-medium" :class="textClass">{{ label }}</span>
  </RouterLink>
</template>

<script setup>
import { computed } from 'vue'
import { RouterLink } from 'vue-router'

const props = defineProps({ to: String, label: String, color: String, emoji: { type: String, default: '+' } })

const borderClass = computed(() => ({
  farm: 'border-farm-300 hover:bg-farm-50',
  amber: 'border-amber-300 hover:bg-amber-50',
  blue: 'border-blue-300 hover:bg-blue-50',
  purple: 'border-purple-300 hover:bg-purple-50',
}[props.color]))

const textClass = computed(() => ({
  farm: 'text-farm-700',
  amber: 'text-amber-700',
  blue: 'text-blue-700',
  purple: 'text-purple-700',
}[props.color]))
</script>
