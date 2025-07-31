import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import api from '../services/api'
import { useAuthStore } from './auth'

// Interfaces basadas en el backend confirmado
interface User {
  id: string
  username: string
  email: string
  role: 'admin' | 'player'
  status: 'active' | 'inactive' | 'banned'
  hashed_password: string
  created_at: string
  updated_at: string
}

interface RoleInfo {
  role: string
  is_alive: boolean
  is_revealed: boolean
  model_player_id?: string | null
  has_transformed?: boolean | null
  has_healing_potion?: boolean | null
  has_poison_potion?: boolean | null
  has_double_vote?: boolean | null
  can_break_ties?: boolean | null
  successor_id?: string | null
  can_revenge_kill?: boolean | null
  has_used_revenge?: boolean | null
  has_used_vision_tonight?: boolean | null
  is_cupid?: boolean | null
  is_lover?: boolean | null
  lover_partner_id?: string | null
  has_acted_tonight?: boolean | null
  target_player_id?: string | null
}

interface Game {
  id: string
  name: string
  creator_id: string
  max_players: number
  players: User[]
  status: 'waiting' | 'started' | 'night' | 'day' | 'paused' | 'finished'
  roles: Record<string, RoleInfo>
  created_at: string
  current_round: number
  is_first_night: boolean
  night_actions?: Record<string, Record<string, string>>
  day_votes?: Record<string, string>
}

interface GameCreate {
  name: string
  max_players: number  // Entre 4 y 24 jugadores
  creator_id: string
}

export const useGamesStore = defineStore('games', () => {
  // Acceso al store de autenticación
  const authStore = useAuthStore()

  // Estado reactivo
  const games = ref<Game[]>([])
  const currentGame = ref<Game | null>(null)
  const isLoading = ref(false)
  const error = ref<string>('')

  // Computed
  const availableGames = computed(() => {
    const userRole = authStore.user?.role

    if (userRole === 'admin') {
      // Los administradores pueden ver todos los juegos
      return games.value
    } else {
      // Los jugadores normales solo ven juegos disponibles para unirse
      return games.value.filter(game => game.status === 'waiting')
    }
  })

  const myGames = computed(() => {
    const userId = getCurrentUserId()
    return games.value.filter(game =>
      game.creator_id === userId ||
      game.players.some(player => player.id === userId)
    )
  })

  const isInGame = computed(() => !!currentGame.value)

  const isGameHost = computed(() => {
    if (!currentGame.value) return false
    const userId = getCurrentUserId()
    return currentGame.value.creator_id === userId
  })

  const currentGamePlayers = computed(() =>
    currentGame.value?.players || []
  )

  const canStartGame = computed(() => {
    if (!currentGame.value || !isGameHost.value) return false
    return currentGame.value.players.length >= 4 &&
           currentGame.value.status === 'waiting'
  })

  // Helper para obtener ID del usuario actual
  function getCurrentUserId(): string {
    // Implementación temporal - en producción vendría del auth store
    const authStore = JSON.parse(localStorage.getItem('auth') || '{}')
    return authStore.user?.id || ''
  }

  // Acciones
  const fetchGames = async () => {
    try {
      isLoading.value = true
      error.value = ''

      const response = await api.get<Game[]>('/games')
      games.value = response.data

      return true
    } catch (err: any) {
      error.value = err.response?.data?.detail || 'Error al cargar los juegos'
      return false
    } finally {
      isLoading.value = false
    }
  }

  const createGame = async (gameData: Omit<GameCreate, 'creator_id'>) => {
    try {
      isLoading.value = true
      error.value = ''

      const createData: GameCreate = {
        ...gameData,
        creator_id: getCurrentUserId()
      }

      const response = await api.post<Game>('/games', createData)
      const newGame = response.data

      // Agregar el nuevo juego a la lista
      games.value.unshift(newGame)

      // Establecer como juego actual
      currentGame.value = newGame

      return newGame
    } catch (err: any) {
      error.value = err.response?.data?.detail || 'Error al crear el juego'
      throw err
    } finally {
      isLoading.value = false
    }
  }

  const joinGame = async (gameId: string) => {
    try {
      isLoading.value = true
      error.value = ''

      await api.post(`/games/${gameId}/join`)

      // Recargar los datos del juego
      await fetchGameDetails(gameId)

      return true
    } catch (err: any) {
      error.value = err.response?.data?.detail || 'Error al unirse al juego'
      return false
    } finally {
      isLoading.value = false
    }
  }

  const leaveGame = async (gameId: string) => {
    try {
      isLoading.value = true
      error.value = ''

      await api.post(`/games/${gameId}/leave`)

      // Si era el juego actual, limpiarlo
      if (currentGame.value?.id === gameId) {
        currentGame.value = null
      }

      // Actualizar la lista de juegos
      await fetchGames()

      return true
    } catch (err: any) {
      error.value = err.response?.data?.detail || 'Error al abandonar el juego'
      return false
    } finally {
      isLoading.value = false
    }
  }

  const fetchGameDetails = async (gameId: string) => {
    try {
      isLoading.value = true
      error.value = ''

      const response = await api.get<Game>(`/games/${gameId}`)
      const gameDetails = response.data

      // Actualizar el juego en la lista
      const gameIndex = games.value.findIndex(g => g.id === gameId)
      if (gameIndex !== -1) {
        games.value[gameIndex] = gameDetails
      }

      // Si es el juego actual, actualizarlo
      if (currentGame.value?.id === gameId) {
        currentGame.value = gameDetails
      }

      return gameDetails
    } catch (err: any) {
      error.value = err.response?.data?.detail || 'Error al cargar detalles del juego'
      throw err
    } finally {
      isLoading.value = false
    }
  }

  const startGame = async (gameId: string) => {
    try {
      isLoading.value = true
      error.value = ''

      const response = await api.post<Game>(`/games/${gameId}/assign-roles`)
      const updatedGame = response.data

      // Actualizar el juego
      if (currentGame.value?.id === gameId) {
        currentGame.value = updatedGame
      }

      // Actualizar en la lista
      const gameIndex = games.value.findIndex(g => g.id === gameId)
      if (gameIndex !== -1) {
        games.value[gameIndex] = updatedGame
      }

      return updatedGame
    } catch (err: any) {
      error.value = err.response?.data?.detail || 'Error al iniciar el juego'
      throw err
    } finally {
      isLoading.value = false
    }
  }

  const updateGameSettings = async (gameId: string, settings: Partial<Game>) => {
    try {
      isLoading.value = true
      error.value = ''

      const response = await api.put<Game>(`/games/${gameId}`, settings)
      const updatedGame = response.data

      // Actualizar el juego
      if (currentGame.value?.id === gameId) {
        currentGame.value = updatedGame
      }

      // Actualizar en la lista
      const gameIndex = games.value.findIndex(g => g.id === gameId)
      if (gameIndex !== -1) {
        games.value[gameIndex] = updatedGame
      }

      return updatedGame
    } catch (err: any) {
      error.value = err.response?.data?.detail || 'Error al actualizar configuración'
      throw err
    } finally {
      isLoading.value = false
    }
  }

  const deleteGame = async (gameId: string) => {
    try {
      isLoading.value = true
      error.value = ''

      await api.delete(`/games/${gameId}`)

      // Remover de la lista
      games.value = games.value.filter(g => g.id !== gameId)

      // Si era el juego actual, limpiarlo
      if (currentGame.value?.id === gameId) {
        currentGame.value = null
      }

      return true
    } catch (err: any) {
      error.value = err.response?.data?.detail || 'Error al eliminar el juego'
      return false
    } finally {
      isLoading.value = false
    }
  }

  const setCurrentGame = (game: Game | null) => {
    currentGame.value = game
  }

  const clearError = () => {
    error.value = ''
  }

  // Función para actualizar datos en tiempo real (se usará más adelante)
  const refreshCurrentGame = async () => {
    if (currentGame.value) {
      await fetchGameDetails(currentGame.value.id)
    }
  }

  return {
    // Estado
    games,
    currentGame,
    isLoading,
    error,

    // Computed
    availableGames,
    myGames,
    isInGame,
    isGameHost,
    currentGamePlayers,
    canStartGame,

    // Acciones
    fetchGames,
    createGame,
    joinGame,
    leaveGame,
    fetchGameDetails,
    startGame,
    updateGameSettings,
    deleteGame,
    setCurrentGame,
    clearError,
    refreshCurrentGame
  }
})
