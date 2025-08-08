import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/authStore'

export function useNavigation() {
  const router = useRouter()
  const auth = useAuthStore()

  const navigateToGames = () => {
    router.push('/partidas')
  }

  const navigateToProfile = () => {
    router.push('/perfil')
  }

  const navigateToAdmin = () => {
    if (auth.isAdmin) {
      router.push('/admin')
    }
  }

  const handleNavigation = (view: string) => {
    switch (view) {
      case 'games':
        navigateToGames()
        break
      case 'profile':
        navigateToProfile()
        break
      case 'admin':
        navigateToAdmin()
        break
    }
  }

  return {
    navigateToGames,
    navigateToProfile,
    navigateToAdmin,
    handleNavigation,
    isAdmin: auth.isAdmin
  }
}
