import { ref } from 'vue'
import { useAuthError } from './useAuthError'
import { useRouter } from 'vue-router'
import { login as authLogin } from '../services/authService'

export function useLogin() {
  const username = ref('')
  const password = ref('')
  const { error, setError, clearError } = useAuthError()
  const loading = ref(false)
  const redirected = ref(false)
  const router = useRouter()


  // Verificar si el usuario fue redirigido
  if (window.history.state && window.history.state.redirected) {
    redirected.value = true
  }

  const onLogin = async () => {
    clearError()
    loading.value = true
    try {
      const result = await authLogin(username.value, password.value)
      if (result && result.access_token) {
        router.push('/partidas')
      } else if (result && result.error) {
        setError(result.error, true)
      }
    } catch (err) {
      setError('Error de conexión. Inténtalo de nuevo.', true)
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
