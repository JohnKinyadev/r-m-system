<template>
  <div class="min-h-screen flex flex-col items-center justify-center px-4 relative overflow-hidden"
       style="background: url('/images/farm-bg.svg') center/cover no-repeat, #1a5c2a">
    <div class="absolute inset-0 bg-black/50 pointer-events-none" />

    <div class="relative z-10 w-full max-w-sm">
      <!-- Logo -->
      <div class="text-center mb-8">
        <div class="inline-flex items-center justify-center w-16 h-16 bg-farm-600 rounded-2xl mb-4">
          <svg class="w-9 h-9 text-white" fill="currentColor" viewBox="0 0 24 24">
            <path d="M12 2L2 7l10 5 10-5-10-5zm0 7L2 14l10 5 10-5-10-5z"/>
          </svg>
        </div>
        <h1 class="text-2xl font-bold text-white">FarmManager</h1>
        <p class="text-farm-300 text-sm mt-1">Ranch & Livestock Edition</p>
      </div>

      <!-- Offline banner — shown above the form when there's no connection -->
      <div v-if="!isOnline"
           class="flex items-center gap-3 bg-amber-500/90 text-white text-sm px-4 py-3 rounded-xl mb-4 shadow">
        <svg class="w-5 h-5 flex-shrink-0" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
          <line x1="1" y1="1" x2="23" y2="23"/>
          <path d="M16.72 11.06A10.94 10.94 0 0119 12.55M5 12.55a10.94 10.94 0 015.17-2.39M10.71 5.05A16 16 0 0122.56 9M1.42 9a15.91 15.91 0 014.7-2.88M8.53 16.11a6 6 0 016.95 0M12 20h.01"/>
        </svg>
        <p>
          <strong>You're offline.</strong>
          Sign-in requires an internet connection.
          <span v-if="hadPriorSession">Reconnect to continue.</span>
        </p>
      </div>

      <!-- Form card -->
      <div class="bg-white rounded-2xl shadow-xl p-6">
        <h2 class="text-lg font-semibold text-gray-800 mb-5">Sign in to your farm</h2>

        <BaseAlert :message="error" type="error" class="mb-4" />

        <form @submit.prevent="handleLogin" class="space-y-4">
          <BaseInput
            v-model="form.email"
            label="Email"
            type="email"
            placeholder="owner@farm.local"
            required
            :disabled="!isOnline"
          />
          <BaseInput
            v-model="form.password"
            label="Password"
            type="password"
            placeholder="••••••••"
            required
            :disabled="!isOnline"
          />
          <BaseButton
            type="submit"
            :loading="loading"
            :disabled="!isOnline"
            class="w-full mt-2"
          >
            {{ isOnline ? 'Sign in' : 'Offline — cannot sign in' }}
          </BaseButton>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useOnlineStatus } from '@/composables/useOnlineStatus'
import BaseInput from '@/components/ui/BaseInput.vue'
import BaseButton from '@/components/ui/BaseButton.vue'
import BaseAlert from '@/components/ui/BaseAlert.vue'

const auth = useAuthStore()
const router = useRouter()
const route = useRoute()
const { isOnline } = useOnlineStatus()

const form = ref({ email: '', password: '' })
const loading = ref(false)
const error = ref('')

// True if there's a stale token in storage — user was previously signed in
const hadPriorSession = computed(() => !!localStorage.getItem('token'))

async function handleLogin() {
  if (!isOnline.value) {
    error.value = 'Sign-in requires an internet connection.'
    return
  }
  error.value = ''
  loading.value = true
  try {
    await auth.login(form.value.email, form.value.password)
    router.push(route.query.redirect || '/dashboard')
  } catch (e) {
    if (e.isOffline) {
      error.value = 'No internet connection. Please reconnect and try again.'
    } else {
      error.value = e.response?.data?.detail || 'Login failed. Check your credentials.'
    }
  } finally {
    loading.value = false
  }
}
</script>
