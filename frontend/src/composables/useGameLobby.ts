import { ref, computed, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/authStore'
import { gameService } from '../services/gameService'
import type { Game } from '../types'
import { fetchUsers, updateUserStatus } from '../services/userService'

export function useGameLobby(gameId: string) {
  const router = useRouter()
  const auth = useAuthStore()
  
  // Estado reactivo
  const game = ref<Game | null>(null)
  const loading = ref(false)
  const notification = ref<{ message: string, type: 'success' | 'error' } | null>(null)
  const creatorUser = ref<any | null>(null)
  const playerUsers = ref<any[]>([])

  // Computed properties
  const isCreator = computed(() => {
    return auth.user && game.value && game.value.creator_id === auth.user.id
  })

  const isPlayerInGame = computed(() => {
    return auth.user && game.value && game.value.players.includes(auth.user)
  })

  const canStartGame = computed(() => {
    return isCreator.value && game.value && game.value.players.length >= 4 && game.value.status === 'waiting'
  })

  const canJoinGame = computed(() => {
    if (!auth.user || !game.value) return false
    if (game.value.status !== 'waiting') return false
    if (game.value.players.length >= game.value.max_players) return false
    return !isPlayerInGame.value
  })

  const canLeaveGame = computed(() => {
    if (!auth.user || !game.value) return false
    if (game.value.status !== 'waiting') return false
    return isPlayerInGame.value && !isCreator.value
  })

  const gameStatusText = computed(() => {
    if (!game.value) return ''
    
    const statusMap: { [key: string]: string } = {
      'waiting': 'Esperando jugadores',
      'started': 'Iniciada',
      'night': 'Fase nocturna',
      'day': 'Fase diurna',
      'paused': 'Pausada',
      'finished': 'Finalizada'
    }
    return statusMap[game.value.status] || game.value.status
  })

  const creatorName = computed(() => {
    if (!game.value) return ''
    if (creatorUser.value) return creatorUser.value.username
    return 'Desconocido'
  })

  // Métodos
  const loadGame = async () => {
    try {
      loading.value = true
      // Notificar a la API que el usuario está en la partida (estado in_game)
      if (auth.user && gameId) {
        try {
          await updateUserStatus(auth.user.id, { status: 'in_game', game_id: gameId })
        } catch (e) {
          // No bloquear la carga si falla, pero mostrar advertencia
          console.warn('No se pudo actualizar el estado del usuario a in_game', e)
        }
      }
      game.value = await gameService.getGameById(gameId)
      // Obtener datos de usuarios (creador y jugadores)
      if (game.value) {
        const { users, error } = await fetchUsers()
        if (error) {
          creatorUser.value = null
          playerUsers.value = []
        } else {
          creatorUser.value = users?.find((u: any) => u.id === game.value!.creator_id) || null
          playerUsers.value = (game.value.players as any[]).map(
            (player: any) => users?.find((u: any) => u.id === (typeof player === 'string' ? player : player.id))
          ).filter(Boolean)
        }
      } else {
        creatorUser.value = null
        playerUsers.value = []
      }
    } catch (error) {
      showNotification('Error al cargar la partida', 'error')
      console.error('Error loading game:', error)
      router.push('/partidas')
    } finally {
      loading.value = false
    }
  }

  const joinGame = async () => {
    if (!canJoinGame.value) return
    
    try {
      loading.value = true
      await gameService.joinGame(gameId)
      showNotification('Te has unido a la partida', 'success')
      await loadGame() // Recargar datos de la partida
    } catch (error) {
      showNotification('Error al unirse a la partida', 'error')
      console.error('Error joining game:', error)
    } finally {
      loading.value = false
    }
  }

  const leaveGame = async () => {
    if (!canLeaveGame.value) return
    
    const confirmLeave = confirm('¿Estás seguro de que quieres abandonar la partida?')
    if (!confirmLeave) return
    
    try {
      loading.value = true
      await gameService.leaveGame(gameId)
      showNotification('Has abandonado la partida', 'success')
      // Actualizar estado del usuario al salir de la partida
      if (auth.user) {
        try {
          await updateUserStatus(auth.user.id, { status: 'active', game_id: undefined })
        } catch (e) {
          console.warn('No se pudo actualizar el estado del usuario al salir', e)
        }
      }
      router.push('/partidas')
    } catch (error) {
      showNotification('Error al abandonar la partida', 'error')
      console.error('Error leaving game:', error)
    } finally {
      loading.value = false
    }
  }

  const startGame = async () => {
    if (!canStartGame.value) return
    
    const confirmStart = confirm('¿Estás seguro de que quieres iniciar la partida? Una vez iniciada, no se podrán añadir más jugadores.')
    if (!confirmStart) return
    
    try {
      loading.value = true
      // TODO: Implementar startGame en el servicio cuando esté disponible
      showNotification('Función de iniciar partida pendiente de implementar', 'error')
    } catch (error) {
      showNotification('Error al iniciar la partida', 'error')
      console.error('Error starting game:', error)
    } finally {
      loading.value = false
    }
  }

  const goBackToGames = async () => {
    // Actualizar estado del usuario al salir de la vista de partida
    if (auth.user) {
      try {
        await updateUserStatus(auth.user.id, { status: 'active', game_id: undefined })
      } catch (e) {
        console.warn('No se pudo actualizar el estado del usuario al salir', e)
      }
    }
    router.push('/partidas')
  }

  const formatDate = (dateString: string): string => {
    const date = new Date(dateString)
    return date.toLocaleDateString('es-ES', {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    })
  }

  // Método de notificaciones
  const showNotification = (message: string, type: 'success' | 'error') => {
    notification.value = { message, type }
    setTimeout(() => {
      notification.value = null
    }, 5000)
  }

  // Limpiar estado al desmontar el componente
  onUnmounted(async () => {
    if (auth.user) {
      try {
        await updateUserStatus(auth.user.id, { status: 'active', game_id: undefined })
      } catch (e) {
        console.warn('No se pudo actualizar el estado del usuario al desmontar', e)
      }
    }
  })

  return {
    // Estado
    game,
    loading,
    notification,
    creatorUser,
    playerUsers,
    // Computed
    isCreator,
    isPlayerInGame,
    canStartGame,
    canJoinGame,
    canLeaveGame,
    gameStatusText,
    creatorName,
    // Métodos
    loadGame,
    joinGame,
    leaveGame,
    startGame,
    goBackToGames,
    formatDate
  }
}
