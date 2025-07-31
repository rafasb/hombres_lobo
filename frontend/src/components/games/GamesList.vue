<template>
  <div class="games-list">
    <DataTable
      :value="games"
      :loading="isLoading"
      paginator
      :rows="10"
      :rowsPerPageOptions="[5, 10, 20]"
      paginatorTemplate="RowsPerPageDropdown FirstPageLink PrevPageLink CurrentPageReport NextPageLink LastPageLink"
      currentPageReportTemplate="{first} a {last} de {totalRecords} juegos"
      dataKey="id"
      :globalFilterFields="['name', 'creator_id']"
      responsiveLayout="scroll"
      class="p-datatable-gridlines"
    >
      <template #header>
        <div class="table-header">
          <h2 class="table-title">
            <i class="pi pi-users"></i>
            Juegos Disponibles
          </h2>
          <div class="table-controls">
            <span class="p-input-icon-left">
              <i class="pi pi-search"></i>
              <InputText
                v-model="filters['global'].value"
                placeholder="Buscar juegos..."
                class="search-input"
              />
            </span>
            <Button
              label="Nuevo Juego"
              icon="pi pi-plus"
              class="p-button-success"
              @click="$emit('create-game')"
            />
            <Button
              label="Actualizar"
              icon="pi pi-refresh"
              class="p-button-outlined"
              @click="$emit('refresh')"
              :loading="isLoading"
            />
          </div>
        </div>
      </template>

      <template #empty>
        <div class="empty-state">
          <i class="pi pi-users" style="font-size: 3rem; color: var(--surface-500)"></i>
          <p>No hay juegos disponibles</p>
          <Button
            label="Crear el primer juego"
            icon="pi pi-plus"
            class="p-button-text"
            @click="$emit('create-game')"
          />
        </div>
      </template>

      <Column field="name" header="Nombre del Juego" sortable style="min-width: 200px">
        <template #body="{ data }">
          <div class="game-name">
            <i class="pi pi-bookmark"></i>
            <span class="name">{{ data.name }}</span>
          </div>
        </template>
      </Column>

      <Column field="players" header="Jugadores" sortable style="min-width: 120px">
        <template #body="{ data }">
          <div class="players-info">
            <i class="pi pi-users"></i>
            <span class="count">{{ data.players.length }}/{{ data.max_players }}</span>
          </div>
        </template>
      </Column>

      <Column field="status" header="Estado" sortable style="min-width: 120px">
        <template #body="{ data }">
          <Tag
            :value="getStatusLabel(data.status)"
            :severity="getStatusSeverity(data.status)"
            :icon="getStatusIcon(data.status)"
          />
        </template>
      </Column>

      <Column field="created_at" header="Creado" sortable style="min-width: 150px">
        <template #body="{ data }">
          <span class="date">{{ formatDate(data.created_at) }}</span>
        </template>
      </Column>

      <Column header="Acciones" style="min-width: 160px">
        <template #body="{ data }">
          <div class="action-buttons">
            <Button
              v-if="canJoinGame(data)"
              label="Unirse"
              icon="pi pi-sign-in"
              class="p-button-sm p-button-success"
              @click="$emit('join-game', data.id)"
            />
            <Button
              v-if="canViewGame(data)"
              label="Ver"
              icon="pi pi-eye"
              class="p-button-sm p-button-outlined"
              @click="$emit('view-game', data.id)"
            />
            <Button
              v-if="canEnterGame(data)"
              label="Entrar"
              icon="pi pi-arrow-right"
              class="p-button-sm"
              @click="$emit('enter-game', data.id)"
            />
          </div>
        </template>
      </Column>
    </DataTable>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import DataTable from 'primevue/datatable'
import Column from 'primevue/column'
import Button from 'primevue/button'
import InputText from 'primevue/inputtext'
import Tag from 'primevue/tag'
import { useGamesStore } from '../../stores/games'
import { useAuthStore } from '../../stores/auth'

// Props
interface Props {
  showMyGamesOnly?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  showMyGamesOnly: false
})

// Emits
const emit = defineEmits<{
  'create-game': []
  'join-game': [gameId: string]
  'view-game': [gameId: string]
  'enter-game': [gameId: string]
  'refresh': []
}>()

// Store
const gamesStore = useGamesStore()
const authStore = useAuthStore()
const { isLoading } = gamesStore

// Computed
const games = computed(() => {
  return props.showMyGamesOnly ? gamesStore.myGames : gamesStore.availableGames
})

// Filtros para la tabla
const filters = ref({
  global: { value: null, matchMode: 'contains' }
})

// Helper para obtener ID del usuario actual
const getCurrentUserId = (): string => {
  return authStore.user?.id?.toString() || ''
}

// Funciones de utilidad
const getStatusLabel = (status: string): string => {
  const labels: Record<string, string> = {
    waiting: 'Esperando',
    started: 'En Juego',
    night: 'Noche',
    day: 'Día',
    paused: 'Pausado',
    finished: 'Finalizado'
  }
  return labels[status] || status
}

const getStatusSeverity = (status: string): string => {
  const severities: Record<string, string> = {
    waiting: 'success',
    started: 'info',
    night: 'warning',
    day: 'warning',
    paused: 'warning',
    finished: 'secondary'
  }
  return severities[status] || 'info'
}

const getStatusIcon = (status: string): string => {
  const icons: Record<string, string> = {
    waiting: 'pi-clock',
    started: 'pi-play',
    night: 'pi-moon',
    day: 'pi-sun',
    paused: 'pi-pause',
    finished: 'pi-check'
  }
  return icons[status] || 'pi-info-circle'
}

const formatDate = (dateString: string): string => {
  return new Date(dateString).toLocaleDateString('es-ES', {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  })
}

const canJoinGame = (game: any): boolean => {
  const userId = getCurrentUserId()
  return (
    game.status === 'waiting' &&
    game.players.length < game.max_players &&
    !game.players.some((player: any) => player.id === userId) &&
    game.creator_id !== userId
  )
}

const canViewGame = (game: any): boolean => {
  // Solo los administradores pueden ver juegos en curso
  const userRole = authStore.user?.role
  return userRole === 'admin' && game.status !== 'waiting'
}

const canEnterGame = (game: any): boolean => {
  const userId = getCurrentUserId()
  return (
    game.players.some((player: any) => player.id === userId) ||
    game.creator_id === userId
  )
}

// Lifecycle
onMounted(() => {
  // Los datos se cargarán desde el componente padre
})
</script>

<style scoped>
.games-list {
  width: 100%;
}

.table-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 1rem;
  margin-bottom: 1rem;
}

.table-title {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin: 0;
  color: var(--primary-color);
}

.table-controls {
  display: flex;
  align-items: center;
  gap: 1rem;
  flex-wrap: wrap;
}

.search-input {
  min-width: 250px;
}

.empty-state {
  text-align: center;
  padding: 3rem 1rem;
  color: var(--text-color-secondary);
}

.empty-state p {
  margin: 1rem 0;
  font-size: 1.1rem;
}

.game-name {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.game-name .name {
  font-weight: 600;
}

.players-info {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.players-info .count {
  font-weight: 600;
}

.date {
  color: var(--text-color-secondary);
  font-size: 0.9rem;
}

.action-buttons {
  display: flex;
  gap: 0.5rem;
  flex-wrap: wrap;
}

/* Responsive */
@media (max-width: 768px) {
  .table-header {
    flex-direction: column;
    align-items: stretch;
  }

  .table-controls {
    justify-content: center;
  }

  .search-input {
    min-width: 200px;
  }

  .action-buttons {
    flex-direction: column;
  }
}
</style>
