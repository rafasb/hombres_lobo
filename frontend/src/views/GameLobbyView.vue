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
            <div v-if="lobby.state.loading" class="text-center py-5">
              <div class="card shadow-sm" style="background: rgba(255, 255, 255, 0.95); backdrop-filter: blur(10px);">
                <div class="card-body py-5">
                  <div class="spinner-border text-primary" style="width: 3rem; height: 3rem;"></div>
                  <p class="text-muted mt-3">Cargando partida...</p>
                </div>
              </div>
            </div>

            <!-- Error state -->
            <div v-else-if="lobby.state.error" class="text-center py-5">
              <div class="card shadow-sm" style="background: rgba(255, 255, 255, 0.95); backdrop-filter: blur(10px);">
                <div class="card-body py-5">
                  <div class="mb-4">
                    <i class="bi bi-exclamation-triangle text-warning" style="font-size: 4rem;"></i>
                  </div>
                  <h2 class="text-warning mb-3">Error al cargar</h2>
                  <p class="text-muted mb-4">{{ lobby.state.error }}</p>
                  <button @click="retryLoad" class="btn btn-primary">
                    <i class="bi bi-arrow-clockwise me-2"></i>
                    Intentar de nuevo
                  </button>
                </div>
              </div>
            </div>

            <!-- Contenido principal cuando no está cargando -->
            <div v-else-if="lobby.state.game && lobby.state.game.value" class="row g-4">
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
                    <h3 class="card-title text-primary mb-3">{{ lobby.state.game.value?.name }}</h3>
                    
                    <div class="row g-3">
                      <div class="col-6">
                        <div class="d-flex flex-column">
                          <small class="text-muted">Estado</small>
                          <span 
                            class="badge align-self-start"
                            :class="{
                              'bg-warning': lobby.state.game.value?.status === 'waiting',
                              'bg-success': lobby.state.game.value?.status === 'started' || lobby.state.game.value?.status === 'night' || lobby.state.game.value?.status === 'day',
                              'bg-secondary': lobby.state.game.value?.status === 'finished',
                              'bg-info': lobby.state.game.value?.status === 'paused'
                            }"
                          >
                            <i class="bi me-1" :class="{
                              'bi-clock': lobby.state.game.value?.status === 'waiting',
                              'bi-play-circle': lobby.state.game.value?.status === 'started' || lobby.state.game.value?.status === 'night' || lobby.state.game.value?.status === 'day',
                              'bi-check-circle': lobby.state.game.value?.status === 'finished',
                              'bi-pause-circle': lobby.state.game.value?.status === 'paused'
                            }"></i>
                            {{ lobby.displayInfo.gameStatusText }}
                          </span>
                        </div>
                      </div>
                      
                      <div class="col-6">
                        <div class="d-flex flex-column">
                          <small class="text-muted">Creador</small>
                          <span class="fw-medium">
                            <i class="bi bi-crown me-1 text-warning"></i>
                            {{ lobby.displayInfo.creatorName }}
                          </span>
                        </div>
                      </div>
                      
                      <div class="col-6">
                        <div class="d-flex flex-column">
                          <small class="text-muted">Jugadores</small>
                          <span class="fw-medium">
                            <i class="bi bi-people me-1"></i>
                            {{ lobby.state.game.value?.players.length }} / {{ lobby.state.game.value?.max_players }}
                          </span>
                        </div>
                      </div>
                      
                      <div class="col-6">
                        <div class="d-flex flex-column">
                          <small class="text-muted">Creada</small>
                          <span class="fw-medium">
                            <i class="bi bi-calendar me-1"></i>
                            {{ lobby.actions.formatDate(lobby.state.game.value?.created_at ?? '') }}
                          </span>
                        </div>
                      </div>
                      
                      <div v-if="lobby.state.game && typeof lobby.state.game.value?.current_round === 'number' && lobby.state.game.value?.current_round > 0" class="col-6">
                        <div class="d-flex flex-column">
                          <small class="text-muted">Ronda</small>
                          <span class="fw-medium">
                            <i class="bi bi-arrow-repeat me-1"></i>
                            {{ lobby.state.game.value?.current_round }}
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
                        Jugadores ({{ lobby.state.game.value?.players.length }})
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
                        v-for="(player, index) in Array.isArray(lobby.users.playerUsers) ? lobby.users.playerUsers : []" 
                        :key="player?.id || `player-${index}`"
                        class="list-group-item"
                        :class="{ 
                          'list-group-item-primary': player?.id === auth.user?.id,
                          'list-group-item-warning': player?.id === lobby.state.game.value?.creator_id && player?.id !== auth.user?.id
                        }"
                        style="background: rgba(255, 255, 255, 0.8);"
                      >
                        <div class="d-flex justify-content-between align-items-center">
                          <div class="d-flex align-items-center gap-2">
                            <!-- Indicador de conexión -->
                            <span 
                              class="badge rounded-pill"
                              :class="getPlayerConnectionStatus(player?.id)?.isConnected ? 'bg-success' : 'bg-secondary'"
                              style="width: 10px; height: 10px;"
                              :title="getPlayerConnectionStatus(player?.id)?.isConnected ? 'Conectado' : 'Desconectado'"
                            ></span>
                            
                            <!-- Nombre del jugador -->
                            <span class="fw-medium">{{ player?.username || 'Usuario desconocido' }}</span>
                            
                            <!-- Indicador de actividad adicional -->
                            <small v-if="getPlayerConnectionStatus(player?.id)?.lastSeen" 
                                  class="text-muted">
                              ({{ getPlayerConnectionStatus(player?.id)?.isConnected ? 'En línea' : 'Desconectado' }})
                            </small>
                          </div>
                          
                          <!-- Badges del jugador -->
                          <div class="d-flex gap-1">
                            <span v-if="player?.id === lobby.state.game.value?.creator_id" class="badge bg-warning text-dark">
                              <i class="bi bi-crown me-1"></i>
                              Creador
                            </span>
                            <span v-if="player?.id === auth.user?.id" class="badge bg-primary">
                              <i class="bi bi-person-check me-1"></i>
                              Tú
                            </span>
                            <span v-if="getPlayerConnectionStatus(player?.id)?.isConnected" class="badge bg-success">
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
                        v-if="lobby.permissions.canJoinGame" 
                        @click="handleJoinGame"
                        :disabled="lobby.state.loading"
                        class="btn btn-success btn-lg"
                      >
                        <span v-if="lobby.state.loading" class="spinner-border spinner-border-sm me-2"></span>
                        <i v-else class="bi bi-box-arrow-in-right me-2"></i>
                        Unirse a la partida
                      </button>

                      <!-- Botón para salir -->
                      <button 
                        v-if="lobby.permissions.canLeaveGame" 
                        @click="lobby.actions.leaveGame"
                        :disabled="lobby.state.loading"
                        class="btn btn-outline-danger btn-lg"
                      >
                        <span v-if="lobby.state.loading" class="spinner-border spinner-border-sm me-2"></span>
                        <i v-else class="bi bi-box-arrow-left me-2"></i>
                        Abandonar partida
                      </button>

                      <!-- Botón para iniciar (solo el creador) -->
                      <button 
                        v-if="lobby.permissions.canStartGame" 
                        @click="lobby.actions.startGame"
                        :disabled="lobby.state.loading"
                        class="btn btn-primary btn-lg"
                      >
                        <span v-if="lobby.state.loading" class="spinner-border spinner-border-sm me-2"></span>
                        <i v-else class="bi bi-play-circle me-2"></i>
                        Iniciar partida
                      </button>
                    </div>

                    <!-- Información adicional para el creador -->
                    <div v-if="lobby.permissions.isCreator && lobby.state.game && lobby.state.game.value?.status === 'waiting'" class="mt-4 text-center">
                      <div v-if="lobby.state.game.value?.players.length < 4" class="alert alert-warning">
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
            <div v-if="lobby.state.notification" 
                 class="position-fixed bottom-0 end-0 p-3" 
                 style="z-index: 1055;">
              <div 
                class="alert mb-0 shadow"
                :class="{
                  'alert-success': lobby.state.notification.value?.type === 'success',
                  'alert-danger': lobby.state.notification.value?.type === 'error'
                }"
                role="alert"
              >
                <i class="bi me-2" :class="{
                  'bi-check-circle': lobby.state.notification.value?.type === 'success',
                  'bi-exclamation-triangle': lobby.state.notification.value?.type === 'error'
                }"></i>
                {{ lobby.state.notification.value?.message }}
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

// Usar el composable refactorizado con estructura anidada
const lobby = useGameLobby(gameId)

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

// Función wrapper para manejar joinGame y actualizar conexiones
const handleJoinGame = async () => {
  await lobby.actions.joinGame()
  // Actualizar estado de jugadores después de unirse
  if (lobby.state.game && lobby.state.game.value) {
    initializePlayersStatus(lobby.state.game.value.players)
  }
}


// Función para reintentar carga
const retryLoad = async () => {
  console.log('Reintentando cargar partida:', gameId)
  if (lobby.actions.loadGame) {
    await lobby.actions.loadGame()
  }
}

// Inicializar conexiones al montar
onMounted(async () => {
  console.log('GameLobbyView mounted, gameId:', gameId)
  console.log('Initial lobby state:', {
    loading: lobby.state.loading,
    game: !!lobby.state.game,
    error: lobby.state.error
  })
  
  // Verificar si hay un método de carga manual
  if (lobby.actions.loadGame) {
    console.log('Calling manual loadGame')
    await lobby.actions.loadGame()
  }
  
  // Luego inicializar el estado de conexión de jugadores
  setTimeout(() => {
    if (lobby.state.game) {
      initializePlayersStatus(lobby.state.game.value?.players ?? [])
    }
    notifyUserJoinedLobby()
  }, 1000)
})
</script>
