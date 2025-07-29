<template>
  <div class="game-view">
    <div class="game-header">
      <button @click="$emit('back-to-games')" class="btn btn-secondary">
        ← Volver a Partidas
      </button>
      <h2>{{ game.name }}</h2>
      <div class="game-phase">
        <span class="phase-indicator" :class="`phase-${game.current_phase}`">
          {{ getPhaseText(game.current_phase) }}
        </span>
      </div>
    </div>

    <div class="game-content">
      <!-- Player Role Info -->
      <div v-if="playerRole" class="card player-info">
        <h3>🎭 Tu Rol</h3>
        <div class="role-display">
          <span class="role-name" :class="`role-${playerRole.role}`">
            {{ getRoleText(playerRole.role) }}
          </span>
          <p class="role-description">{{ getRoleDescription(playerRole.role) }}</p>
        </div>
      </div>

      <!-- Game Status -->
      <div class="card game-status">
        <h3>📊 Estado del Juego</h3>
        <div class="status-info">
          <p><strong>Jugadores:</strong> {{ game.players?.length || 0 }}/{{ game.max_players }}</p>
          <p><strong>Ronda:</strong> {{ game.round || 1 }}</p>
          <p><strong>Fase:</strong> {{ getPhaseText(game.current_phase) }}</p>
        </div>
      </div>

      <!-- Players List -->
      <div class="card players-list">
        <h3>👥 Jugadores</h3>
        <div class="players-grid">
          <div 
            v-for="player in game.players" 
            :key="player.id"
            class="player-card"
            :class="{ 
              'player-dead': player.status === 'dead',
              'player-current': player.username === user.username 
            }"
          >
            <div class="player-name">{{ player.username }}</div>
            <div class="player-status">
              {{ player.status === 'alive' ? '🟢' : '💀' }}
              {{ player.status === 'alive' ? 'Vivo' : 'Muerto' }}
            </div>
          </div>
        </div>
      </div>

      <!-- Game Actions -->
      <div v-if="game.status === 'playing' && availableActions.length > 0" class="card game-actions">
        <h3>⚡ Acciones Disponibles</h3>
        <div class="actions-list">
          <button 
            v-for="action in availableActions" 
            :key="action.type"
            @click="performAction(action)"
            class="btn btn-primary action-btn"
          >
            {{ action.label }}
          </button>
        </div>
      </div>

      <!-- Game Log -->
      <div class="card game-log">
        <h3>📜 Historia del Juego</h3>
        <div class="log-entries">
          <div v-if="!game.game_log || game.game_log.length === 0" class="no-log">
            No hay eventos registrados
          </div>
          <div 
            v-else
            v-for="(entry, index) in game.game_log" 
            :key="index"
            class="log-entry"
          >
            <span class="log-time">Ronda {{ entry.round || '?' }}</span>
            <span class="log-message">{{ entry.message }}</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { gamesAPI, gameActionsAPI } from '../services/api.js'

const props = defineProps(['game', 'user'])
const emit = defineEmits(['back-to-games'])

const gameData = ref(props.game)
const playerRole = ref(null)

onMounted(() => {
  loadGameDetails()
})

const loadGameDetails = async () => {
  try {
    const response = await gamesAPI.getGame(props.game.id)
    gameData.value = response.data
    
    // Find player's role
    const player = gameData.value.players?.find(p => p.username === props.user.username)
    if (player) {
      playerRole.value = player
    }
  } catch (err) {
    console.error('Error loading game details:', err)
  }
}

const availableActions = computed(() => {
  const actions = []
  
  if (!playerRole.value || playerRole.value.status === 'dead') {
    return actions
  }

  const phase = gameData.value.current_phase
  const role = playerRole.value.role

  // Day voting
  if (phase === 'day') {
    actions.push({
      type: 'day_vote',
      label: '🗳️ Votar Linchamiento'
    })
  }

  // Night actions based on role
  if (phase === 'night') {
    switch (role) {
      case 'werewolf':
        actions.push({
          type: 'werewolf_vote',
          label: '🐺 Votar Víctima'
        })
        break
      case 'seer':
        actions.push({
          type: 'seer_investigate',
          label: '🔮 Investigar Jugador'
        })
        break
      case 'witch':
        actions.push({
          type: 'witch_heal',
          label: '💚 Usar Poción de Curación'
        })
        actions.push({
          type: 'witch_poison',
          label: '💀 Usar Poción de Veneno'
        })
        break
      case 'hunter':
        if (playerRole.value.status === 'dying') {
          actions.push({
            type: 'hunter_shoot',
            label: '🏹 Disparar Antes de Morir'
          })
        }
        break
      case 'cupid':
        if (gameData.value.round === 1) {
          actions.push({
            type: 'cupid_choose_lovers',
            label: '💕 Elegir Enamorados'
          })
        }
        break
      case 'wild_child':
        if (gameData.value.round === 1) {
          actions.push({
            type: 'wild_child_choose_model',
            label: '👶 Elegir Modelo'
          })
        }
        break
    }
  }

  return actions
})

const performAction = (action) => {
  // This would open a modal or component for the specific action
  console.log('Performing action:', action)
  alert(`Acción: ${action.label}\n\nEsta funcionalidad se implementará en el siguiente paso.`)
}

const getPhaseText = (phase) => {
  const phaseMap = {
    'waiting': 'Esperando Jugadores',
    'night': 'Noche 🌙',
    'day': 'Día ☀️',
    'voting': 'Votación 🗳️',
    'finished': 'Juego Terminado'
  }
  return phaseMap[phase] || phase
}

const getRoleText = (role) => {
  const roleMap = {
    'villager': 'Aldeano',
    'werewolf': 'Hombre Lobo',
    'seer': 'Vidente',
    'witch': 'Bruja',
    'hunter': 'Cazador',
    'sheriff': 'Alguacil',
    'cupid': 'Cupido',
    'wild_child': 'Niño Salvaje'
  }
  return roleMap[role] || role
}

const getRoleDescription = (role) => {
  const descriptions = {
    'villager': 'Tu objetivo es identificar y eliminar a todos los Hombres Lobo.',
    'werewolf': 'Cada noche, elige una víctima junto con los otros lobos. Oculta tu identidad durante el día.',
    'seer': 'Cada noche puedes investigar la verdadera identidad de un jugador.',
    'witch': 'Tienes dos pociones: una de curación y una de veneno. Úsalas sabiamente.',
    'hunter': 'Si mueres, puedes llevarte a otro jugador contigo.',
    'sheriff': 'Tu voto cuenta doble y decides en caso de empate.',
    'cupid': 'En la primera noche, elige dos jugadores para que se enamoren.',
    'wild_child': 'Elige un modelo en la primera noche. Si muere, te conviertes en Hombre Lobo.'
  }
  return descriptions[role] || 'Rol especial en el juego.'
}
</script>

<style scoped>
.game-view {
  max-width: 1200px;
  width: 100%;
}

.game-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
  color: white;
  flex-wrap: wrap;
  gap: 1rem;
}

.game-header h2 {
  margin: 0;
  flex: 1;
  text-align: center;
}

.phase-indicator {
  padding: 0.5rem 1rem;
  border-radius: 20px;
  font-weight: bold;
  font-size: 1rem;
}

.phase-waiting {
  background: #fff3cd;
  color: #856404;
}

.phase-night {
  background: #1a1a2e;
  color: #eee;
}

.phase-day {
  background: #fff9c4;
  color: #8b6914;
}

.phase-voting {
  background: #d1ecf1;
  color: #0c5460;
}

.phase-finished {
  background: #f8d7da;
  color: #721c24;
}

.game-content {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
  gap: 1.5rem;
}

.card {
  background: white;
  border-radius: 10px;
  padding: 1.5rem;
  box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1);
}

.card h3 {
  margin: 0 0 1rem 0;
  color: #333;
  font-size: 1.2rem;
}

.player-info {
  grid-column: 1 / -1;
}

.role-display {
  text-align: center;
}

.role-name {
  display: inline-block;
  padding: 0.5rem 1rem;
  border-radius: 25px;
  font-weight: bold;
  font-size: 1.1rem;
  margin-bottom: 1rem;
}

.role-villager {
  background: #e8f5e8;
  color: #2e7d32;
}

.role-werewolf {
  background: #ffebee;
  color: #c62828;
}

.role-seer {
  background: #e3f2fd;
  color: #1565c0;
}

.role-witch {
  background: #f3e5f5;
  color: #7b1fa2;
}

.role-hunter {
  background: #fff3e0;
  color: #ef6c00;
}

.role-sheriff {
  background: #fce4ec;
  color: #ad1457;
}

.role-cupid {
  background: #fce4ec;
  color: #e91e63;
}

.role-wild_child {
  background: #e8f5e8;
  color: #388e3c;
}

.role-description {
  color: #666;
  font-style: italic;
  margin: 0;
}

.status-info p {
  margin: 0.5rem 0;
  color: #666;
}

.players-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
  gap: 0.75rem;
}

.player-card {
  background: #f8f9fa;
  border-radius: 8px;
  padding: 0.75rem;
  text-align: center;
  transition: all 0.2s;
}

.player-current {
  background: #e3f2fd;
  border: 2px solid #2196f3;
}

.player-dead {
  background: #ffebee;
  opacity: 0.7;
}

.player-name {
  font-weight: 500;
  margin-bottom: 0.25rem;
}

.player-status {
  font-size: 0.8rem;
  color: #666;
}

.actions-list {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.action-btn {
  padding: 0.75rem;
  text-align: left;
}

.log-entries {
  max-height: 300px;
  overflow-y: auto;
}

.no-log {
  text-align: center;
  color: #666;
  font-style: italic;
  padding: 1rem;
}

.log-entry {
  display: flex;
  padding: 0.5rem 0;
  border-bottom: 1px solid #eee;
  gap: 1rem;
}

.log-entry:last-child {
  border-bottom: none;
}

.log-time {
  font-size: 0.8rem;
  color: #666;
  min-width: 80px;
}

.log-message {
  flex: 1;
  color: #333;
}

@media (max-width: 768px) {
  .game-header {
    flex-direction: column;
    text-align: center;
  }
  
  .game-content {
    grid-template-columns: 1fr;
  }
  
  .players-grid {
    grid-template-columns: repeat(auto-fill, minmax(120px, 1fr));
  }
}
</style>