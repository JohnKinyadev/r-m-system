<template>
  <div class="space-y-4">
    <!-- Header row -->
    <div class="flex flex-wrap gap-2 items-center justify-between">
      <h2 class="text-lg font-bold text-gray-800">
        {{ auth.isOwner ? 'All Animals' : 'My Animals' }}
        <span class="ml-2 text-sm font-normal text-gray-400">({{ animals.length }})</span>
      </h2>
      <RouterLink v-if="auth.isOwner || auth.hasModule('animals')" to="/animals/new">
        <BaseButton>+ Add Animal</BaseButton>
      </RouterLink>
    </div>

    <!-- Filters -->
    <div class="flex gap-2 flex-wrap">
      <select v-model="filterStatus" class="input-field w-auto text-sm" @change="load">
        <option value="">All Statuses</option>
        <option value="active">Active</option>
        <option value="sold">Sold</option>
        <option value="deceased">Deceased</option>
      </select>
      <select v-model="filterType" class="input-field w-auto text-sm" @change="load">
        <option value="">All Types</option>
        <option v-for="lt in livestockTypes" :key="lt.id" :value="lt.id">{{ lt.name }}</option>
      </select>
    </div>

    <!-- List -->
    <div v-if="loading" class="grid grid-cols-1 gap-3">
      <div v-for="i in 4" :key="i" class="card animate-pulse h-20 bg-gray-100" />
    </div>

    <div v-else-if="animals.length === 0" class="card text-center py-12">
      <p class="text-4xl mb-2">🐾</p>
      <p class="text-gray-500 font-medium">No animals found</p>
      <p v-if="!auth.isOwner" class="text-sm text-gray-400 mt-1">Ask your farm owner to assign animals to you.</p>
    </div>

    <div v-else class="grid grid-cols-1 gap-3">
      <RouterLink
        v-for="a in animals"
        :key="a.id"
        :to="`/animals/${a.id}`"
        class="card flex items-center gap-4 hover:shadow-md transition-all hover:-translate-y-0.5 border-l-4"
        :class="statusBorderClass(a.status)"
      >
        <!-- Animal emoji avatar -->
        <div class="w-12 h-12 rounded-full bg-farm-50 flex items-center justify-center text-2xl flex-shrink-0 border border-farm-100">
          {{ getAnimalEmoji(a.livestock_type_name) }}
        </div>

        <div class="flex-1 min-w-0">
          <p class="font-semibold text-gray-800 truncate">{{ a.name || a.tag_number }}</p>
          <p class="text-xs text-gray-500 truncate">{{ a.livestock_type_name }} · {{ a.gender }} · Tag #{{ a.tag_number }}</p>
          <p v-if="a.age_days" class="text-xs text-gray-400">
            {{ Math.floor(a.age_days / 365) }}y {{ Math.floor((a.age_days % 365) / 30) }}m old
          </p>
        </div>

        <div class="flex flex-col items-end gap-1 flex-shrink-0">
          <span :class="statusBadge(a.status)">{{ a.status }}</span>
          <svg class="w-4 h-4 text-gray-300" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
            <path d="M9 18l6-6-6-6"/>
          </svg>
        </div>
      </RouterLink>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { RouterLink } from 'vue-router'
import { listAnimals } from '@/api/animals'
import { listLivestockTypes } from '@/api/livestock'
import { useAuthStore } from '@/stores/auth'
import { getAnimalEmoji } from '@/utils/animalEmoji'
import BaseButton from '@/components/ui/BaseButton.vue'

const auth = useAuthStore()
const animals = ref([])
const livestockTypes = ref([])
const loading = ref(true)
const filterStatus = ref('')
const filterType = ref('')

const statusBadge = (s) => ({ active: 'badge-active', sold: 'badge-sold', deceased: 'badge-deceased' }[s])
const statusBorderClass = (s) => ({
  active:   'border-l-green-400',
  sold:     'border-l-blue-400',
  deceased: 'border-l-gray-300',
}[s] ?? 'border-l-gray-200')

async function load() {
  loading.value = true
  const params = {}
  if (filterStatus.value) params.status = filterStatus.value
  if (filterType.value) params.livestock_type_id = filterType.value
  animals.value = await listAnimals(params)
  loading.value = false
}

onMounted(async () => {
  livestockTypes.value = await listLivestockTypes()
  await load()
})
</script>
