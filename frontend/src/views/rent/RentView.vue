<template>
  <div class="space-y-4">
    <div class="flex items-center justify-between gap-3">
      <p class="text-sm text-gray-500">{{ tenancies.length }} tenancy record(s)</p>
      <BaseButton @click="openMoveIn">+ Move In Tenant</BaseButton>
    </div>

    <div class="grid lg:grid-cols-[1fr_1.2fr] gap-4">
      <div class="space-y-3">
        <div
          v-for="tenancy in tenancies"
          :key="tenancy.id"
          class="card cursor-pointer transition-colors"
          :class="selected?.id === tenancy.id ? 'border-farm-500 bg-farm-50' : ''"
          @click="selectTenancy(tenancy)"
        >
          <div class="flex items-start justify-between gap-3">
            <div class="min-w-0">
              <p class="font-semibold text-gray-800 truncate">{{ tenancy.tenant_name }}</p>
              <p class="text-sm text-gray-500 truncate">{{ tenancy.property_name }} - Unit {{ tenancy.unit_number }}</p>
            </div>
            <span :class="Number(tenancy.balance) > 0 ? 'text-red-600' : 'text-green-700'" class="font-bold">
              {{ formatMoney(tenancy.balance) }}
            </span>
          </div>
          <div class="flex items-center justify-between mt-3 text-xs text-gray-400">
            <span>Rent {{ formatMoney(tenancy.monthly_rent) }}</span>
            <span>Due day {{ tenancy.rent_due_day }}</span>
          </div>
        </div>
      </div>

      <div class="card min-h-[22rem]">
        <div v-if="!selected" class="h-full flex items-center justify-center text-gray-400 text-sm">
          Select a tenancy to view the ledger.
        </div>
        <template v-else>
          <div class="flex items-start justify-between gap-3 mb-4">
            <div>
              <h3 class="font-semibold text-gray-800">{{ selected.tenant_name }}</h3>
              <p class="text-sm text-gray-500">{{ selected.property_name }} - Unit {{ selected.unit_number }}</p>
            </div>
            <div class="text-right">
              <p class="text-xs text-gray-400">Balance</p>
              <p class="font-bold" :class="Number(selected.balance) > 0 ? 'text-red-600' : 'text-green-700'">
                {{ formatMoney(selected.balance) }}
              </p>
            </div>
          </div>

          <div class="overflow-x-auto">
            <table class="w-full text-sm">
              <thead class="text-left text-xs text-gray-400 border-b">
                <tr>
                  <th class="py-2">Date</th>
                  <th class="py-2">Description</th>
                  <th class="py-2 text-right">Debit</th>
                  <th class="py-2 text-right">Credit</th>
                  <th class="py-2 text-right">Balance</th>
                </tr>
              </thead>
              <tbody class="divide-y divide-gray-100">
                <tr v-for="entry in ledger" :key="entry.id">
                  <td class="py-2 whitespace-nowrap">{{ formatDate(entry.entry_date) }}</td>
                  <td class="py-2">{{ entry.description }}</td>
                  <td class="py-2 text-right">{{ Number(entry.debit) ? formatMoney(entry.debit) : '-' }}</td>
                  <td class="py-2 text-right">{{ Number(entry.credit) ? formatMoney(entry.credit) : '-' }}</td>
                  <td class="py-2 text-right font-medium">{{ formatMoney(entry.balance_after) }}</td>
                </tr>
              </tbody>
            </table>
          </div>
        </template>
      </div>
    </div>

    <BaseModal :open="showMoveIn" title="Move In Tenant" @close="showMoveIn = false">
      <form @submit.prevent="submitMoveIn" class="space-y-3">
        <BaseAlert :message="error" type="error" />
        <BaseInput v-model="moveIn.tenant_id" label="Tenant" type="select" required>
          <option value="">Select tenant</option>
          <option v-for="tenant in tenants" :key="tenant.id" :value="tenant.id">{{ tenant.full_name }}</option>
        </BaseInput>
        <BaseInput v-model="moveIn.unit_id" label="Vacant Unit" type="select" required>
          <option value="">Select unit</option>
          <option v-for="unit in vacantUnits" :key="unit.id" :value="unit.id">
            {{ unit.property_name }} - {{ unit.unit_number }} ({{ formatMoney(unit.monthly_rent) }})
          </option>
        </BaseInput>
        <div class="grid grid-cols-2 gap-3">
          <BaseInput v-model="moveIn.start_date" label="Start Date" type="date" required />
          <BaseInput v-model="moveIn.rent_due_day" label="Due Day" type="number" required />
        </div>
        <div class="grid grid-cols-2 gap-3">
          <BaseInput v-model="moveIn.monthly_rent" label="Monthly Rent" type="number" required />
          <BaseInput v-model="moveIn.deposit_amount" label="Deposit" type="number" required />
        </div>
        <label class="flex items-center gap-2 text-sm text-gray-700">
          <input v-model="moveIn.opening_charge" type="checkbox" class="w-4 h-4 rounded text-farm-600 border-gray-300 focus:ring-farm-500" />
          Create opening rent and deposit charges
        </label>
        <BaseButton type="submit" :loading="saving" class="w-full">Create Tenancy</BaseButton>
      </form>
    </BaseModal>
  </div>
</template>

<script setup>
import { computed, onMounted, ref, watch } from 'vue'
import { listLedgerEntries } from '@/api/ledger'
import { createTenancy, listTenancies } from '@/api/tenancies'
import { listTenants } from '@/api/tenants'
import { listUnits } from '@/api/units'
import BaseAlert from '@/components/ui/BaseAlert.vue'
import BaseButton from '@/components/ui/BaseButton.vue'
import BaseInput from '@/components/ui/BaseInput.vue'
import BaseModal from '@/components/ui/BaseModal.vue'

const tenancies = ref([])
const tenants = ref([])
const units = ref([])
const selected = ref(null)
const ledger = ref([])
const showMoveIn = ref(false)
const saving = ref(false)
const error = ref('')
const moveIn = ref({})

const vacantUnits = computed(() => units.value.filter(u => u.status === 'vacant'))
const today = () => new Date().toISOString().slice(0, 10)
const formatDate = (value) => value ? new Date(value).toLocaleDateString('en-KE') : ''
const formatMoney = (value) =>
  new Intl.NumberFormat('en-KE', { style: 'currency', currency: 'KES', maximumFractionDigits: 0 }).format(Number(value || 0))

async function load() {
  ;[tenancies.value, tenants.value, units.value] = await Promise.all([
    listTenancies(),
    listTenants(),
    listUnits(),
  ])
  if (!selected.value && tenancies.value.length) selectTenancy(tenancies.value[0])
}

async function selectTenancy(tenancy) {
  selected.value = tenancy
  ledger.value = await listLedgerEntries({ tenancy_id: tenancy.id })
}

function openMoveIn() {
  const unit = vacantUnits.value[0]
  moveIn.value = {
    tenant_id: '',
    unit_id: unit?.id || '',
    start_date: today(),
    monthly_rent: unit?.monthly_rent || '',
    deposit_amount: unit?.deposit_amount || '',
    rent_due_day: unit?.rent_due_day || 5,
    opening_charge: true,
  }
  error.value = ''
  showMoveIn.value = true
}

async function submitMoveIn() {
  saving.value = true
  error.value = ''
  try {
    await createTenancy(moveIn.value)
    selected.value = null
    await load()
    showMoveIn.value = false
  } catch (e) {
    error.value = e.response?.data?.detail || 'Failed to create tenancy.'
  } finally {
    saving.value = false
  }
}

watch(() => moveIn.value.unit_id, (unitId) => {
  const unit = units.value.find(u => String(u.id) === String(unitId))
  if (unit) {
    moveIn.value.monthly_rent = unit.monthly_rent
    moveIn.value.deposit_amount = unit.deposit_amount
    moveIn.value.rent_due_day = unit.rent_due_day
  }
})

onMounted(load)
</script>
