import { ref, computed } from 'vue'
import { useUserStatusOnView } from './useUserStatus'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/authStore'
import { gameService } from '../services/gameService'
import type { Game } from '../types'

export function useGamesList() {
  // Actualizar estado del usuario a 'active' al entrar en la vista, salvo si está 'banned'
  useUserStatusOnView('active')
  const router = useRouter()
  const auth = useAuthStore()
  
  // Estado reactivo
  const games = ref<Game[]>([])
  const loading = ref(false)
  const showCreateModal = ref(false)
  const notification = ref<{ message: string, type: 'success' | 'error' } | null>(null)
  
  const newGame = ref({
    name: '',
    maxPlayers: 8
  })

  // Opciones para número de jugadores
  const playerOptions = Array.from({ length: 22 }, (_, i) => i + 4) // De 4 a 25 jugadores

  // Computed properties
  const hasGames = computed(() => games.value.length > 0)
  
  // Métodos de carga
  const loadGames = async () => {
    try {
      loading.value = true
      games.value = await gameService.getGames()
    } catch (error) {
      showNotification('Error al cargar las partidas', 'error')
      console.error('Error loading games:', error)
    } finally {
      loading.value = false
    }
  }

  // Métodos de gestión de partidas
  const createGame = async () => {
    if (!auth.user) return
    
    try {
      loading.value = true
      await gameService.createGame(newGame.value.name, newGame.value.maxPlayers, auth.user.id)
      showNotification('Partida creada correctamente', 'success')
      closeCreateModal()
      await loadGames()
    } catch (error) {
      showNotification('Error al crear la partida', 'error')
      console.error('Error creating game:', error)
    } finally {
      loading.value = false
    }
  }

  const joinGame = async (gameId: string) => {
    try {
      loading.value = true
      await gameService.joinGame(gameId)
      showNotification('Te has unido a la partida', 'success')
      await loadGames()
    } catch (error) {
      showNotification('Error al unirse a la partida', 'error')
      console.error('Error joining game:', error)
    } finally {
      loading.value = false
    }
  }

  const leaveGame = async (gameId: string) => {
    try {
      loading.value = true
      await gameService.leaveGame(gameId)
      showNotification('Has abandonado la partida', 'success')
      await loadGames()
    } catch (error) {
      showNotification('Error al abandonar la partida', 'error')
      console.error('Error leaving game:', error)
    } finally {
      loading.value = false
    }
  }

  const deleteGame = async (gameId: string) => {
    if (!auth.user) return
    
    // Verificar que el usuario tenga permisos (admin o creador de la partida)
    const game = games.value.find(g => g.id === gameId)
    if (!game) return
    
    if (!auth.isAdmin && game.creator_id !== auth.user.id) {
      showNotification('No tienes permisos para eliminar esta partida', 'error')
      return
    }
    
    const confirmDelete = confirm('¿Estás seguro de que quieres eliminar esta partida? Esta acción no se puede deshacer.')
    if (!confirmDelete) return
    
    try {
      loading.value = true
      await gameService.deleteGame(gameId)
      showNotification('Partida eliminada correctamente', 'success')
      await loadGames()
    } catch (error) {
      showNotification('Error al eliminar la partida', 'error')
      console.error('Error deleting game:', error)
    } finally {
      loading.value = false
    }
  }

  const viewGame = (gameId: string) => {
    router.push(`/partida/${gameId}`)
  }

  // Métodos de validación
  const canJoinGame = (game: Game): boolean => {
    if (!auth.user) return false
    if (game.status !== 'waiting') return false
    if (game.players.length >= game.max_players) return false
    return !game.players.some(player => player.id === auth.user!.id)
  }

  const canLeaveGame = (game: Game): boolean => {
    if (!auth.user) return false
    if (game.status !== 'waiting') return false
    return game.players.some(player => player.id === auth.user!.id)
  }

  const canViewGame = (game: Game): boolean => {
    if (!auth.user) return false
    return game.players.some(player => player.id === auth.user!.id)
  }

  const canDeleteGame = (game: Game): boolean => {
    if (!auth.user) return false
    return auth.isAdmin || game.creator_id === auth.user.id
  }

  // Métodos de utilidad
  const getCreatorName = (game: Game): string => {
    const creator = game.players.find(player => player.id === game.creator_id)
    return creator?.username || 'Desconocido'
  }

  const getStatusText = (status: string): string => {
    const statusMap: { [key: string]: string } = {
      'waiting': 'Esperando',
      'started': 'Iniciada',
      'night': 'Noche',
      'day': 'Día',
      'paused': 'Pausada',
      'finished': 'Finalizada'
    }
    return statusMap[status] || status
  }

  const getGameCardClass = (status: string): string => {
    return `game-card-${status}`
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

  // Métodos del modal
  const closeCreateModal = () => {
    showCreateModal.value = false
    newGame.value = {
      name: '',
      maxPlayers: 8
    }
  }

  const openCreateModal = () => {
    showCreateModal.value = true
  }

  // Método de notificaciones
  const showNotification = (message: string, type: 'success' | 'error') => {
    notification.value = { message, type }
    setTimeout(() => {
      notification.value = null
    }, 5000)
  }

  const updateNewGame = (gameData: { name: string, maxPlayers: number }) => {
    newGame.value = gameData
  }

  return {
    // Estado
    games,
    loading,
    showCreateModal,
    notification,
    newGame,
    playerOptions,
    hasGames,
    auth,
    
    // Métodos
    loadGames,
    createGame,
    joinGame,
    leaveGame,
    deleteGame,
    viewGame,
    canJoinGame,
    canLeaveGame,
    canViewGame,
    canDeleteGame,
    getCreatorName,
    getStatusText,
    getGameCardClass,
    formatDate,
    closeCreateModal,
    openCreateModal,
    showNotification,
    updateNewGame
  }
}
