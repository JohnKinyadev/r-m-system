<template>
  <div class="space-y-4">
    <div class="flex items-center justify-between gap-3">
      <p class="text-sm text-gray-500">{{ requests.length }} maintenance request(s)</p>
      <BaseButton @click="openCreate">+ Add Request</BaseButton>
    </div>

    <div class="grid lg:grid-cols-2 gap-3">
      <div v-for="item in requests" :key="item.id" class="card">
        <div class="flex items-start justify-between gap-3">
          <div class="min-w-0">
            <p class="font-semibold text-gray-800 truncate">{{ item.title }}</p>
            <p class="text-sm text-gray-500 truncate">{{ item.property_name }} {{ item.unit_number ? `- Unit ${item.unit_number}` : '' }}</p>
          </div>
          <span :class="statusBadge(item.status)">{{ labelize(item.status) }}</span>
        </div>
        <p class="text-sm text-gray-600 mt-3">{{ item.description || 'No description.' }}</p>
        <div class="flex items-center justify-between mt-4 text-sm">
          <span class="text-gray-400">{{ labelize(item.priority) }} priority</span>
          <span class="font-semibold text-gray-800">{{ formatMoney(item.cost) }}</span>
        </div>
      </div>
    </div>

    <BaseModal :open="showModal" title="Add Maintenance Request" @close="showModal = false">
      <form @submit.prevent="submit" class="space-y-3">
        <BaseAlert :message="error" type="error" />
        <BaseInput v-model="form.property_id" label="Property" type="select" required>
          <option value="">Select property</option>
          <option v-for="property in properties" :key="property.id" :value="property.id">{{ property.name }}</option>
        </BaseInput>
        <BaseInput v-model="form.unit_id" label="Unit" type="select">
          <option value="">No specific unit</option>
          <option v-for="unit in unitsForProperty" :key="unit.id" :value="unit.id">{{ unit.unit_number }}</option>
        </BaseInput>
        <BaseInput v-model="form.title" label="Title" required />
        <BaseInput v-model="form.description" label="Description" type="textarea" />
        <BaseInput v-model="form.priority" label="Priority" type="select" required>
          <option value="low">Low</option>
          <option value="normal">Normal</option>
          <option value="high">High</option>
          <option value="urgent">Urgent</option>
        </BaseInput>
        <BaseInput v-model="form.reported_date" label="Reported Date" type="date" required />
        <BaseInput v-model="form.cost" label="Estimated / Actual Cost" type="number" />
        <BaseButton type="submit" :loading="saving" class="w-full">Save Request</BaseButton>
      </form>
    </BaseModal>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { createMaintenanceRequest, listMaintenanceRequests } from '@/api/maintenance'
import { listProperties } from '@/api/properties'
import { listUnits } from '@/api/units'
import BaseAlert from '@/components/ui/BaseAlert.vue'
import BaseButton from '@/components/ui/BaseButton.vue'
import BaseInput from '@/components/ui/BaseInput.vue'
import BaseModal from '@/components/ui/BaseModal.vue'

const requests = ref([])
const properties = ref([])
const units = ref([])
const showModal = ref(false)
const saving = ref(false)
const error = ref('')
const form = ref({})

const unitsForProperty = computed(() => units.value.filter(u => String(u.property_id) === String(form.value.property_id)))
const today = () => new Date().toISOString().slice(0, 10)
const labelize = (value) => String(value || '').replaceAll('_', ' ')
const formatMoney = (value) =>
  new Intl.NumberFormat('en-KE', { style: 'currency', currency: 'KES', maximumFractionDigits: 0 }).format(Number(value || 0))
const statusBadge = (status) => ({
  open: 'badge-sold',
  assigned: 'badge-sold',
  in_progress: 'badge-active',
  resolved: 'badge-active',
  cancelled: 'badge-deceased',
}[status] || 'badge-deceased')

async function load() {
  ;[requests.value, properties.value, units.value] = await Promise.all([
    listMaintenanceRequests(),
    listProperties(),
    listUnits(),
  ])
}

function openCreate() {
  form.value = { property_id: '', unit_id: '', title: '', description: '', priority: 'normal', reported_date: today(), cost: 0 }
  error.value = ''
  showModal.value = true
}

async function submit() {
  saving.value = true
  error.value = ''
  try {
    const payload = { ...form.value, unit_id: form.value.unit_id || null }
    await createMaintenanceRequest(payload)
    await load()
    showModal.value = false
  } catch (e) {
    error.value = e.response?.data?.detail || 'Failed to save maintenance request.'
  } finally {
    saving.value = false
  }
}

onMounted(load)
</script>
