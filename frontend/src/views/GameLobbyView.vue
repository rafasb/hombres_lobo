<template>
  <div class="min-vh-100" style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);">
    <!-- Navegación común -->
    <NavigationBar 
      :show-admin="auth?.isAdmin"
      @navigate="handleNavigation"
    />

    <div class="mobile-container">
      <div class="container-fluid">
        <div class="row justify-content-center">
          <div class="col-12">
            <!-- Header con navegación de retorno -->
            <div class="card shadow-sm mb-4" style="background: rgba(255, 255, 255, 0.95); backdrop-filter: blur(10px); border: none; border-radius: 15px;">
              <div class="card-body">
                <div class="d-flex align-items-center gap-3">
                  <div>
                    <h1 class="card-title mb-0 text-primary fw-bold">
                      <i class="bi bi-door-open me-2"></i>
                      Lobby de la Partida
                    </h1>
                  </div>
                </div>
              </div>
            </div>

      <!-- Indicador de carga -->
      <div v-if="loading" class="text-center py-5">
        <div class="card shadow-sm" style="background: rgba(255, 255, 255, 0.95); backdrop-filter: blur(10px);">
          <div class="card-body py-5">
            <div class="spinner-border text-primary" style="width: 3rem; height: 3rem;"></div>
            <p class="text-muted mt-3">Cargando partida...</p>
          </div>
        </div>
      </div>

      <!-- Contenido principal cuando no está cargando -->
      <div v-else-if="game" class="row g-4">
        <!-- Estado de conexión WebSocket -->
        <div class="col-12">
          <ConnectionStatus
            :gameConnectionState="gameConnectionState"
            :connectionStatus="connectionStatus"
            :connectionStatusText="connectionStatusText"
            :connectionStatusClass="connectionStatusClass"
            :isUserActiveInLobby="isUserActiveInLobby"
            :connectionHealthText="connectionHealthText"
            @reconnect="initializeConnection"
          />
        </div>

        <!-- Información de la partida -->
        <div class="col-12 col-lg-6">
          <div class="card shadow-sm h-100" style="background: rgba(255, 255, 255, 0.95); backdrop-filter: blur(10px);">
            <div class="card-header bg-primary text-white">
              <h5 class="mb-0">
                <i class="bi bi-info-circle me-2"></i>
                Información de la Partida
              </h5>
            </div>
            <div class="card-body">
              <h3 class="card-title text-primary mb-3">{{ game.name }}</h3>
              
              <div class="row g-3">
                <div class="col-6">
                  <div class="d-flex flex-column">
                    <small class="text-muted">Estado</small>
                    <span 
                      class="badge align-self-start"
                      :class="{
                        'bg-warning': game.status === 'waiting',
                        'bg-success': game.status === 'started' || game.status === 'night' || game.status === 'day',
                        'bg-secondary': game.status === 'finished',
                        'bg-info': game.status === 'paused'
                      }"
                    >
                      <i class="bi me-1" :class="{
                        'bi-clock': game.status === 'waiting',
                        'bi-play-circle': game.status === 'started' || game.status === 'night' || game.status === 'day',
                        'bi-check-circle': game.status === 'finished',
                        'bi-pause-circle': game.status === 'paused'
                      }"></i>
                      {{ gameStatusText }}
                    </span>
                  </div>
                </div>
                
                <div class="col-6">
                  <div class="d-flex flex-column">
                    <small class="text-muted">Creador</small>
                    <span class="fw-medium">
                      <i class="bi bi-crown me-1 text-warning"></i>
                      {{ creatorName }}
                    </span>
                  </div>
                </div>
                
                <div class="col-6">
                  <div class="d-flex flex-column">
                    <small class="text-muted">Jugadores</small>
                    <span class="fw-medium">
                      <i class="bi bi-people me-1"></i>
                      {{ game.players.length }} / {{ game.max_players }}
                    </span>
                  </div>
                </div>
                
                <div class="col-6">
                  <div class="d-flex flex-column">
                    <small class="text-muted">Creada</small>
                    <span class="fw-medium">
                      <i class="bi bi-calendar me-1"></i>
                      {{ formatDate(game.created_at ?? '') }}
                    </span>
                  </div>
                </div>
                
                <div v-if="game && typeof game.current_round === 'number' && game.current_round > 0" class="col-6">
                  <div class="d-flex flex-column">
                    <small class="text-muted">Ronda</small>
                    <span class="fw-medium">
                      <i class="bi bi-arrow-repeat me-1"></i>
                      {{ game.current_round }}
                    </span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Lista de jugadores -->
        <div class="col-12 col-lg-6">
          <div class="card shadow-sm h-100" style="background: rgba(255, 255, 255, 0.95); backdrop-filter: blur(10px);">
            <div class="card-header bg-primary text-white">
              <div class="d-flex justify-content-between align-items-center">
                <h5 class="mb-0">
                  <i class="bi bi-people-fill me-2"></i>
                  Jugadores ({{ game.players.length }})
                </h5>
                <small>
                  <i class="bi bi-wifi me-1"></i>
                  {{ gameConnectionState.connectedPlayersCount }} conectados
                </small>
              </div>
            </div>
            <div class="card-body p-0">
              <div class="list-group list-group-flush">
                <div 
                  v-for="player in playerUsers" 
                  :key="player.id"
                  class="list-group-item"
                  :class="{ 
                    'list-group-item-primary': player.id === auth.user?.id,
                    'list-group-item-warning': player.id === game.creator_id && player.id !== auth.user?.id
                  }"
                  style="background: rgba(255, 255, 255, 0.8);"
                >
                  <div class="d-flex justify-content-between align-items-center">
                    <div class="d-flex align-items-center gap-2">
                      <!-- Indicador de conexión -->
                      <span 
                        class="badge rounded-pill"
                        :class="getPlayerConnectionStatus(player.id)?.isConnected ? 'bg-success' : 'bg-secondary'"
                        style="width: 10px; height: 10px;"
                        :title="getPlayerConnectionStatus(player.id)?.isConnected ? 'Conectado' : 'Desconectado'"
                      ></span>
                      
                      <!-- Nombre del jugador -->
                      <span class="fw-medium">{{ player.username }}</span>
                      
                      <!-- Indicador de actividad adicional -->
                      <small v-if="getPlayerConnectionStatus(player.id)?.lastSeen" 
                            class="text-muted">
                        ({{ getPlayerConnectionStatus(player.id)?.isConnected ? 'En línea' : 'Desconectado' }})
                      </small>
                    </div>
                    
                    <!-- Badges del jugador -->
                    <div class="d-flex gap-1">
                      <span v-if="player.id === game.creator_id" class="badge bg-warning text-dark">
                        <i class="bi bi-crown me-1"></i>
                        Creador
                      </span>
                      <span v-if="player.id === auth.user?.id" class="badge bg-primary">
                        <i class="bi bi-person-check me-1"></i>
                        Tú
                      </span>
                      <span v-if="getPlayerConnectionStatus(player.id)?.isConnected" class="badge bg-success">
                        <i class="bi bi-wifi me-1"></i>
                        Online
                      </span>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Acciones del jugador -->
        <div class="col-12">
          <div class="card shadow-sm" style="background: rgba(255, 255, 255, 0.95); backdrop-filter: blur(10px);">
            <div class="card-header bg-primary text-white">
              <h5 class="mb-0">
                <i class="bi bi-gear me-2"></i>
                Acciones
              </h5>
            </div>
            <div class="card-body">
              <div class="d-flex flex-wrap gap-3 justify-content-center">
                <!-- Botón para unirse -->
                <button 
                  v-if="canJoinGame" 
                  @click="joinGame"
                  :disabled="loading"
                  class="btn btn-success btn-lg"
                >
                  <span v-if="loading" class="spinner-border spinner-border-sm me-2"></span>
                  <i v-else class="bi bi-box-arrow-in-right me-2"></i>
                  Unirse a la partida
                </button>

                <!-- Botón para salir -->
                <button 
                  v-if="canLeaveGame" 
                  @click="leaveGame"
                  :disabled="loading"
                  class="btn btn-outline-danger btn-lg"
                >
                  <span v-if="loading" class="spinner-border spinner-border-sm me-2"></span>
                  <i v-else class="bi bi-box-arrow-left me-2"></i>
                  Abandonar partida
                </button>

                <!-- Botón para iniciar (solo el creador) -->
                <button 
                  v-if="canStartGame" 
                  @click="startGame"
                  :disabled="loading"
                  class="btn btn-primary btn-lg"
                >
                  <span v-if="loading" class="spinner-border spinner-border-sm me-2"></span>
                  <i v-else class="bi bi-play-circle me-2"></i>
                  Iniciar partida
                </button>
              </div>

              <!-- Información adicional para el creador -->
              <div v-if="isCreator && game.status === 'waiting'" class="mt-4 text-center">
                <div v-if="game.players.length < 4" class="alert alert-warning">
                  <i class="bi bi-exclamation-triangle me-2"></i>
                  <strong>Atención:</strong> Se necesitan al menos 4 jugadores para iniciar la partida
                </div>
                <div v-else class="alert alert-success">
                  <i class="bi bi-check-circle me-2"></i>
                  <strong>¡Perfecto!</strong> La partida está lista para comenzar
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Mensaje de error si no se encontró la partida -->
      <div v-else class="text-center py-5">
        <div class="card shadow-sm" style="background: rgba(255, 255, 255, 0.95); backdrop-filter: blur(10px);">
          <div class="card-body py-5">
            <div class="mb-4">
              <i class="bi bi-exclamation-circle text-danger" style="font-size: 4rem;"></i>
            </div>
            <h2 class="text-danger mb-3">Partida no encontrada</h2>
            <p class="text-muted mb-4">La partida que buscas no existe o no tienes permisos para verla.</p>
          </div>
        </div>
      </div>

      <!-- Notificaciones -->
      <div v-if="notification" 
           class="position-fixed bottom-0 end-0 p-3" 
           style="z-index: 1055;">
        <div 
          class="alert mb-0 shadow"
          :class="{
            'alert-success': notification.type === 'success',
            'alert-danger': notification.type === 'error'
          }"
          role="alert"
        >
          <i class="bi me-2" :class="{
            'bi-check-circle': notification.type === 'success',
            'bi-exclamation-triangle': notification.type === 'error'
          }"></i>
          {{ notification.message }}
        </div>
      </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { useGameLobby } from '../composables/useGameLobby'
import { useGameConnection } from '../composables/useGameConnection'
import { useNavigation } from '../composables/useNavigation'
import { useAuthStore } from '../stores/authStore'
import NavigationBar from '../components/NavigationBar.vue'
import ConnectionStatus from '../components/ConnectionStatus.vue'

const route = useRoute()
const gameId = route.params.id as string
const auth = useAuthStore()
const { handleNavigation } = useNavigation()

const {
  // Estado
  game,
  playerUsers,
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
  joinGame: originalJoinGame,
  leaveGame: originalLeaveGame,
  startGame,
  formatDate
} = useGameLobby(gameId)

// Funciones wrapper para actualizar estado de jugadores
const joinGame = async () => {
  await originalJoinGame()
  if (game.value) {
    initializePlayersStatus(game.value.players)
  }
}

const leaveGame = async () => {
  await originalLeaveGame()
  // No actualizamos el estado aquí porque leaveGame redirige
}

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
  initializePlayersStatus,
  notifyUserJoinedLobby
} = useGameConnection(gameId)

// Cargar la partida al montar el componente
onMounted(async () => {
  // Cargar datos de la partida
  await loadGame()
  
  // Si se cargó correctamente, inicializar estado de jugadores
  if (game.value) {
    initializePlayersStatus(game.value.players)
  }
  
  // Notificar que el usuario se unió al lobby después de un pequeño retraso
  setTimeout(() => {
    notifyUserJoinedLobby()
  }, 1000)
})
</script>
