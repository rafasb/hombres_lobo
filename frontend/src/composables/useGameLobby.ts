/**
 * Composable principal refactorizado siguiendo principios SOLID
 * Aplica Composition Pattern en lugar de un composable monolítico
 * Sigue SRP, ISP, OCP y DIP
 */
import { onMounted, onUnmounted } from 'vue'
import { useAuthStore } from '../stores/authStore'
import { updateUserStatus } from '../services/userService'

// Importar composables específicos
import { useGameLobbyState } from './useGameLobbyState'
import { useGameLobbyUsers } from './useGameLobbyUsers'
import { useGameLobbyPermissions } from './useGameLobbyPermissions'
import { useGameLobbyDisplayInfo } from './useGameLobbyDisplayInfo'
import { useGameLobbyActions } from './useGameLobbyActions'

export function useGameLobby(gameId: string) {
  const auth = useAuthStore()

  // Composables específicos (cada uno con una responsabilidad)
  const { 
    game, 
    loading, 
    error,
    notification, 
    setGame, 
    setLoading, 
    setError,
    showNotification, 
    clearNotification 
  } = useGameLobbyState()

  const { 
    creatorUser, 
    playerUsers, 
    refreshUsers 
  } = useGameLobbyUsers()

  const permissions = useGameLobbyPermissions(game)

  const displayInfo = useGameLobbyDisplayInfo(game, creatorUser)

  const actions = useGameLobbyActions(
    gameId,
    permissions.canJoinGame,
    permissions.canLeaveGame,
    permissions.canStartGame,
    setGame,
    setLoading,
    setError,
    showNotification,
    refreshUsers
  )

  // Inicialización al montar el componente
  onMounted(async () => {
    await actions.loadGame()
  })

  // Limpieza al desmontar
  onUnmounted(async () => {
    if (auth.user) {
      try {
        await updateUserStatus(auth.user.id, { status: 'online', game_id: undefined })
      } catch (e) {
        console.warn('No se pudo actualizar el estado del usuario al desmontar', e)
      }
    }
  })

  // Retornar interface bien estructurada siguiendo ISP
  return {
    // Estado básico
    state: {
      game,
      loading,
      error,
      notification
    },
    
    // Usuarios
    users: {
      creatorUser,
      playerUsers
    },
    
    // Permisos (computed properties reactivos)
    permissions: {
      isCreator: permissions.isCreator,
      isPlayerInGame: permissions.isPlayerInGame,
      canStartGame: permissions.canStartGame,
      canJoinGame: permissions.canJoinGame,
      canLeaveGame: permissions.canLeaveGame
    },
    
    // Información para mostrar
    displayInfo: {
      gameStatusText: displayInfo.gameStatusText,
      creatorName: displayInfo.creatorName
    },
    
    // Acciones disponibles
    actions: {
      loadGame: actions.loadGame,
      joinGame: actions.joinGame,
      leaveGame: actions.leaveGame,
      startGame: actions.startGame,
      formatDate: displayInfo.formatDate
    },
    
    // Métodos adicionales de estado
    helpers: {
      showNotification,
      clearNotification,
      refreshUsers
    }
  }
}
