<template>
  <RouterView />
  <AppUpdateBanner />
  <ToastContainer />
</template>

<script setup>
import { RouterView } from 'vue-router'
import { onMounted } from 'vue'
import { useAuthStore } from '@/stores/auth'
import AppUpdateBanner from '@/components/AppUpdateBanner.vue'
import ToastContainer from '@/components/ToastContainer.vue'

const auth = useAuthStore()

onMounted(() => {
  auth.initFromStorage()
})
</script>
