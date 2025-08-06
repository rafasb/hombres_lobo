import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/authStore'
import { login as authLogin } from '../services/authService'

export function useLogin() {
  const username = ref('')
  const password = ref('')
  const error = ref('')
  const loading = ref(false)
  const redirected = ref(false)
  const router = useRouter()
  const auth = useAuthStore()

  // Verificar si el usuario fue redirigido
  if (window.history.state && window.history.state.redirected) {
    redirected.value = true
  }

  const onLogin = async () => {
    error.value = ''
    loading.value = true
    
    try {
      const result = await authLogin(username.value, password.value)
      if (result && result.access_token) {
        router.push('/partidas')
      } else if (result && result.error) {
        error.value = result.error
        auth.logout()
      }
    } catch (err) {
      error.value = 'Error de conexión. Inténtalo de nuevo.'
      auth.logout()
    }
    
    loading.value = false
  }

  const navigateToRegister = () => {
    router.push('/register')
  }

  return {
    // Estado
    username,
    password,
    error,
    loading,
    redirected,
    // Métodos
    onLogin,
    navigateToRegister
  }
}
