<template>
  <div class="space-y-4">

    <!-- Stale-cache notice -->
    <div v-if="fromCache"
         class="flex items-center gap-2 text-xs text-amber-700 bg-amber-50 border border-amber-200 px-3 py-2 rounded-lg">
      <span>📶</span>
      <span>Showing cached data — connect to refresh.</span>
    </div>

    <div v-if="loading" class="space-y-3">
      <div v-for="i in 4" :key="i" class="card animate-pulse h-28 bg-gray-100" />
    </div>

    <template v-else>
      <!-- Herd overview -->
      <div class="card">
        <h3 class="font-semibold text-gray-700 mb-3">Herd Overview</h3>
        <div class="grid grid-cols-2 sm:grid-cols-4 gap-3">
          <ReportStat label="Active"            :value="dashboard?.active_animals"     color="green" />
          <ReportStat label="Sold"              :value="dashboard?.sold_animals"       color="blue"  />
          <ReportStat label="Deceased"          :value="dashboard?.deceased_animals"   color="gray"  />
          <ReportStat label="Births This Month" :value="dashboard?.births_this_month"  color="amber" />
        </div>
      </div>

      <!-- Herd health summary -->
      <div class="card">
        <h3 class="font-semibold text-gray-700 mb-3">Health Log Summary</h3>
        <p class="text-sm text-gray-500 mb-2">
          Total logs: <span class="font-semibold text-gray-700">{{ herdHealth?.total_logs ?? '—' }}</span>
        </p>
        <div class="flex flex-wrap gap-2">
          <span
            v-for="(count, type) in herdHealth?.by_type"
            :key="type"
            class="bg-gray-100 text-gray-700 text-xs px-3 py-1 rounded-full capitalize"
          >{{ type }}: {{ count }}</span>
        </div>
      </div>

      <!-- Birth & mortality -->
      <div class="card">
        <h3 class="font-semibold text-gray-700 mb-3">Birth & Mortality</h3>
        <div class="grid grid-cols-3 gap-3">
          <ReportStat label="Births Recorded" :value="birthMortality?.total_births_recorded" color="green" />
          <ReportStat label="Deceased"         :value="birthMortality?.deceased"              color="red"   />
          <ReportStat label="Sold"             :value="birthMortality?.sold"                  color="blue"  />
        </div>
      </div>

      <!-- Feed consumption -->
      <div class="card">
        <h3 class="font-semibold text-gray-700 mb-3">Feed Consumption (Top Animals)</h3>
        <div v-if="!feedConsumption?.length" class="text-sm text-gray-400">No data yet.</div>
        <ul v-else class="divide-y divide-gray-100">
          <li
            v-for="row in feedConsumption.slice(0, 10)"
            :key="row.animal_id"
            class="py-2 flex items-center justify-between text-sm"
          >
            <span class="text-gray-700">Animal #{{ row.animal_id }}</span>
            <span class="font-medium text-gray-800">{{ Number(row.total_consumed).toFixed(2) }} units</span>
          </li>
        </ul>
      </div>
    </template>
  </div>
</template>

<script setup>
import { ref, onMounted, defineComponent, h } from 'vue'
import { getDashboardSummary, getHerdHealth, getBirthMortality, getFeedConsumption } from '@/api/reports'

const loading         = ref(true)
const fromCache       = ref(false)
const dashboard       = ref(null)
const herdHealth      = ref(null)
const birthMortality  = ref(null)
const feedConsumption = ref([])

const ReportStat = defineComponent({
  props: ['label', 'value', 'color'],
  setup(props) {
    const colors = {
      green: 'text-green-600', blue: 'text-blue-600',
      gray:  'text-gray-500',  amber: 'text-amber-600', red: 'text-red-600',
    }
    return () => h('div', { class: 'text-center' }, [
      h('p', { class: `text-2xl font-bold ${colors[props.color] || 'text-gray-700'}` }, props.value ?? '—'),
      h('p', { class: 'text-xs text-gray-400 mt-0.5' }, props.label),
    ])
  },
})

onMounted(async () => {
  const results = await Promise.all([
    getDashboardSummary(),
    getHerdHealth(),
    getBirthMortality(),
    getFeedConsumption(),
  ])

  ;[dashboard.value, herdHealth.value, birthMortality.value, feedConsumption.value] = results

  // axios offline shortcut returns { status:200, offline:true }
  // The actual response objects come back as { data: ..., offline: true } from the interceptor
  // We detect it from the response header set in index.js
  // Actually we detect via checking if the data came from kv (null dashboard = no cache yet)
  // Simple heuristic: if offline and we got data, it's from cache
  const { isOnline } = await import('@/composables/useOnlineStatus')
  fromCache.value = !isOnline.value

  loading.value = false
})
</script>
