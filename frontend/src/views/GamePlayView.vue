<template>
  <div class="game-play-view">
    <!-- Loading state -->
    <div v-if="isConnecting || isLoading" class="loading-overlay">
      <div class="loading-content">
        <ProgressSpinner />
        <h3>{{ isConnecting ? 'Conectando al juego...' : 'Cargando...' }}</h3>
        <p>Por favor espera mientras se establece la conexión</p>
      </div>
    </div>

    <!-- Error state -->
    <div v-else-if="connectionError || error" class="error-overlay">
      <div class="error-content">
        <i class="pi pi-exclamation-triangle text-6xl text-red-500 mb-4"></i>
        <h3>Error de conexión</h3>
        <p>{{ connectionError || error }}</p>
        <div class="error-actions">
          <Button
            label="Reintentar conexión"
            icon="pi pi-refresh"
            @click="handleReconnect"
            :loading="isConnecting"
          />
          <Button
            label="Volver al lobby"
            icon="pi pi-arrow-left"
            severity="secondary"
            @click="goToLobby"
          />
        </div>
      </div>
    </div>

    <!-- Main game content -->
    <div v-else-if="isConnected && gameState.gameId" class="game-content">
      <!-- Header con información del juego -->
      <div class="game-header">
        <div class="game-title">
          <h2>
            <i class="pi pi-moon mr-2"></i>
            Hombres Lobo - Sala {{ gameState.gameId.slice(-4) }}
          </h2>
          <div class="connection-status">
            <div class="connection-indicator connected"></div>
            <span>Conectado</span>
          </div>
        </div>

        <div class="game-controls">
          <Button
            icon="pi pi-cog"
            severity="secondary"
            text
            @click="showSettings = true"
            title="Configuración"
          />
          <Menu ref="userMenu" :model="userMenuItems" popup />
          <Button
            icon="pi pi-user"
            severity="secondary"
            text
            @click="toggleUserMenu"
            aria-haspopup="true"
            aria-controls="user_menu"
            title="Opciones de usuario"
          />
        </div>
      </div>

      <!-- Game Phase Indicator -->
      <GamePhaseIndicator />

      <!-- Main game grid -->
      <div class="game-grid">
        <!-- Left column: Players and Chat -->
        <div class="left-column">
          <!-- Players Grid -->
          <PlayersGrid />

          <!-- Chat Component (cuando esté implementado) -->
          <div class="chat-placeholder">
            <div class="chat-header">
              <h4>
                <i class="pi pi-comments mr-2"></i>
                Chat del juego
              </h4>
            </div>
            <div class="chat-content">
              <p class="text-center text-500 p-4">
                Chat en desarrollo...
              </p>
            </div>
          </div>
        </div>

        <!-- Right column: Voting and Actions -->
        <div class="right-column">
          <!-- Voting Panel -->
          <VotingPanel v-if="isVotingActive || voteResults" />

          <!-- Role Actions Panel (placeholder) -->
          <div v-if="isNight && isUserAlive" class="role-actions-placeholder">
            <div class="role-actions-header">
              <h4>
                <i class="pi pi-moon mr-2"></i>
                Acciones Nocturnas
              </h4>
            </div>
            <div class="role-actions-content">
              <Message severity="info" :closable="false">
                <i class="pi pi-info-circle mr-2"></i>
                Las acciones de roles especiales estarán disponibles próximamente
              </Message>
            </div>
          </div>

          <!-- Game Info Panel -->
          <div class="info-panel">
            <h4>
              <i class="pi pi-info-circle mr-2"></i>
              Información del Juego
            </h4>

            <div class="info-items">
              <div class="info-item">
                <span class="info-label">Jugadores:</span>
                <span class="info-value">{{ players.length }}</span>
              </div>

              <div class="info-item">
                <span class="info-label">Vivos:</span>
                <span class="info-value text-green-600">{{ livingPlayers.length }}</span>
              </div>

              <div class="info-item">
                <span class="info-label">Muertos:</span>
                <span class="info-value text-red-600">{{ deadPlayers.length }}</span>
              </div>

              <div class="info-item">
                <span class="info-label">Fase:</span>
                <span class="info-value">{{ phaseInfo.name }}</span>
              </div>
            </div>

            <!-- Debug info (solo en development) -->
            <div v-if="isDevelopment" class="debug-info">
              <Divider />
              <h5>Debug Info:</h5>
              <pre class="debug-text">{{ debugInfo }}</pre>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- No game state -->
    <div v-else class="no-game-content">
      <div class="no-game-message">
        <i class="pi pi-gamepad text-6xl text-400 mb-4"></i>
        <h3>No hay juego activo</h3>
        <p>No se encontró información del juego. Verifica la URL o vuelve al lobby.</p>
        <Button
          label="Ir al lobby"
          icon="pi pi-home"
          @click="goToLobby"
        />
      </div>
    </div>

    <!-- Settings Dialog -->
    <Dialog
      v-model:visible="showSettings"
      header="Configuración del Juego"
      :modal="true"
      :closable="true"
      :style="{ width: '400px' }"
    >
      <div class="settings-content">
        <div class="setting-item">
          <label class="setting-label">
            <Checkbox v-model="settings.soundEnabled" binary />
            Habilitar sonidos
          </label>
        </div>

        <div class="setting-item">
          <label class="setting-label">
            <Checkbox v-model="settings.notificationsEnabled" binary />
            Habilitar notificaciones
          </label>
        </div>

        <div class="setting-item">
          <label class="setting-label">Volumen:</label>
          <Slider
            v-model="settings.volume"
            :min="0"
            :max="100"
            class="mt-2"
          />
        </div>
      </div>

      <template #footer>
        <Button
          label="Cerrar"
          icon="pi pi-times"
          @click="showSettings = false"
        />
      </template>
    </Dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useRealtimeGameStore } from '@/stores/realtime-game'
import { useAuthStore } from '@/stores/auth'
import { useGamePhase } from '@/composables/useGamePhase'
import { useVoting } from '@/composables/useVoting'
import { useToast } from 'primevue/usetoast'

import GamePhaseIndicator from '@/components/game/GamePhaseIndicator.vue'
import VotingPanel from '@/components/game/VotingPanel.vue'
import PlayersGrid from '@/components/game/PlayersGrid.vue'

import Button from 'primevue/button'
import Menu from 'primevue/menu'
import ProgressSpinner from 'primevue/progressspinner'
import Dialog from 'primevue/dialog'
import Checkbox from 'primevue/checkbox'
import Slider from 'primevue/slider'
import Message from 'primevue/message'
import Divider from 'primevue/divider'

// Importar estilos CSS
import '@/assets/styles/game-play-view.css'

const route = useRoute()
const router = useRouter()
const toast = useToast()

const realtimeGameStore = useRealtimeGameStore()
const authStore = useAuthStore()

const {
  isNight,
  phaseInfo
} = useGamePhase()

const {
  isVotingActive,
  voteResults
} = useVoting()

// Estado local
const showSettings = ref(false)
const userMenu = ref()
const settings = ref({
  soundEnabled: true,
  notificationsEnabled: true,
  volume: 50
})

// Menú del usuario (computed para actualizarse reactivamente)
const userMenuItems = computed(() => {
  const baseItems: Array<any> = [
    {
      label: `Usuario: ${authStore.user?.username}`,
      disabled: true,
      class: 'user-info-menu-item'
    },
    {
      separator: true
    }
  ]

  // Añadir botón de reinicio solo para el creador del juego
  const currentUserId = authStore.user?.id
  const gameData = gameState.value

  if (currentUserId && gameData?.gameId) {
    // Aquí podrías añadir lógica para verificar si es el creador
    // Por ahora lo añadimos para todos (para testing)
    baseItems.push({
      label: 'Reiniciar partida',
      icon: 'pi pi-refresh',
      command: () => handleRestartGame(),
      class: 'restart-game-menu-item'
    })

    baseItems.push({
      separator: true
    })
  }

  baseItems.push(
    {
      label: 'Salir del juego',
      icon: 'pi pi-sign-out',
      command: () => handleDisconnect()
    },
    {
      label: 'Cerrar sesión',
      icon: 'pi pi-power-off',
      command: () => handleLogout()
    }
  )

  return baseItems
})

// Computeds
const gameState = computed(() => realtimeGameStore.gameState)
const isConnected = computed(() => realtimeGameStore.isConnected)
const isConnecting = computed(() => realtimeGameStore.isConnecting)
const isLoading = computed(() => realtimeGameStore.isLoading)
const connectionError = computed(() => realtimeGameStore.connectionError)
const error = computed(() => realtimeGameStore.error)
const players = computed(() => gameState.value.players)
const livingPlayers = computed(() => gameState.value.livingPlayers)
const deadPlayers = computed(() => gameState.value.deadPlayers)
const isUserAlive = computed(() => realtimeGameStore.isUserAlive)

const isDevelopment = computed(() => {
  return import.meta.env.DEV
})

const debugInfo = computed(() => {
  if (!isDevelopment.value) return null

  return {
    gameId: gameState.value.gameId,
    phase: gameState.value.phase,
    connectedPlayers: gameState.value.connectedPlayers.length,
    votingSession: gameState.value.votingSession?.session_id || null,
    userVote: gameState.value.userVote,
    isHost: gameState.value.isHost
  }
})

// Lifecycle
onMounted(async () => {
  const gameId = route.params.gameId as string
  console.log('GamePlayView mounted with gameId:', gameId)

  if (!gameId) {
    toast.add({
      severity: 'error',
      summary: 'Error',
      detail: 'ID de juego no válido',
      life: 3000
    })
    await router.push('/games')
    return
  }

  // Conectar al juego
  if (!isConnected.value) {
    try {
      console.log('Intentando conectar al juego:', gameId)
      await realtimeGameStore.connectToGame(gameId)

      // Unirse al juego y solicitar estado después de conectar
      console.log('Conexión establecida, uniéndose al juego')
      setTimeout(() => {
        realtimeGameStore.requestJoinGame()
        realtimeGameStore.requestGameStatus()
      }, 1000)

    } catch (error) {
      console.error('Error conectando al juego:', error)
      toast.add({
        severity: 'error',
        summary: 'Error de conexión',
        detail: 'No se pudo conectar al juego',
        life: 5000
      })
    }
  }
})

onUnmounted(() => {
  // Limpiar la conexión si es necesario
  if (isConnected.value) {
    realtimeGameStore.disconnectFromGame()
  }
})

// Métodos
const handleReconnect = async () => {
  const gameId = route.params.gameId as string
  if (gameId) {
    try {
      await realtimeGameStore.connectToGame(gameId)

      toast.add({
        severity: 'success',
        summary: 'Reconectado',
        detail: 'Conexión restablecida exitosamente',
        life: 3000
      })
    } catch (error) {
      toast.add({
        severity: 'error',
        summary: 'Error de reconexión',
        detail: 'No se pudo restablecer la conexión',
        life: 3000
      })
    }
  }
}

const handleDisconnect = async () => {
  try {
    await realtimeGameStore.disconnectFromGame()
    await router.push('/games')

    toast.add({
      severity: 'info',
      summary: 'Desconectado',
      detail: 'Has salido del juego',
      life: 3000
    })
  } catch (error) {
    console.error('Error al desconectar:', error)
  }
}

const toggleUserMenu = (event: Event) => {
  userMenu.value.toggle(event)
}

const handleLogout = async () => {
  try {
    await authStore.logout()

    toast.add({
      severity: 'success',
      summary: 'Sesión Cerrada',
      detail: 'Has cerrado sesión exitosamente',
      life: 3000
    })

    // Redirigir a la página de login
    await router.push('/login')

  } catch (error) {
    toast.add({
      severity: 'error',
      summary: 'Error',
      detail: 'No se pudo cerrar la sesión',
      life: 3000
    })
  }
}

const goToLobby = async () => {
  await router.push('/games')
}

const handleRestartGame = async () => {
  try {
    // Confirmar con el usuario
    const confirmed = window.confirm('¿Estás seguro de que quieres reiniciar la partida? Esta acción no se puede deshacer.')

    if (!confirmed) return

    // Enviar comando de reinicio al WebSocket
    const success = realtimeGameStore.requestRestartGame()

    if (success) {
      toast.add({
        severity: 'info',
        summary: 'Reiniciando partida...',
        detail: 'Se ha enviado la solicitud de reinicio',
        life: 3000
      })
    } else {
      toast.add({
        severity: 'error',
        summary: 'Error',
        detail: 'No se pudo enviar la solicitud de reinicio',
        life: 3000
      })
    }

  } catch (error) {
    console.error('Error al reiniciar partida:', error)
    toast.add({
      severity: 'error',
      summary: 'Error',
      detail: 'No se pudo reiniciar la partida',
      life: 3000
    })
  }
}
</script>

<style>
/* Estilos específicos que requieren :deep() para PrimeVue */
:deep(.restart-game-menu-item) {
  color: var(--orange-500) !important;
}

:deep(.restart-game-menu-item:hover) {
  background-color: var(--orange-50) !important;
  color: var(--orange-600) !important;
}

:deep(.user-info-menu-item) {
  font-weight: 600;
  background: var(--surface-100);
  border-radius: 4px;
  margin-bottom: 4px;
}

:deep(.p-menu .p-menuitem-link) {
  border-radius: 4px;
}
</style>
