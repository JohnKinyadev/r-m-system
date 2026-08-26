<template>
  <div v-if="loading" class="flex flex-col items-center justify-center py-16 gap-3 text-gray-400">
    <span class="text-5xl animate-bounce">{{ emoji }}</span>
    <p class="text-sm">Loading…</p>
  </div>

  <div v-else-if="!animal" class="text-center py-12 text-gray-400">Animal not found.</div>

  <div v-else class="space-y-4 max-w-2xl mx-auto">
    <!-- Header card -->
    <div class="card relative overflow-hidden">
      <!-- Decorative emoji watermark -->
      <span class="absolute right-4 top-4 text-6xl opacity-10 select-none pointer-events-none">{{ emoji }}</span>

      <div class="flex items-start justify-between">
        <div>
          <div class="flex items-center gap-2 mb-1">
            <span class="text-3xl">{{ emoji }}</span>
            <h2 class="text-xl font-bold text-gray-800">{{ animal.name || animal.tag_number }}</h2>
          </div>
          <p class="text-sm text-gray-500">Tag #{{ animal.tag_number }} · {{ animal.livestock_type_name }}</p>
        </div>
        <span :class="statusBadge(animal.status)">{{ animal.status }}</span>
      </div>

      <div class="grid grid-cols-2 gap-3 mt-4">
        <InfoItem label="Gender"        :value="animal.gender" />
        <InfoItem label="Age"           :value="ageLabel" />
        <InfoItem label="Date of Birth" :value="animal.date_of_birth || '—'" />
        <InfoItem label="Notes"         :value="animal.notes || '—'" />
      </div>

      <div class="flex gap-2 mt-4">
        <RouterLink v-if="auth.isOwner" :to="`/animals/${animal.id}/edit`">
          <BaseButton variant="secondary" class="text-sm">Edit</BaseButton>
        </RouterLink>
      </div>
    </div>

    <!-- Worker assignment (owner only) -->
    <div v-if="auth.isOwner" class="card">
      <div class="flex items-center justify-between mb-3">
        <h3 class="font-semibold text-gray-700">Assigned Workers</h3>
        <span class="text-xs text-gray-400">{{ assignedIds.length }} assigned</span>
      </div>

      <div v-if="allWorkers.length === 0" class="text-sm text-gray-400 text-center py-3">
        No workers added yet. <RouterLink to="/workers" class="text-farm-600 underline">Add workers</RouterLink>
      </div>
      <div v-else class="space-y-2">
        <label
          v-for="w in allWorkers"
          :key="w.id"
          class="flex items-center gap-3 p-2 rounded-lg hover:bg-gray-50 cursor-pointer transition-colors"
        >
          <input
            type="checkbox"
            :checked="assignedIds.includes(w.id)"
            @change="toggleWorker(w)"
            class="w-4 h-4 rounded text-farm-600 border-gray-300 focus:ring-farm-500"
          />
          <div class="w-8 h-8 rounded-full bg-farm-100 flex items-center justify-center text-farm-700 text-xs font-bold flex-shrink-0">
            {{ initials(w.full_name) }}
          </div>
          <div class="flex-1">
            <p class="text-sm font-medium text-gray-800">{{ w.full_name }}</p>
            <p class="text-xs text-gray-400">{{ w.email }}</p>
          </div>
          <span v-if="assignedIds.includes(w.id)" class="text-xs text-farm-600 font-medium">Assigned</span>
        </label>
      </div>
    </div>

    <!-- Health logs -->
    <div class="card">
      <div class="flex items-center justify-between mb-3">
        <h3 class="font-semibold text-gray-700">Health History</h3>
        <BaseButton class="text-sm" @click="showHealthModal = true">+ Log</BaseButton>
      </div>
      <div v-if="healthLogs.length === 0" class="text-sm text-gray-400 text-center py-4">No health logs yet.</div>
      <ul v-else class="divide-y divide-gray-100">
        <li v-for="log in healthLogs" :key="log.id" class="py-2.5">
          <div class="flex items-center justify-between">
            <span class="text-xs font-medium bg-gray-100 text-gray-600 px-2 py-0.5 rounded-full capitalize">{{ log.log_type }}</span>
            <div class="flex items-center gap-2">
              <span v-if="log._offline" class="text-xs text-amber-500">⏳ pending sync</span>
              <span class="text-xs text-gray-400">{{ formatDate(log.logged_at) }}</span>
            </div>
          </div>
          <p v-if="log.description" class="text-sm text-gray-700 mt-1">{{ log.description }}</p>
          <p v-if="log.weight_kg" class="text-xs text-gray-500 mt-0.5">Weight: {{ log.weight_kg }} kg</p>
        </li>
      </ul>
    </div>

    <!-- Health log modal -->
    <BaseModal :open="showHealthModal" title="Log Health Event" @close="showHealthModal = false">
      <form @submit.prevent="submitHealthLog" class="space-y-3">
        <div>
          <label class="text-sm font-medium text-gray-700">Type</label>
          <select v-model="healthForm.log_type" class="input-field mt-1" required>
            <option value="observation">Observation</option>
            <option value="vaccination">Vaccination</option>
            <option value="treatment">Treatment</option>
            <option value="weight">Weight</option>
            <option value="deworming">Deworming</option>
          </select>
        </div>
        <BaseInput v-model="healthForm.description" label="Description" type="textarea" />
        <BaseInput v-model="healthForm.weight_kg" label="Weight (kg)" type="number" />
        <BaseInput v-model="healthForm.vaccine_name" label="Vaccine Name" />
        <BaseButton type="submit" :loading="healthLoading" class="w-full">Save Log</BaseButton>
      </form>
    </BaseModal>

    <FloatingAnimals ref="floater" />
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, RouterLink } from 'vue-router'
import { getAnimal, getAnimalWorkers, setAnimalWorkers } from '@/api/animals'
import { listHealthLogs, createHealthLog } from '@/api/health'
import { listUsers } from '@/api/users'
import { useAuthStore } from '@/stores/auth'
import { useToastStore } from '@/stores/toast'
import { getAnimalEmoji } from '@/utils/animalEmoji'
import { useOfflineMutation } from '@/composables/useOfflineMutation'
import { kvSet } from '@/db/offlineDb'
import BaseButton from '@/components/ui/BaseButton.vue'
import BaseModal from '@/components/ui/BaseModal.vue'
import BaseInput from '@/components/ui/BaseInput.vue'
import FloatingAnimals from '@/components/FloatingAnimals.vue'

const route = useRoute()
const auth = useAuthStore()
const toast = useToastStore()

const animal = ref(null)
const healthLogs = ref([])
const allWorkers = ref([])
const assignedIds = ref([])
const loading = ref(true)
const showHealthModal = ref(false)
const healthLoading = ref(false)
const floater = ref(null)
const healthForm = ref({ log_type: 'observation', description: '', weight_kg: '', vaccine_name: '' })
const { execute } = useOfflineMutation()

const emoji = computed(() => getAnimalEmoji(animal.value?.livestock_type_name ?? ''))

const statusBadge = (s) => ({ active: 'badge-active', sold: 'badge-sold', deceased: 'badge-deceased' }[s])
const formatDate = (d) => d ? new Date(d).toLocaleDateString('en-KE', { day: '2-digit', month: 'short', year: 'numeric' }) : '—'
const initials = (n) => n.split(' ').map(w => w[0]).slice(0, 2).join('').toUpperCase()

const ageLabel = computed(() => {
  if (!animal.value?.age_days) return '—'
  const y = Math.floor(animal.value.age_days / 365)
  const m = Math.floor((animal.value.age_days % 365) / 30)
  return y > 0 ? `${y}y ${m}m` : `${m} month${m !== 1 ? 's' : ''}`
})

const InfoItem = {
  template: '<div><p class="text-xs text-gray-400 uppercase tracking-wide">{{ label }}</p><p class="text-sm font-medium text-gray-700 capitalize">{{ value }}</p></div>',
  props: ['label', 'value'],
}

async function toggleWorker(worker) {
  const prev = [...assignedIds.value]
  const isAdding = !assignedIds.value.includes(worker.id)

  assignedIds.value = isAdding
    ? [...assignedIds.value, worker.id]
    : assignedIds.value.filter(id => id !== worker.id)

  try {
    await setAnimalWorkers(animal.value.id, assignedIds.value)
    if (isAdding) {
      toast.celebrate(
        'Worker assigned!',
        `${worker.full_name} is now responsible for ${animal.value.name || animal.value.tag_number}`,
        emoji.value,
      )
      floater.value?.celebrate([emoji.value, '🎉', emoji.value, '✨', emoji.value])
    } else {
      toast.info('Assignment removed', `${worker.full_name} unassigned from this animal`, emoji.value)
    }
  } catch {
    assignedIds.value = prev
    toast.warning('Could not update assignment', 'Please try again.')
  }
}

onMounted(async () => {
  const id = route.params.id
  const tasks = [getAnimal(id), listHealthLogs(id)]
  if (auth.isOwner) tasks.push(listUsers(), getAnimalWorkers(id))

  const results = await Promise.all(tasks)
  animal.value     = results[0]
  healthLogs.value = results[1]

  // Cache health logs to KV so this animal's detail works offline next visit
  if (results[1]?.length) kvSet(`health_logs_${id}`, results[1])

  if (auth.isOwner) {
    allWorkers.value = results[2].filter(u => u.role.name === 'farm_worker')
    assignedIds.value = results[3]
  }

  loading.value = false

  // Worker celebration: show floating animals on first view of assigned animal
  if (!auth.isOwner && animal.value) {
    const key = `celebrated_animal_${id}`
    if (!sessionStorage.getItem(key)) {
      sessionStorage.setItem(key, '1')
      setTimeout(() => floater.value?.celebrate([emoji.value, emoji.value, '⭐', emoji.value, '🌟']), 400)
      toast.celebrate(
        `Your animal!`,
        `${animal.value.name || animal.value.tag_number} is assigned to you`,
        emoji.value,
      )
    }
  }
})

async function submitHealthLog() {
  healthLoading.value = true
  try {
    const payload = { ...healthForm.value, animal_id: animal.value.id }
    if (!payload.weight_kg)    delete payload.weight_kg
    if (!payload.vaccine_name) delete payload.vaccine_name
    if (!payload.description)  delete payload.description

    const log = await execute(
      () => createHealthLog(payload),
      () => ({ ...payload, logged_at: new Date().toISOString() }),
    )

    healthLogs.value.unshift(log)
    // Update the KV cache with the new log included
    kvSet(`health_logs_${animal.value.id}`, healthLogs.value)

    showHealthModal.value = false
    const typeLabel = healthForm.value.log_type
    healthForm.value = { log_type: 'observation', description: '', weight_kg: '', vaccine_name: '' }

    if (!log._offline) {
      toast.success('Health log saved', `${typeLabel} recorded for ${animal.value.name || animal.value.tag_number}`, '💉')
    }
  } catch (e) {
    toast.warning('Could not save log', e.response?.data?.detail || 'Please try again.')
  } finally {
    healthLoading.value = false
  }
}
</script>
