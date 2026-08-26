<template>
  <div class="space-y-4">
    <div class="flex items-center justify-between gap-3">
      <p class="text-sm text-gray-500">{{ expenses.length }} expense record(s)</p>
      <BaseButton @click="openCreate">+ Add Expense</BaseButton>
    </div>

    <div class="card overflow-x-auto">
      <table class="w-full text-sm">
        <thead class="text-left text-xs text-gray-400 border-b">
          <tr>
            <th class="py-2">Date</th>
            <th class="py-2">Property</th>
            <th class="py-2">Category</th>
            <th class="py-2">Description</th>
            <th class="py-2 text-right">Amount</th>
          </tr>
        </thead>
        <tbody class="divide-y divide-gray-100">
          <tr v-for="expense in expenses" :key="expense.id">
            <td class="py-3">{{ formatDate(expense.expense_date) }}</td>
            <td class="py-3">{{ expense.property_name || 'Portfolio' }}</td>
            <td class="py-3">{{ labelize(expense.category) }}</td>
            <td class="py-3">{{ expense.description }}</td>
            <td class="py-3 text-right font-semibold text-red-600">{{ formatMoney(expense.amount) }}</td>
          </tr>
        </tbody>
      </table>
    </div>

    <BaseModal :open="showModal" title="Add Expense" @close="showModal = false">
      <form @submit.prevent="submit" class="space-y-3">
        <BaseAlert :message="error" type="error" />
        <BaseInput v-model="form.property_id" label="Property" type="select">
          <option value="">Portfolio-level expense</option>
          <option v-for="property in properties" :key="property.id" :value="property.id">{{ property.name }}</option>
        </BaseInput>
        <BaseInput v-model="form.expense_date" label="Date" type="date" required />
        <BaseInput v-model="form.category" label="Category" type="select" required>
          <option value="repairs">Repairs</option>
          <option value="caretaker">Caretaker</option>
          <option value="water">Water</option>
          <option value="electricity">Electricity</option>
          <option value="security">Security</option>
          <option value="garbage">Garbage</option>
          <option value="tax">Tax</option>
          <option value="other">Other</option>
        </BaseInput>
        <BaseInput v-model="form.amount" label="Amount" type="number" required />
        <BaseInput v-model="form.description" label="Description" required />
        <BaseInput v-model="form.notes" label="Notes" type="textarea" />
        <BaseButton type="submit" :loading="saving" class="w-full">Save Expense</BaseButton>
      </form>
    </BaseModal>
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import { createExpense, listExpenses } from '@/api/expenses'
import { listProperties } from '@/api/properties'
import BaseAlert from '@/components/ui/BaseAlert.vue'
import BaseButton from '@/components/ui/BaseButton.vue'
import BaseInput from '@/components/ui/BaseInput.vue'
import BaseModal from '@/components/ui/BaseModal.vue'

const expenses = ref([])
const properties = ref([])
const showModal = ref(false)
const saving = ref(false)
const error = ref('')
const form = ref({})

const today = () => new Date().toISOString().slice(0, 10)
const formatDate = (value) => value ? new Date(value).toLocaleDateString('en-KE') : ''
const labelize = (value) => String(value || '').replaceAll('_', ' ')
const formatMoney = (value) =>
  new Intl.NumberFormat('en-KE', { style: 'currency', currency: 'KES', maximumFractionDigits: 0 }).format(Number(value || 0))

async function load() {
  ;[expenses.value, properties.value] = await Promise.all([listExpenses(), listProperties()])
}

function openCreate() {
  form.value = { property_id: '', expense_date: today(), category: 'repairs', amount: '', description: '', notes: '' }
  error.value = ''
  showModal.value = true
}

async function submit() {
  saving.value = true
  error.value = ''
  try {
    const payload = { ...form.value, property_id: form.value.property_id || null }
    await createExpense(payload)
    await load()
    showModal.value = false
  } catch (e) {
    error.value = e.response?.data?.detail || 'Failed to save expense.'
  } finally {
    saving.value = false
  }
}

onMounted(load)
</script>
