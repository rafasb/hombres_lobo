<template>
  <div class="game-lobby-view">
    <!        <div class="game-actions">
          <!-- Solo el host puede iniciar el juego -->
          <Button
            v-if="isHost && canStartGame"
            :label="isConnected ? 'Iniciar Juego (Tiempo Real)' : 'Iniciar Juego'"
            icon="pi pi-play"
            @click="isConnected ? startGameRealtime() : startGame()"
            :loading="isStartingGame"
            :class="isConnected ? 'p-button-success' : 'p-button-warning'"
          /> state -->
    <div v-if="isLoading" class="loading-container">
      <ProgressSpinner />
      <p>Cargando sala de espera...</p>
    </div>

    <!-- Error state -->
    <div v-else-if="error" class="error-container">
      <Message severity="error" :closable="false">
        <div class="error-content">
          <h3>Error al cargar el juego</h3>
          <p>{{ error }}</p>
          <div class="error-actions">
            <Button label="Reintentar" @click="loadGameData" class="p-button-sm" />
            <Button label="Volver a Juegos" @click="goToGames" class="p-button-sm p-button-text" />
          </div>
        </div>
      </Message>
    </div>

    <!-- Main lobby interface -->
    <div v-else-if="currentGame" class="lobby-container">
      <!-- Game header -->
      <div class="game-header">
        <div class="game-info">
          <h1 class="game-title">
            <i class="pi pi-users"></i>
            {{ currentGame.name }}
            <!-- WebSocket connection indicator -->
            <Tag
              v-if="isConnected"
              value="Tiempo Real"
              severity="success"
              icon="pi pi-circle-fill"
              class="realtime-indicator"
              style="margin-left: 1rem; font-size: 0.75rem;"
            />
          </h1>
          <div class="game-meta">
            <Tag :value="gameStatusLabel" :severity="gameStatusSeverity" />
            <span class="game-id">ID: {{ currentGame.id.slice(-8) }}</span>
            <span class="created-by">
              Creado por: <strong>{{ gameCreator?.username || 'Desconocido' }}</strong>
            </span>
          </div>
        </div>

        <div class="game-actions">
          <!-- Solo el host puede iniciar el juego -->
          <Button
            v-if="isHost && canStartGame"
            label="Iniciar Juego"
            icon="pi pi-play"
            @click="startGame"
            :loading="isStartingGame"
            class="p-button-success"
          />

          <!-- Botón para salir del juego -->
          <Button
            label="Salir del Juego"
            icon="pi pi-sign-out"
            @click="leaveGame"
            :loading="isLeavingGame"
            class="p-button-outlined p-button-secondary"
          />
        </div>
      </div>

      <!-- Main content grid -->
      <div class="lobby-content">
        <!-- Players section -->
        <div class="players-section">
          <Card class="players-card">
            <template #header>
              <div class="section-header">
                <h3>
                  <i class="pi pi-users"></i>
                  Jugadores ({{ currentGame.players.length }}/{{ currentGame.max_players }})
                </h3>
                <div class="players-progress">
                  <ProgressBar
                    :value="playersPercentage"
                    :showValue="false"
                    class="players-bar"
                  />
                  <span class="progress-text">
                    {{ currentGame.players.length }} de {{ currentGame.max_players }}
                  </span>
                </div>
              </div>
            </template>
            <template #content>
              <PlayersList
                :players="currentGame.players"
                :host-id="currentGame.creator_id"
                :current-user-id="authStore.user?.id.toString()"
              />
            </template>
          </Card>
        </div>

        <!-- Game settings section -->
        <div class="settings-section" v-if="isHost">
          <Card class="settings-card">
            <template #header>
              <h3>
                <i class="pi pi-cog"></i>
                Configuración del Juego
              </h3>
            </template>
            <template #content>
              <GameSettings
                :game="currentGame"
                :can-edit="isHost && currentGame.status === 'waiting'"
                @update-settings="handleUpdateSettings"
              />
            </template>
          </Card>
        </div>

        <!-- Game info section -->
        <div class="info-section">
          <Card class="info-card">
            <template #header>
              <h3>
                <i class="pi pi-info-circle"></i>
                Información del Juego
              </h3>
            </template>
            <template #content>
              <div class="game-info-content">
                <div class="info-item">
                  <span class="info-label">Estado:</span>
                  <Tag :value="gameStatusLabel" :severity="gameStatusSeverity" />
                </div>
                <div class="info-item">
                  <span class="info-label">Jugadores necesarios:</span>
                  <span class="info-value">Mínimo 4 jugadores</span>
                </div>
                <div class="info-item">
                  <span class="info-label">Creado el:</span>
                  <span class="info-value">{{ formatDate(currentGame.created_at) }}</span>
                </div>
                <div class="info-item" v-if="currentGame.current_round > 0">
                  <span class="info-label">Ronda actual:</span>
                  <span class="info-value">{{ currentGame.current_round }}</span>
                </div>

                <!-- Game rules info -->
                <Divider />
                <div class="rules-section">
                  <h4>
                    <i class="pi pi-book"></i>
                    Roles en esta partida
                  </h4>
                  <div class="roles-info">
                    <div v-for="(roleInfo, roleName) in currentGame.roles" :key="roleName" class="role-item">
                      <span class="role-name">{{ roleName }}</span>
                      <Badge :value="roleInfo.role" />
                    </div>
                  </div>
                </div>
              </div>
            </template>
          </Card>
        </div>
      </div>

      <!-- Status messages -->
      <div class="status-messages" v-if="statusMessage">
        <Message :severity="statusMessage.severity" :closable="false">
          {{ statusMessage.text }}
        </Message>
      </div>
    </div>

    <!-- No game found -->
    <div v-else class="no-game-container">
      <Message severity="warn" :closable="false">
        <h3>Juego no encontrado</h3>
        <p>El juego que buscas no existe o ya no está disponible.</p>
        <Button label="Volver a Juegos" @click="goToGames" class="p-button-sm" />
      </Message>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useGamesStore } from '../stores/games'
import { useAuthStore } from '../stores/auth'
import { useToast } from 'primevue/usetoast'
import { useGameWebSocket } from '../composables/useGameWebSocket'

// PrimeVue components
import Card from 'primevue/card'
import Button from 'primevue/button'
import Message from 'primevue/message'
import Tag from 'primevue/tag'
import Badge from 'primevue/badge'
import ProgressSpinner from 'primevue/progressspinner'
import ProgressBar from 'primevue/progressbar'
import Divider from 'primevue/divider'

// Custom components
import PlayersList from '../components/games/PlayersList.vue'
import GameSettings from '../components/games/GameSettings.vue'

// Stores and utilities
const route = useRoute()
const router = useRouter()
const gamesStore = useGamesStore()
const authStore = useAuthStore()
const toast = useToast()

// WebSocket integration
const {
  isConnected,
  isConnecting,
  connectionError,
  gameState,
  connectToGame,
  disconnect,
  startGame: startGameWebSocket,
  joinGame: joinGameWebSocket,
  getStatus
} = useGameWebSocket()

// Reactive state
const isLoading = ref(true)
const error = ref<string | null>(null)
const isLeavingGame = ref(false)
const isStartingGame = ref(false)
const refreshInterval = ref<number | null>(null)

// Status message for user feedback
const statusMessage = ref<{severity: string, text: string} | null>(null)

// Computed properties
const gameId = computed(() => route.params.gameId as string)
const currentGame = computed(() => gamesStore.currentGame)
const isHost = computed(() => {
  return currentGame.value && authStore.user &&
         currentGame.value.creator_id === authStore.user.id.toString()
})

const gameCreator = computed(() => {
  if (!currentGame.value) return null
  return currentGame.value.players.find(p => p.id === currentGame.value!.creator_id)
})

const canStartGame = computed(() => {
  if (!currentGame.value) return false
  return currentGame.value.status === 'waiting' &&
         currentGame.value.players.length >= 4
})

const playersPercentage = computed(() => {
  if (!currentGame.value) return 0
  return (currentGame.value.players.length / currentGame.value.max_players) * 100
})

const gameStatusLabel = computed(() => {
  if (!currentGame.value) return 'Desconocido'
  const statusLabels = {
    'waiting': 'Esperando jugadores',
    'started': 'En progreso',
    'night': 'Fase nocturna',
    'day': 'Fase diurna',
    'paused': 'Pausado',
    'finished': 'Finalizado'
  }
  return statusLabels[currentGame.value.status] || currentGame.value.status
})

const gameStatusSeverity = computed(() => {
  if (!currentGame.value) return 'secondary'
  const severityMap = {
    'waiting': 'info',
    'started': 'success',
    'night': 'warning',
    'day': 'success',
    'paused': 'warning',
    'finished': 'secondary'
  }
  return severityMap[currentGame.value.status] || 'secondary'
})

// Methods
const loadGameData = async () => {
  try {
    isLoading.value = true
    error.value = null

    const success = await gamesStore.fetchGameDetails(gameId.value)
    if (!success) {
      error.value = 'No se pudo cargar la información del juego'
      return
    }

    // Check if user is in the game
    if (currentGame.value && authStore.user) {
      const isPlayerInGame = currentGame.value.players.some(
        p => p.id === authStore.user!.id.toString()
      )

      if (!isPlayerInGame) {
        statusMessage.value = {
          severity: 'warn',
          text: 'No estás participando en este juego. ¿Quieres unirte?'
        }
      }
    }

  } catch (err: any) {
    error.value = err.message || 'Error desconocido al cargar el juego'
  } finally {
    isLoading.value = false
  }
}

const startGame = async () => {
  if (!currentGame.value || !canStartGame.value) return

  try {
    isStartingGame.value = true
    const success = await gamesStore.startGame(currentGame.value.id)

    if (success) {
      toast.add({
        severity: 'success',
        summary: 'Juego iniciado',
        detail: '¡La partida ha comenzado!',
        life: 3000
      })

      // Redirect to game play view when that's implemented
      // router.push(`/games/${currentGame.value.id}/play`)

    } else {
      toast.add({
        severity: 'error',
        summary: 'Error',
        detail: 'No se pudo iniciar el juego',
        life: 5000
      })
    }
  } catch (err: any) {
    toast.add({
      severity: 'error',
      summary: 'Error',
      detail: err.message || 'Error al iniciar el juego',
      life: 5000
    })
  } finally {
    isStartingGame.value = false
  }
}

// WebSocket specific functions
const reconnectWebSocket = async () => {
  if (gameId.value) {
    await connectToGame(gameId.value)
    if (isConnected) {
      toast.add({
        severity: 'success',
        summary: 'Conectado',
        detail: 'Conexión en tiempo real restablecida',
        life: 3000
      })
    }
  }
}

const startGameRealtime = async () => {
  if (!isConnected) {
    toast.add({
      severity: 'warn',
      summary: 'Sin conexión',
      detail: 'No hay conexión en tiempo real para iniciar el juego',
      life: 5000
    })
    return
  }

  try {
    isStartingGame.value = true
    const success = startGameWebSocket()

    if (success) {
      toast.add({
        severity: 'info',
        summary: 'Iniciando juego',
        detail: 'Enviando solicitud de inicio...',
        life: 3000
      })
    }
  } catch (err: any) {
    toast.add({
      severity: 'error',
      summary: 'Error',
      detail: 'Error enviando solicitud de inicio',
      life: 5000
    })
  } finally {
    setTimeout(() => {
      isStartingGame.value = false
    }, 2000)
  }
}

const leaveGame = async () => {
  if (!currentGame.value) return

  try {
    isLeavingGame.value = true
    const success = await gamesStore.leaveGame(currentGame.value.id)

    if (success) {
      toast.add({
        severity: 'info',
        summary: 'Has salido del juego',
        detail: 'Volviendo a la lista de juegos...',
        life: 3000
      })

      // Redirect back to games list
      router.push('/games')
    } else {
      toast.add({
        severity: 'error',
        summary: 'Error',
        detail: 'No se pudo salir del juego',
        life: 5000
      })
    }
  } catch (err: any) {
    toast.add({
      severity: 'error',
      summary: 'Error',
      detail: err.message || 'Error al salir del juego',
      life: 5000
    })
  } finally {
    isLeavingGame.value = false
  }
}

const handleUpdateSettings = async (settings: any) => {
  if (!currentGame.value) return

  try {
    const success = await gamesStore.updateGameSettings(currentGame.value.id, settings)

    if (success) {
      toast.add({
        severity: 'success',
        summary: 'Configuración actualizada',
        detail: 'Los cambios se han guardado correctamente',
        life: 3000
      })
    } else {
      toast.add({
        severity: 'error',
        summary: 'Error',
        detail: 'No se pudo actualizar la configuración',
        life: 5000
      })
    }
  } catch (err: any) {
    toast.add({
      severity: 'error',
      summary: 'Error',
      detail: err.message || 'Error al actualizar configuración',
      life: 5000
    })
  }
}

const goToGames = () => {
  router.push('/games')
}

const formatDate = (dateStr: string) => {
  return new Date(dateStr).toLocaleString('es-ES', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  })
}

// Auto-refresh game data every 5 seconds
const startAutoRefresh = () => {
  refreshInterval.value = setInterval(async () => {
    if (currentGame.value && !isLoading.value) {
      await gamesStore.fetchGameDetails(gameId.value)
    }
  }, 5000)
}

const stopAutoRefresh = () => {
  if (refreshInterval.value) {
    clearInterval(refreshInterval.value)
    refreshInterval.value = null
  }
}

// Lifecycle
onMounted(async () => {
  await loadGameData()
  startAutoRefresh()
})

onUnmounted(() => {
  stopAutoRefresh()
})
</script>

<style src="../assets/styles/game-lobby-view.css" scoped></style>
