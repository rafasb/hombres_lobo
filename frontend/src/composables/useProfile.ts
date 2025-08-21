import { computed } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/authStore'

export function useProfile() {
  const router = useRouter()
  const auth = useAuthStore()

  const goToLogin = (logout = true) => {
    if (logout) auth.logout()
    router.push('/login')
  }

  const roleClass = computed(() => {
    return auth.user?.role === 'admin' ? 'bg-danger' : 'bg-primary'
  })

  const roleText = computed(() => {
    return auth.user?.role === 'admin' ? 'Administrador' : 'Jugador'
  })



  return {
    auth,
    goToLogin,
    roleClass,
    roleText
  }
}
