<template>
  <div class="game-lobby">
    <!-- Header con navegación -->
    <div class="lobby-header">
      <button @click="goBackToGames" class="back-button">
        ← Volver a las partidas
      </button>
      <h1 class="lobby-title">Lobby de la Partida</h1>
    </div>

    <!-- Indicador de carga -->
    <div v-if="loading" class="loading-container">
      <div class="loading-spinner">Cargando...</div>
    </div>

    <!-- Contenido principal cuando no está cargando -->
    <div v-else-if="game" class="lobby-content">
      <!-- Estado de conexión WebSocket -->
      <ConnectionStatus
        :gameConnectionState="gameConnectionState"
        :connectionStatus="connectionStatus"
        :connectionStatusText="connectionStatusText"
        :connectionStatusClass="connectionStatusClass"
        :isUserActiveInLobby="isUserActiveInLobby"
        :connectionHealthText="connectionHealthText"
        @reconnect="initializeConnection"
      />

      <!-- Información de la partida -->
      <div class="game-info-section">
        <div class="game-info-card">
          <h2 class="game-name">{{ game.name }}</h2>
          <div class="game-details">
            <div class="detail-item">
              <span class="detail-label">Estado:</span>
              <span class="game-status" :class="`status-${game.status}`">
                {{ gameStatusText }}
              </span>
            </div>
            <div class="detail-item">
              <span class="detail-label">Creador:</span>
              <span class="detail-value">{{ creatorName }}</span>
            </div>
            <div class="detail-item">
              <span class="detail-label">Jugadores:</span>
              <span class="detail-value">{{ game.players.length }} / {{ game.max_players }}</span>
            </div>
            <div class="detail-item">
              <span class="detail-label">Creada:</span>
              <span class="detail-value">{{ formatDate(game.created_at) }}</span>
            </div>
            <div v-if="game.current_round > 0" class="detail-item">
              <span class="detail-label">Ronda:</span>
              <span class="detail-value">{{ game.current_round }}</span>
            </div>
          </div>
        </div>
      </div>

        <!-- Lista de jugadores -->
        <div class="players-section">
          <h3 class="section-title">Jugadores ({{ game.players.length }})</h3>
          <div class="players-list">
            <div 
              v-for="player in game.players" 
              :key="player.id"
              class="player-card"
              :class="{ 
                'is-creator': player.id === game.creator_id, 
                'is-current-user': player.id === auth.user?.id,
                'is-connected': getPlayerConnectionStatus(player.id)?.isConnected
              }"
            >
              <div class="player-info">
                <div class="player-name-container">
                  <div class="connection-indicator" :class="{ 'online': getPlayerConnectionStatus(player.id)?.isConnected }"></div>
                  <span class="player-name">{{ player.username }}</span>
                </div>
                <div class="player-badges">
                  <span v-if="player.id === game.creator_id" class="badge creator-badge">
                    👑 Creador
                  </span>
                  <span v-if="player.id === auth.user?.id" class="badge current-user-badge">
                    Tú
                  </span>
                  <span v-if="getPlayerConnectionStatus(player.id)?.isConnected" class="badge online-badge">
                    ● En línea
                  </span>
                </div>
              </div>
            </div>
          </div>
        </div>

      <!-- Acciones del jugador -->
      <div class="actions-section">
        <div class="actions-container">
          <!-- Botón para unirse -->
          <button 
            v-if="canJoinGame" 
            @click="joinGame"
            :disabled="loading"
            class="action-button join-button"
          >
            Unirse a la partida
          </button>

          <!-- Botón para salir -->
          <button 
            v-if="canLeaveGame" 
            @click="leaveGame"
            :disabled="loading"
            class="action-button leave-button"
          >
            Abandonar partida
          </button>

          <!-- Botón para iniciar (solo el creador) -->
          <button 
            v-if="canStartGame" 
            @click="startGame"
            :disabled="loading"
            class="action-button start-button"
          >
            Iniciar partida
          </button>

          <!-- Información adicional para el creador -->
          <div v-if="isCreator && game.status === 'waiting'" class="creator-info">
            <p v-if="game.players.length < 4" class="info-message warning">
              ⚠️ Se necesitan al menos 4 jugadores para iniciar la partida
            </p>
            <p v-else class="info-message success">
              ✅ La partida está lista para comenzar
            </p>
          </div>
        </div>
      </div>
    </div>

    <!-- Mensaje de error si no se encontró la partida -->
    <div v-else class="error-container">
      <div class="error-message">
        <h2>Partida no encontrada</h2>
        <p>La partida que buscas no existe o no tienes permisos para verla.</p>
        <button @click="goBackToGames" class="action-button">
          Volver a las partidas
        </button>
      </div>
    </div>

    <!-- Notificaciones -->
    <div v-if="notification" :class="`notification notification-${notification.type}`">
      {{ notification.message }}
    </div>
  </div>
</template>

<script setup lang="ts">
import { onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { useGameLobby } from '../composables/useGameLobby'
import { useGameConnection } from '../composables/useGameConnection'
import { useAuthStore } from '../stores/authStore'
import ConnectionStatus from '../components/ConnectionStatus.vue'

const route = useRoute()
const gameId = route.params.id as string
const auth = useAuthStore()

const {
  // Estado
  game,
  loading,
  notification,
  
  // Computed
  isCreator,
  canStartGame,
  canJoinGame,
  canLeaveGame,
  gameStatusText,
  creatorName,
  
  // Métodos
  loadGame,
  joinGame,
  leaveGame,
  startGame,
  goBackToGames,
  formatDate
} = useGameLobby(gameId)

// WebSocket connection management
const {
  // Estado
  gameConnectionState,
  connectionStatus,
  
  // Computed
  connectionStatusText,
  connectionStatusClass,
  isUserActiveInLobby,
  connectionHealthText,
  
  // Métodos
  getPlayerConnectionStatus,
  initializeConnection,
  notifyUserJoinedLobby
} = useGameConnection(gameId)

// Cargar la partida al montar el componente
onMounted(() => {
  loadGame()
  // Notificar que el usuario se unió al lobby después de un pequeño retraso
  setTimeout(() => {
    notifyUserJoinedLobby()
  }, 1000)
})
</script>
