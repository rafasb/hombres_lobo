/**
 * WebSocket Service para comunicación en tiempo real
 * Maneja la conexión WebSocket con el backend usando WebSocket nativo
 */

import { ref, reactive } from 'vue'
import type { Ref } from 'vue'

export interface WebSocketMessage {
  type: string
  game_id?: string
  user_id?: string
  timestamp?: string
  data?: any
  [key: string]: any
}

export interface ConnectionState {
  connected: boolean
  connecting: boolean
  error: string | null
  lastHeartbeat: Date | null
}

class WebSocketService {
  private ws: WebSocket | null = null
  private gameId: string | null = null
  private token: string | null = null
  private reconnectAttempts = 0
  private maxReconnectAttempts = 5
  private reconnectInterval = 3000
  private heartbeatInterval: number | null = null
  private messageQueue: WebSocketMessage[] = []

  // Estado reactivo
  public connectionState: Ref<ConnectionState> = ref({
    connected: false,
    connecting: false,
    error: null,
    lastHeartbeat: null
  })

  // Event handlers reactivos
  private eventHandlers: Map<string, Array<(message: WebSocketMessage) => void>> = new Map()

  /**
   * Conectar al WebSocket del juego
   */
  async connect(gameId: string, token: string): Promise<boolean> {
    if (this.connectionState.value.connected || this.connectionState.value.connecting) {
      console.warn('Ya conectado o conectando')
      return false
    }

    this.gameId = gameId
    this.token = token
    this.connectionState.value.connecting = true
    this.connectionState.value.error = null

    try {
      const wsUrl = `ws://localhost:8000/ws/${gameId}?token=${token}`
      this.ws = new WebSocket(wsUrl)

      return new Promise((resolve, reject) => {
        if (!this.ws) {
          reject(new Error('No se pudo crear WebSocket'))
          return
        }

        this.ws.onopen = () => {
          console.log(`WebSocket conectado al juego ${gameId}`)
          this.connectionState.value.connected = true
          this.connectionState.value.connecting = false
          this.connectionState.value.error = null
          this.reconnectAttempts = 0

          // Enviar mensajes en cola
          this.flushMessageQueue()

          // Iniciar heartbeat
          this.startHeartbeat()

          resolve(true)
        }

        this.ws.onmessage = (event) => {
          try {
            const message: WebSocketMessage = JSON.parse(event.data)
            this.handleMessage(message)
          } catch (error) {
            console.error('Error parsing WebSocket message:', error)
          }
        }

        this.ws.onerror = (error) => {
          console.error('WebSocket error:', error)
          this.connectionState.value.error = 'Error de conexión WebSocket'
          this.connectionState.value.connecting = false
          reject(error)
        }

        this.ws.onclose = (event) => {
          console.log('WebSocket cerrado:', event.code, event.reason)
          this.connectionState.value.connected = false
          this.connectionState.value.connecting = false

          this.stopHeartbeat()

          // Intentar reconectar si no fue un cierre intencional
          if (event.code !== 1000 && this.reconnectAttempts < this.maxReconnectAttempts) {
            this.attemptReconnect()
          }
        }
      })
    } catch (error) {
      console.error('Error conectando WebSocket:', error)
      this.connectionState.value.connecting = false
      this.connectionState.value.error = 'Error de conexión'
      return false
    }
  }

  /**
   * Desconectar WebSocket
   */
  disconnect(): void {
    if (this.ws) {
      this.ws.close(1000, 'Desconexión intencional')
      this.ws = null
    }
    this.stopHeartbeat()
    this.connectionState.value.connected = false
    this.connectionState.value.connecting = false
    this.gameId = null
    this.token = null
  }

  /**
   * Enviar mensaje
   */
  send(message: WebSocketMessage): boolean {
    if (!this.connectionState.value.connected || !this.ws) {
      console.warn('WebSocket no conectado, agregando mensaje a cola')
      this.messageQueue.push(message)
      return false
    }

    try {
      this.ws.send(JSON.stringify(message))
      return true
    } catch (error) {
      console.error('Error enviando mensaje:', error)
      return false
    }
  }

  /**
   * Suscribirse a eventos
   */
  on(eventType: string, handler: (message: WebSocketMessage) => void): void {
    if (!this.eventHandlers.has(eventType)) {
      this.eventHandlers.set(eventType, [])
    }
    this.eventHandlers.get(eventType)!.push(handler)
  }

  /**
   * Desuscribirse de eventos
   */
  off(eventType: string, handler?: (message: WebSocketMessage) => void): void {
    if (!this.eventHandlers.has(eventType)) return

    const handlers = this.eventHandlers.get(eventType)!
    if (handler) {
      const index = handlers.indexOf(handler)
      if (index > -1) {
        handlers.splice(index, 1)
      }
    } else {
      this.eventHandlers.set(eventType, [])
    }
  }

  /**
   * Enviar mensaje de chat
   */
  sendChatMessage(message: string, channel: string = 'all'): boolean {
    return this.send({
      type: 'chat_message',
      message,
      channel,
      timestamp: new Date().toISOString()
    })
  }

  /**
   * Unirse al juego
   */
  joinGame(): boolean {
    return this.send({
      type: 'join_game',
      timestamp: new Date().toISOString()
    })
  }

  /**
   * Iniciar juego
   */
  startGame(): boolean {
    return this.send({
      type: 'start_game',
      timestamp: new Date().toISOString()
    })
  }

  /**
   * Obtener estado del juego
   */
  getGameStatus(): void {
    this.send({
      type: 'get_game_status'
    })
  }

  /**
   * Emitir un voto
   */
  castVote(targetPlayerId: string): void {
    this.send({
      type: 'cast_vote',
      data: {
        target_player_id: targetPlayerId
      }
    })
  }

  /**
   * Obtener estado de votación actual
   */
  getVotingStatus(): void {
    this.send({
      type: 'get_voting_status'
    })
  }

  /**
   * Forzar siguiente fase (solo para creador)
   */
  forceNextPhase(): void {
    this.send({
      type: 'force_next_phase'
    })
  }

  /**
   * Enviar heartbeat
   */

  /**
   * Manejar mensaje entrante
   */
  private handleMessage(message: WebSocketMessage): void {
    console.log('WebSocket mensaje recibido:', message.type, message)

    // Manejar heartbeat
    if (message.type === 'heartbeat') {
      this.connectionState.value.lastHeartbeat = new Date()
      if (message.response !== 'pong') {
        // Responder al ping del servidor
        this.send({
          type: 'heartbeat',
          timestamp: message.timestamp
        })
      }
      return
    }

    // Emitir evento a handlers suscritos
    const handlers = this.eventHandlers.get(message.type) || []
    console.log(`Handlers para ${message.type}:`, handlers.length)
    handlers.forEach(handler => {
      try {
        handler(message)
      } catch (error) {
        console.error(`Error en handler para ${message.type}:`, error)
      }
    })

    // También emitir a handlers genéricos
    const allHandlers = this.eventHandlers.get('*') || []
    allHandlers.forEach(handler => {
      try {
        handler(message)
      } catch (error) {
        console.error('Error en handler genérico:', error)
      }
    })
  }

  /**
   * Vaciar cola de mensajes
   */
  private flushMessageQueue(): void {
    while (this.messageQueue.length > 0 && this.connectionState.value.connected) {
      const message = this.messageQueue.shift()
      if (message) {
        this.send(message)
      }
    }
  }

  /**
   * Iniciar heartbeat
   */
  private startHeartbeat(): void {
    this.stopHeartbeat()
    this.heartbeatInterval = window.setInterval(() => {
      if (this.connectionState.value.connected) {
        this.send({
          type: 'heartbeat',
          timestamp: new Date().toISOString()
        })
      }
    }, 30000) // Cada 30 segundos
  }

  /**
   * Detener heartbeat
   */
  private stopHeartbeat(): void {
    if (this.heartbeatInterval) {
      clearInterval(this.heartbeatInterval)
      this.heartbeatInterval = null
    }
  }

  /**
   * Intentar reconectar
   */
  private attemptReconnect(): void {
    if (!this.gameId || !this.token) return

    this.reconnectAttempts++
    console.log(`Intentando reconectar... (${this.reconnectAttempts}/${this.maxReconnectAttempts})`)

    setTimeout(() => {
      if (this.gameId && this.token) {
        this.connect(this.gameId, this.token)
      }
    }, this.reconnectInterval * this.reconnectAttempts)
  }
}

// Instancia singleton
export const websocketService = new WebSocketService()

// Composable para usar en componentes Vue
export function useWebSocket() {
  return {
    connectionState: websocketService.connectionState,
    connect: websocketService.connect.bind(websocketService),
    disconnect: websocketService.disconnect.bind(websocketService),
    send: websocketService.send.bind(websocketService),
    on: websocketService.on.bind(websocketService),
    off: websocketService.off.bind(websocketService),
    sendChatMessage: websocketService.sendChatMessage.bind(websocketService),
    joinGame: websocketService.joinGame.bind(websocketService),
    startGame: websocketService.startGame.bind(websocketService),
    getGameStatus: websocketService.getGameStatus.bind(websocketService),
    castVote: websocketService.castVote.bind(websocketService),
    getVotingStatus: websocketService.getVotingStatus.bind(websocketService),
    forceNextPhase: websocketService.forceNextPhase.bind(websocketService)
  }
}
