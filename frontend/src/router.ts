import { createRouter, createWebHistory } from 'vue-router'
import Login from './components/Login.vue'
import Register from './components/Register.vue'
import Profile from './components/Profile.vue'
import AdminView from './views/AdminView.vue'
import GamesList from './components/GamesList.vue'
import GameLobby from './components/GameLobby.vue'
import { useAuthStore } from './stores/authStore'

const routes = [
  { path: '/login', component: Login },
  { path: '/register', component: Register },
  { path: '/perfil', component: Profile },
  { path: '/admin', component: AdminView },
  { path: '/partidas', component: GamesList },
  { path: '/partida/:id', component: GameLobby },
  { path: '/', redirect: '/partidas' },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

router.beforeEach((to, _from, next) => {
  const auth = useAuthStore()
  if ((to.path === '/perfil' || to.path === '/partidas' || to.path.startsWith('/partida/')) && !auth.isAuthenticated) {
    next({ path: '/login', state: { redirected: true } })
  } else if (to.path === '/admin' && (!auth.isAuthenticated || !auth.isAdmin)) {
    next({ path: '/login', state: { redirected: true } })
  } else {
    next()
  }
})

export default router
