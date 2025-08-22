import { computed, onUnmounted } from 'vue'
import { BaseWebSocketManager } from './BaseWebSocketManager'
import type {
  WebSocketMessage,
  GameWebSocketMessage
} from '../types'

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
          this.startHeartbeat()
          resolve()
        }

        this.ws.onclose = (event) => {
          console.log('WebSocket closed:', event)
          this.status.value.isConnected = false
          this.stopHeartbeat()

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
          try {
            const parsed = JSON.parse(event.data)
            if (parsed && typeof parsed.type === 'string') {
              const message = parsed as GameWebSocketMessage | WebSocketMessage
              this.dispatchMessage(message as any)
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

    this.stopHeartbeat()

    if (this.ws) {
      this.ws.close(1000, 'Client disconnect')
      this.ws = null
    }

    this.status.value.isConnected = false
  }

  send(message: WebSocketMessage): boolean {
    if (!this.ws || this.ws.readyState !== WebSocket.OPEN) {
      console.warn('WebSocket not connected, cannot send message:', message)
      return false
    }

    try {
      this.ws.send(JSON.stringify({
        ...message,
        timestamp: new Date().toISOString()
      }))
      return true
    } catch (error) {
      console.error('Error sending WebSocket message:', error)
      return false
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

  protected startHeartbeat(): void {
    this.heartbeatTimer = setInterval(() => {
      if (this.ws && this.ws.readyState === WebSocket.OPEN) {
        // Usar 'heartbeat' como en el backend en lugar de 'ping'
        this.send({ type: 'heartbeat' })
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

