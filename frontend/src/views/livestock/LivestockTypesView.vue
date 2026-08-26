<template>
  <div class="space-y-4">
    <div class="flex justify-between items-center">
      <p class="text-sm text-gray-500">{{ types.length }} type(s) registered</p>
      <BaseButton v-if="isOwner" @click="openModal()">+ Add Type</BaseButton>
    </div>

    <div v-if="loading" class="text-center py-12 text-gray-400">Loading…</div>
    <div v-else-if="types.length === 0" class="card text-center py-12 text-gray-400">
      No livestock types registered yet.
    </div>
    <div v-else class="space-y-3">
      <div v-for="lt in types" :key="lt.id" class="card">
        <div class="flex items-start justify-between">
          <div>
            <h3 class="font-semibold text-gray-800">{{ lt.name }}</h3>
            <p v-if="lt.breed" class="text-sm text-gray-500">{{ lt.breed }}</p>
          </div>
          <div class="flex gap-2">
            <button v-if="isOwner" @click="openModal(lt)" class="text-xs text-farm-600 hover:underline">Edit</button>
            <button v-if="isOwner" @click="remove(lt)" class="text-xs text-red-500 hover:underline">Delete</button>
          </div>
        </div>
        <div class="grid grid-cols-2 gap-2 mt-3">
          <div class="text-sm"><span class="text-gray-400">Gestation:</span> {{ lt.gestation_period_days ? `${lt.gestation_period_days} days` : '—' }}</div>
          <div class="text-sm"><span class="text-gray-400">Lifespan:</span> {{ lt.average_lifespan_years ? `${lt.average_lifespan_years} yrs` : '—' }}</div>
        </div>
        <div v-if="lt.vaccine_schedules?.length" class="mt-3">
          <p class="text-xs font-medium text-gray-500 mb-1">Vaccine Schedule</p>
          <div class="flex flex-wrap gap-1">
            <span v-for="vs in lt.vaccine_schedules" :key="vs.id" class="text-xs bg-blue-50 text-blue-700 px-2 py-0.5 rounded-full">
              {{ vs.vaccine_name }} (day {{ vs.first_dose_age_days }})
            </span>
          </div>
        </div>
      </div>
    </div>

    <!-- Add/Edit Modal -->
    <BaseModal :open="showModal" :title="editing ? 'Edit Livestock Type' : 'Add Livestock Type'" @close="showModal = false">
      <form @submit.prevent="submit" class="space-y-3">
        <BaseAlert :message="error" type="error" />
        <BaseInput v-model="form.name" label="Type Name" required placeholder="e.g. Angus Cattle" />
        <BaseInput v-model="form.breed" label="Breed (optional)" placeholder="e.g. Angus" />
        <BaseInput v-model="form.gestation_period_days" label="Gestation Period (days)" type="number" />
        <BaseInput v-model="form.average_lifespan_years" label="Avg Lifespan (years)" type="number" />

        <div>
          <div class="flex items-center justify-between mb-2">
            <p class="text-sm font-medium text-gray-700">Vaccine Schedules</p>
            <button type="button" @click="addVaccine" class="text-xs text-farm-600 hover:underline">+ Add</button>
          </div>
          <div v-for="(vs, i) in form.vaccine_schedules" :key="i" class="flex gap-2 mb-2">
            <input v-model="vs.vaccine_name" placeholder="Vaccine name" class="input-field flex-1 text-sm" />
            <input v-model.number="vs.first_dose_age_days" placeholder="Day" type="number" class="input-field w-20 text-sm" />
            <button type="button" @click="form.vaccine_schedules.splice(i,1)" class="text-red-400 text-sm px-1">✕</button>
          </div>
        </div>

        <BaseButton type="submit" :loading="saving" class="w-full">{{ editing ? 'Save' : 'Create' }}</BaseButton>
      </form>
    </BaseModal>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { listLivestockTypes, createLivestockType, updateLivestockType, deleteLivestockType } from '@/api/livestock'
import BaseButton from '@/components/ui/BaseButton.vue'
import BaseModal from '@/components/ui/BaseModal.vue'
import BaseInput from '@/components/ui/BaseInput.vue'
import BaseAlert from '@/components/ui/BaseAlert.vue'

const auth = useAuthStore()
const isOwner = auth.isOwner

const types = ref([])
const loading = ref(true)
const showModal = ref(false)
const saving = ref(false)
const editing = ref(null)
const error = ref('')
const form = ref({ name: '', breed: '', gestation_period_days: '', average_lifespan_years: '', vaccine_schedules: [] })

function openModal(lt = null) {
  editing.value = lt
  error.value = ''
  if (lt) {
    form.value = { name: lt.name, breed: lt.breed || '', gestation_period_days: lt.gestation_period_days || '', average_lifespan_years: lt.average_lifespan_years || '', vaccine_schedules: lt.vaccine_schedules?.map(v => ({ ...v })) || [] }
  } else {
    form.value = { name: '', breed: '', gestation_period_days: '', average_lifespan_years: '', vaccine_schedules: [] }
  }
  showModal.value = true
}

function addVaccine() {
  form.value.vaccine_schedules.push({ vaccine_name: '', first_dose_age_days: 0, interval_days: null })
}

async function submit() {
  saving.value = true
  error.value = ''
  try {
    const payload = { ...form.value }
    if (!payload.breed) delete payload.breed
    if (!payload.gestation_period_days) delete payload.gestation_period_days
    if (!payload.average_lifespan_years) delete payload.average_lifespan_years
    if (editing.value) {
      await updateLivestockType(editing.value.id, payload)
    } else {
      await createLivestockType(payload)
    }
    types.value = await listLivestockTypes()
    showModal.value = false
  } catch (e) {
    error.value = e.response?.data?.detail || 'Failed to save.'
  } finally {
    saving.value = false
  }
}

async function remove(lt) {
  if (!confirm(`Delete "${lt.name}"? This cannot be undone.`)) return
  await deleteLivestockType(lt.id)
  types.value = types.value.filter(t => t.id !== lt.id)
}

onMounted(async () => {
  types.value = await listLivestockTypes()
  loading.value = false
})
</script>
