<template>
  <div class="games-container">
    <div class="games-header">
      <h2>🎮 Partidas Disponibles</h2>
      <button @click="showCreateForm = !showCreateForm" class="btn btn-primary">
        {{ showCreateForm ? 'Cancelar' : 'Crear Partida' }}
      </button>
    </div>

    <!-- Create Game Form -->
    <div v-if="showCreateForm" class="card create-game-form">
      <h3>Crear Nueva Partida</h3>
      
      <div v-if="error" class="alert alert-error">
        {{ error }}
      </div>

      <form @submit.prevent="createGame">
        <div class="form-group">
          <label for="game-name">Nombre de la Partida:</label>
          <input 
            id="game-name"
            v-model="newGame.name" 
            type="text" 
            required 
            placeholder="Ej: Partida de Medianoche"
          />
        </div>
        
        <div class="form-group">
          <label for="max-players">Máximo de Jugadores:</label>
          <select id="max-players" v-model="newGame.maxPlayers" required>
            <option value="6">6 jugadores</option>
            <option value="8">8 jugadores</option>
            <option value="10">10 jugadores</option>
            <option value="12">12 jugadores</option>
            <option value="15">15 jugadores</option>
            <option value="18">18 jugadores</option>
          </select>
        </div>
        
        <button type="submit" class="btn btn-primary" :disabled="loading">
          {{ loading ? 'Creando...' : 'Crear Partida' }}
        </button>
      </form>
    </div>

    <!-- Games List -->
    <div class="games-grid">
      <div v-if="loadingGames" class="loading">
        Cargando partidas...
      </div>
      
      <div v-else-if="games.length === 0" class="no-games">
        <p>No hay partidas disponibles</p>
        <p>¡Crea la primera partida!</p>
      </div>
      
      <div v-else>
        <div v-for="game in games" :key="game.id" class="game-card">
          <div class="game-header">
            <h3>{{ game.name }}</h3>
            <span class="game-status" :class="`status-${game.status}`">
              {{ getStatusText(game.status) }}
            </span>
          </div>
          
          <div class="game-info">
            <p><strong>Creador:</strong> {{ game.created_by }}</p>
            <p><strong>Jugadores:</strong> {{ game.players?.length || 0 }}/{{ game.max_players }}</p>
            <p><strong>Estado:</strong> {{ getPhaseText(game.current_phase) }}</p>
          </div>
          
          <div class="game-actions">
            <button 
              v-if="game.status === 'waiting' && !isPlayerInGame(game)"
              @click="joinGame(game)" 
              class="btn btn-primary"
              :disabled="game.players?.length >= game.max_players"
            >
              {{ game.players?.length >= game.max_players ? 'Completa' : 'Unirse' }}
            </button>
            
            <button 
              v-if="isPlayerInGame(game)"
              @click="selectGame(game)" 
              class="btn btn-secondary"
            >
              Ver Partida
            </button>
            
            <button 
              v-if="game.created_by === user.username && game.status === 'waiting'"
              @click="startGame(game)" 
              class="btn btn-primary"
              :disabled="(game.players?.length || 0) < 4"
            >
              {{ (game.players?.length || 0) < 4 ? 'Min 4 jugadores' : 'Iniciar' }}
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { gamesAPI } from '../services/api.js'

const props = defineProps(['user'])
const emit = defineEmits(['select-game'])

const games = ref([])
const loadingGames = ref(true)
const showCreateForm = ref(false)
const loading = ref(false)
const error = ref('')

const newGame = ref({
  name: '',
  maxPlayers: 8
})

onMounted(() => {
  loadGames()
})

const loadGames = async () => {
  try {
    loadingGames.value = true
    const response = await gamesAPI.getGames()
    games.value = response.data
  } catch (err) {
    console.error('Error loading games:', err)
    error.value = 'Error al cargar las partidas'
  } finally {
    loadingGames.value = false
  }
}

const createGame = async () => {
  if (!newGame.value.name) {
    error.value = 'Por favor, ingresa un nombre para la partida'
    return
  }

  loading.value = true
  error.value = ''

  try {
    const gameData = {
      name: newGame.value.name,
      max_players: parseInt(newGame.value.maxPlayers),
      created_by: props.user.username
    }
    
    await gamesAPI.createGame(gameData)
    
    // Reset form
    newGame.value.name = ''
    newGame.value.maxPlayers = 8
    showCreateForm.value = false
    
    // Reload games
    await loadGames()
    
  } catch (err) {
    console.error('Error creating game:', err)
    error.value = err.response?.data?.detail || 'Error al crear la partida'
  } finally {
    loading.value = false
  }
}

const joinGame = async (game) => {
  try {
    await gamesAPI.joinGame(game.id, { player_username: props.user.username })
    await loadGames() // Refresh games list
  } catch (err) {
    console.error('Error joining game:', err)
    error.value = err.response?.data?.detail || 'Error al unirse a la partida'
  }
}

const startGame = async (game) => {
  try {
    await gamesAPI.startGame(game.id)
    await loadGames() // Refresh games list
  } catch (err) {
    console.error('Error starting game:', err)
    error.value = err.response?.data?.detail || 'Error al iniciar la partida'
  }
}

const selectGame = (game) => {
  emit('select-game', game)
}

const isPlayerInGame = (game) => {
  return game.players?.some(player => player.username === props.user.username)
}

const getStatusText = (status) => {
  const statusMap = {
    'waiting': 'Esperando',
    'playing': 'En Juego',
    'finished': 'Terminada'
  }
  return statusMap[status] || status
}

const getPhaseText = (phase) => {
  const phaseMap = {
    'waiting': 'Sala de Espera',
    'night': 'Noche',
    'day': 'Día',
    'voting': 'Votación',
    'finished': 'Finalizada'
  }
  return phaseMap[phase] || phase
}
</script>

<style scoped>
.games-container {
  max-width: 1200px;
  width: 100%;
}

.games-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
  color: white;
}

.games-header h2 {
  margin: 0;
}

.create-game-form {
  margin-bottom: 2rem;
}

.create-game-form h3 {
  margin-bottom: 1rem;
  color: #333;
}

.create-game-form select {
  width: 100%;
  padding: 0.75rem;
  border: 1px solid #ddd;
  border-radius: 5px;
  font-size: 1rem;
  background: white;
}

.games-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
  gap: 1.5rem;
}

.loading, .no-games {
  grid-column: 1 / -1;
  text-align: center;
  padding: 3rem;
  color: white;
  font-size: 1.1rem;
}

.game-card {
  background: white;
  border-radius: 10px;
  padding: 1.5rem;
  box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1);
  transition: transform 0.2s;
}

.game-card:hover {
  transform: translateY(-2px);
}

.game-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}

.game-header h3 {
  margin: 0;
  color: #333;
}

.game-status {
  padding: 0.25rem 0.75rem;
  border-radius: 15px;
  font-size: 0.8rem;
  font-weight: 500;
}

.status-waiting {
  background: #fff3cd;
  color: #856404;
}

.status-playing {
  background: #d1ecf1;
  color: #0c5460;
}

.status-finished {
  background: #f8d7da;
  color: #721c24;
}

.game-info {
  margin-bottom: 1rem;
}

.game-info p {
  margin: 0.25rem 0;
  color: #666;
}

.game-actions {
  display: flex;
  gap: 0.5rem;
}

.game-actions .btn {
  flex: 1;
  padding: 0.5rem;
  font-size: 0.9rem;
}

@media (max-width: 768px) {
  .games-header {
    flex-direction: column;
    gap: 1rem;
    text-align: center;
  }
  
  .games-grid {
    grid-template-columns: 1fr;
  }
  
  .game-actions {
    flex-direction: column;
  }
}
</style>