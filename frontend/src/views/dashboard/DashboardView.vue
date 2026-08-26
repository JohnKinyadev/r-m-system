<template>
  <div class="space-y-5">

    <!-- Worker welcome banner with celebration -->
    <div v-if="!auth.isOwner && myAnimals.length > 0"
         class="card bg-gradient-to-r from-farm-700 to-farm-500 text-white relative overflow-hidden">
      <div class="relative z-10">
        <p class="text-xs uppercase tracking-widest opacity-75 mb-1">Your herd today</p>
        <p class="text-2xl font-bold">
          {{ myAnimals.length }} animal{{ myAnimals.length !== 1 ? 's' : '' }} assigned to you
        </p>
        <div class="flex gap-2 mt-3 flex-wrap">
          <RouterLink
            v-for="a in myAnimals.slice(0, 4)"
            :key="a.id"
            :to="`/animals/${a.id}`"
            class="flex items-center gap-1.5 bg-white/20 hover:bg-white/30 px-3 py-1.5 rounded-full text-sm transition-colors"
          >
            <span>{{ getAnimalEmoji(a.livestock_type_name) }}</span>
            <span>{{ a.name || a.tag_number }}</span>
          </RouterLink>
          <RouterLink v-if="myAnimals.length > 4" to="/animals"
            class="bg-white/20 hover:bg-white/30 px-3 py-1.5 rounded-full text-sm">
            +{{ myAnimals.length - 4 }} more
          </RouterLink>
        </div>
      </div>
      <!-- decorative floating emojis -->
      <span class="absolute right-4 top-2 text-5xl opacity-20 select-none pointer-events-none">
        {{ primaryEmoji }}
      </span>
    </div>

    <!-- Stats grid -->
    <div class="grid grid-cols-2 lg:grid-cols-4 gap-3">
      <StatCard label="Active Animals"   :value="summary?.active_animals     ?? '—'" color="green"  icon="paw"      />
      <StatCard label="Births This Month" :value="summary?.births_this_month  ?? '—'" color="blue"   icon="baby"     />
      <StatCard label="Upcoming Births"  :value="summary?.upcoming_births    ?? '—'" color="amber"  icon="calendar" />
      <StatCard label="Low Stock Feeds"  :value="summary?.low_stock_feed_types?.length ?? '—'" color="red" icon="alert" />
    </div>

    <!-- Low feed alerts -->
    <div v-if="summary?.low_stock_feed_types?.length" class="card border border-red-100 bg-red-50">
      <div class="flex items-center gap-2 mb-2">
        <span class="text-xl">⚠️</span>
        <h3 class="font-semibold text-red-700">Low Feed Stock</h3>
      </div>
      <div class="flex flex-wrap gap-2">
        <span
          v-for="name in summary.low_stock_feed_types"
          :key="name"
          class="bg-red-100 text-red-700 text-xs font-medium px-3 py-1 rounded-full"
        >{{ name }}</span>
      </div>
    </div>

    <!-- Quick actions -->
    <div class="card">
      <h3 class="font-semibold text-gray-700 mb-3">Quick Actions</h3>
      <div class="grid grid-cols-2 sm:grid-cols-4 gap-2">
        <QuickAction v-if="auth.hasModule('animals')"  to="/animals/new" label="Add Animal"    color="farm"   emoji="🐾" />
        <QuickAction v-if="auth.hasModule('feed')"     to="/feed"        label="Log Feeding"   color="amber"  emoji="🌾" />
        <QuickAction v-if="auth.hasModule('health')"   to="/health"      label="Health Log"    color="blue"   emoji="💉" />
        <QuickAction v-if="auth.hasModule('mating')"   to="/mating"      label="Mating Event"  color="purple" emoji="🔗" />
      </div>
    </div>

    <!-- Recent animals -->
    <div class="card">
      <div class="flex items-center justify-between mb-3">
        <h3 class="font-semibold text-gray-700">
          {{ auth.isOwner ? 'Recent Animals' : 'My Animals' }}
        </h3>
        <RouterLink to="/animals" class="text-sm text-farm-600 font-medium">View all →</RouterLink>
      </div>

      <!-- Loading skeleton -->
      <div v-if="loading" class="space-y-2">
        <div v-for="i in 4" :key="i" class="flex items-center gap-3 py-2">
          <div class="w-9 h-9 rounded-full bg-gray-100 animate-pulse flex-shrink-0" />
          <div class="flex-1 space-y-1">
            <div class="h-3 bg-gray-100 rounded animate-pulse w-2/3" />
            <div class="h-3 bg-gray-100 rounded animate-pulse w-1/3" />
          </div>
        </div>
      </div>

      <div v-else-if="animals.length === 0" class="text-center py-6 text-gray-400 text-sm">
        <span class="text-3xl block mb-1">🐾</span>No animals yet
      </div>

      <ul v-else class="divide-y divide-gray-100">
        <li
          v-for="a in animals.slice(0, 5)"
          :key="a.id"
          class="py-2.5 flex items-center gap-3"
        >
          <span class="text-xl flex-shrink-0">{{ getAnimalEmoji(a.livestock_type_name) }}</span>
          <div class="flex-1 min-w-0">
            <p class="text-sm font-medium text-gray-800 truncate">{{ a.name || a.tag_number }}</p>
            <p class="text-xs text-gray-400 truncate">{{ a.livestock_type_name }} · Tag #{{ a.tag_number }}</p>
          </div>
          <span :class="statusBadge(a.status)">{{ a.status }}</span>
        </li>
      </ul>
    </div>
  </div>

  <FloatingAnimals ref="floater" />
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { RouterLink } from 'vue-router'
import { getDashboardSummary } from '@/api/reports'
import { listAnimals } from '@/api/animals'
import { useAuthStore } from '@/stores/auth'
import { useToastStore } from '@/stores/toast'
import { getAnimalEmoji } from '@/utils/animalEmoji'
import StatCard from '@/components/dashboard/StatCard.vue'
import QuickAction from '@/components/dashboard/QuickAction.vue'
import FloatingAnimals from '@/components/FloatingAnimals.vue'

const auth = useAuthStore()
const toast = useToastStore()

const summary = ref(null)
const animals = ref([])
const myAnimals = ref([])
const loading = ref(true)
const floater = ref(null)

const statusBadge = (s) => ({ active: 'badge-active', sold: 'badge-sold', deceased: 'badge-deceased' }[s])

const primaryEmoji = computed(() => {
  if (!myAnimals.value.length) return '🐾'
  return getAnimalEmoji(myAnimals.value[0]?.livestock_type_name ?? '')
})

onMounted(async () => {
  loading.value = true
  ;[summary.value, animals.value] = await Promise.all([
    getDashboardSummary(),
    listAnimals({ status: 'active' }),
  ])
  loading.value = false

  // Worker welcome celebration — only on first session visit
  if (!auth.isOwner) {
    myAnimals.value = animals.value
    if (myAnimals.value.length > 0 && !sessionStorage.getItem('welcomed')) {
      sessionStorage.setItem('welcomed', '1')
      const emojis = [...new Set(myAnimals.value.map(a => getAnimalEmoji(a.livestock_type_name)))]
      setTimeout(() => floater.value?.celebrate(emojis), 600)
      toast.celebrate(
        `Welcome back, ${auth.user?.full_name?.split(' ')[0]}! 🌟`,
        `You have ${myAnimals.value.length} animal${myAnimals.value.length !== 1 ? 's' : ''} in your care today.`,
        primaryEmoji.value,
      )
    }
  }
})
</script>
