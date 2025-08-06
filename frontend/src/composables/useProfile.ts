import { computed } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/authStore'

export function useProfile() {
  const router = useRouter()
  const auth = useAuthStore()

  const handleLogout = () => {
    auth.logout()
    router.push('/login')
  }

  const roleClass = computed(() => {
    return auth.user?.role === 'admin' ? 'role-admin' : 'role-player'
  })

  const roleText = computed(() => {
    return auth.user?.role === 'admin' ? 'Administrador' : 'Jugador'
  })

  const navigateToGames = () => {
    router.push('/partidas')
  }

  const navigateToAdmin = () => {
    router.push('/admin')
  }

  const navigateToLogin = () => {
    router.push('/login')
  }

  return {
    auth,
    handleLogout,
    roleClass,
    roleText,
    navigateToGames,
    navigateToAdmin,
    navigateToLogin
  }
}
