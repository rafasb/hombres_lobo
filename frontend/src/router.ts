import { createRouter, createWebHistory } from 'vue-router'
import Login from './components/Login.vue'
import Profile from './components/Profile.vue'
import Admin from './components/Admin.vue'
import { useAuthStore } from './stores/authStore'

const routes = [
  { path: '/login', component: Login },
  { path: '/perfil', component: Profile },
  { path: '/admin', component: Admin },
  { path: '/', redirect: '/login' },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

router.beforeEach((to, from, next) => {
  const auth = useAuthStore()
  if (to.path === '/perfil' && !auth.isAuthenticated) {
    next({ path: '/login', state: { redirected: true } })
  } else if (to.path === '/admin' && (!auth.isAuthenticated || !auth.isAdmin)) {
    next({ path: '/login', state: { redirected: true } })
  } else {
    next()
  }
})

export default router
