<template>
  <div class="max-w-lg mx-auto">
    <BaseCard>
      <h2 class="text-lg font-semibold text-gray-800 mb-5">{{ isEdit ? 'Edit Animal' : 'Add Animal' }}</h2>
      <BaseAlert :message="error" type="error" class="mb-4" />

      <form @submit.prevent="submit" class="space-y-4">
        <BaseInput v-model="form.tag_number" label="Tag Number" required :disabled="isEdit" />
        <BaseInput v-model="form.name"       label="Name (optional)" />

        <div>
          <label class="text-sm font-medium text-gray-700">Livestock Type <span class="text-red-500">*</span></label>
          <select v-model="form.livestock_type_id" class="input-field mt-1" required>
            <option value="">Select type</option>
            <option v-for="lt in livestockTypes" :key="lt.id" :value="lt.id">
              {{ lt.name }} {{ lt.breed ? `(${lt.breed})` : '' }}
            </option>
          </select>
        </div>

        <div>
          <label class="text-sm font-medium text-gray-700">Gender <span class="text-red-500">*</span></label>
          <select v-model="form.gender" class="input-field mt-1" required>
            <option value="">Select</option>
            <option value="male">Male</option>
            <option value="female">Female</option>
          </select>
        </div>

        <BaseInput v-model="form.date_of_birth" label="Date of Birth" type="date" />
        <BaseInput v-model="form.notes"          label="Notes"         type="textarea" />

        <div v-if="isEdit">
          <label class="text-sm font-medium text-gray-700">Status</label>
          <select v-model="form.status" class="input-field mt-1">
            <option value="active">Active</option>
            <option value="sold">Sold</option>
            <option value="deceased">Deceased</option>
          </select>
        </div>

        <div class="flex gap-3 pt-2">
          <BaseButton type="submit" :loading="loading">{{ isEdit ? 'Save Changes' : 'Add Animal' }}</BaseButton>
          <BaseButton variant="secondary" @click="$router.back()">Cancel</BaseButton>
        </div>
      </form>
    </BaseCard>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter }      from 'vue-router'
import { createAnimal, updateAnimal, getAnimal } from '@/api/animals'
import { listLivestockTypes } from '@/api/livestock'
import { useOfflineMutation } from '@/composables/useOfflineMutation'
import BaseCard   from '@/components/ui/BaseCard.vue'
import BaseInput  from '@/components/ui/BaseInput.vue'
import BaseButton from '@/components/ui/BaseButton.vue'
import BaseAlert  from '@/components/ui/BaseAlert.vue'

const { execute } = useOfflineMutation()
const route  = useRoute()
const router = useRouter()

const isEdit         = computed(() => !!route.params.id)
const loading        = ref(false)
const error          = ref('')
const livestockTypes = ref([])

const form = ref({
  tag_number: '', name: '', livestock_type_id: '', gender: '',
  date_of_birth: '', notes: '', status: 'active',
})

onMounted(async () => {
  livestockTypes.value = await listLivestockTypes()
  if (isEdit.value) {
    const animal = await getAnimal(route.params.id)
    Object.assign(form.value, {
      ...animal,
      livestock_type_id: animal.livestock_type_id,
      date_of_birth: animal.date_of_birth || '',
    })
  }
})

async function submit() {
  error.value = ''
  loading.value = true
  try {
    const payload = { ...form.value }
    if (!payload.date_of_birth) delete payload.date_of_birth
    if (!payload.name)          delete payload.name
    if (!payload.notes)         delete payload.notes

    if (isEdit.value) {
      await execute(() => updateAnimal(route.params.id, {
        name: payload.name,
        status: payload.status,
        date_of_birth: payload.date_of_birth,
        notes: payload.notes,
      }))
      // ID is already known — safe to navigate even if queued offline
      router.push(`/animals/${route.params.id}`)
    } else {
      const animal = await execute(() => createAnimal(payload))
      if (animal._offline) {
        // Temp ID — navigate to list; animal will appear after sync
        router.push('/animals')
      } else {
        router.push(`/animals/${animal.id}`)
      }
    }
  } catch (e) {
    error.value = e.response?.data?.detail || 'Failed to save animal.'
  } finally {
    loading.value = false
  }
}
</script>
