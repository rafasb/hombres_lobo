<template>
  <GamesListView
    :games="games"
    :loading="loading"
    :showCreateModal="showCreateModal"
    :notification="notification"
    :newGame="newGame"
    :playerOptions="playerOptions"
    :hasGames="hasGames"
    :auth="auth"
    :canJoinGame="canJoinGame"
    :canLeaveGame="canLeaveGame"
    :canViewGame="canViewGame"
    :canDeleteGame="canDeleteGame"
    :getCreatorName="getCreatorName"
    :getStatusText="getStatusText"
    :getGameCardClass="getGameCardClass"
    :formatDate="formatDate"
    @createGame="createGame"
    @joinGame="joinGame"
    @leaveGame="leaveGame"
    @deleteGame="deleteGame"
    @viewGame="viewGame"
    @closeCreateModal="closeCreateModal"
    @openCreateModal="openCreateModal"
    @navigate="handleNavigation"
    @updateNewGame="updateNewGame"
  />
</template>

<script setup lang="ts">
import { onMounted } from 'vue'
import GamesListView from '../views/GamesListView.vue'
import { useGamesList } from '../composables/useGamesList'
import { useNavigation } from '../composables/useNavigation'
import '../styles/games.css'

// Usar los composables
const {
  games,
  loading,
  showCreateModal,
  notification,
  newGame,
  playerOptions,
  hasGames,
  auth,
  loadGames,
  createGame,
  joinGame,
  leaveGame,
  deleteGame,
  viewGame,
  canJoinGame,
  canLeaveGame,
  canViewGame,
  canDeleteGame,
  getCreatorName,
  getStatusText,
  getGameCardClass,
  formatDate,
  closeCreateModal,
  openCreateModal,
  updateNewGame
} = useGamesList()

const { handleNavigation } = useNavigation()

// Cargar partidas al montar el componente
onMounted(() => {
  loadGames()
})
</script>
