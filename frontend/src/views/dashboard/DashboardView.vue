<template>
  <div class="space-y-5">
    <div class="card bg-gradient-to-r from-farm-700 to-farm-500 text-white">
      <div class="flex flex-col sm:flex-row sm:items-end sm:justify-between gap-3">
        <div>
          <p class="text-xs uppercase tracking-widest opacity-75 mb-1">{{ summary?.period || 'Current month' }}</p>
          <p class="text-2xl font-bold">Landlord control center</p>
          <p class="text-sm text-farm-100 mt-1">Rent, occupancy, arrears, and operations in one view.</p>
        </div>
        <div class="text-left sm:text-right">
          <p class="text-xs text-farm-100">Collection rate</p>
          <p class="text-3xl font-bold">{{ summary?.collection_rate ?? 0 }}%</p>
        </div>
      </div>
    </div>

    <div class="grid grid-cols-2 lg:grid-cols-4 gap-3">
      <StatCard label="Expected Rent" :value="formatMoney(summary?.expected_rent)" color="green" icon="money" />
      <StatCard label="Collected" :value="formatMoney(summary?.collected_rent)" color="blue" icon="money" />
      <StatCard label="Outstanding" :value="formatMoney(summary?.outstanding_rent)" color="amber" icon="receipt" />
      <StatCard label="Net Income" :value="formatMoney(summary?.net_income)" color="purple" icon="bar-chart" />
    </div>

    <div class="grid grid-cols-2 lg:grid-cols-4 gap-3">
      <StatCard label="Properties" :value="summary?.properties ?? '-'" color="green" icon="building" />
      <StatCard label="Units" :value="summary?.units ?? '-'" color="blue" icon="home" />
      <StatCard label="Occupied" :value="summary?.occupied_units ?? '-'" color="purple" icon="users" />
      <StatCard label="Vacant" :value="summary?.vacant_units ?? '-'" color="amber" icon="home" />
    </div>

    <div class="card">
      <div class="flex items-center justify-between mb-3">
        <h3 class="font-semibold text-gray-700">Action Center</h3>
        <RouterLink to="/reports" class="text-sm text-farm-600 font-medium">View reports</RouterLink>
      </div>
      <div class="grid sm:grid-cols-2 lg:grid-cols-5 gap-2">
        <RouterLink
          v-for="item in actionItems"
          :key="item.label"
          :to="actionRoute(item.label)"
          class="border border-gray-100 rounded-xl p-3 hover:border-farm-300 hover:bg-farm-50 transition-colors"
        >
          <p class="text-2xl font-bold text-gray-800">{{ item.count }}</p>
          <p class="text-xs text-gray-500">{{ item.label }}</p>
        </RouterLink>
      </div>
    </div>

    <div class="grid lg:grid-cols-2 gap-4">
      <div class="card">
        <div class="flex items-center justify-between mb-3">
          <h3 class="font-semibold text-gray-700">Outstanding Tenants</h3>
          <RouterLink to="/rent" class="text-sm text-farm-600 font-medium">Open ledger</RouterLink>
        </div>
        <div v-if="loading" class="text-sm text-gray-400 py-6">Loading...</div>
        <div v-else-if="arrears.length === 0" class="text-sm text-gray-400 py-6">No outstanding balances.</div>
        <ul v-else class="divide-y divide-gray-100">
          <li v-for="row in arrears.slice(0, 5)" :key="row.tenancy_id" class="py-3 flex items-center justify-between gap-3">
            <div class="min-w-0">
              <p class="text-sm font-medium text-gray-800 truncate">{{ row.tenant }}</p>
              <p class="text-xs text-gray-400 truncate">{{ row.property }} - Unit {{ row.unit }}</p>
            </div>
            <span class="text-sm font-semibold text-red-600">{{ formatMoney(row.balance) }}</span>
          </li>
        </ul>
      </div>

      <div class="card">
        <div class="flex items-center justify-between mb-3">
          <h3 class="font-semibold text-gray-700">Recent Units</h3>
          <RouterLink to="/units" class="text-sm text-farm-600 font-medium">View all</RouterLink>
        </div>
        <div v-if="loading" class="text-sm text-gray-400 py-6">Loading...</div>
        <ul v-else class="divide-y divide-gray-100">
          <li v-for="unit in units.slice(0, 6)" :key="unit.id" class="py-3 flex items-center justify-between gap-3">
            <div class="min-w-0">
              <p class="text-sm font-medium text-gray-800 truncate">{{ unit.property_name }} - {{ unit.unit_number }}</p>
              <p class="text-xs text-gray-400 truncate">{{ unit.unit_type }} - {{ formatMoney(unit.monthly_rent) }}</p>
            </div>
            <span :class="statusBadge(unit.status)">{{ labelize(unit.status) }}</span>
          </li>
        </ul>
      </div>
    </div>

    <div class="card">
      <h3 class="font-semibold text-gray-700 mb-3">Quick Actions</h3>
      <div class="grid grid-cols-2 sm:grid-cols-4 gap-2">
        <QuickAction v-if="auth.hasModule('properties')" to="/properties" label="Add Property" color="farm" emoji="+" />
        <QuickAction v-if="auth.hasModule('units')" to="/units" label="Add Unit" color="amber" emoji="+" />
        <QuickAction v-if="auth.hasModule('tenants')" to="/tenants" label="Add Tenant" color="blue" emoji="+" />
        <QuickAction v-if="auth.hasModule('payments')" to="/payments" label="Record Payment" color="purple" emoji="+" />
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { RouterLink } from 'vue-router'
import { getArrearsReport, getDashboardSummary } from '@/api/reports'
import { listUnits } from '@/api/units'
import { useAuthStore } from '@/stores/auth'
import StatCard from '@/components/dashboard/StatCard.vue'
import QuickAction from '@/components/dashboard/QuickAction.vue'

const auth = useAuthStore()
const summary = ref(null)
const arrears = ref([])
const units = ref([])
const loading = ref(true)

const actionItems = computed(() => summary.value?.needs_attention ?? [])

const formatMoney = (value) =>
  new Intl.NumberFormat('en-KE', { style: 'currency', currency: 'KES', maximumFractionDigits: 0 }).format(Number(value || 0))

const labelize = (value) => String(value || '').replaceAll('_', ' ')

const statusBadge = (status) => ({
  occupied: 'badge-active',
  notice_given: 'badge-sold',
  vacant: 'badge-sold',
  maintenance: 'badge-deceased',
  unavailable: 'badge-deceased',
  reserved: 'badge-sold',
}[status] || 'badge-deceased')

const actionRoute = (label) => {
  if (label.includes('maintenance')) return '/maintenance'
  if (label.includes('Vacant')) return '/units'
  if (label.includes('Leases')) return '/rent'
  return '/rent'
}

onMounted(async () => {
  loading.value = true
  ;[summary.value, arrears.value, units.value] = await Promise.all([
    getDashboardSummary(),
    getArrearsReport(),
    listUnits(),
  ])
  loading.value = false
})
</script>
