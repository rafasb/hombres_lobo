import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/authStore'
import { gameService, type Game } from '../services/gameService'

export function useGameLobby(gameId: string) {
  const router = useRouter()
  const auth = useAuthStore()
  
  // Estado reactivo
  const game = ref<Game | null>(null)
  const loading = ref(false)
  const notification = ref<{ message: string, type: 'success' | 'error' } | null>(null)

  // Computed properties
  const isCreator = computed(() => {
    return auth.user && game.value && game.value.creator_id === auth.user.id
  })

  const isPlayerInGame = computed(() => {
    return auth.user && game.value && game.value.players.some(player => player.id === auth.user!.id)
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
    const creator = game.value.players.find(player => player.id === game.value!.creator_id)
    return creator?.username || 'Desconocido'
  })

  // Métodos
  const loadGame = async () => {
    try {
      loading.value = true
      game.value = await gameService.getGameById(gameId)
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

  const goBackToGames = () => {
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

  return {
    // Estado
    game,
    loading,
    notification,
    
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
