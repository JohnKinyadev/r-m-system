<template>
  <div class="space-y-4">
    <!-- Tabs -->
    <div class="flex gap-1 bg-gray-100 p-1 rounded-lg">
      <button v-for="tab in tabs" :key="tab.key" @click="activeTab = tab.key"
        class="flex-1 py-1.5 text-sm font-medium rounded-md transition-colors"
        :class="activeTab === tab.key ? 'bg-white text-farm-700 shadow-sm' : 'text-gray-500'"
      >{{ tab.label }}</button>
    </div>

    <!-- Feed Types -->
    <div v-if="activeTab === 'types'" class="space-y-3">
      <div class="flex justify-between items-center">
        <p class="text-sm text-gray-500">{{ feedTypes.length }} feed type(s)</p>
        <BaseButton v-if="isOwner" @click="showFeedTypeModal = true">+ Add Type</BaseButton>
      </div>
      <div v-if="feedTypes.length === 0" class="card text-center py-8 text-gray-400 text-sm">
        No feed types yet.
      </div>
      <div v-for="ft in feedTypes" :key="ft.id" class="card flex items-center justify-between">
        <div>
          <p class="font-medium text-gray-800">🌾 {{ ft.name }}</p>
          <p class="text-sm text-gray-500">{{ ft.current_stock }} {{ ft.unit }} in stock</p>
        </div>
        <div class="text-right">
          <span v-if="ft.current_stock <= ft.low_stock_threshold" class="badge-sold text-xs">Low Stock</span>
          <p class="text-xs text-gray-400 mt-1">Threshold: {{ ft.low_stock_threshold }} {{ ft.unit }}</p>
          <span v-if="ft._offline" class="text-xs text-amber-500 block">⏳ pending sync</span>
        </div>
      </div>
    </div>

    <!-- Log Feeding Session -->
    <div v-if="activeTab === 'log'" class="max-w-lg">
      <div class="card space-y-4">
        <p class="text-sm text-gray-500">Feed will be divided equally among all active animals.</p>
        <BaseAlert :message="feedSuccess" type="success" />
        <BaseAlert :message="feedError"   type="error" />
        <form @submit.prevent="submitFeedLog" class="space-y-3">
          <div>
            <label class="text-sm font-medium text-gray-700">Feed Type <span class="text-red-500">*</span></label>
            <select v-model="feedForm.feed_type_id" class="input-field mt-1" required>
              <option value="">Select feed type</option>
              <option v-for="ft in feedTypes" :key="ft.id" :value="ft.id">
                {{ ft.name }} ({{ ft.current_stock }} {{ ft.unit }})
              </option>
            </select>
          </div>
          <BaseInput v-model="feedForm.total_quantity" label="Total Quantity"        type="number"         required placeholder="e.g. 50" />
          <BaseInput v-model="feedForm.session_date"   label="Session Date & Time"   type="datetime-local" required />
          <BaseButton type="submit" :loading="feedLoading" class="w-full">Log Feeding Session</BaseButton>
        </form>
      </div>
    </div>

    <!-- Stock Arrival -->
    <div v-if="activeTab === 'stock'" class="max-w-lg">
      <div class="card space-y-4">
        <BaseAlert :message="stockSuccess" type="success" />
        <BaseAlert :message="stockError"   type="error" />
        <form @submit.prevent="submitStockArrival" class="space-y-3">
          <div>
            <label class="text-sm font-medium text-gray-700">Feed Type <span class="text-red-500">*</span></label>
            <select v-model="stockForm.feed_type_id" class="input-field mt-1" required>
              <option value="">Select feed type</option>
              <option v-for="ft in feedTypes" :key="ft.id" :value="ft.id">{{ ft.name }}</option>
            </select>
          </div>
          <BaseInput v-model="stockForm.quantity"   label="Quantity Received"  type="number"         required />
          <BaseInput v-model="stockForm.arrived_at" label="Arrival Date"       type="datetime-local" required />
          <BaseInput v-model="stockForm.notes"      label="Notes"              type="textarea" />
          <BaseButton type="submit" :loading="stockLoading" class="w-full">Record Stock Arrival</BaseButton>
        </form>
      </div>
    </div>

    <!-- Feed Type Modal (owner only) -->
    <BaseModal :open="showFeedTypeModal" title="Add Feed Type" @close="showFeedTypeModal = false">
      <form @submit.prevent="submitFeedType" class="space-y-3">
        <BaseInput v-model="ftForm.name"                label="Feed Name"          required placeholder="e.g. Hay" />
        <BaseInput v-model="ftForm.unit"                label="Unit"               required placeholder="kg, bags, bales…" />
        <BaseInput v-model="ftForm.low_stock_threshold" label="Low Stock Threshold" type="number" />
        <BaseButton type="submit" :loading="ftLoading" class="w-full">Create</BaseButton>
      </form>
    </BaseModal>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useAuthStore }   from '@/stores/auth'
import { listFeedTypes, createFeedType, logFeedingSession, logStockArrival } from '@/api/feed'
import { useOfflineMutation } from '@/composables/useOfflineMutation'
import BaseButton from '@/components/ui/BaseButton.vue'
import BaseInput  from '@/components/ui/BaseInput.vue'
import BaseModal  from '@/components/ui/BaseModal.vue'
import BaseAlert  from '@/components/ui/BaseAlert.vue'

const { execute } = useOfflineMutation()
const auth    = useAuthStore()
const isOwner = auth.isOwner

const tabs = [
  { key: 'types', label: 'Feed Types'    },
  { key: 'log',   label: 'Log Feeding'   },
  { key: 'stock', label: 'Stock Arrival' },
]
const activeTab = ref('types')

const feedTypes        = ref([])
const showFeedTypeModal = ref(false)
const ftLoading        = ref(false)
const ftForm           = ref({ name: '', unit: 'kg', low_stock_threshold: 50 })

const feedForm    = ref({ feed_type_id: '', total_quantity: '', session_date: '' })
const feedLoading = ref(false)
const feedError   = ref('')
const feedSuccess = ref('')

const stockForm    = ref({ feed_type_id: '', quantity: '', arrived_at: '', notes: '' })
const stockLoading = ref(false)
const stockSuccess = ref('')
const stockError   = ref('')

async function loadFeedTypes() { feedTypes.value = await listFeedTypes() }

async function submitFeedType() {
  ftLoading.value = true
  try {
    const ft = await execute(
      () => createFeedType({ ...ftForm.value }),
      () => ({ ...ftForm.value, id: -Date.now(), current_stock: 0 }),
    )
    feedTypes.value.push(ft)
    showFeedTypeModal.value = false
    ftForm.value = { name: '', unit: 'kg', low_stock_threshold: 50 }
  } catch (e) {
    // show nothing — modal stays open, user can retry
  } finally {
    ftLoading.value = false
  }
}

async function submitFeedLog() {
  feedLoading.value = true; feedError.value = ''; feedSuccess.value = ''
  try {
    await execute(() => logFeedingSession({
      ...feedForm.value,
      total_quantity: parseFloat(feedForm.value.total_quantity),
    }))
    feedSuccess.value = 'Feeding session logged!'
    feedForm.value = { feed_type_id: '', total_quantity: '', session_date: '' }
    // Refresh feed types (stock levels may have changed) — only meaningful online
    if (!feedSuccess.value.includes('offline')) await loadFeedTypes()
  } catch (e) {
    feedError.value = e.response?.data?.detail || 'Failed to log session.'
  } finally {
    feedLoading.value = false
  }
}

async function submitStockArrival() {
  stockLoading.value = true; stockSuccess.value = ''; stockError.value = ''
  try {
    await execute(() => logStockArrival({
      ...stockForm.value,
      quantity: parseFloat(stockForm.value.quantity),
    }))
    stockSuccess.value = 'Stock arrival recorded!'
    stockForm.value = { feed_type_id: '', quantity: '', arrived_at: '', notes: '' }
  } catch (e) {
    stockError.value = e.response?.data?.detail || 'Failed to record arrival.'
  } finally {
    stockLoading.value = false
  }
}

onMounted(loadFeedTypes)
</script>
