/**
 * Composable específico para permisos del lobby
 * Responsabilidad única: Calcular qué acciones puede realizar el usuario
 * Sigue SRP (Single Responsibility Principle) e ISP (Interface Segregation)
 */
import { computed, type Ref } from 'vue'
import type { Game } from '../types'
import type { GameLobbyPermissions } from '../interfaces/GameLobbyInterfaces'
import { useAuthStore } from '../stores/authStore'

export function useGameLobbyPermissions(game: Ref<Game | null>): GameLobbyPermissions {
  const auth = useAuthStore()

  // Computed properties para permisos (reactivo a cambios en game)
  const isCreator = computed(() => {
    return !!(auth.user && game.value && game.value.creator_id === auth.user.id)
  })

  const isPlayerInGame = computed(() => {
    return !!(auth.user && game.value && game.value.players.some(
      (player: any) => (typeof player === 'string' ? player : player.id) === auth.user!.id
    ))
  })

  const canStartGame = computed(() => {
    if (!isCreator.value || !game.value) return false
    return game.value.players.length >= 4 && game.value.status === 'waiting'
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

  // Retornar como objeto que implementa la interface
  return {
    isCreator,
    isPlayerInGame,
    canStartGame,
    canJoinGame,
    canLeaveGame
  } satisfies GameLobbyPermissions
}
