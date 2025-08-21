import { onMounted } from 'vue'
import { useAuthStore } from '../stores/authStore'
import { updateUserStatus } from '../services/userService'

/**
 * Hook para actualizar el estado del usuario al entrar en una vista.
 * @param status Estado al que actualizar ('active', 'in_game', etc)
 */
export function useUserStatusOnView(status: string) {
  const auth = useAuthStore()
  onMounted(async () => {
    // Si el usuario está baneado, no actualizar
    if (auth.user && (auth.user as any).status !== 'banned') {
      try {
        await updateUserStatus(auth.user.id, { status })
      } catch (e) {
        console.warn(`No se pudo actualizar el estado del usuario a ${status}`, e)
      }
    }
  })
}
