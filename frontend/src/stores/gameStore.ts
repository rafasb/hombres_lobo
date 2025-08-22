import { defineStore } from 'pinia'
import type { GamePlayer } from '../types'
import { logoutEventBus } from './authStore'

/**
 * Store para gestionar la información de la partida cuando el usuario está dentro de una partida.
 * Principios SOLID aplicados de forma pragmática:
 * - Single Responsibility: este store solo gestiona el estado de la partida en cliente.
 * - Dependency Inversion: dependemos de la abstracción `logoutEventBus` para limpiar estado al logout.
 * - Open/Closed: el store expone acciones que permiten extensión sin cambiar su implementación interna.
 */
export const useGameStore = defineStore('game', {
  state: () => ({
    gameId: '' as string, // id de la partida a la que pertenece el usuario
    // players contiene los demás jugadores (excluye al usuario local si es necesario)
    players: [] as GamePlayer[],
    // Flags y mensajes para manejo de carga/errores desde la UI
    loadingPlayers: false,
    loadingAction: false,
    errorMessage: null as string | null,
  }),

  getters: {
    inGame(state) {
      return state.gameId !== ''
    },
    // Devuelve solo los ids de los jugadores
    playerIds: (state) => state.players.map(p => p.id),
    // Mapa rápido id -> jugador
    playersById: (state) => state.players.reduce<Record<string, GamePlayer>>((acc, p) => {
      acc[p.id] = p
      return acc
    }, {}),
  },

  actions: {
    setGameId(id: string) {
      this.gameId = id
    },

    setPlayers(players: GamePlayer[]) {
      // Reemplaza la lista completa de jugadores
      this.players = players.slice()
    },

    addOrUpdatePlayer(player: GamePlayer) {
      const idx = this.players.findIndex(p => p.id === player.id)
      if (idx === -1) {
        this.players.push(player)
      } else {
        // Mantener inmutabilidad parcial: reemplazar el objeto en su posición
        this.players.splice(idx, 1, { ...this.players[idx], ...player })
      }
    },

    removePlayer(playerId: string) {
      this.players = this.players.filter(p => p.id !== playerId)
    },

    updatePlayerStatus(playerId: string, partial: Partial<GamePlayer>) {
      const idx = this.players.findIndex(p => p.id === playerId)
      if (idx !== -1) {
        this.players.splice(idx, 1, { ...this.players[idx], ...partial })
      }
    },

    // Flags y errores
    setLoadingPlayers(v: boolean) {
      this.loadingPlayers = v
    },
    setLoadingAction(v: boolean) {
      this.loadingAction = v
    },
    setError(message: string | null) {
      this.errorMessage = message
    },

    clear() {
      this.gameId = ''
      this.players = []
      this.loadingPlayers = false
      this.loadingAction = false
      this.errorMessage = null
    }
  }
})

// Limpiar el store cuando se hace logout globalmente
// Se usa una suscripción ligera para mantener separación de responsabilidades
const unsubscribe = logoutEventBus.on(() => {
  try {
    const store = useGameStore()
    store.clear()
  } catch (e) {
    // Ignorar si se ejecuta fuera de un contexto activo de Pinia
    // (por ejemplo durante tests o en servidor)
  }
})

export { unsubscribe as unsubscribeGameStoreOnLogout }
