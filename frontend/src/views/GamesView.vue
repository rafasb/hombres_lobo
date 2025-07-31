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
import Badge from 'primevue/badge'
import GamesList from '../components/games/GamesList.vue'
import CreateGameModal from '../components/games/CreateGameModal.vue'
import DebugGamesStore from '../components/DebugGamesStore.vue'
import { useGamesStore } from '../stores/games'

// Composables
const router = useRouter()
const toast = useToast()

// Store
const gamesStore = useGamesStore()
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

// Lifecycle
onMounted(async () => {
  // Cargar juegos al montar el componente
  await fetchGames()
})
</script>

<style scoped>
.games-view {
  max-width: 1200px;
  margin: 0 auto;
  padding: 1rem;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 2rem;
  flex-wrap: wrap;
  gap: 1rem;
}

.header-content {
  flex: 1;
  min-width: 300px;
}

.page-title {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  margin: 0 0 0.5rem 0;
  color: var(--primary-color);
  font-size: 2rem;
  font-weight: 700;
}

.page-subtitle {
  color: var(--text-color-secondary);
  margin: 0;
  font-size: 1.1rem;
}

.header-stats {
  display: flex;
  gap: 1rem;
}

.stat-card {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  background: var(--surface-50);
  border: 1px solid var(--surface-200);
  border-radius: 8px;
  padding: 1rem;
  min-width: 120px;
}

.stat-card i {
  font-size: 1.5rem;
  color: var(--primary-color);
}

.stat-info {
  display: flex;
  flex-direction: column;
}

.stat-number {
  font-size: 1.5rem;
  font-weight: 700;
  color: var(--text-color);
  line-height: 1.2;
}

.stat-label {
  font-size: 0.875rem;
  color: var(--text-color-secondary);
}

.games-tabs {
  margin-top: 1rem;
}

.games-tabs :deep(.p-tabview-nav-link) {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.games-tabs :deep(.p-tabview-panels) {
  padding: 1.5rem 0 0 0;
}

/* Responsive */
@media (max-width: 768px) {
  .games-view {
    padding: 0.5rem;
  }

  .page-header {
    flex-direction: column;
    align-items: stretch;
  }

  .header-stats {
    justify-content: space-around;
  }

  .stat-card {
    flex: 1;
    min-width: auto;
    justify-content: center;
  }

  .page-title {
    font-size: 1.5rem;
  }

  .page-subtitle {
    font-size: 1rem;
  }
}

@media (max-width: 480px) {
  .header-stats {
    flex-direction: column;
  }

  .stat-card {
    justify-content: flex-start;
  }
}
</style>
