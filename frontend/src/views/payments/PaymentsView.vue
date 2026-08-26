<template>
  <div class="space-y-4">
    <div class="flex items-center justify-between gap-3">
      <p class="text-sm text-gray-500">{{ payments.length }} payment(s)</p>
      <BaseButton @click="openCreate">+ Record Payment</BaseButton>
    </div>

    <div class="card overflow-x-auto">
      <table class="w-full text-sm">
        <thead class="text-left text-xs text-gray-400 border-b">
          <tr>
            <th class="py-2">Date</th>
            <th class="py-2">Tenant</th>
            <th class="py-2">Unit</th>
            <th class="py-2">Method</th>
            <th class="py-2 text-right">Amount</th>
          </tr>
        </thead>
        <tbody class="divide-y divide-gray-100">
          <tr v-for="payment in payments" :key="payment.id">
            <td class="py-3">{{ formatDate(payment.payment_date) }}</td>
            <td class="py-3">{{ payment.tenant_name }}</td>
            <td class="py-3">{{ payment.property_name }} - {{ payment.unit_number }}</td>
            <td class="py-3">{{ labelize(payment.method) }}</td>
            <td class="py-3 text-right font-semibold text-green-700">{{ formatMoney(payment.amount) }}</td>
          </tr>
        </tbody>
      </table>
    </div>

    <BaseModal :open="showModal" title="Record Payment" @close="showModal = false">
      <form @submit.prevent="submit" class="space-y-3">
        <BaseAlert :message="error" type="error" />
        <BaseInput v-model="form.tenancy_id" label="Tenant / Unit" type="select" required>
          <option value="">Select tenancy</option>
          <option v-for="tenancy in tenancies" :key="tenancy.id" :value="tenancy.id">
            {{ tenancy.tenant_name }} - {{ tenancy.property_name }} {{ tenancy.unit_number }}
          </option>
        </BaseInput>
        <BaseInput v-model="form.amount" label="Amount" type="number" required />
        <BaseInput v-model="form.payment_date" label="Payment Date" type="date" required />
        <BaseInput v-model="form.method" label="Method" type="select" required>
          <option value="cash">Cash</option>
          <option value="mpesa">M-Pesa</option>
          <option value="bank_transfer">Bank Transfer</option>
          <option value="card">Card</option>
          <option value="other">Other</option>
        </BaseInput>
        <BaseInput v-model="form.reference" label="Reference" placeholder="MPESA code, receipt no." />
        <BaseInput v-model="form.payer_phone" label="Payer Phone" />
        <BaseButton type="submit" :loading="saving" class="w-full">Save Payment</BaseButton>
      </form>
    </BaseModal>
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import { createPayment, listPayments } from '@/api/payments'
import { listTenancies } from '@/api/tenancies'
import BaseAlert from '@/components/ui/BaseAlert.vue'
import BaseButton from '@/components/ui/BaseButton.vue'
import BaseInput from '@/components/ui/BaseInput.vue'
import BaseModal from '@/components/ui/BaseModal.vue'

const payments = ref([])
const tenancies = ref([])
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
  ;[payments.value, tenancies.value] = await Promise.all([listPayments(), listTenancies()])
}

function openCreate() {
  form.value = { tenancy_id: '', amount: '', payment_date: today(), method: 'mpesa', reference: '', payer_phone: '' }
  error.value = ''
  showModal.value = true
}

async function submit() {
  saving.value = true
  error.value = ''
  try {
    await createPayment(form.value)
    await load()
    showModal.value = false
  } catch (e) {
    error.value = e.response?.data?.detail || 'Failed to record payment.'
  } finally {
    saving.value = false
  }
}

onMounted(load)
</script>
