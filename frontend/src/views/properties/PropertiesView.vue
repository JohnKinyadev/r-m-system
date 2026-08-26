<template>
  <div class="space-y-4">
    <div class="flex items-center justify-between gap-3">
      <p class="text-sm text-gray-500">{{ properties.length }} propert{{ properties.length === 1 ? 'y' : 'ies' }}</p>
      <BaseButton v-if="auth.isOwner" @click="openCreate">+ Add Property</BaseButton>
    </div>

    <div v-if="loading" class="text-center py-12 text-gray-400">Loading...</div>
    <div v-else-if="properties.length === 0" class="card text-center py-8 text-gray-400">No properties yet.</div>

    <div v-else class="grid lg:grid-cols-2 gap-3">
      <div v-for="property in properties" :key="property.id" class="card">
        <div class="flex items-start justify-between gap-3">
          <div class="min-w-0">
            <p class="font-semibold text-gray-800 truncate">{{ property.name }}</p>
            <p class="text-sm text-gray-500 truncate">{{ property.address }}, {{ property.city }}</p>
          </div>
          <span :class="statusBadge(property.status)">{{ labelize(property.status) }}</span>
        </div>
        <div class="grid grid-cols-3 gap-2 mt-4 text-center">
          <div class="rounded-xl bg-gray-50 p-3">
            <p class="text-lg font-bold text-gray-800">{{ property.total_units }}</p>
            <p class="text-xs text-gray-400">Units</p>
          </div>
          <div class="rounded-xl bg-green-50 p-3">
            <p class="text-lg font-bold text-green-700">{{ property.occupied_units }}</p>
            <p class="text-xs text-gray-400">Occupied</p>
          </div>
          <div class="rounded-xl bg-amber-50 p-3">
            <p class="text-lg font-bold text-amber-700">{{ property.vacant_units }}</p>
            <p class="text-xs text-gray-400">Vacant</p>
          </div>
        </div>
        <div class="flex justify-between items-center mt-4">
          <p class="text-xs text-gray-400">{{ property.property_type }} - {{ property.code }}</p>
          <RouterLink :to="`/units?property=${property.id}`" class="text-sm text-farm-600 font-medium">View units</RouterLink>
        </div>
      </div>
    </div>

    <BaseModal :open="showModal" title="Add Property" @close="showModal = false">
      <form @submit.prevent="submit" class="space-y-3">
        <BaseAlert :message="error" type="error" />
        <BaseInput v-model="form.code" label="Property Code" placeholder="GV" required />
        <BaseInput v-model="form.name" label="Property Name" placeholder="Greenview Apartments" required />
        <BaseInput v-model="form.property_type" label="Property Type" placeholder="Apartment Block" required />
        <BaseInput v-model="form.address" label="Address" required />
        <BaseInput v-model="form.city" label="City" required />
        <BaseInput v-model="form.notes" label="Notes" type="textarea" />
        <BaseButton type="submit" :loading="saving" class="w-full">Save Property</BaseButton>
      </form>
    </BaseModal>
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import { RouterLink } from 'vue-router'
import { createProperty, listProperties } from '@/api/properties'
import { useAuthStore } from '@/stores/auth'
import BaseAlert from '@/components/ui/BaseAlert.vue'
import BaseButton from '@/components/ui/BaseButton.vue'
import BaseInput from '@/components/ui/BaseInput.vue'
import BaseModal from '@/components/ui/BaseModal.vue'

const auth = useAuthStore()
const properties = ref([])
const loading = ref(true)
const showModal = ref(false)
const saving = ref(false)
const error = ref('')
const form = ref({ code: '', name: '', property_type: '', address: '', city: '', notes: '' })

const labelize = (value) => String(value || '').replaceAll('_', ' ')
const statusBadge = (status) => status === 'active' ? 'badge-active' : status === 'maintenance' ? 'badge-sold' : 'badge-deceased'

async function load() {
  properties.value = await listProperties()
}

function openCreate() {
  form.value = { code: '', name: '', property_type: '', address: '', city: '', notes: '' }
  error.value = ''
  showModal.value = true
}

async function submit() {
  saving.value = true
  error.value = ''
  try {
    await createProperty(form.value)
    await load()
    showModal.value = false
  } catch (e) {
    error.value = e.response?.data?.detail || 'Failed to save property.'
  } finally {
    saving.value = false
  }
}

onMounted(async () => {
  await load()
  loading.value = false
})
</script>
