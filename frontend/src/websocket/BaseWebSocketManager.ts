// La función principal de BaseWebSocketManager es manejar la lógica común
// para suscribirse y despachar mensajes WebSocket recibidos del backend.
// Solo envía respuestas de heartbeat cuando el backend lo solicita.
// Todas las demás interacciones del usuario (unirse a juego, cambiar estado, etc.)
// deben hacerse vía llamadas API REST normales, no mediante mensajes WebSocket.
import { ref } from 'vue'
import type {
  GameWebSocketMessage,
  WebSocketMessageType,
  ConnectionStatus,
  MessageHandler,
  MessageHandlersMap,
  WebSocketMessageMap
} from '../types'

/**
 * Base class for WebSocket managers.
 * 
 * Key principles:
 * 1. Frontend only RECEIVES messages from backend via WebSocket
 * 2. Frontend only RESPONDS to heartbeat messages (no other outgoing messages)
 * 3. All user interactions should generate API calls, not WebSocket messages
 * 4. Message types are synchronized with backend's messages_types.py
 */
export abstract class BaseWebSocketManager {
  protected messageHandlers: MessageHandlersMap = new Map()

  public status = ref<ConnectionStatus>({
    isConnected: false,
    isReconnecting: false,
    lastConnected: null,
    reconnectAttempts: 0,
    error: null
  })

  protected heartbeatResponseTimer: number | null = null

  public readonly maxReconnectAttempts = 5
  public readonly heartbeatResponseDelay = 1000 // Delay before responding to heartbeat

  /**
   * Subscribe to specific message types with proper typing
   * Returns an unsubscribe function
   */
  subscribe<K extends WebSocketMessageType>(
    messageType: K, 
    handler: MessageHandler<WebSocketMessageMap[K]>
  ): () => void {
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

  /**
   * Dispatch incoming messages to registered handlers
   * Validates message structure and handles heartbeat responses automatically
   */
  protected dispatchMessage(message: GameWebSocketMessage): void {
    // Procesa los mensajes que tienen un campo "type"
    // message está parseado según WebSocketMessage interface
    console.log(`[BaseWebSocketManager] Dispatching message of type ${message.type}`)
    if (!message || typeof message.type !== 'string') {
      console.warn('[BaseWebSocketManager] Mensaje inválido recibido:', message)
      return
    }

    // Log errors for debugging
    if (message.type === 'error') {
      console.warn('[BaseWebSocketManager] Mensaje de error recibido:', message)
    }

    // Auto-respond to heartbeat messages
    if (message.type === 'heartbeat') {
      this.handleHeartbeat()
    }

    // Dispatch to registered handlers
    const handlers = this.messageHandlers.get(message.type)
    if (handlers) {
      console.log(`[BaseWebSocketManager] Dispatching 2 message of type '${message.type}' to ${handlers.length} handlers`)
      handlers.forEach(handler => {
        try {
          // Pass the data payload to the handler, with fallback to undefined for messages without data
          const payload = message.data !== undefined ? message.data : undefined
          handler(payload)
        } catch (error) {
          console.error(`Error in message handler for ${message.type}:`, error)
        }
      })
    }
    else {
      if (message.type !== 'heartbeat') {// Avoid cluttering logs with heartbeat messages
        console.log(`[BaseWebSocketManager] No handlers registered for message type '${message.type}'`)}
    }
  }

  /**
   * Handle heartbeat messages by responding after a short delay
   * This is the ONLY message the frontend should send via WebSocket
   */
  private handleHeartbeat(): void {
    // Clear any existing heartbeat response timer
    if (this.heartbeatResponseTimer) {
      clearTimeout(this.heartbeatResponseTimer)
    }

    // Respond to heartbeat after a short delay
    this.heartbeatResponseTimer = setTimeout(() => {
      try {
        this.sendHeartbeatResponse()
      } catch (error) {
        console.warn('[BaseWebSocketManager] Error sending heartbeat response:', error)
      }
    }, this.heartbeatResponseDelay)
  }

  protected stopHeartbeatResponse(): void {
    if (this.heartbeatResponseTimer) {
      clearTimeout(this.heartbeatResponseTimer)
      this.heartbeatResponseTimer = null
    }
  }

  /**
   * Send heartbeat response - the ONLY message type the frontend should send
   * Subclasses must implement this method
   */
  protected abstract sendHeartbeatResponse(): void

  /**
   * Generic method for cleanup when disconnecting
   */
  protected cleanup(): void {
    this.stopHeartbeatResponse()
    this.messageHandlers.clear()
  }
}
