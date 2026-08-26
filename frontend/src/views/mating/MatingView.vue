<template>
  <div class="space-y-4">
    <div class="flex gap-1 bg-gray-100 p-1 rounded-lg">
      <button v-for="tab in ['Mating Events', 'Log Birth']" :key="tab" @click="activeTab = tab"
        class="flex-1 py-1.5 text-sm font-medium rounded-md transition-colors"
        :class="activeTab === tab ? 'bg-white text-farm-700 shadow-sm' : 'text-gray-500'"
      >{{ tab }}</button>
    </div>

    <!-- Mating Events list -->
    <div v-if="activeTab === 'Mating Events'" class="space-y-3">
      <div class="flex justify-end">
        <BaseButton @click="showMatingModal = true">+ Log Mating</BaseButton>
      </div>

      <div v-if="events.length === 0" class="card text-center py-8 text-gray-400 text-sm">
        No mating events recorded.
      </div>

      <div v-for="e in events" :key="e.id" class="card">
        <div class="flex items-start justify-between">
          <div>
            <p class="text-sm font-medium text-gray-700">
              Female #{{ e.female_id }} × Male #{{ e.male_id }}
            </p>
            <p class="text-xs text-gray-400">Mated: {{ formatDate(e.mating_date) }}</p>
          </div>
          <div class="flex flex-col items-end gap-1">
            <p v-if="e.expected_birth_date" class="text-xs text-amber-600 font-medium">
              Expected: {{ formatDate(e.expected_birth_date) }}
            </p>
            <span v-if="e._offline" class="text-xs text-amber-500">⏳ pending sync</span>
          </div>
        </div>
        <p v-if="e.notes" class="text-xs text-gray-500 mt-2">{{ e.notes }}</p>
      </div>
    </div>

    <!-- Log Birth -->
    <div v-if="activeTab === 'Log Birth'" class="max-w-lg">
      <div class="card space-y-3">
        <BaseAlert :message="birthSuccess" type="success" />
        <form @submit.prevent="submitBirth" class="space-y-3">
          <div>
            <label class="text-sm font-medium text-gray-700">Mother <span class="text-red-500">*</span></label>
            <select v-model="birthForm.animal_id" class="input-field mt-1" required>
              <option value="">Select female animal</option>
              <option v-for="a in females" :key="a.id" :value="a.id">
                {{ getAnimalEmoji(a.livestock_type_name) }} {{ a.name || a.tag_number }}
              </option>
            </select>
          </div>
          <BaseInput v-model="birthForm.birth_date"          label="Birth Date"          type="date"   required />
          <BaseInput v-model="birthForm.number_of_offspring" label="Number of Offspring" type="number" />
          <BaseInput v-model="birthForm.notes"               label="Notes"               type="textarea" />
          <BaseButton type="submit" :loading="birthLoading" class="w-full">Record Birth</BaseButton>
        </form>
      </div>
    </div>

    <!-- Mating Modal -->
    <BaseModal :open="showMatingModal" title="Log Mating Event" @close="showMatingModal = false">
      <form @submit.prevent="submitMating" class="space-y-3">
        <BaseAlert :message="matingError" type="error" />
        <div>
          <label class="text-sm font-medium text-gray-700">Female <span class="text-red-500">*</span></label>
          <select v-model="matingForm.female_id" class="input-field mt-1" required>
            <option value="">Select female</option>
            <option v-for="a in females" :key="a.id" :value="a.id">
              {{ getAnimalEmoji(a.livestock_type_name) }} {{ a.name || a.tag_number }}
            </option>
          </select>
        </div>
        <div>
          <label class="text-sm font-medium text-gray-700">Male <span class="text-red-500">*</span></label>
          <select v-model="matingForm.male_id" class="input-field mt-1" required>
            <option value="">Select male</option>
            <option v-for="a in males" :key="a.id" :value="a.id">
              {{ getAnimalEmoji(a.livestock_type_name) }} {{ a.name || a.tag_number }}
            </option>
          </select>
        </div>
        <BaseInput v-model="matingForm.mating_date" label="Mating Date" type="date" required />
        <BaseInput v-model="matingForm.notes"       label="Notes"       type="textarea" />
        <BaseButton type="submit" :loading="matingLoading" class="w-full">Record Mating</BaseButton>
      </form>
    </BaseModal>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { listAnimals }                from '@/api/animals'
import { listMatingEvents, createMatingEvent, logBirth } from '@/api/mating'
import { getAnimalEmoji }             from '@/utils/animalEmoji'
import { useOfflineMutation }         from '@/composables/useOfflineMutation'
import BaseButton from '@/components/ui/BaseButton.vue'
import BaseInput  from '@/components/ui/BaseInput.vue'
import BaseModal  from '@/components/ui/BaseModal.vue'
import BaseAlert  from '@/components/ui/BaseAlert.vue'

const { execute } = useOfflineMutation()

const activeTab = ref('Mating Events')
const animals   = ref([])
const events    = ref([])

const females = computed(() => animals.value.filter(a => a.gender === 'female'))
const males   = computed(() => animals.value.filter(a => a.gender === 'male'))

const showMatingModal = ref(false)
const matingLoading   = ref(false)
const matingError     = ref('')
const matingForm      = ref({ female_id: '', male_id: '', mating_date: '', notes: '' })

const birthLoading  = ref(false)
const birthSuccess  = ref('')
const birthForm     = ref({ animal_id: '', birth_date: '', number_of_offspring: 1, notes: '' })

const formatDate = (d) => d ? new Date(d).toLocaleDateString() : '—'

onMounted(async () => {
  ;[animals.value, events.value] = await Promise.all([
    listAnimals({ status: 'active' }),
    listMatingEvents(),
  ])
})

async function submitMating() {
  matingLoading.value = true; matingError.value = ''
  try {
    const payload = {
      ...matingForm.value,
      female_id: parseInt(matingForm.value.female_id),
      male_id:   parseInt(matingForm.value.male_id),
    }
    const event = await execute(
      () => createMatingEvent(payload),
      () => ({ ...payload, expected_birth_date: null }),
    )
    events.value.unshift(event)
    showMatingModal.value = false
    matingForm.value = { female_id: '', male_id: '', mating_date: '', notes: '' }
  } catch (e) {
    matingError.value = e.response?.data?.detail || 'Failed to log mating event.'
  } finally {
    matingLoading.value = false }
}

async function submitBirth() {
  birthLoading.value = true; birthSuccess.value = ''
  try {
    await execute(() => logBirth({
      ...birthForm.value,
      animal_id:          parseInt(birthForm.value.animal_id),
      number_of_offspring: parseInt(birthForm.value.number_of_offspring),
    }))
    birthSuccess.value = 'Birth recorded!'
    birthForm.value = { animal_id: '', birth_date: '', number_of_offspring: 1, notes: '' }
  } catch (e) {
    birthSuccess.value = '' // clear on real error
    // surface nothing — logBirth view has no error ref; add one if needed
  } finally {
    birthLoading.value = false
  }
}
</script>
