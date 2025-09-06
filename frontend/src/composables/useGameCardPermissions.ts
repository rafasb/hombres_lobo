import { computed, toRef } from 'vue'
import { useAuthStore } from '../stores/authStore'
import type { Game, GameSummary } from '../types'

// Union type para aceptar tanto Game completo como GameSummary
type GameCardData = Game | GameSummary

export function useGameCardPermissions(gameRef: GameCardData) {
  const auth = useAuthStore()
  
  // Convertir el prop en una ref reactiva
  const game = toRef(() => gameRef)

  const canJoinGame = computed(() => {
    if (!auth.user) return false
    if (game.value.status !== 'waiting') return false
    
    // Obtener el número actual de jugadores según el tipo
    let currentPlayers = 0
    if ('current_players' in game.value) {
      currentPlayers = game.value.current_players
    } else if ('players' in game.value && typeof game.value.players === 'object') {
      currentPlayers = Object.keys(game.value.players).length
    } else if ('player_ids' in game.value && Array.isArray(game.value.player_ids)) {
      currentPlayers = game.value.player_ids.length
    }
    
    if (currentPlayers >= game.value.max_players) return false
    // Verificar que el usuario no esté ya en la partida
    if (game.value.player_ids && game.value.player_ids.includes(auth.user.id)) return false
    return true
  })

  const canLeaveGame = computed(() => {
    if (!auth.user) return false
    if (game.value.status !== 'waiting') return false
    // Verificar que el usuario esté en la partida y no sea el creador
    if (!game.value.player_ids || !game.value.player_ids.includes(auth.user.id)) return false
    if (game.value.creator_id === auth.user.id) return false
    return true
  })

  const canViewGame = computed(() => {
    if (!auth.user) return false
    // Verificar que el usuario esté en la partida o sea administrador
    if (auth.isAdmin) return true
    if (game.value.player_ids && game.value.player_ids.includes(auth.user.id)) return true
    return false
  })

  const canDeleteGame = computed(() => {
    if (!auth.user) return false
    // Usar creator_id directamente de GameSummary para verificar permisos
    return auth.isAdmin || game.value.creator_id === auth.user.id
  })

  return {
    canJoinGame,
    canLeaveGame,
    canViewGame,
    canDeleteGame
  }
}
