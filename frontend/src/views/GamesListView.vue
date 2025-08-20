<template>
  <div class="min-vh-100" style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);">
    <!-- Navegación común -->
    <NavigationBar 
      :show-admin="auth.isAdmin"
      @navigate="handleNavigation"
    />

    <div class="mobile-container">
      <div class="container-fluid">
        <div class="row justify-content-center">
          <div class="col-12">
            <!-- Header -->
            <div class="card mb-4" style="background: rgba(255, 255, 255, 0.95); backdrop-filter: blur(10px); border: none; border-radius: 15px;">
              <div class="card-body d-flex justify-content-between align-items-center">
                <h1 class="mb-0 fw-bold text-dark">
                  <i class="bi bi-controller me-2"></i>
                  Partidas Disponibles
                </h1>
                <button 
                  class="btn btn-primary btn-lg d-flex align-items-center gap-2"
                  @click="openCreateModal"
                  style="border-radius: 25px; box-shadow: 0 4px 15px rgba(0, 123, 255, 0.3);"
                >
                  <i class="bi bi-plus-circle"></i>
                  <span class="d-none d-sm-inline">Crear Partida</span>
                </button>
              </div>
            </div>

            <!-- Lista de partidas -->
            <div class="row g-4" v-if="hasGames">
              <div 
                class="col-12 col-md-6 col-lg-4" 
                v-for="game in games" 
                :key="game.id"
              >
                <div class="card h-100 game-card-hover" 
                     style="background: rgba(255, 255, 255, 0.95); backdrop-filter: blur(10px); border: none; border-radius: 15px; box-shadow: 0 8px 25px rgba(0, 0, 0, 0.1); transition: transform 0.3s ease;"
                     :class="getBootstrapCardClass(game.status)">
                  
                  <div class="card-header d-flex justify-content-between align-items-center border-0 pb-2" 
                       style="background: transparent;">
                    <h5 class="card-title mb-0 fw-bold text-dark text-truncate" style="max-width: 200px;">
                      {{ game.name }}
                    </h5>
                    <span class="badge fs-6" :class="getStatusBadgeClass(game.status)">
                      {{ getStatusText(game.status) }}
                    </span>
                  </div>
                  
                  <div class="card-body pt-2">
                    <div class="mb-3">
                      <div class="d-flex justify-content-between mb-2">
                        <span class="text-muted">Jugadores:</span>
                        <span class="fw-semibold">{{ game.players.length }}/{{ game.max_players }}</span>
                      </div>
                      
                      <div class="d-flex justify-content-between mb-2">
                        <span class="text-muted">Creador:</span>
                        <span class="fw-semibold text-truncate" style="max-width: 120px;">{{ getCreatorName(game) }}</span>
                      </div>
                      
                      <div class="d-flex justify-content-between mb-2">
                        <span class="text-muted">Creada:</span>
                        <span class="fw-semibold">{{ formatDate(game.created_at) }}</span>
                      </div>
                      
                      <div class="d-flex justify-content-between mb-2" v-if="game.status !== 'waiting'">
                        <span class="text-muted">Ronda:</span>
                        <span class="fw-semibold">{{ game.current_round }}</span>
                      </div>
                    </div>
                    
                    <div class="d-flex flex-wrap gap-2">
                      <button 
                        v-if="canJoinGame(game)" 
                        class="btn btn-success flex-fill"
                        @click="joinGame(game.id)"
                        :disabled="loading"
                        style="border-radius: 10px;"
                      >
                        <i class="bi bi-box-arrow-in-right me-1"></i>
                        Unirse
                      </button>
                      
                      <button 
                        v-if="canLeaveGame(game)" 
                        class="btn btn-warning flex-fill"
                        @click="leaveGame(game.id)"
                        :disabled="loading"
                        style="border-radius: 10px;"
                      >
                        <i class="bi bi-box-arrow-left me-1"></i>
                        Abandonar
                      </button>
                      
                      <button 
                        v-if="canViewGame(game)" 
                        class="btn btn-info flex-fill"
                        @click="viewGame(game.id)"
                        style="border-radius: 10px;"
                      >
                        <i class="bi bi-eye me-1"></i>
                        Ver
                      </button>
                      
                      <button 
                        v-if="canDeleteGame(game)" 
                        class="btn btn-danger flex-fill"
                        @click="deleteGame(game.id)"
                        :disabled="loading"
                        style="border-radius: 10px;"
                      >
                        <i class="bi bi-trash me-1"></i>
                        Eliminar
                      </button>
                    </div>
                  </div>
                </div>
              </div>
            </div>
            
            <!-- Estado vacío -->
            <div v-else-if="!loading" class="text-center py-5">
              <div class="card" style="background: rgba(255, 255, 255, 0.95); backdrop-filter: blur(10px); border: none; border-radius: 15px;">
                <div class="card-body py-5">
                  <i class="bi bi-controller display-1 text-muted mb-3"></i>
                  <h4 class="text-muted mb-3">No hay partidas disponibles</h4>
                  <button 
                    class="btn btn-primary btn-lg d-flex align-items-center gap-2 mx-auto"
                    @click="openCreateModal"
                    style="border-radius: 25px;"
                  >
                    <i class="bi bi-plus-circle"></i>
                    Crear la primera partida
                  </button>
                </div>
              </div>
            </div>
            
            <!-- Estado de carga -->
            <div v-if="loading" class="text-center py-5">
              <div class="card" style="background: rgba(255, 255, 255, 0.95); backdrop-filter: blur(10px); border: none; border-radius: 15px;">
                <div class="card-body py-5">
                  <div class="spinner-border text-primary mb-3" role="status">
                    <span class="visually-hidden">Cargando...</span>
                  </div>
                  <h5 class="text-muted">Cargando partidas...</h5>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Modal para crear partida -->
    <div 
      v-if="showCreateModal"
      class="modal fade show d-block"
      tabindex="-1" 
      style="background-color: rgba(0, 0, 0, 0.5);"
      @click.self="closeCreateModal"
    >
      <div class="modal-dialog modal-dialog-centered modal-lg">
        <div class="modal-content" style="border-radius: 15px; border: none;">
          <CreateGameModal
            :gameData="newGame"
            :playerOptions="playerOptions"
            :loading="loading"
            @close="closeCreateModal"
            @create="createGame"
            @update:gameData="updateNewGame"
          />
        </div>
      </div>
    </div>

    <!-- Notificación -->
    <div v-if="notification" 
         class="position-fixed bottom-0 start-50 translate-middle-x mb-3" 
         style="z-index: 1050;">
      <div class="alert" 
           :class="notification.type === 'success' ? 'alert-success' : 'alert-danger'" 
           style="border-radius: 10px; box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);">
        {{ notification.message }}
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import CreateGameModal from '../components/CreateGameModal.vue'
import NavigationBar from '../components/NavigationBar.vue'

// Props para recibir los datos y métodos del composable
interface Props {
  games: any[]
  loading: boolean
  showCreateModal: boolean
  notification: any
  newGame: any
  playerOptions: number[]
  hasGames: boolean
  auth: any
  canJoinGame: (game: any) => boolean
  canLeaveGame: (game: any) => boolean
  canViewGame: (game: any) => boolean
  canDeleteGame: (game: any) => boolean
  getCreatorName: (game: any) => string
  getStatusText: (status: string) => string
  getGameCardClass: (status: string) => string
  formatDate: (dateString: string) => string
}

interface Emits {
  (e: 'createGame'): void
  (e: 'joinGame', gameId: string): void
  (e: 'leaveGame', gameId: string): void
  (e: 'deleteGame', gameId: string): void
  (e: 'viewGame', gameId: string): void
  (e: 'closeCreateModal'): void
  (e: 'openCreateModal'): void
  (e: 'navigate', view: string): void
  (e: 'updateNewGame', value: any): void
}

defineProps<Props>()
const emit = defineEmits<Emits>()

// Métodos que emiten eventos al padre
const createGame = () => emit('createGame')
const joinGame = (gameId: string) => emit('joinGame', gameId)
const leaveGame = (gameId: string) => emit('leaveGame', gameId)
const deleteGame = (gameId: string) => emit('deleteGame', gameId)
const viewGame = (gameId: string) => emit('viewGame', gameId)
const closeCreateModal = () => emit('closeCreateModal')
const openCreateModal = () => emit('openCreateModal')
const handleNavigation = (view: string) => emit('navigate', view)
const updateNewGame = (value: any) => emit('updateNewGame', value)

// Funciones auxiliares para Bootstrap
const getBootstrapCardClass = (status: string) => {
  const baseClasses = 'border-start border-4'
  switch (status) {
    case 'waiting':
      return `${baseClasses} border-success`
    case 'started':
    case 'night':
    case 'day':
      return `${baseClasses} border-primary`
    case 'paused':
      return `${baseClasses} border-warning`
    case 'finished':
      return `${baseClasses} border-secondary opacity-75`
    default:
      return baseClasses
  }
}

const getStatusBadgeClass = (status: string) => {
  switch (status) {
    case 'waiting':
      return 'bg-success'
    case 'started':
    case 'night':
    case 'day':
      return 'bg-primary'
    case 'paused':
      return 'bg-warning'
    case 'finished':
      return 'bg-secondary'
    default:
      return 'bg-secondary'
  }
}
</script>

<style scoped>
.game-card-hover:hover {
  transform: translateY(-5px);
}
</style>
