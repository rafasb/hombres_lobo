import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { register as registerService } from '../services/registerService'

export function useRegister() {
  const username = ref('')
  const email = ref('')
  const password = ref('')
  const confirmPassword = ref('')
  const error = ref('')
  const success = ref('')
  const loading = ref(false)
  const router = useRouter()

  const onRegister = async () => {
    error.value = ''
    success.value = ''
    
    // Validaciones del lado del cliente
    if (password.value !== confirmPassword.value) {
      error.value = 'Las contraseñas no coinciden'
      return
    }
    
    if (password.value.length < 6) {
      error.value = 'La contraseña debe tener al menos 6 caracteres'
      return
    }
    
    loading.value = true
    const result = await registerService(username.value, email.value, password.value)
    
    if (result && result.success) {
      success.value = 'Usuario registrado correctamente. Redirigiendo al login...'
      // Redirigir al login después de 2 segundos
      setTimeout(() => {
        router.push('/login')
      }, 2000)
    } else if (result && result.error) {
      error.value = result.error
    }
    loading.value = false
  }

  return {
    username,
    email,
    password,
    confirmPassword,
    error,
    success,
    loading,
    onRegister
  }
}
