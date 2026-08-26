<template>
  <div class="space-y-4">
    <div class="grid grid-cols-2 lg:grid-cols-4 gap-3">
      <ReportStat label="Expected" :value="formatMoney(dashboard?.expected_rent)" color="green" />
      <ReportStat label="Collected" :value="formatMoney(dashboard?.collected_rent)" color="blue" />
      <ReportStat label="Outstanding" :value="formatMoney(dashboard?.outstanding_rent)" color="amber" />
      <ReportStat label="Expenses" :value="formatMoney(dashboard?.expenses)" color="red" />
    </div>

    <div class="grid lg:grid-cols-2 gap-4">
      <div class="card">
        <h3 class="font-semibold text-gray-700 mb-3">Arrears</h3>
        <div v-if="arrears.length === 0" class="text-sm text-gray-400">No outstanding balances.</div>
        <ul v-else class="divide-y divide-gray-100">
          <li v-for="row in arrears" :key="row.tenancy_id" class="py-3 flex justify-between gap-3">
            <div class="min-w-0">
              <p class="text-sm font-medium text-gray-800 truncate">{{ row.tenant }}</p>
              <p class="text-xs text-gray-400 truncate">{{ row.property }} - Unit {{ row.unit }}</p>
            </div>
            <span class="font-semibold text-red-600">{{ formatMoney(row.balance) }}</span>
          </li>
        </ul>
      </div>

      <div class="card">
        <h3 class="font-semibold text-gray-700 mb-3">Property Performance</h3>
        <div v-if="performance.length === 0" class="text-sm text-gray-400">No property data yet.</div>
        <ul v-else class="divide-y divide-gray-100">
          <li v-for="row in performance" :key="row.property_id" class="py-3">
            <div class="flex items-center justify-between gap-3">
              <div class="min-w-0">
                <p class="text-sm font-medium text-gray-800 truncate">{{ row.property }}</p>
                <p class="text-xs text-gray-400">{{ row.units }} unit(s)</p>
              </div>
              <span class="font-semibold text-gray-800">{{ formatMoney(row.monthly_rent) }}</span>
            </div>
          </li>
        </ul>
      </div>
    </div>
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import { getArrearsReport, getDashboardSummary, getPropertyPerformance } from '@/api/reports'

const dashboard = ref(null)
const arrears = ref([])
const performance = ref([])
const colorClasses = {
  green: 'bg-green-50 text-green-700',
  blue: 'bg-blue-50 text-blue-700',
  amber: 'bg-amber-50 text-amber-700',
  red: 'bg-red-50 text-red-700',
}

const ReportStat = {
  props: ['label', 'value', 'color'],
  computed: {
    classes() {
      return colorClasses[this.color] || colorClasses.green
    },
  },
  template: `
    <div class="card">
      <p class="text-xs text-gray-400 mb-1">{{ label }}</p>
      <p class="text-xl font-bold px-3 py-2 rounded-xl inline-block" :class="classes">{{ value }}</p>
    </div>
  `,
}

const formatMoney = (value) =>
  new Intl.NumberFormat('en-KE', { style: 'currency', currency: 'KES', maximumFractionDigits: 0 }).format(Number(value || 0))

onMounted(async () => {
  ;[dashboard.value, arrears.value, performance.value] = await Promise.all([
    getDashboardSummary(),
    getArrearsReport(),
    getPropertyPerformance(),
  ])
})
</script>
