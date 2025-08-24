import { defineStore } from 'pinia'
import type { GamePlayer } from '../types/game'
import { logoutEventBus } from './authStore'

export const usePlayerStore = defineStore('player', {
  state: () => ({
    // lista de jugadores en la partida (vacía por defecto)
    players: [] as GamePlayer[],
    loading: false,
    error: null as string | null,
  }),

  getters: {
    count: (state) => state.players.length,
    byId: (state) => (id: string) => state.players.find(p => p.id === id) as GamePlayer | undefined,
  },

  actions: {
    setPlayers(list: GamePlayer[]) {
      this.players = list.slice()
    },
    addOrUpdate(player: GamePlayer) {
      const idx = this.players.findIndex(p => p.id === player.id)
      if (idx === -1) this.players.push(player)
      else this.players.splice(idx, 1, { ...this.players[idx], ...player })
    },
    remove(id: string) {
      this.players = this.players.filter(p => p.id !== id)
    },
    setLoading(v: boolean) {
      this.loading = v
    },
    setError(msg: string | null) {
      this.error = msg
    },
    clear() {
      this.players = []
      this.loading = false
      this.error = null
    }
  }
})

// limpiar store al hacer logout global
logoutEventBus.on(() => {
  try {
    const s = usePlayerStore()
    s.clear()
  } catch (e) {
    // noop
  }
})

export default usePlayerStore
