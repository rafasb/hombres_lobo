/**
 * Composable específico para acciones del lobby
 * Responsabilidad única: Gestionar las acciones que puede realizar el usuario
 * Sigue SRP (Single Responsibility Principle) y DIP (Dependency Inversion)
 */
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/authStore'
import { gameService } from '../services/gameService'
import { updateUserStatus } from '../services/userService'
import type { Game } from '../types'
import type { ComputedRef } from 'vue'

export function useGameLobbyActions(
  gameId: string,
  canJoinGame: ComputedRef<boolean>,
  canLeaveGame: ComputedRef<boolean>,
  canStartGame: ComputedRef<boolean>,
  setGame: (game: Game | null) => void,
  setLoading: (loading: boolean) => void,
  setError: (error: string | null) => void,
  showNotification: (message: string, type: 'success' | 'error') => void,
  refreshUsers: (game: Game | null) => Promise<void>
) {
  const router = useRouter()
  const auth = useAuthStore()

  // Cargar datos completos de la partida
  const loadGame = async () => {
    console.log('[loadGame] INICIO');
    try {
      setLoading(true)
      setError(null) // Limpiar errores previos
      console.log('[loadGame] setLoading(true) y setError(null)');
      // Notificar a la API que el usuario está en la partida
      if (auth.user && gameId) {
        try {
          console.log('[loadGame] updateUserStatus', auth.user.id, gameId);
          await updateUserStatus(auth.user.id, { status: 'in_game', game_id: gameId })
          console.log('[loadGame] updateUserStatus OK');
        } catch (e) {
          console.warn('[loadGame] No se pudo actualizar el estado del usuario a in_game', e)
        }
      }
      console.log('[loadGame] Antes de gameService.getGameById', gameId);
      const gameData = await gameService.getGameById(gameId)
      console.log('[loadGame] gameService.getGameById OK', gameData);
      setGame(gameData)
      console.log('[loadGame] setGame OK');
      // Cargar usuarios después de cargar la partida
      await refreshUsers(gameData)
      console.log('[loadGame] refreshUsers OK');
    } catch (error: any) {
      const errorMessage = error?.response?.data?.detail || error?.message || 'Error desconocido al cargar la partida'
      setError(errorMessage)
      showNotification('Error al cargar la partida', 'error')
      console.error('[loadGame] Error loading game:', error)
      // Solo redirigir si es un error 404 (partida no encontrada)
      if (error?.response?.status === 404) {
        router.push('/partidas')
      }
    } finally {
      setLoading(false)
      console.log('[loadGame] setLoading(false) FIN');
    }
  }

  // Unirse a la partida
  const joinGame = async () => {
    if (!canJoinGame.value) return
    
    try {
      setLoading(true)
      setError(null)
      await gameService.joinGame(gameId)
      showNotification('Te has unido a la partida', 'success')
      await loadGame() // Recargar datos
    } catch (error: any) {
      const errorMessage = error?.response?.data?.detail || error?.message || 'Error al unirse a la partida'
      setError(errorMessage)
      showNotification('Error al unirse a la partida', 'error')
      console.error('Error joining game:', error)
    } finally {
      setLoading(false)
    }
  }

  // Abandonar la partida
  const leaveGame = async () => {
    if (!canLeaveGame.value) return
    
    const confirmLeave = confirm('¿Estás seguro de que quieres abandonar la partida?')
    if (!confirmLeave) return
    
    try {
      setLoading(true)
      setError(null)
      await gameService.leaveGame(gameId)
      showNotification('Has abandonado la partida', 'success')
      
      // Actualizar estado del usuario al salir
      if (auth.user) {
        try {
          await updateUserStatus(auth.user.id, { status: 'online', game_id: undefined })
        } catch (e) {
          console.warn('No se pudo actualizar el estado del usuario al salir', e)
        }
      }
      
      router.push('/partidas')
    } catch (error: any) {
      const errorMessage = error?.response?.data?.detail || error?.message || 'Error al abandonar la partida'
      setError(errorMessage)
      showNotification('Error al abandonar la partida', 'error')
      console.error('Error leaving game:', error)
    } finally {
      setLoading(false)
    }
  }

  // Iniciar la partida (solo creador)
  const startGame = async () => {
    if (!canStartGame.value) return
    
    const confirmStart = confirm(
      '¿Estás seguro de que quieres iniciar la partida? ' +
      'Una vez iniciada, no se podrán añadir más jugadores.'
    )
    if (!confirmStart) return
    
    try {
      setLoading(true)
      setError(null)
      // TODO: Implementar startGame en el servicio cuando esté disponible
      showNotification('Función de iniciar partida pendiente de implementar', 'error')
    } catch (error: any) {
      const errorMessage = error?.response?.data?.detail || error?.message || 'Error al iniciar la partida'
      setError(errorMessage)
      showNotification('Error al iniciar la partida', 'error')
      console.error('Error starting game:', error)
    } finally {
      setLoading(false)
    }
  }

  return {
    loadGame,
    joinGame,
    leaveGame,
    startGame
  }
}
