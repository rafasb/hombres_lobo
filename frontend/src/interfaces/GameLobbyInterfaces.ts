/**
 * Interfaces para GameLobbyView siguiendo el Interface Segregation Principle (ISP)
 * Cada interface tiene una responsabilidad específica y bien definida
 */
import type { ComputedRef } from 'vue'
import type { Game } from '../types'

// Notificación del sistema
export interface GameNotification {
  message: string
  type: 'success' | 'error'
}

// Estado básico del lobby de la partida
export interface GameLobbyState {
  game: Game | null
  loading: boolean
  notification: GameNotification | null
}

// Información de usuarios en el lobby
export interface GameLobbyUsers {
  creatorUser: any | null
  playerUsers: any[]
}

// Permisos y capacidades del usuario actual
export interface GameLobbyPermissions {
  isCreator: ComputedRef<boolean>
  isPlayerInGame: ComputedRef<boolean>
  canStartGame: ComputedRef<boolean>
  canJoinGame: ComputedRef<boolean>
  canLeaveGame: ComputedRef<boolean>
}

// Información derivada para mostrar en la UI
export interface GameLobbyDisplayInfo {
  gameStatusText: string
  creatorName: string
}

// Acciones disponibles para el usuario
export interface GameLobbyActions {
  loadGame: () => Promise<void>
  joinGame: () => Promise<void>
  leaveGame: () => Promise<void>
  startGame: () => Promise<void>
  formatDate: (dateString: string) => string
}

// Información de conexión WebSocket
export interface GameConnectionInfo {
  connectionStatus: string
  connectionStatusText: string
  connectionStatusClass: string
  isUserActiveInLobby: boolean
  connectionHealthText: string
}

// Información de un jugador específico
export interface PlayerInfo {
  id: string
  username: string
  isCreator: boolean
  isCurrentUser: boolean
  isConnected: boolean
  lastSeen?: Date
}

// Interface principal que combina todo para la vista (composición)
export interface GameLobbyViewModel {
  state: GameLobbyState
  users: GameLobbyUsers
  permissions: GameLobbyPermissions
  displayInfo: GameLobbyDisplayInfo
  actions: GameLobbyActions
  connection: GameConnectionInfo
}
