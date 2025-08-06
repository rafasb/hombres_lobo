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
    :getCreatorName="getCreatorName"
    :getStatusText="getStatusText"
    :getGameCardClass="getGameCardClass"
    :formatDate="formatDate"
    @createGame="createGame"
    @joinGame="joinGame"
    @leaveGame="leaveGame"
    @viewGame="viewGame"
    @closeCreateModal="closeCreateModal"
    @openCreateModal="openCreateModal"
    @navigateToProfile="navigateToProfile"
    @navigateToAdmin="navigateToAdmin"
    @navigateToGames="navigateToGames"
    @updateNewGame="updateNewGame"
  />
</template>

<script setup lang="ts">
import { onMounted } from 'vue'
import GamesListView from '../views/GamesListView.vue'
import { useGamesList } from '../composables/useGamesList'
import '../styles/games.css'

// Usar el composable
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
  viewGame,
  canJoinGame,
  canLeaveGame,
  canViewGame,
  getCreatorName,
  getStatusText,
  getGameCardClass,
  formatDate,
  closeCreateModal,
  openCreateModal,
  navigateToProfile,
  navigateToAdmin,
  navigateToGames,
  updateNewGame
} = useGamesList()

// Cargar partidas al montar el componente
onMounted(() => {
  loadGames()
})
</script>
