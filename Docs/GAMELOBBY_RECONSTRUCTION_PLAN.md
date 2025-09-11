# 🚧 Plan de Reconstrucción GameLobbyView - Paso a Paso

## Objetivo

Reconstruir la vista `GameLobbyView.vue` de forma incremental para entender y depurar el funcionamiento del WebSocket y la carga de datos de partida.

## Estado Actual - Paso 1: Vista Básica

### ✅ **Implementado**

1. **Template básico** con:
   - Header de identificación
   - Panel de debug visible
   - Visualización del JSON de datos
   - Estados de carga

2. **Script mínimo** con:
   - Obtención del `gameId` desde la ruta
   - Estado básico (`loading`, `game`)
   - Función de carga simulada
   - Logging de consola para debug

### 🎯 **Funcionalidades de Debug**

- **Estado de Carga**: Indica si está cargando o completado
- **Game Data**: Muestra si los datos están disponibles
- **Datos JSON**: Visualización completa de los datos recibidos
- **Console Logging**: Trazabilidad en la consola del navegador

## Plan de Pasos Siguientes

### **Paso 2: Integración con gameService**
```typescript
// Añadir import real
import { gameService } from '../services/gameService'

// Implementar carga real
const loadGame = async () => {
  try {
    const gameData = await gameService.getGameById(gameId)
    game.value = gameData
  } catch (error) {
    // Manejo de errores
  }
}
```

### **Paso 3: Añadir WebSocket Básico**
```typescript
// Añadir WebSocket manager
import { useWebSocket } from '../websocket/WebSocketManager'

// Crear conexión y suscribirse a game_status
const wsManager = useWebSocket(gameId)
```

### **Paso 4: Mostrar Información de la Partida**
```vue
<!-- Información básica de la partida -->
<div v-if="game" class="card">
  <h3>{{ game.name }}</h3>
  <p>Estado: {{ game.status }}</p>
  <p>Jugadores: {{ game.players?.length || 0 }}</p>
</div>
```

### **Paso 5: Lista de Jugadores**
```vue
<!-- Lista de jugadores -->
<div v-if="game?.players" class="players-list">
  <div v-for="player in game.players" :key="player.player_id">
    {{ player.username }} - {{ player.user_status }}
  </div>
</div>
```

### **Paso 6: Estados de Conexión WebSocket**
```typescript
// Añadir estado de conexión
const connectionStatus = ref('disconnected')
const wsMessages = ref([])

// Mostrar mensajes WebSocket en tiempo real
```

### **Paso 7: Acciones del Usuario**
```vue
<!-- Botones de acción -->
<button @click="joinGame">Unirse</button>
<button @click="leaveGame">Salir</button>
<button @click="startGame" v-if="isCreator">Iniciar</button>
```

### **Paso 8: Integración con Stores de Pinia**
```typescript
// Añadir stores reactivos
import { useGameStore } from '../stores/gameStore'
import { usePlayerStore } from '../stores/player'

// Sincronizar datos con stores
```

## Ventajas de Este Enfoque

### 🔍 **Debugging Progresivo**
- Cada paso es verificable
- Panel de debug visible en todo momento
- Logging detallado en consola
- Datos JSON visibles para inspección

### 🚀 **Desarrollo Incremental**
- Funcionalidad mínima viable en cada paso
- Fácil identificación de problemas
- Testing individual de cada componente
- Rollback sencillo si algo falla

### 📊 **Visibilidad Total**
- Estado de cada componente visible
- Datos en tiempo real
- Mensajes WebSocket rastreables
- Errores claramente identificados

## Próximo Paso Recomendado

### **Implementar Paso 2: gameService Real**

¿Quieres que proceda con la integración del `gameService` real para cargar datos de la partida desde el backend?

```typescript
// Siguiente implementación:
import { gameService } from '../services/gameService'

const loadGame = async () => {
  console.log('🚀 Cargando partida real desde API:', gameId)
  loading.value = true
  
  try {
    const gameData = await gameService.getGameById(gameId)
    game.value = gameData
    console.log('✅ Datos reales cargados:', gameData)
  } catch (error) {
    console.error('❌ Error cargando partida:', error)
    game.value = null
  } finally {
    loading.value = false
  }
}
```

## Estado del Debug Panel

El panel de debug actual te mostrará:
- ✅ **Game ID** obtenido de la ruta
- ✅ **Estado de carga** (Cargando/Completado)
- ✅ **Disponibilidad de datos** (Cargado/No disponible)
- ✅ **JSON completo** de los datos simulados
- ✅ **Logging de consola** para trazabilidad

Esto te permitirá verificar que todo funciona antes de añadir más complejidad.
