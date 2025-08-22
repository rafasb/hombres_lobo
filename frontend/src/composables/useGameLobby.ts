import { ref, computed, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/authStore'
import { gameService } from '../services/gameService'
import type { Game, User } from '../types'
import { fetchUsers, updateUserStatus } from '../services/userService'
import { useGameStore } from '../stores/gameStore'

export function useGameLobby(gameId: string) {
  const router = useRouter()
  const auth = useAuthStore()
  const gameStore = useGameStore()

  const game = ref<Game | null>(null)
  const loading = ref(false)
  const notification = ref<{ message: string, type: 'success' | 'error' } | null>(null)
  const creatorUser = ref<User | null>(null)
  const playerUsers = ref<User[]>([])

  const isCreator = computed(() => !!(auth.user && game.value && game.value.creator_id === auth.user.id))

  const isPlayerInGame = computed(() => {
    if (!auth.user || !game.value) return false
    return game.value.players.some((p: any) => (typeof p === 'string' ? p === auth.user!.id : p.id === auth.user!.id))
  })

  const canStartGame = computed(() => isCreator.value && !!game.value && game.value.players.length >= 4 && game.value.status === 'waiting')
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
    const statusMap: Record<string, string> = {
      waiting: 'Esperando jugadores',
      started: 'Iniciada',
      night: 'Fase nocturna',
      day: 'Fase diurna',
      paused: 'Pausada',
      finished: 'Finalizada'
    }
    return statusMap[game.value.status] || game.value.status
  })

  const creatorName = computed(() => {
    if (!game.value) return ''
    if (creatorUser.value) return creatorUser.value.username
    return 'Desconocido'
  })

  const loadGame = async () => {
    loading.value = true
    gameStore.setLoadingPlayers(true)
    gameStore.setError(null)
    try {
      if (auth.user && gameId) {
        try { await updateUserStatus(auth.user.id, { status: 'in_game', game_id: gameId }) } catch (e) { console.warn('No se pudo actualizar in_game', e) }
      }

      const g = await gameService.getGameById(gameId)
      game.value = g

      if (game.value) {
        const { users, error } = await fetchUsers(game.value.id || gameId)
        if (!error && users) {
          creatorUser.value = users.find(u => u.id === game.value!.creator_id) || null
          playerUsers.value = (game.value.players as any[]).map((player: any) => users.find(u => u.id === (typeof player === 'string' ? player : player.id))).filter(Boolean) as User[]

          try {
            gameStore.setGameId(game.value.id)
            const mappedPlayers = (game.value.players as any[]).map(p => (typeof p === 'string' ? { id: p, username: users.find(u => u.id === p)?.username ?? 'unknown' } : { id: p.id, username: users.find(u => u.id === p.id)?.username ?? p.username ?? 'unknown' }))
            gameStore.setPlayers(mappedPlayers)
          } catch (e) {
            console.warn('No se pudo sincronizar gameStore:', e)
          }
        } else {
          creatorUser.value = null
          playerUsers.value = []
        }
      } else {
        creatorUser.value = null
        playerUsers.value = []
      }
    } catch (err) {
      showNotification('Error al cargar la partida', 'error')
      console.error('Error loading game:', err)
      router.push('/partidas')
    } finally {
      loading.value = false
      gameStore.setLoadingPlayers(false)
    }
  }

  const joinGame = async () => {
    if (!canJoinGame.value) return
    loading.value = true
    gameStore.setLoadingAction(true)
    gameStore.setError(null)
    try {
      const resp = await gameService.joinGame(gameId)
      showNotification('Te has unido a la partida', 'success')
      gameStore.setGameId(resp.game_id)
      await loadGame()
    } catch (err) {
      showNotification('Error al unirse a la partida', 'error')
      console.error('Error joining game:', err)
    } finally {
      loading.value = false
      gameStore.setLoadingAction(false)
    }
  }

  const leaveGame = async () => {
    if (!canLeaveGame.value) return
    const confirmLeave = confirm('¿Estás seguro de que quieres abandonar la partida?')
    if (!confirmLeave) return
    loading.value = true
    gameStore.setLoadingAction(true)
    gameStore.setError(null)
    try {
      await gameService.leaveGame(gameId)
      showNotification('Has abandonado la partida', 'success')
      if (auth.user) {
        try { await updateUserStatus(auth.user.id, { status: 'active', game_id: undefined }) } catch (e) { console.warn('No se pudo actualizar el estado del usuario al salir', e) }
      }
      gameStore.clear()
      router.push('/partidas')
    } catch (err) {
      showNotification('Error al abandonar la partida', 'error')
      console.error('Error leaving game:', err)
    } finally {
      loading.value = false
      gameStore.setLoadingAction(false)
    }
  }

  const startGame = async () => {
    if (!canStartGame.value) return
    const confirmStart = confirm('¿Estás seguro de que quieres iniciar la partida? Una vez iniciada, no se podrán añadir más jugadores.')
    if (!confirmStart) return
    loading.value = true
    try {
      showNotification('Función de iniciar partida pendiente de implementar', 'error')
    } catch (err) {
      showNotification('Error al iniciar la partida', 'error')
      console.error('Error starting game:', err)
    } finally {
      loading.value = false
    }
  }

  const goBackToGames = async () => {
    if (auth.user) {
      try { await updateUserStatus(auth.user.id, { status: 'active', game_id: undefined }) } catch (e) { console.warn('No se pudo actualizar el estado del usuario al salir', e) }
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

  const showNotification = (message: string, type: 'success' | 'error') => {
    notification.value = { message, type }
    setTimeout(() => { notification.value = null }, 5000)
  }

  onUnmounted(async () => {
    if (auth.user) {
      try { await updateUserStatus(auth.user.id, { status: 'active', game_id: undefined }) } catch (e) { console.warn('No se pudo actualizar el estado del usuario al desmontar', e) }
    }
    try { gameStore.clear() } catch (e) { /* ignore */ }
  })

  return {
    game,
    loading,
    notification,
    creatorUser,
    playerUsers,
    isCreator,
    isPlayerInGame,
    canStartGame,
    canJoinGame,
    canLeaveGame,
    gameStatusText,
    creatorName,
    loadGame,
    joinGame,
    leaveGame,
    startGame,
    goBackToGames,
    formatDate
  }
}