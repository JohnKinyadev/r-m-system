<template>
  <Teleport to="body">
    <Transition name="fade">
      <div v-if="active" class="fixed inset-0 pointer-events-none z-[9998] overflow-hidden">
        <span
          v-for="p in particles"
          :key="p.id"
          :style="p.style"
          class="absolute text-4xl select-none"
        >{{ p.emoji }}</span>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup>
import { ref } from 'vue'

const active = ref(false)
const particles = ref([])

function randomBetween(a, b) {
  return a + Math.random() * (b - a)
}

/**
 * Trigger the celebration.
 * @param {string[]} emojis - array of emojis to rain down
 * @param {number} count - how many particles
 */
function celebrate(emojis = ['🐄', '🐑', '🐐', '🐷', '🐔'], count = 18) {
  particles.value = Array.from({ length: count }, (_, i) => {
    const left = randomBetween(2, 98)
    const delay = randomBetween(0, 1.2)
    const duration = randomBetween(2.4, 4.0)
    const size = randomBetween(1.8, 3.2)
    const emoji = emojis[i % emojis.length]
    return {
      id: i,
      emoji,
      style: {
        left: `${left}%`,
        bottom: `-60px`,
        fontSize: `${size}rem`,
        animation: `floatUp ${duration}s ${delay}s ease-out forwards`,
        opacity: 0,
      },
    }
  })

  active.value = true
  // Clean up after the longest animation + delay
  const maxMs = (4.0 + 1.2) * 1000 + 400
  setTimeout(() => {
    active.value = false
    particles.value = []
  }, maxMs)
}

defineExpose({ celebrate })
</script>

<style>
@keyframes floatUp {
  0%   { transform: translateY(0)     rotate(0deg);   opacity: 0.9; }
  20%  { opacity: 1; }
  80%  { opacity: 0.85; }
  100% { transform: translateY(-110vh) rotate(360deg); opacity: 0; }
}
.fade-enter-active, .fade-leave-active { transition: opacity 0.3s; }
.fade-enter-from, .fade-leave-to       { opacity: 0; }
</style>
