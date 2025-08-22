import { computed } from 'vue'
import { useRouter } from 'vue-router'
import { useGameStore } from '../stores/gameStore'
import { gameService } from '../services/gameService'
import type { GamePlayer } from '../types'

/**
 * Composable que expone una API de alto nivel para que componentes y vistas interactúen
 * con el store de partida. Mantiene SRP: este archivo solo orquesta operaciones entre
 * store y servicios, sin contener lógica de negocio pesada.
 */
export function useGame() {
  const store = useGameStore()
  const router = useRouter()

  const inGame = computed(() => store.inGame)
  const players = computed(() => store.players)
  const playerIds = computed(() => store.playerIds)
  const loadingPlayers = computed(() => store.loadingPlayers)
  const loadingAction = computed(() => store.loadingAction)
  const errorMessage = computed(() => store.errorMessage)

  async function joinGame(gameId: string) {
    store.setLoadingAction(true)
    store.setError(null)
    try {
      const resp = await gameService.joinGame(gameId)
      store.setGameId(resp.game_id)
      // Cargar jugadores actuales
      const game = await gameService.getGameById(resp.game_id)
      if (game && game.players) store.setPlayers(game.players)
      return resp
    } catch (e: any) {
      store.setError(e?.message || 'Error joining game')
      throw e
    } finally {
      store.setLoadingAction(false)
    }
  }

  async function leaveGame() {
    if (!store.gameId) return null
    store.setLoadingAction(true)
    store.setError(null)
    try {
      const resp = await gameService.leaveGame(store.gameId)
      store.clear()
      try { router.push({ name: 'GamesList' }) } catch (e) { /* ignore */ }
      return resp
    } catch (e: any) {
      store.setError(e?.message || 'Error leaving game')
      throw e
    } finally {
      store.setLoadingAction(false)
    }
  }

  async function loadGamePlayers(gameId?: string) {
    const id = gameId || store.gameId
    if (!id) return [] as GamePlayer[]
    store.setLoadingPlayers(true)
    store.setError(null)
    try {
      const game = await gameService.getGameById(id)
      if (game && game.players) {
        store.setPlayers(game.players)
        return game.players
      }
      return [] as GamePlayer[]
    } catch (e: any) {
      store.setError(e?.message || 'Error loading players')
      return [] as GamePlayer[]
    } finally {
      store.setLoadingPlayers(false)
    }
  }

  async function refreshAlivePlayers() {
    if (!store.gameId) return [] as GamePlayer[]
    store.setLoadingPlayers(true)
    store.setError(null)
    try {
      const alive = await gameService.getAlivePlayers(store.gameId)
      store.setPlayers(alive)
      return alive
    } catch (e: any) {
      store.setError(e?.message || 'Error refreshing alive players')
      return [] as GamePlayer[]
    } finally {
      store.setLoadingPlayers(false)
    }
  }

  function addOrUpdatePlayer(p: GamePlayer) {
    store.addOrUpdatePlayer(p)
  }

  function removePlayer(id: string) {
    store.removePlayer(id)
  }

  async function castDayVote(targetId: string) {
    if (!store.gameId) throw new Error('Not in a game')
    store.setLoadingAction(true)
    store.setError(null)
    try {
      return await gameService.castDayVote(store.gameId, targetId)
    } catch (e: any) {
      store.setError(e?.message || 'Error casting vote')
      throw e
    } finally {
      store.setLoadingAction(false)
    }
  }

  return {
    // state
    inGame,
    players,
    playerIds,
  loadingPlayers,
  loadingAction,
  errorMessage,

    // actions
    joinGame,
    leaveGame,
    loadGamePlayers,
    refreshAlivePlayers,
    addOrUpdatePlayer,
    removePlayer,
    castDayVote,

    // direct access if needed
    rawStore: store
  }
}
