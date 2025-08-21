/**
 * Composable específico para gestionar usuarios del lobby
 * Responsabilidad única: Cargar y gestionar información de usuarios
 * Sigue SRP (Single Responsibility Principle)
 */
import { ref, type Ref } from 'vue'
import type { Game, User } from '../types'
import { fetchUsers } from '../services/userService'

export function useGameLobbyUsers() {
  // Estado reactivo
  const creatorUser = ref<User | null>(null)
  const playerUsers = ref<User[]>([])

  // Cargar información de usuarios basada en la partida
  const loadUsers = async (game: Game | null) => {
    if (!game) {
      creatorUser.value = null
      playerUsers.value = []
      return
    }

    try {
      const { users, error } = await fetchUsers()
      
      if (error) {
        creatorUser.value = null
        playerUsers.value = []
        return
      }

      // Buscar el usuario creador
      creatorUser.value = users?.find((u: any) => u.id === game.creator_id) || null

      // Mapear jugadores con sus datos de usuario y filtrar los undefined
      playerUsers.value = (game.players as any[]).map(
        (player: any) => users?.find((u: any) => u.id === (typeof player === 'string' ? player : player.id))
      ).filter((u): u is User => u !== undefined)

    } catch (error) {
      console.error('Error loading users:', error)
      creatorUser.value = null
      playerUsers.value = []
    }
  }

  // Método para actualizar usuarios después de cambios en la partida
  const refreshUsers = async (game: Game | null) => {
    await loadUsers(game)
  }

  return {
    // Estado reactivo
    creatorUser: creatorUser as Ref<User | null>,
    playerUsers: playerUsers as Ref<User[]>,
    // Métodos
    loadUsers,
    refreshUsers
  }
}
