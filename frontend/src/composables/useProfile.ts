import { computed } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/authStore'

export function useProfile() {
  const isAdmin = computed(() => user?.role === 'admin')
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

  const roleInfo = computed(() => {
    return roleMap[auth.user?.role as 'admin' | 'player'] || { class: 'bg-secondary', text: 'Desconocido' }
  })



  const user = auth.user
  const username = computed(() => user?.username || '')
  const role = computed(() => user?.role || '')

  return {
    user,
    username,
    role,
    isAdmin,
    goToLogin,
    roleInfo
  }
}
