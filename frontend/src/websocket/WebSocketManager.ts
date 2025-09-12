/// La función principal de WebSocketManager es manejar una conexión WebSocket
/// con el backend para recibir actualizaciones del estado del juego y del usuario.
/// Solo envía respuestas de heartbeat cuando el backend lo solicita.
/// Todas las demás interacciones del usuario (unirse a juego, cambiar estado, etc.)
/// deben hacerse vía llamadas API REST normales, no mediante mensajes WebSocket.
///
/// Key behaviors:
/// - Only receives messages from backend
/// - Only sends heartbeat responses when requested by backend
/// - All other user interactions should use API calls, not WebSocket messages
import { computed, onUnmounted } from 'vue'
import { BaseWebSocketManager } from './BaseWebSocketManager'
import { useUserStore } from '../stores/userStore'
import type {
  GameWebSocketMessage
} from '../types'

/**
 * WebSocket Manager implementation that extends BaseWebSocketManager
 * 
 * Key behaviors:
 * - Only receives messages from backend
 * - Only sends heartbeat responses when requested by backend
 * - All other user interactions should use API calls, not WebSocket messages
 */
export class WebSocketManager extends BaseWebSocketManager {
  private ws: WebSocket | null = null
  private reconnectTimer: number | null = null

  private url: string
  private token?: string

  public readonly reconnectDelay = 3000

  constructor(url: string, token?: string) {
    super()
    this.url = url
    this.token = token
  }

  connect(): Promise<void> {
    return new Promise((resolve, reject) => {
      try {
        const wsUrl = this.token
          ? `${this.url}?token=${encodeURIComponent(this.token)}`
          : this.url

        this.ws = new WebSocket(wsUrl)

        this.ws.onopen = () => {
          console.log('WebSocket connected')
          this.status.value = {
            isConnected: true,
            isReconnecting: false,
            lastConnected: new Date(),
            reconnectAttempts: 0,
            error: null
          }
          
          // Actualizar el estado en userStore
          try {
            const userStore = useUserStore()
            userStore.setWebSocketConnected(true)
            console.log('[WebSocket] Estado actualizado en userStore: connected')
          } catch (error) {
            console.warn('[WebSocket] No se pudo actualizar userStore:', error)
          }
          
          resolve()
        }

        this.ws.onclose = (event) => {
          console.log('WebSocket closed:', event)
          this.status.value.isConnected = false
          this.stopHeartbeatResponse()

          // Actualizar el estado en userStore
          try {
            const userStore = useUserStore()
            userStore.setWebSocketConnected(false)
            console.log('[WebSocket] Estado actualizado en userStore: disconnected')
          } catch (error) {
            console.warn('[WebSocket] No se pudo actualizar userStore:', error)
          }

          if (!event.wasClean && this.status.value.reconnectAttempts < this.maxReconnectAttempts) {
            this.attemptReconnect()
          }
        }

        this.ws.onerror = (error) => {
          console.error('WebSocket error:', error)
          this.status.value.error = 'Error de conexión WebSocket'
          reject(error)
        }

        this.ws.onmessage = (event) => {
          // Solo procesar mensajes que tengan un campo "type"
          try {
            const parsed = JSON.parse(event.data)
            if (parsed && typeof parsed.type === 'string') {
              const message = parsed as GameWebSocketMessage
              this.dispatchMessage(message)
              console.log('[Websocket] Received WebSocket message:', message)
            } else {
              console.warn('Received WebSocket message without type:', parsed)
            }
          } catch (error) {
            console.error('Error parsing WebSocket message:', error)
          }
        }

      } catch (error) {
        console.error('Error creating WebSocket connection:', error)
        this.status.value.error = 'No se pudo establecer la conexión'
        reject(error)
      }
    })
  }

  disconnect(): void {
    if (this.reconnectTimer) {
      clearTimeout(this.reconnectTimer)
      this.reconnectTimer = null
    }

    this.stopHeartbeatResponse()
    this.cleanup()

    if (this.ws) {
      this.ws.close(1000, 'Client disconnect')
      this.ws = null
    }

    this.status.value.isConnected = false
    
    // Actualizar el estado en userStore
    try {
      const userStore = useUserStore()
      userStore.setWebSocketConnected(false)
      console.log('[WebSocket] Estado actualizado en userStore: disconnected (manual)')
    } catch (error) {
      console.warn('[WebSocket] No se pudo actualizar userStore:', error)
    }
  }

  /**
   * Send heartbeat response - the ONLY message the frontend should send
   */
  protected sendHeartbeatResponse(): void {
    if (!this.ws || this.ws.readyState !== WebSocket.OPEN) {
      console.warn('WebSocket not connected, cannot send heartbeat response')
      return
    }

    try {
      this.ws.send(JSON.stringify({
        type: 'heartbeat',
        data: { response: 'pong' },
        timestamp: new Date().toISOString()
      }))
    } catch (error) {
      console.error('Error sending heartbeat response:', error)
    }
  }

  private attemptReconnect(): void {
    if (this.status.value.reconnectAttempts >= this.maxReconnectAttempts) {
      console.log('Max reconnection attempts reached')
      this.status.value.error = 'Se agotaron los intentos de reconexión'
      return
    }

    this.status.value.isReconnecting = true
    this.status.value.reconnectAttempts++

    console.log(`Attempting to reconnect... (${this.status.value.reconnectAttempts}/${this.maxReconnectAttempts})`)

    this.reconnectTimer = setTimeout(() => {
      this.connect().catch((error) => {
        console.error('Reconnection failed:', error)
        if (this.status.value.reconnectAttempts < this.maxReconnectAttempts) {
          this.attemptReconnect()
        } else {
          this.status.value.isReconnecting = false
          this.status.value.error = 'No se pudo reconectar al servidor'
        }
      })
    }, this.reconnectDelay)
  }
}

// Instancia global para compartir entre componentes
let wsManager: WebSocketManager | null = null

export function useWebSocket(gameId?: string) {
  const createConnection = (token?: string) => {
    const baseUrl = 'ws://localhost:8000'
    const wsUrl = gameId ? `${baseUrl}/ws/${gameId}` : `${baseUrl}/ws`

    if (wsManager) {
      wsManager.disconnect()
    }

    wsManager = new WebSocketManager(wsUrl, token)
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
    // Solo desconectar si no hay otros componentes usando la conexión
    // En una implementación real, usaríamos un contador de referencias
  })

  return {
    createConnection,
    getConnection,
    connectionStatus
  }
}

