import { ref, computed, onUnmounted } from 'vue'
import { gameService } from '../services/gameService'
import type {
  WebSocketMessage,
  WebSocketMessageType,
  ConnectionStatus,
  MessageHandler,
  MessageHandlersMap
} from '../types'

export class WebSocketPollingManager {
  private pollingTimer: number | null = null
  private heartbeatTimer: number | null = null
  private messageHandlers: MessageHandlersMap = new Map()
  private gameId: string
  private isActive = false
  
  public status = ref<ConnectionStatus>({
    isConnected: false,
    isReconnecting: false,
    lastConnected: null,
    reconnectAttempts: 0,
    error: null
  })

  public readonly maxReconnectAttempts = 5
  public readonly pollingInterval = 3000 // 3 segundos
  public readonly heartbeatInterval = 30000

  constructor(gameId: string) {
    this.gameId = gameId
  }

  connect(): Promise<void> {
    return new Promise((resolve, reject) => {
      try {
        console.log('Starting WebSocket simulation via polling for game:', this.gameId)
        
        this.isActive = true
        this.status.value = {
          isConnected: true,
          isReconnecting: false,
          lastConnected: new Date(),
          reconnectAttempts: 0,
          error: null
        }
        
        this.startPolling()
        this.startHeartbeat()
        resolve()
        
      } catch (error) {
        console.error('Error starting polling connection:', error)
        this.status.value.error = 'No se pudo establecer la conexión'
        reject(error)
      }
    })
  }

  disconnect(): void {
    console.log('Disconnecting WebSocket polling')
    
    this.isActive = false
    
    if (this.pollingTimer) {
      clearInterval(this.pollingTimer)
      this.pollingTimer = null
    }

    this.stopHeartbeat()
    this.status.value.isConnected = false
  }

  send(message: WebSocketMessage): boolean {
    console.log('WebSocket message (simulated):', message)
    
    // Simular el envío del mensaje procesándolo localmente
    setTimeout(() => {
      this.simulateMessage(message)
    }, 100)
    
    return true
  }

  // Subscribe genérico para recibir payload tipado según WebSocketMessageMap
  subscribe<K extends WebSocketMessageType>(messageType: K, handler: MessageHandler): () => void {
    const key = messageType as WebSocketMessageType
    if (!this.messageHandlers.has(key)) {
      this.messageHandlers.set(key, [])
    }

    this.messageHandlers.get(key)!.push(handler)

    return () => {
      const handlers = this.messageHandlers.get(key)
      if (handlers) {
        const index = handlers.indexOf(handler)
        if (index > -1) {
          handlers.splice(index, 1)
        }
      }
    }
  }

  private startPolling(): void {
    this.pollingTimer = setInterval(async () => {
      if (!this.isActive) return
      
      try {
        // Obtener información actualizada del juego
        const gameData = await gameService.getGameById(this.gameId)
        
        // Simular estado de conexión de los jugadores
        const playersStatus = gameData.players.map((player: any) => ({
          playerId: player.id,
          username: player.username,
          isConnected: Math.random() > 0.3, // Simular 70% de conexión
          lastSeen: new Date()
        }))

        // Emitir actualización de estado del juego
        this.handleMessage({
          type: 'game_connection_state',
          data: {
            isUserConnected: true,
            isUserInGame: true,
            connectedPlayersCount: playersStatus.filter((p: any) => p.isConnected).length,
            totalPlayersCount: playersStatus.length,
            playersStatus: playersStatus,
            lastUpdate: new Date()
          }
        })

        // Emitir actualización de jugadores
        this.handleMessage({
          type: 'players_status_update',
          data: playersStatus
        })

      } catch (error) {
        console.error('Error in polling:', error)
        this.handleConnectionError()
      }
    }, this.pollingInterval)
  }

  private simulateMessage(message: WebSocketMessage): void {
    // Simular respuestas del servidor basadas en el tipo de mensaje
    switch (message.type) {
      case 'get_game_status':
        // Simular respuesta de estado del juego
        setTimeout(() => {
          this.handleMessage({
            type: 'game_connection_state',
            data: {
              isUserConnected: true,
              isUserInGame: true,
              connectedPlayersCount: 3,
              totalPlayersCount: 4,
              playersStatus: [],
              lastUpdate: new Date()
            }
          })
        }, 200)
        break

      case 'join_game':
        console.log('User joined game:', message.data)
        this.handleMessage({
          type: 'user_connection_status',
          data: { isConnected: true, isInGame: true }
        })
        break

      case 'player_left_game':
        console.log('Player left game:', message.data)
        break

      case 'heartbeat':
        // Simular respuesta de heartbeat si es necesario
        setTimeout(() => {
          this.handleMessage({ type: 'heartbeat' })
        }, 50)
        break
    }
  }

  private handleMessage(message: WebSocketMessage): void {
  const handlers = this.messageHandlers.get((message as any).type as WebSocketMessageType)
    if (handlers) {
      handlers.forEach(handler => {
        try {
          handler(message.data)
        } catch (error) {
          console.error(`Error in message handler for ${message.type}:`, error)
        }
      })
    }
  }

  private handleConnectionError(): void {
    this.status.value.reconnectAttempts++
    
    if (this.status.value.reconnectAttempts >= this.maxReconnectAttempts) {
      this.status.value.error = 'Se agotaron los intentos de conexión'
      this.disconnect()
    }
  }

  private startHeartbeat(): void {
    this.heartbeatTimer = setInterval(() => {
      if (this.isActive) {
        this.send({ type: 'heartbeat' })
      }
    }, this.heartbeatInterval)
  }

  private stopHeartbeat(): void {
    if (this.heartbeatTimer) {
      clearInterval(this.heartbeatTimer)
      this.heartbeatTimer = null
    }
  }
}

// Instancia global para compartir entre componentes
let wsManager: WebSocketPollingManager | null = null

export function useWebSocketPolling(gameId?: string) {
  const createConnection = () => {
    if (!gameId) {
      throw new Error('gameId is required for WebSocket connection')
    }
    
    if (wsManager) {
      wsManager.disconnect()
    }
    
    wsManager = new WebSocketPollingManager(gameId)
    return wsManager
  }

  const getConnection = () => wsManager

  const connectionStatus = computed(() => wsManager?.status.value || {
    isConnected: false,
    isReconnecting: false,
    lastConnected: null,
    reconnectAttempts: 0,
    error: null
  })

  onUnmounted(() => {
    // Cleanup será manejado por el componente principal
  })

  return {
    createConnection,
    getConnection,
    connectionStatus
  }
}
