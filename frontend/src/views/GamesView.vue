<template>
  <div class="games-view">
    <!-- Debug Info (temporal) -->
    <DebugGamesStore />

    <!-- Header de la página -->
    <div class="page-header">
      <div class="header-content">
        <h1 class="page-title">
          <i class="pi pi-users"></i>
          Gestión de Juegos
        </h1>
        <p class="page-subtitle">
          Únete a partidas existentes o crea tu propio juego
        </p>
      </div>

      <div class="header-actions">
        <div class="header-stats" v-if="!isLoading">
          <div class="stat-card">
            <i class="pi pi-play-circle"></i>
            <div class="stat-info">
              <span class="stat-number">{{ availableGames.length }}</span>
              <span class="stat-label">Disponibles</span>
            </div>
          </div>
          <div class="stat-card">
            <i class="pi pi-bookmark"></i>
            <div class="stat-info">
              <span class="stat-number">{{ myGames.length }}</span>
              <span class="stat-label">Mis Juegos</span>
            </div>
          </div>
        </div>

        <div class="user-actions">
          <div class="user-info">
            <i class="pi pi-user"></i>
            <span>{{ authStore.user?.username }}</span>
          </div>
          <Button
            label="Cerrar Sesión"
            icon="pi pi-sign-out"
            severity="secondary"
            size="small"
            @click="handleLogout"
          />
        </div>
      </div>
    </div>

    <!-- Navegación por pestañas -->
    <TabView v-model:activeIndex="activeTab" class="games-tabs">
      <TabPanel value="0" header="Todos los Juegos">
        <GamesList
          :show-my-games-only="false"
          @create-game="openCreateGameModal"
          @join-game="handleJoinGame"
          @view-game="handleViewGame"
          @enter-game="handleEnterGame"
          @delete-game="handleDeleteGame"
          @refresh="handleRefresh"
        />
      </TabPanel>

      <TabPanel value="1" header="Mis Juegos">
        <GamesList
          :show-my-games-only="true"
          @create-game="openCreateGameModal"
          @join-game="handleJoinGame"
          @view-game="handleViewGame"
          @enter-game="handleEnterGame"
          @delete-game="handleDeleteGame"
          @refresh="handleRefresh"
        />
      </TabPanel>
    </TabView>

    <!-- Modal para crear juego -->
    <CreateGameModal
      v-model:visible="showCreateModal"
      @game-created="handleCreateGame"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useToast } from 'primevue/usetoast'
import TabView from 'primevue/tabview'
import TabPanel from 'primevue/tabpanel'
import Button from 'primevue/button'
import Badge from 'primevue/badge'
import GamesList from '../components/games/GamesList.vue'
import CreateGameModal from '../components/games/CreateGameModal.vue'
import DebugGamesStore from '../components/DebugGamesStore.vue'
import { useGamesStore } from '../stores/games'
import { useAuthStore } from '../stores/auth'

// Composables
const router = useRouter()
const toast = useToast()

// Stores
const gamesStore = useGamesStore()
const authStore = useAuthStore()
const {
  isLoading,
  availableGames,
  myGames,
  fetchGames,
  createGame,
  joinGame,
  setCurrentGame
} = gamesStore

// Estado reactivo
const activeTab = ref(0)
const showCreateModal = ref(false)

// Métodos
const openCreateGameModal = () => {
  showCreateModal.value = true
}

const handleCreateGame = async (gameData: { name: string; max_players: number }) => {
  try {
    const newGame = await createGame(gameData)

    showCreateModal.value = false

    toast.add({
      severity: 'success',
      summary: 'Juego Creado',
      detail: `El juego "${newGame.name}" ha sido creado exitosamente`,
      life: 3000
    })

    // Navegar a la sala de juego
    router.push(`/game/${newGame.id}`)

  } catch (error: any) {
    toast.add({
      severity: 'error',
      summary: 'Error al Crear Juego',
      detail: error.response?.data?.detail || 'No se pudo crear el juego',
      life: 5000
    })
  }
}

const handleJoinGame = async (gameId: string) => {
  try {
    const success = await joinGame(gameId)

    if (success) {
      toast.add({
        severity: 'success',
        summary: 'Unido al Juego',
        detail: 'Te has unido al juego exitosamente',
        life: 3000
      })

      // Navegar a la sala de juego
      router.push(`/game/${gameId}`)
    }

  } catch (error: any) {
    toast.add({
      severity: 'error',
      summary: 'Error al Unirse',
      detail: error.response?.data?.detail || 'No se pudo unir al juego',
      life: 5000
    })
  }
}

const handleViewGame = (gameId: string) => {
  // Navegar a vista de solo lectura (espectador)
  router.push(`/game/${gameId}?mode=spectator`)
}

const handleEnterGame = (gameId: string) => {
  // Navegar al juego
  router.push(`/game/${gameId}`)
}

const handleDeleteGame = async (gameId: string) => {
  try {
    // Confirmar con el usuario
    const confirmed = window.confirm('¿Estás seguro de que quieres eliminar esta partida? Esta acción no se puede deshacer.')

    if (!confirmed) return

    const success = await gamesStore.deleteGame(gameId)

    if (success) {
      toast.add({
        severity: 'success',
        summary: 'Partida Eliminada',
        detail: 'La partida ha sido eliminada exitosamente',
        life: 3000
      })
    } else {
      toast.add({
        severity: 'error',
        summary: 'Error al Eliminar',
        detail: 'No se pudo eliminar la partida',
        life: 5000
      })
    }

  } catch (error: any) {
    toast.add({
      severity: 'error',
      summary: 'Error al Eliminar',
      detail: error.response?.data?.detail || 'No se pudo eliminar la partida',
      life: 5000
    })
  }
}

const handleRefresh = async () => {
  try {
    await fetchGames()

    toast.add({
      severity: 'info',
      summary: 'Actualizado',
      detail: 'Lista de juegos actualizada',
      life: 2000
    })

  } catch (error) {
    toast.add({
      severity: 'warn',
      summary: 'Aviso',
      detail: 'No se pudo actualizar la lista de juegos',
      life: 3000
    })
  }
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
    router.push('/login')

  } catch (error) {
    toast.add({
      severity: 'error',
      summary: 'Error',
      detail: 'No se pudo cerrar la sesión',
      life: 3000
    })
  }
}

// Lifecycle
onMounted(async () => {
  // Cargar juegos al montar el componente
  await fetchGames()
})
</script>

<style src="../assets/styles/games-view.css" scoped></style>
