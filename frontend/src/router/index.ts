import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import LoginView from '../views/LoginView.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'home',
      redirect: '/dashboard'
    },
    {
      path: '/login',
      name: 'login',
      component: LoginView,
      meta: { guest: true }
    },
    {
      path: '/register',
      name: 'register',
      component: () => import('../views/RegisterView.vue'),
      meta: { guest: true }
    },
    {
      path: '/dashboard',
      name: 'dashboard',
      component: () => import('../views/DashboardView.vue'),
      meta: { requiresAuth: true }
    },
    {
      path: '/games',
      name: 'games',
      component: () => import('../views/GamesView.vue'),
      meta: { requiresAuth: true }
    },
    {
      path: '/games/:gameId',
      name: 'game-lobby',
      component: () => import('../views/GameLobbyView.vue'),
      meta: { requiresAuth: true }
    },
    {
      path: '/games/:gameId/view',
      name: 'game-view',
      component: () => import('../views/GameLobbyView.vue'),
      meta: { requiresAuth: true },
      props: { viewOnly: true }
    },
    {
      path: '/test-websocket',
      name: 'test-websocket',
      component: () => import('../components/WebSocketTest.vue'),
      meta: { requiresAuth: true }
    }
  ]
})

// Guard de navegación
router.beforeEach(async (to, from, next) => {
  const authStore = useAuthStore()

  // Asegurar que el store está inicializado
  if (!authStore.isInitialized) {
    await authStore.initialize()
  }

  if (to.meta.requiresAuth && !authStore.isAuthenticated) {
    next('/login')
  } else if (to.meta.guest && authStore.isAuthenticated) {
    next('/dashboard')
  } else {
    next()
  }
})

export default router
