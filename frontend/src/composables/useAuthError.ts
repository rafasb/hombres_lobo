import { ref } from 'vue'
import { useAuthStore } from '../stores/authStore'

/**
 * Composable para gestión de errores de formularios de autenticación.
 */
export function useAuthError() {
  const error = ref('')
  const auth = useAuthStore()

  const setError = (msg: string, doLogout = false) => {
    error.value = msg
    if (doLogout) {
      auth.logout()
    }
  }

  const clearError = () => {
    error.value = ''
  }

  return {
    error,
    setError,
    clearError
  }
}
