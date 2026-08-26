<template>
  <div class="space-y-4">
    <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3">
      <BaseInput v-model="search" placeholder="Search tenant, phone, or email" @update:modelValue="load" />
      <BaseButton @click="openCreate">+ Add Tenant</BaseButton>
    </div>

    <div v-if="loading" class="text-center py-12 text-gray-400">Loading...</div>
    <div v-else class="space-y-3">
      <div v-for="tenant in tenants" :key="tenant.id" class="card flex items-center justify-between gap-4">
        <div class="min-w-0">
          <p class="font-semibold text-gray-800 truncate">{{ tenant.full_name }}</p>
          <p class="text-sm text-gray-500 truncate">{{ tenant.phone }} - {{ tenant.email || 'No email' }}</p>
          <p class="text-xs text-gray-400 truncate">
            {{ tenant.current_property_name || 'No property' }} {{ tenant.current_unit_number ? `- Unit ${tenant.current_unit_number}` : '' }}
          </p>
        </div>
        <div class="text-right flex-shrink-0">
          <p class="text-xs text-gray-400">Balance</p>
          <p class="font-bold" :class="Number(tenant.balance) > 0 ? 'text-red-600' : 'text-green-700'">
            {{ formatMoney(tenant.balance) }}
          </p>
        </div>
      </div>
    </div>

    <BaseModal :open="showModal" title="Add Tenant" @close="showModal = false">
      <form @submit.prevent="submit" class="space-y-3">
        <BaseAlert :message="error" type="error" />
        <BaseInput v-model="form.full_name" label="Full Name" required />
        <BaseInput v-model="form.phone" label="Phone" required />
        <BaseInput v-model="form.email" label="Email" type="email" />
        <BaseInput v-model="form.national_id" label="ID / Passport" />
        <BaseInput v-model="form.emergency_contact" label="Emergency Contact" />
        <BaseInput v-model="form.notes" label="Notes" type="textarea" />
        <BaseButton type="submit" :loading="saving" class="w-full">Save Tenant</BaseButton>
      </form>
    </BaseModal>
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import { createTenant, listTenants } from '@/api/tenants'
import BaseAlert from '@/components/ui/BaseAlert.vue'
import BaseButton from '@/components/ui/BaseButton.vue'
import BaseInput from '@/components/ui/BaseInput.vue'
import BaseModal from '@/components/ui/BaseModal.vue'

const tenants = ref([])
const loading = ref(true)
const search = ref('')
const showModal = ref(false)
const saving = ref(false)
const error = ref('')
const form = ref({})

const formatMoney = (value) =>
  new Intl.NumberFormat('en-KE', { style: 'currency', currency: 'KES', maximumFractionDigits: 0 }).format(Number(value || 0))

async function load() {
  tenants.value = await listTenants(search.value ? { q: search.value } : {})
}

function openCreate() {
  form.value = { full_name: '', phone: '', email: '', national_id: '', emergency_contact: '', notes: '' }
  error.value = ''
  showModal.value = true
}

async function submit() {
  saving.value = true
  error.value = ''
  try {
    await createTenant(form.value)
    await load()
    showModal.value = false
  } catch (e) {
    error.value = e.response?.data?.detail || 'Failed to save tenant.'
  } finally {
    saving.value = false
  }
}

onMounted(async () => {
  await load()
  loading.value = false
})
</script>
