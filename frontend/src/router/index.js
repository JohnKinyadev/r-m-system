import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const routes = [
  {
    path: '/login',
    name: 'login',
    component: () => import('@/views/auth/LoginView.vue'),
    meta: { public: true },
  },
  {
    path: '/',
    component: () => import('@/components/layout/AppLayout.vue'),
    meta: { requiresAuth: true },
    children: [
      { path: '', redirect: '/dashboard' },
      { path: 'dashboard',        name: 'dashboard',       component: () => import('@/views/dashboard/DashboardView.vue') },
      { path: 'animals',          name: 'animals',         component: () => import('@/views/animals/AnimalsListView.vue'),      meta: { module: 'animals' } },
      { path: 'animals/new',      name: 'animals-new',     component: () => import('@/views/animals/AnimalFormView.vue'),       meta: { module: 'animals' } },
      { path: 'animals/:id',      name: 'animal-detail',   component: () => import('@/views/animals/AnimalDetailView.vue'),     meta: { module: 'animals' } },
      { path: 'animals/:id/edit', name: 'animal-edit',     component: () => import('@/views/animals/AnimalFormView.vue'),       meta: { module: 'animals' } },
      { path: 'livestock-types',  name: 'livestock-types', component: () => import('@/views/livestock/LivestockTypesView.vue'), meta: { module: 'livestock_types' } },
      { path: 'feed',             name: 'feed',            component: () => import('@/views/feed/FeedView.vue'),                meta: { module: 'feed' } },
      { path: 'health',           name: 'health',          component: () => import('@/views/health/HealthView.vue'),            meta: { module: 'health' } },
      { path: 'mating',           name: 'mating',          component: () => import('@/views/mating/MatingView.vue'),            meta: { module: 'mating' } },
      { path: 'reports',          name: 'reports',         component: () => import('@/views/reports/ReportsView.vue'),          meta: { module: 'reports' } },
      { path: 'notifications',    name: 'notifications',   component: () => import('@/views/notifications/NotificationsView.vue') },
      { path: 'workers',          name: 'workers',         component: () => import('@/views/workers/WorkersView.vue'),          meta: { ownerOnly: true } },
      { path: 'profile',          name: 'profile',         component: () => import('@/views/profile/ProfileView.vue') },
    ],
  },
  { path: '/:pathMatch(.*)*', redirect: '/' },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

router.beforeEach((to) => {
  const auth = useAuthStore()

  if (to.meta.requiresAuth && !auth.isLoggedIn) {
    return { name: 'login', query: { redirect: to.fullPath } }
  }
  if (to.meta.public && auth.isLoggedIn) {
    return { name: 'dashboard' }
  }
  if (to.meta.ownerOnly && !auth.isOwner) {
    return { name: 'dashboard' }
  }
  // Module-level guard: workers without the module are redirected to dashboard
  if (to.meta.module && !auth.isOwner && !auth.hasModule(to.meta.module)) {
    return { name: 'dashboard' }
  }
})

export default router
