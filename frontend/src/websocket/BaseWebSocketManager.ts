import { ref } from 'vue'
import type {
  WebSocketMessage,
  WebSocketMessageType,
  ConnectionStatus,
  MessageHandler,
  MessageHandlersMap
} from '../types'

export abstract class BaseWebSocketManager {
  protected messageHandlers: MessageHandlersMap = new Map()

  public status = ref<ConnectionStatus>({
    isConnected: false,
    isReconnecting: false,
    lastConnected: null,
    reconnectAttempts: 0,
    error: null
  })

  protected heartbeatTimer: number | null = null

  public readonly maxReconnectAttempts = 5
  public readonly heartbeatInterval = 30000

  // Subscribe genérico reutilizable
  subscribe<K extends WebSocketMessageType>(messageType: K, handler: MessageHandler<any>): () => void {
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

  // Centraliza el dispatch a handlers registrados
  protected dispatchMessage(message: WebSocketMessage): void {
    if (!message || typeof (message as any).type !== 'string') {
      console.warn('[BaseWebSocketManager] Mensaje inválido recibido:', message)
      return
    }

    if ((message as any).type === 'error') {
      console.warn('[BaseWebSocketManager] Mensaje de error recibido:', message)
    }

    const handlers = this.messageHandlers.get((message as any).type as WebSocketMessageType)
    if (handlers) {
      handlers.forEach(handler => {
        try {
          const payload = (message as any).data !== undefined ? (message as any).data : message
          if (payload === undefined) {
            console.warn(`[BaseWebSocketManager] Handler for ${(message as any).type} will receive undefined payload`)
          }
          handler(payload)
        } catch (error) {
          console.error(`Error in message handler for ${(message as any).type}:`, error)
        }
      })
    }
  }

  // Heartbeat reutilizable; requiere que la subclase implemente `send`
  protected startHeartbeat(): void {
    this.stopHeartbeat()
    this.heartbeatTimer = setInterval(() => {
      try {
        // Intentar enviar heartbeat; la subclase decide cómo enviarlo y si está conectada
        this.send({ type: 'heartbeat' })
      } catch {
        // ignorar errores de send en heartbeat
      }
    }, this.heartbeatInterval)
  }

  protected stopHeartbeat(): void {
    if (this.heartbeatTimer) {
      clearInterval(this.heartbeatTimer)
      this.heartbeatTimer = null
    }
  }

  // La subclase debe implementar cómo se envía un mensaje (WebSocket directo o simulación)
  abstract send(message: WebSocketMessage): boolean
}
