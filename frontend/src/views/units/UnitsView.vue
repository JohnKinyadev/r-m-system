<template>
  <div class="space-y-4">
    <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3">
      <div class="flex gap-2">
        <BaseInput v-model="filters.status" type="select" class="w-44" @update:modelValue="load">
          <option value="">All statuses</option>
          <option value="vacant">Vacant</option>
          <option value="occupied">Occupied</option>
          <option value="maintenance">Maintenance</option>
          <option value="notice_given">Notice Given</option>
        </BaseInput>
      </div>
      <BaseButton v-if="auth.isOwner" @click="openCreate">+ Add Unit</BaseButton>
    </div>

    <div v-if="loading" class="text-center py-12 text-gray-400">Loading...</div>
    <div v-else class="grid sm:grid-cols-2 xl:grid-cols-3 gap-3">
      <div v-for="unit in units" :key="unit.id" class="card">
        <div class="flex items-start justify-between gap-3">
          <div>
            <p class="font-semibold text-gray-800">{{ unit.property_name }} - {{ unit.unit_number }}</p>
            <p class="text-sm text-gray-500">{{ unit.unit_type }}</p>
          </div>
          <span :class="statusBadge(unit.status)">{{ labelize(unit.status) }}</span>
        </div>
        <div class="grid grid-cols-2 gap-2 mt-4">
          <div class="rounded-xl bg-gray-50 p-3">
            <p class="text-xs text-gray-400">Monthly rent</p>
            <p class="font-bold text-gray-800">{{ formatMoney(unit.monthly_rent) }}</p>
          </div>
          <div class="rounded-xl bg-gray-50 p-3">
            <p class="text-xs text-gray-400">Balance</p>
            <p class="font-bold" :class="Number(unit.balance) > 0 ? 'text-red-600' : 'text-green-700'">{{ formatMoney(unit.balance) }}</p>
          </div>
        </div>
        <div class="mt-4 text-sm">
          <p class="text-gray-500">Tenant</p>
          <p class="font-medium text-gray-800 truncate">{{ unit.current_tenant_name || 'No active tenant' }}</p>
        </div>
      </div>
    </div>

    <BaseModal :open="showModal" title="Add Unit" @close="showModal = false">
      <form @submit.prevent="submit" class="space-y-3">
        <BaseAlert :message="error" type="error" />
        <BaseInput v-model="form.property_id" label="Property" type="select" required>
          <option value="">Select property</option>
          <option v-for="property in properties" :key="property.id" :value="property.id">{{ property.name }}</option>
        </BaseInput>
        <BaseInput v-model="form.unit_number" label="Unit Number" required />
        <BaseInput v-model="form.unit_type" label="Unit Type" placeholder="Bedsitter" required />
        <div class="grid grid-cols-2 gap-3">
          <BaseInput v-model="form.bedrooms" label="Bedrooms" type="number" required />
          <BaseInput v-model="form.bathrooms" label="Bathrooms" type="number" required />
        </div>
        <div class="grid grid-cols-2 gap-3">
          <BaseInput v-model="form.monthly_rent" label="Monthly Rent" type="number" required />
          <BaseInput v-model="form.deposit_amount" label="Deposit" type="number" required />
        </div>
        <BaseInput v-model="form.rent_due_day" label="Rent Due Day" type="number" required />
        <BaseButton type="submit" :loading="saving" class="w-full">Save Unit</BaseButton>
      </form>
    </BaseModal>
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import { useRoute } from 'vue-router'
import { createUnit, listUnits } from '@/api/units'
import { listProperties } from '@/api/properties'
import { useAuthStore } from '@/stores/auth'
import BaseAlert from '@/components/ui/BaseAlert.vue'
import BaseButton from '@/components/ui/BaseButton.vue'
import BaseInput from '@/components/ui/BaseInput.vue'
import BaseModal from '@/components/ui/BaseModal.vue'

const route = useRoute()
const auth = useAuthStore()
const units = ref([])
const properties = ref([])
const loading = ref(true)
const showModal = ref(false)
const saving = ref(false)
const error = ref('')
const filters = ref({ status: '' })
const form = ref({})

const formatMoney = (value) =>
  new Intl.NumberFormat('en-KE', { style: 'currency', currency: 'KES', maximumFractionDigits: 0 }).format(Number(value || 0))
const labelize = (value) => String(value || '').replaceAll('_', ' ')
const statusBadge = (status) => ({
  occupied: 'badge-active',
  vacant: 'badge-sold',
  reserved: 'badge-sold',
  notice_given: 'badge-sold',
  maintenance: 'badge-deceased',
  unavailable: 'badge-deceased',
}[status] || 'badge-deceased')

async function load() {
  const params = {}
  if (filters.value.status) params.status = filters.value.status
  if (route.query.property) params.property_id = route.query.property
  units.value = await listUnits(params)
}

function openCreate() {
  form.value = {
    property_id: '',
    unit_number: '',
    unit_type: '',
    bedrooms: 1,
    bathrooms: 1,
    monthly_rent: '',
    deposit_amount: '',
    rent_due_day: 5,
  }
  error.value = ''
  showModal.value = true
}

async function submit() {
  saving.value = true
  error.value = ''
  try {
    await createUnit(form.value)
    await load()
    showModal.value = false
  } catch (e) {
    error.value = e.response?.data?.detail || 'Failed to save unit.'
  } finally {
    saving.value = false
  }
}

onMounted(async () => {
  ;[properties.value] = await Promise.all([listProperties()])
  await load()
  loading.value = false
})
</script>
