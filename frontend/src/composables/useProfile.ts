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


  const roleMap = {
    admin: { class: 'bg-danger', text: 'Administrador' },
    player: { class: 'bg-primary', text: 'Jugador' }
  }

  const roleClass = computed(() => {
    return roleMap[auth.user?.role as 'admin' | 'player']?.class || 'bg-secondary'
  })

  const roleText = computed(() => {
    return roleMap[auth.user?.role as 'admin' | 'player']?.text || 'Desconocido'
  })



  return {
    auth,
    goToLogin,
    roleClass,
    roleText
  }
}
