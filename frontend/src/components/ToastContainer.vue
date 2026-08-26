<template>
  <Teleport to="body">
    <div class="fixed top-4 right-4 z-[9999] flex flex-col gap-2 pointer-events-none max-w-sm w-full">
      <TransitionGroup name="toast">
        <div
          v-for="t in toasts"
          :key="t.id"
          :class="[
            'pointer-events-auto flex items-start gap-3 px-4 py-3 rounded-xl shadow-lg border',
            typeClasses[t.type],
          ]"
        >
          <!-- Icon / emoji -->
          <span class="text-2xl flex-shrink-0 leading-none mt-0.5">{{ t.icon || defaultIcon[t.type] }}</span>

          <div class="flex-1 min-w-0">
            <p class="font-semibold text-sm leading-tight">{{ t.title }}</p>
            <p v-if="t.message" class="text-xs mt-0.5 opacity-80 leading-snug">{{ t.message }}</p>
          </div>

          <button @click="store.remove(t.id)" class="flex-shrink-0 opacity-50 hover:opacity-100 text-lg leading-none mt-0.5">&times;</button>
        </div>
      </TransitionGroup>
    </div>
  </Teleport>
</template>

<script setup>
import { computed } from 'vue'
import { useToastStore } from '@/stores/toast'

const store = useToastStore()
const toasts = computed(() => store.toasts)

const typeClasses = {
  success:   'bg-green-50  border-green-200  text-green-900',
  info:      'bg-blue-50   border-blue-200   text-blue-900',
  warning:   'bg-amber-50  border-amber-200  text-amber-900',
  celebrate: 'bg-farm-50   border-farm-300   text-farm-900',
}

const defaultIcon = {
  success:   '✅',
  info:      'ℹ️',
  warning:   '⚠️',
  celebrate: '🎉',
}
</script>

<style scoped>
.toast-enter-active  { transition: all 0.3s cubic-bezier(0.34, 1.56, 0.64, 1); }
.toast-leave-active  { transition: all 0.2s ease-in; }
.toast-enter-from    { transform: translateX(110%); opacity: 0; }
.toast-leave-to      { transform: translateX(110%); opacity: 0; }
.toast-move          { transition: transform 0.3s ease; }
</style>
