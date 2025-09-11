<!-- VISTA DE LA PARTIDA (juego) 
 Los stores de Pinia ya se inicializan desde App.vue
 -->

<template>
  <div class="min-vh-100" style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);">
    <div class="mobile-container">
      <div class="container-fluid">
        <div class="row justify-content-center">
          <div class="col-12">
            <!-- Header básico -->
            <div class="card shadow-sm mb-4" style="background: rgba(255, 255, 255, 0.95); backdrop-filter: blur(10px); border: none; border-radius: 15px;">
              <div class="card-body">
                <h1 class="card-title mb-0 text-primary fw-bold">
                  <i class="bi bi-door-open me-2"></i>
                  🚧 GameLobby - Reconstrucción Paso a Paso
                </h1>
                <p class="text-muted mb-0">Game ID: {{ gameId }}</p>
              </div>
            </div>

            <!-- Panel de Debug con datos reales -->
            <div class="card shadow-sm mb-4" style="background: rgba(255, 255, 255, 0.95);">
              <div class="card-header bg-info text-white">
                <h5 class="mb-0">🔧 Debug Panel - Datos Reactivos</h5>
              </div>
              <div class="card-body">
                <div class="row g-3 mb-3">
                  <div class="col-md-4">
                    <strong>Estado de Carga:</strong>
                    <span class="badge ms-2" :class="loading ? 'bg-warning' : 'bg-success'">
                      {{ loading ? 'Cargando...' : 'Completado' }}
                    </span>
                  </div>
                  <div class="col-md-4">
                    <strong>WebSocket:</strong>
                    <span class="badge ms-2" :class="isConnected ? 'bg-success' : 'bg-danger'">
                      {{ isConnected ? 'Conectado' : 'Desconectado' }}
                    </span>
                  </div>
                  <div class="col-md-4">
                    <strong>Game Data:</strong>
                    <span class="badge ms-2" :class="gameData ? 'bg-success' : 'bg-warning'">
                      {{ gameData ? 'Cargado' : 'Sin datos' }}
                    </span>
                  </div>
                </div>

                <!-- Error si existe -->
                <div v-if="error" class="alert alert-danger">
                  ❌ {{ error }}
                </div>
                
                <!-- Usuario actual -->
                <div v-if="currentUser" class="mb-3">
                  <h6>👤 Usuario Actual:</h6>
                  <div class="bg-light p-2 rounded small">
                    <strong>ID:</strong> {{ currentUser.id }}<br>
                    <strong>Username:</strong> {{ currentUser.username }}<br>
                    <strong>Status:</strong> {{ currentUser.status }}
                  </div>
                </div>

                <!-- Jugador actual -->
                <div v-if="currentPlayer" class="mb-3">
                  <h6>🎭 Jugador en Partida:</h6>
                  <div class="bg-light p-2 rounded small">
                    <strong>Player ID:</strong> {{ currentPlayer.player_id }}<br>
                    <strong>Alive:</strong> {{ currentPlayer.is_alive ? '✅ Vivo' : '💀 Muerto' }}<br>
                    <!-- <strong>Connected:</strong> {{ currentPlayer.is_connected ? '🟢 Conectado' : '🔴 Desconectado' }} -->
                  </div>
                </div>

                <!-- Lista de jugadores -->
                <div v-if="players && players.length > 0" class="mb-3">
                  <h6>👥 Jugadores ({{ players.length }}):</h6>
                  <div class="bg-light p-2 rounded small">
                    <div v-for="player in players" :key="player.player_id" class="mb-1">
                      <strong>{{ player.username }}</strong> - 
                      {{ player.is_alive ? '✅' : '💀' }} - 
                      <!-- {{ player.is_connected ? '🟢' : '🔴' }} -  -->
                      {{ player.user_status }}
                    </div>
                  </div>
                </div>
                
                <!-- Datos completos del juego -->
                <div v-if="gameData" class="mt-3">
                  <h6>📊 Datos Completos de la Partida:</h6>
                  <pre class="bg-light p-2 rounded small" style="max-height: 300px; overflow-y: auto;">{{ JSON.stringify(gameData, null, 2) }}</pre>
                </div>
                
                <div v-else-if="!loading" class="mt-3">
                  <div class="alert alert-warning">
                    ⚠️ No se han cargado los datos de la partida desde el store
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watchEffect } from 'vue'
import { useRoute } from 'vue-router'
import { useUserStore } from '../stores/userStore'
import { useGameStore } from '../stores/gameStore'
import { useStoreInitialization } from '../composables/useStoreInitialization'
import { useWebSocket } from '../websocket/WebSocketManager'
import { useAuthStore } from '../stores/authStore'
import { gameService } from '../services/gameService'
import { getProfile } from '../services/authService'

// Obtener parámetros de la ruta
const route = useRoute()
const gameId = route.params.id as string

// Acceso a los stores y funciones de inicialización
const userStore = useUserStore()
const gameStore = useGameStore()
const authStore = useAuthStore()
const { loadGameData: storeLoadGameData } = useStoreInitialization()

// Establecer conexión WebSocket específica para este juego
const { createConnection } = useWebSocket(gameId)

// Estado de carga
const loading = ref(true)
const error = ref<string | null>(null)

// Datos reactivos desde los stores
const currentUser = computed(() => userStore.user)
const players = computed(() => gameStore.players)

// Crear objeto gameData reactivo desde el gameStore
const gameData = computed(() => ({
  gameId: gameStore.gameId,
  status: gameStore.gameStatus,
  players: gameStore.players,
  connectedPlayers: gameStore.connectedPlayersCount,
  totalPlayers: gameStore.totalPlayersCount,
  phase: gameStore.currentPhase,
  isFirstNight: gameStore.isFirstNight
}))

// Encontrar el jugador actual en la lista de players
const currentPlayer = computed(() => {
  if (!currentUser.value || !players.value) return null
  return players.value.find(p => p.player_id === currentUser.value?.id)
})

// WebSocket connection status - usar solo el estado de Pinia
const isConnected = computed(() => {
  // Usar solo el estado centralizado del userStore
  const connected = userStore.isWebSocketConnected
  
  console.log('🔌 Estado WebSocket (desde Pinia):', { 
    connected,
    userStatus: userStore.status,
    lastUpdate: userStore.lastStatusUpdate
  })
  
  return connected
})

// Función para cargar datos del juego
const loadGameData = async () => {
  console.log('🚀 Iniciando carga completa de datos para la partida:', gameId)
  loading.value = true
  error.value = null
  
  try {
    console.log('📦 Los stores ya están inicializados desde App.vue')
    
    console.log('👤 1. Cargando información del usuario actual...')
    // 1. Cargar información del usuario actual (quien está logueado)
    const profileResult = await getProfile()
    if (profileResult.user) {
      // Crear un objeto User completo con los datos básicos
      const userProfile = profileResult.user
      const fullUser = {
        id: userProfile.id,
        username: userProfile.username,
        role: userProfile.role as 'admin' | 'player',
        email: '', // Campo requerido pero no disponible en este endpoint
        status: 'connected' as const,
        in_game: true, // Está en juego porque está en GameLobby
        game_id: gameId // Asignar el gameId actual
      }
      userStore.setUser(fullUser)
      console.log('✅ Usuario cargado:', fullUser)
    } else {
      console.error('❌ Error cargando perfil:', profileResult.error)
    }
    
    console.log('🎮 2. Cargando datos específicos de partida...')
    // 2. Cargar datos específicos de partida en los stores
    await storeLoadGameData(gameId)
    
    console.log('🔌 3. Estableciendo conexión WebSocket para el juego...')
    // 3. Establecer conexión WebSocket específica para este juego
    if (authStore.token) {
      try {
        const wsManager = createConnection(authStore.token)
        await wsManager.connect()
        console.log('✅ Conexión WebSocket establecida para juego:', gameId)
      } catch (error) {
        console.error('❌ Error estableciendo conexión WebSocket:', error)
      }
    } else {
      console.warn('⚠️  No hay token de autenticación para WebSocket')
    }
    
    console.log('🌐 4. Cargando datos del juego desde la API...')
    // 4. Cargar datos del juego desde la API (información pública)
    const gameInfo = await gameService.getGameById(gameId)
    console.log('📋 Información del juego obtenida:', gameInfo)
    
    // 5. Sincronizar los datos obtenidos con los stores
    if (gameInfo) {
      console.log('📊 5. Sincronizando datos con los stores...')
      
      // Actualizar gameStore con la información de la partida
      gameStore.setGameId(gameInfo.game_id)
      gameStore.setGameStatus(gameInfo.status)
      gameStore.setCurrentPhase(`Round ${gameInfo.current_round}`)
      gameStore.setFirstNight(gameInfo.is_first_night)
      
      // Actualizar la lista de jugadores si existe
      if (gameInfo.players && Array.isArray(gameInfo.players)) {
        console.log('👥 Sincronizando lista de jugadores:', gameInfo.players)
        gameStore.setPlayers(gameInfo.players)
      }
      
      // Actualizar información de conexión
      gameStore.setConnectionInfo(gameInfo.current_players, gameInfo.max_players)
      
      console.log('✅ Datos sincronizados con los stores')
    }
    
    // TODO: 6. Cargar información privada del jugador actual desde la API
    // Esta información incluiría el rol, habilidades, etc.
    // await playerService.getCurrentPlayerInfo(gameId)
    
    console.log('✅ Datos del juego cargados completamente')
  } catch (err) {
    console.error('❌ Error cargando datos del juego:', err)
    error.value = 'Error al cargar los datos del juego'
  } finally {
    loading.value = false
  }
}

// Watcher para observar cambios en los datos reactivos
watchEffect(() => {
  console.log('🔄 Datos reactivos actualizados:')
  console.log('- Usuario:', currentUser.value)
  console.log('- Jugador actual:', currentPlayer.value)
  console.log('- Game Data:', gameData.value)
  console.log('- Lista jugadores:', players.value)
  console.log('- WebSocket conectado:', isConnected.value)
  
  // Log adicional para debugging del WebSocket (simplificado)
  console.log('🔌 Estado WebSocket desde Pinia:')
  console.log('  - userStore.isWebSocketConnected:', userStore.isWebSocketConnected)
})

// Cargar al montar
onMounted(async () => {
  console.log('🎯 Componente montado. Game ID:', gameId)
  await loadGameData()
})
</script>
