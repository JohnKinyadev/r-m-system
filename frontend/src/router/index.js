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
      { path: 'dashboard',     name: 'dashboard',     component: () => import('@/views/dashboard/DashboardView.vue') },
      { path: 'properties',    name: 'properties',    component: () => import('@/views/properties/PropertiesView.vue'),    meta: { module: 'properties' } },
      { path: 'units',         name: 'units',         component: () => import('@/views/units/UnitsView.vue'),              meta: { module: 'units' } },
      { path: 'tenants',       name: 'tenants',       component: () => import('@/views/tenants/TenantsView.vue'),          meta: { module: 'tenants' } },
      { path: 'rent',          name: 'rent',          component: () => import('@/views/rent/RentView.vue'),                meta: { module: 'rent' } },
      { path: 'payments',      name: 'payments',      component: () => import('@/views/payments/PaymentsView.vue'),        meta: { module: 'payments' } },
      { path: 'maintenance',   name: 'maintenance',   component: () => import('@/views/maintenance/MaintenanceView.vue'),  meta: { module: 'maintenance' } },
      { path: 'expenses',      name: 'expenses',      component: () => import('@/views/expenses/ExpensesView.vue'),        meta: { module: 'expenses' } },
      { path: 'reports',       name: 'reports',       component: () => import('@/views/reports/ReportsView.vue'),          meta: { module: 'reports' } },
      { path: 'notifications', name: 'notifications', component: () => import('@/views/notifications/NotificationsView.vue') },
      { path: 'caretakers',    name: 'caretakers',    component: () => import('@/views/workers/WorkersView.vue'),          meta: { ownerOnly: true } },
      { path: 'profile',       name: 'profile',       component: () => import('@/views/profile/ProfileView.vue') },
    ],
  },
  { path: '/:pathMatch(.*)*', redirect: '/' },
]

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
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
