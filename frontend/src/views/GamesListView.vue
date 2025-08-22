<template>
  <div class="min-vh-100" style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);">
  <!-- Navegación común -->
  <PageWithNav :show-admin="showAdmin" @navigate="handleNavigation">

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
              <div class="col-12 col-md-6 col-lg-4" v-for="game in games" :key="game.id">
                <GameCard
                  :game="game"
                  :loading="loading"
                  :canJoinGame="canJoinGame"
                  :canLeaveGame="canLeaveGame"
                  :canViewGame="canViewGame"
                  :canDeleteGame="canDeleteGame"
                  :getCreatorName="getCreatorName"
                  :formatDate="formatDate"
                  @join="joinGame"
                  @leave="leaveGame"
                  @view="viewGame"
                  @delete="deleteGame"
                />
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
  </PageWithNav>
  </div>
</template>

<script setup lang="ts">
import CreateGameModal from '../components/CreateGameModal.vue'
import PageWithNav from '../components/PageWithNav.vue'
import GameCard from '../components/GameCard.vue'
import type { Game, AuthUser } from '../types'
import { computed, toRefs } from 'vue'

// Props para recibir los datos y métodos del composable
interface Props {
  games: Game[]
  loading: boolean
  showCreateModal: boolean
  notification: any
  newGame: any
  playerOptions: number[]
  hasGames: boolean
  // Puede ser AuthUser o el store de auth (Pinia); permitimos también cualquier forma para compatibilidad
  auth: AuthUser | any
  canJoinGame: (game: Game) => boolean
  canLeaveGame: (game: Game) => boolean
  canViewGame: (game: Game) => boolean
  canDeleteGame: (game: Game) => boolean
  getCreatorName: (game: Game) => string
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

const props = defineProps<Props>()
const emit = defineEmits<Emits>()

// Keep prop reactivity: use toRefs so children react to parent ref changes
const {
  auth,
  games,
  loading,
  showCreateModal,
  notification,
  newGame,
  playerOptions,
  hasGames,
  getCreatorName,
  formatDate,
  canJoinGame,
  canLeaveGame,
  canViewGame,
  canDeleteGame
} = toRefs(props as any)

const showAdmin = computed(() => {
  const a: any = auth?.value ?? auth
  return a?.role === 'admin' || a?.isAdmin === true || a?.user?.role === 'admin'
})

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

// Helpers imported from composable: getBootstrapCardClass, getStatusBadgeClass, getStatusText
</script>

<style scoped>
.game-card-hover:hover {
  transform: translateY(-5px);
}
</style>
