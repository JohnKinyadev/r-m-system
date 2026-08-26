<template>
  <div class="space-y-4">
    <div class="flex justify-between items-center">
      <p class="text-sm text-gray-500">{{ workers.length }} worker(s)</p>
      <BaseButton @click="openCreate">+ Add Worker</BaseButton>
    </div>

    <div v-if="loading" class="text-center py-12 text-gray-400">Loading…</div>
    <div v-else-if="workers.length === 0" class="card text-center py-8 text-gray-400">No workers yet.</div>

    <div v-else class="space-y-3">
      <div v-for="w in workers" :key="w.id" class="card space-y-3">
        <!-- Worker header -->
        <div class="flex items-center gap-3">
          <div class="w-10 h-10 rounded-full bg-gray-200 flex items-center justify-center font-bold text-gray-600 flex-shrink-0">
            {{ initials(w.full_name) }}
          </div>
          <div class="flex-1 min-w-0">
            <p class="font-medium text-gray-800">{{ w.full_name }}</p>
            <p class="text-sm text-gray-500 truncate">{{ w.email }}</p>
          </div>
          <div class="flex flex-col items-end gap-1">
            <span :class="w.is_active ? 'badge-active' : 'badge-deceased'">
              {{ w.is_active ? 'Active' : 'Inactive' }}
            </span>
            <div class="flex gap-3">
              <button @click="toggleActive(w)" class="text-xs text-farm-600 hover:underline">
                {{ w.is_active ? 'Deactivate' : 'Activate' }}
              </button>
              <button @click="removeWorker(w)" class="text-xs text-red-500 hover:underline">Remove</button>
            </div>
          </div>
        </div>

        <!-- Module permissions -->
        <div class="border-t pt-3">
          <p class="text-xs font-semibold text-gray-500 mb-2 uppercase tracking-wide">Module Access</p>
          <div class="grid grid-cols-2 sm:grid-cols-3 gap-2">
            <label
              v-for="mod in MODULES"
              :key="mod.key"
              class="flex items-center gap-2 cursor-pointer select-none"
            >
              <input
                type="checkbox"
                :checked="workerHasModule(w, mod.key)"
                @change="toggleModule(w, mod.key)"
                class="w-4 h-4 rounded text-farm-600 border-gray-300 focus:ring-farm-500"
              />
              <span class="text-sm text-gray-700">{{ mod.label }}</span>
            </label>
          </div>
        </div>
      </div>
    </div>

    <!-- Create worker modal -->
    <BaseModal :open="showModal" title="Add Farm Worker" @close="showModal = false">
      <form @submit.prevent="submit" class="space-y-3">
        <BaseAlert :message="error" type="error" />
        <BaseInput v-model="form.full_name" label="Full Name" required />
        <BaseInput v-model="form.email" label="Email" type="email" required />
        <BaseInput v-model="form.password" label="Temporary Password" type="password" required
          hint="Min 8 chars, must include uppercase, lowercase, and a number." />

        <div>
          <p class="text-sm font-medium text-gray-700 mb-2">Initial Module Access</p>
          <div class="grid grid-cols-2 gap-2">
            <label v-for="mod in MODULES" :key="mod.key" class="flex items-center gap-2 cursor-pointer">
              <input type="checkbox" v-model="form.modules" :value="mod.key"
                class="w-4 h-4 rounded text-farm-600 border-gray-300 focus:ring-farm-500" />
              <span class="text-sm text-gray-700">{{ mod.label }}</span>
            </label>
          </div>
        </div>

        <BaseButton type="submit" :loading="saving" class="w-full">Create Worker Account</BaseButton>
      </form>
    </BaseModal>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { listUsers, createUser, updateUser, deleteUser, listRoles } from '@/api/users'
import { getWorkerPermissions, setWorkerPermissions } from '@/api/permissions'
import BaseButton from '@/components/ui/BaseButton.vue'
import BaseModal from '@/components/ui/BaseModal.vue'
import BaseInput from '@/components/ui/BaseInput.vue'
import BaseAlert from '@/components/ui/BaseAlert.vue'

const MODULES = [
  { key: 'animals',         label: 'Animals' },
  { key: 'livestock_types', label: 'Livestock Types' },
  { key: 'health',          label: 'Health Records' },
  { key: 'feed',            label: 'Feed Management' },
  { key: 'mating',          label: 'Mating & Births' },
  { key: 'reports',         label: 'Reports' },
]

const users        = ref([])
const roles        = ref([])
const loading      = ref(true)
const showModal    = ref(false)
const saving       = ref(false)
const error        = ref('')
// Map of user_id → Set of granted module keys (loaded lazily per worker)
const workerPerms  = ref({})

const form = ref({ full_name: '', email: '', password: '', modules: [] })

const workers = computed(() => users.value.filter(u => u.role.name === 'farm_worker'))

const initials = (name) => name.split(' ').map(w => w[0]).slice(0, 2).join('').toUpperCase()

function workerHasModule(worker, mod) {
  return workerPerms.value[worker.id]?.has(mod) ?? false
}

async function loadWorkerPermissions(worker) {
  try {
    const mods = await getWorkerPermissions(worker.id)
    workerPerms.value = { ...workerPerms.value, [worker.id]: new Set(mods) }
  } catch {
    workerPerms.value = { ...workerPerms.value, [worker.id]: new Set() }
  }
}

async function toggleModule(worker, mod) {
  const current = new Set(workerPerms.value[worker.id] ?? [])
  current.has(mod) ? current.delete(mod) : current.add(mod)
  workerPerms.value = { ...workerPerms.value, [worker.id]: current }
  try {
    await setWorkerPermissions(worker.id, [...current])
  } catch {
    // Revert on failure
    await loadWorkerPermissions(worker)
  }
}

async function loadUsers() {
  users.value = await listUsers()
  await Promise.all(workers.value.map(loadWorkerPermissions))
}

function openCreate() {
  form.value = { full_name: '', email: '', password: '', modules: [] }
  error.value = ''
  showModal.value = true
}

async function submit() {
  saving.value = true; error.value = ''
  try {
    const workerRole = roles.value.find(r => r.name === 'farm_worker')
    const created = await createUser({ full_name: form.value.full_name, email: form.value.email, password: form.value.password, role_id: workerRole.id })
    if (form.value.modules.length) {
      await setWorkerPermissions(created.id, form.value.modules)
    }
    await loadUsers()
    showModal.value = false
  } catch (e) {
    error.value = e.response?.data?.detail || 'Failed to create worker.'
  } finally { saving.value = false }
}

async function toggleActive(w) {
  await updateUser(w.id, { is_active: !w.is_active })
  await loadUsers()
}

async function removeWorker(w) {
  if (!confirm(`Remove ${w.full_name}? This cannot be undone.`)) return
  await deleteUser(w.id)
  users.value = users.value.filter(u => u.id !== w.id)
}

onMounted(async () => {
  roles.value = await listRoles()
  await loadUsers()
  loading.value = false
})
</script>
