/**
 * Composable específico para el estado del lobby
 * Responsabilidad única: Gestionar el estado básico (loading, notifications)
 * Sigue SRP (Single Responsibility Principle)
 */
import { ref, type Ref } from 'vue'
import type { GameNotification } from '../interfaces/GameLobbyInterfaces'
import type { Game } from '../types'

export function useGameLobbyState() {
  // Estado reactivo
  const game = ref<Game | null>(null)
  const loading = ref(false)
  const error = ref<string | null>(null)
  const notification = ref<GameNotification | null>(null)

  // Métodos para modificar el estado
  const setGame = (newGame: Game | null) => {
    game.value = newGame
    // Limpiar error cuando se carga correctamente
    if (newGame) {
      error.value = null
    }
  }

  const setLoading = (isLoading: boolean) => {
    loading.value = isLoading
  }

  const setError = (errorMessage: string | null) => {
    error.value = errorMessage
  }

  const showNotification = (message: string, type: 'success' | 'error') => {
    notification.value = { message, type }
    setTimeout(() => {
      notification.value = null
    }, 5000)
  }

  const clearNotification = () => {
    notification.value = null
  }

  return {
    // Estado reactivo
    game: game as Ref<Game | null>,
    loading: loading as Ref<boolean>,
    error: error as Ref<string | null>,
    notification: notification as Ref<GameNotification | null>,
    // Métodos
    setGame,
    setLoading,
    setError,
    showNotification,
    clearNotification
  }
}
