import { computed, onUnmounted } from 'vue'
import { gameService } from '../services/gameService'
import { useWebSocket } from './WebSocketManager'
import { BaseWebSocketManager } from './BaseWebSocketManager'
import type {
  WebSocketMessage,
  WebSocketMessageType,
  MessageHandler
} from '../types'

export class WebSocketPollingManager extends BaseWebSocketManager {
  private pollingTimer: number | null = null
  private gameId: string
  private token?: string
  private isActive = false
  private simulate = false

  // Real WebSocketManager instance (when not simulating)
  private realManager: any | null = null

  public readonly pollingInterval = 3000 // 3 segundos

  // constructor allows enabling simulation or passing token
  constructor(gameId: string, options?: { simulate?: boolean; token?: string }) {
    super()
    this.gameId = gameId
    this.simulate = !!options?.simulate
    this.token = options?.token
  }

  connect(): Promise<void> {
    if (this.simulate) {
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

    return new Promise(async (resolve, reject) => {
      try {
        const ws = useWebSocket(this.gameId)
        this.realManager = ws.createConnection(this.token)

        // Mirror status ref to the real manager's status so UI reactivity is preserved
        this.status = this.realManager.status

        await this.realManager.connect()

        resolve()
      } catch (error) {
        console.error('Error creating real WebSocket connection:', error)
        this.status.value.error = 'No se pudo establecer la conexión'
        reject(error)
      }
    })
  }

  disconnect(): void {
    console.log('Disconnecting WebSocket polling/manager')

    this.isActive = false

    if (this.realManager) {
      try {
        this.realManager.disconnect()
      } catch (e) {
        console.warn('Error while disconnecting real manager', e)
      }
      this.realManager = null
      this.status.value = {
        isConnected: false,
        isReconnecting: false,
        lastConnected: null,
        reconnectAttempts: 0,
        error: null
      }
      return
    }

    if (this.pollingTimer) {
      clearInterval(this.pollingTimer)
      this.pollingTimer = null
    }

    this.stopHeartbeat()
    this.status.value.isConnected = false
  }

  send(message: WebSocketMessage): boolean {
    if (this.realManager) {
      return this.realManager.send(message)
    }

    console.log('WebSocket message (simulated):', message)

    setTimeout(() => {
      this.simulateMessage(message)
    }, 100)

    return true
  }

  subscribe<K extends WebSocketMessageType>(messageType: K, handler: MessageHandler<any>): () => void {
    if (this.realManager) {
      return this.realManager.subscribe(messageType as any, handler as any)
    }
    return super.subscribe(messageType, handler)
  }

  private startPolling(): void {
    this.pollingTimer = setInterval(async () => {
      if (!this.isActive) return
      
      try {
        const gameData = await gameService.getGameById(this.gameId)
        
        const playersStatus = gameData.players.map((player: any) => ({
          playerId: player.id,
          username: player.username,
          isConnected: Math.random() > 0.3,
          lastSeen: new Date()
        }))

        this.dispatchMessage({
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

        this.dispatchMessage({
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
    switch (message.type) {
      case 'get_game_status':
        setTimeout(() => {
          this.dispatchMessage({
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
        this.dispatchMessage({
          type: 'user_connection_status',
          data: { isConnected: true, isInGame: true }
        })
        break

      case 'player_left_game':
        console.log('Player left game:', message.data)
        break
    }
  }

  private handleConnectionError(): void {
    this.status.value.reconnectAttempts++
    
    if (this.status.value.reconnectAttempts >= this.maxReconnectAttempts) {
      this.status.value.error = 'Se agotaron los intentos de conexión'
      this.disconnect()
    }
  }

  // Override heartbeat to respect `isActive` for polling/simulation
  protected startHeartbeat(): void {
    this.stopHeartbeat()
    this.heartbeatTimer = setInterval(() => {
      if (this.isActive || this.realManager) {
        try {
          this.send({ type: 'heartbeat' })
        } catch {
          // ignore
        }
      }
    }, this.heartbeatInterval)
  }

  protected stopHeartbeat(): void {
    if (this.heartbeatTimer) {
      clearInterval(this.heartbeatTimer)
      this.heartbeatTimer = null
    }
  }
}

// Instancia global para compartir entre componentes
let wsManager: WebSocketPollingManager | null = null

export function useWebSocketPolling(gameId?: string) {
  const createConnection = (options?: { token?: string; simulate?: boolean }) => {
    if (!gameId) {
      throw new Error('gameId is required for WebSocket connection')
    }

    if (wsManager) {
      wsManager.disconnect()
    }

    wsManager = new WebSocketPollingManager(gameId, options)
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
