import { ref, computed, onUnmounted } from 'vue'

export interface WebSocketMessage {
  type: string
  data?: any
  timestamp?: string
}

export interface ConnectionStatus {
  isConnected: boolean
  isReconnecting: boolean
  lastConnected: Date | null
  reconnectAttempts: number
  error: string | null
}

export class WebSocketManager {
  private ws: WebSocket | null = null
  private reconnectTimer: number | null = null
  private heartbeatTimer: number | null = null
  private messageHandlers: Map<string, ((data: any) => void)[]> = new Map()
  
  // Add explicit property declarations
  private url: string
  private token?: string
  
  public status = ref<ConnectionStatus>({
    isConnected: false,
    isReconnecting: false,
    lastConnected: null,
    reconnectAttempts: 0,
    error: null
  })

  public readonly maxReconnectAttempts = 5
  public readonly reconnectDelay = 3000
  public readonly heartbeatInterval = 30000

  constructor(url: string, token?: string) {
    this.url = url
    this.token = token
  }

  connect(): Promise<void> {
    return new Promise((resolve, reject) => {
      try {
        // Construir URL con token si está disponible
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
          
          // Intentar reconectar si no fue un cierre intencional
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
            const message: WebSocketMessage = JSON.parse(event.data)
            this.handleMessage(message)
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

  subscribe(messageType: string, handler: (data: any) => void): () => void {
    if (!this.messageHandlers.has(messageType)) {
      this.messageHandlers.set(messageType, [])
    }

    this.messageHandlers.get(messageType)!.push(handler)

    // Devolver función para unsubscribe
    return () => {
      const handlers = this.messageHandlers.get(messageType)
      if (handlers) {
        const index = handlers.indexOf(handler)
        if (index > -1) {
          handlers.splice(index, 1)
        }
      }
    }
  }

  private handleMessage(message: WebSocketMessage): void {
    const handlers = this.messageHandlers.get(message.type)
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

  private startHeartbeat(): void {
    this.heartbeatTimer = setInterval(() => {
      if (this.ws && this.ws.readyState === WebSocket.OPEN) {
        // Usar 'heartbeat' como en el backend en lugar de 'ping'
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
let wsManager: WebSocketManager | null = null

export function useWebSocket(gameId?: string) {
  const createConnection = (token?: string) => {
    const baseUrl = import.meta.env.VITE_WS_URL || 'ws://localhost:8000'
    // Corregir URL para coincidir con el backend: /ws/{gameId} en lugar de /ws/games/{gameId}
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

  // Cleanup al desmontar componentes
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
