<template>
  <div class="space-y-4">
    <div class="card">
      <h3 class="font-semibold text-gray-700 mb-3">Log Health Event</h3>

      <BaseAlert :message="success" type="success" class="mb-3" />
      <BaseAlert :message="error"   type="error"   class="mb-3" />

      <form @submit.prevent="submit" class="space-y-3">
        <div>
          <label class="text-sm font-medium text-gray-700">Animal <span class="text-red-500">*</span></label>
          <select v-model="form.animal_id" class="input-field mt-1" required>
            <option value="">Select animal</option>
            <option v-for="a in animals" :key="a.id" :value="a.id">
              {{ getAnimalEmoji(a.livestock_type_name) }} {{ a.name || a.tag_number }} ({{ a.livestock_type_name }})
            </option>
          </select>
        </div>

        <div>
          <label class="text-sm font-medium text-gray-700">Event Type <span class="text-red-500">*</span></label>
          <select v-model="form.log_type" class="input-field mt-1" required>
            <option value="observation">Observation</option>
            <option value="vaccination">Vaccination</option>
            <option value="treatment">Treatment</option>
            <option value="weight">Weight Recording</option>
            <option value="deworming">Deworming</option>
          </select>
        </div>

        <BaseInput v-model="form.description"  label="Description / Notes" type="textarea" />
        <BaseInput v-model="form.weight_kg"    label="Weight (kg)"          type="number" />
        <BaseInput v-model="form.vaccine_name" label="Vaccine / Drug Name" />

        <BaseButton type="submit" :loading="loading" class="w-full">Save Health Log</BaseButton>
      </form>
    </div>

    <!-- Recent logs -->
    <div v-if="recentLogs.length" class="card">
      <h3 class="font-semibold text-gray-700 mb-3">Recent Health Events</h3>
      <ul class="divide-y divide-gray-100">
        <li v-for="log in recentLogs" :key="log.id" class="py-2.5">
          <div class="flex items-center justify-between">
            <span class="text-xs font-medium bg-gray-100 text-gray-600 px-2 py-0.5 rounded-full capitalize">
              {{ log.log_type }}
            </span>
            <div class="flex items-center gap-2">
              <span v-if="log._offline" class="text-xs text-amber-500">⏳ pending sync</span>
              <span class="text-xs text-gray-400">{{ formatDate(log.logged_at) }}</span>
            </div>
          </div>
          <p v-if="log.description" class="text-sm text-gray-700 mt-1">{{ log.description }}</p>
          <p v-if="log.weight_kg"   class="text-xs text-gray-500 mt-0.5">Weight: {{ log.weight_kg }} kg</p>
        </li>
      </ul>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { listAnimals }  from '@/api/animals'
import { createHealthLog } from '@/api/health'
import { getAnimalEmoji }  from '@/utils/animalEmoji'
import { useOfflineMutation } from '@/composables/useOfflineMutation'
import BaseInput  from '@/components/ui/BaseInput.vue'
import BaseButton from '@/components/ui/BaseButton.vue'
import BaseAlert  from '@/components/ui/BaseAlert.vue'

const { execute } = useOfflineMutation()

const animals    = ref([])
const loading    = ref(false)
const success    = ref('')
const error      = ref('')
const recentLogs = ref([])

const form = ref({ animal_id: '', log_type: 'observation', description: '', weight_kg: '', vaccine_name: '' })
const formatDate = (d) => d ? new Date(d).toLocaleDateString() : '—'

onMounted(async () => { animals.value = await listAnimals({ status: 'active' }) })

async function submit() {
  loading.value = true; success.value = ''; error.value = ''
  try {
    const payload = { ...form.value }
    if (!payload.weight_kg)    delete payload.weight_kg
    if (!payload.vaccine_name) delete payload.vaccine_name
    if (!payload.description)  delete payload.description

    const log = await execute(
      () => createHealthLog(payload),
      () => ({ ...payload, logged_at: new Date().toISOString() }),
    )

    recentLogs.value.unshift(log)
    success.value = log._offline
      ? 'Saved offline — will sync when reconnected ☁️'
      : 'Health event logged successfully.'
    form.value = { animal_id: '', log_type: 'observation', description: '', weight_kg: '', vaccine_name: '' }
  } catch (e) {
    error.value = e.response?.data?.detail || 'Failed to save log.'
  } finally {
    loading.value = false
  }
}
</script>
