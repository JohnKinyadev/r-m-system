<template>
  <div class="max-w-lg mx-auto space-y-4">

    <!-- User card -->
    <div class="bg-white rounded-2xl shadow-sm p-6 text-center">
      <div class="w-20 h-20 rounded-full bg-farm-700 text-white text-2xl font-bold
                  flex items-center justify-center mx-auto mb-4">
        {{ initials }}
      </div>
      <h2 class="text-xl font-bold text-gray-900">{{ auth.user?.full_name }}</h2>
      <p class="text-gray-500 text-sm mt-0.5">{{ auth.user?.email }}</p>
      <span class="inline-block mt-2 px-3 py-1 bg-farm-100 text-farm-700 text-xs font-semibold rounded-full">
        {{ roleLabel }}
      </span>
      <p class="text-xs text-gray-400 mt-3">Member since {{ memberSince }}</p>
    </div>

    <!-- Change password -->
    <div class="bg-white rounded-2xl shadow-sm p-6">
      <h3 class="font-semibold text-gray-800 mb-4">Change Password</h3>

      <BaseAlert :message="pwError"   type="error"   class="mb-3" />
      <BaseAlert :message="pwSuccess" type="success" class="mb-3" />

      <form @submit.prevent="handlePasswordChange" class="space-y-4">
        <BaseInput
          v-model="pw.current"
          label="Current password"
          type="password"
          placeholder="••••••••"
          required
        />
        <BaseInput
          v-model="pw.newPw"
          label="New password"
          type="password"
          placeholder="Min. 8 characters"
          required
        />
        <BaseInput
          v-model="pw.confirm"
          label="Confirm new password"
          type="password"
          placeholder="••••••••"
          required
        />
        <BaseButton type="submit" :loading="pwLoading" class="w-full">
          Update Password
        </BaseButton>
      </form>
    </div>

    <!-- Sign out -->
    <div class="bg-white rounded-2xl shadow-sm p-6">
      <h3 class="font-semibold text-gray-800 mb-1">Account</h3>
      <p class="text-sm text-gray-500 mb-4">You will be signed out on all tabs.</p>
      <button
        @click="auth.logout()"
        class="w-full py-3 px-4 bg-red-50 text-red-600 font-medium rounded-xl
               hover:bg-red-100 active:bg-red-200 transition-colors
               flex items-center justify-center gap-2"
      >
        <svg class="w-4 h-4" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
          <path d="M9 21H5a2 2 0 01-2-2V5a2 2 0 012-2h4"/>
          <polyline points="16 17 21 12 16 7"/>
          <line x1="21" y1="12" x2="9" y2="12"/>
        </svg>
        Sign out
      </button>
    </div>

  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { changePassword } from '@/api/users'
import BaseInput from '@/components/ui/BaseInput.vue'
import BaseButton from '@/components/ui/BaseButton.vue'
import BaseAlert from '@/components/ui/BaseAlert.vue'

const auth = useAuthStore()

const initials = computed(() => {
  const name = auth.user?.full_name || ''
  return name.split(' ').map(w => w[0]).slice(0, 2).join('').toUpperCase()
})

const roleLabel = computed(() =>
  auth.user?.role?.name === 'farm_owner' ? 'Farm Owner' : 'Farm Worker'
)

const memberSince = computed(() => {
  const d = auth.user?.created_at
  if (!d) return '—'
  return new Date(d).toLocaleDateString('en-KE', { year: 'numeric', month: 'long' })
})

const pw = ref({ current: '', newPw: '', confirm: '' })
const pwLoading = ref(false)
const pwError   = ref('')
const pwSuccess = ref('')

async function handlePasswordChange() {
  pwError.value   = ''
  pwSuccess.value = ''

  if (pw.value.newPw !== pw.value.confirm) {
    pwError.value = 'New passwords do not match.'
    return
  }
  if (pw.value.newPw.length < 8) {
    pwError.value = 'Password must be at least 8 characters.'
    return
  }

  pwLoading.value = true
  try {
    await changePassword({ current_password: pw.value.current, new_password: pw.value.newPw })
    pwSuccess.value = 'Password updated successfully.'
    pw.value = { current: '', newPw: '', confirm: '' }
  } catch (e) {
    pwError.value = e.response?.data?.detail || 'Failed to update password.'
  } finally {
    pwLoading.value = false
  }
}
</script>
