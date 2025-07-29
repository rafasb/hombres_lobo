# 🎮 FASE 5: Gestión de Juegos - Plan de Acción

## 🎯 Objetivo de Esta Fase
Implementar la gestión completa de juegos: crear partidas, unirse a juegos, lista de juegos disponibles, y la interfaz de sala de espera.

## ⏱️ Tiempo Estimado
**Duración:** 3-4 días  
**Prioridad:** ALTA (Funcionalidad core del juego)

## ✅ PRERREQUISITOS COMPLETADOS
- ✅ Sistema de autenticación funcionando
- ✅ Backend FastAPI con endpoints de juegos existentes
- ✅ Frontend Vue.js 3 con routing y estado
- ✅ Comunicación API establecida

---

## 📋 TAREAS ESPECÍFICAS

### 1️⃣ CREAR STORE DE JUEGOS CON PINIA
**Prioridad:** 🔴 CRÍTICA  
**Tiempo:** 1 hora  
**Archivo:** `frontend/src/stores/games.ts`

#### Funcionalidades Requeridas
- Estado de juegos disponibles
- Estado del juego actual del usuario
- Acciones para crear, unirse, salir de juegos
- Gestión de jugadores en sala de espera

### 2️⃣ INTERFAZ DE LISTA DE JUEGOS
**Prioridad:** 🔴 CRÍTICA  
**Tiempo:** 1.5 horas  
**Archivos:** 
- `frontend/src/views/GamesView.vue`
- `frontend/src/components/games/GamesList.vue`
- `frontend/src/components/games/CreateGameModal.vue`

#### Funcionalidades Requeridas
- Lista de juegos disponibles con filtros
- Botón para crear nuevo juego
- Botón para unirse a juegos existentes
- Estado del juego (esperando, en progreso, finalizado)

### 3️⃣ SALA DE ESPERA DEL JUEGO
**Prioridad:** 🔴 CRÍTICA  
**Tiempo:** 2 horas  
**Archivos:**
- `frontend/src/views/GameLobbyView.vue`
- `frontend/src/components/games/PlayersList.vue`
- `frontend/src/components/games/GameSettings.vue`

#### Funcionalidades Requeridas
- Lista de jugadores unidos
- Configuración del juego (roles disponibles)
- Botón para iniciar juego (solo host)
- Chat de sala (opcional en esta fase)

### 4️⃣ INTEGRACIÓN CON BACKEND
**Prioridad:** 🔴 CRÍTICA  
**Tiempo:** 1 hora  

#### Endpoints a integrar
- `GET /games` - Lista de juegos
- `POST /games` - Crear juego
- `POST /games/{game_id}/join` - Unirse a juego
- `POST /games/{game_id}/leave` - Salir de juego
- `GET /games/{game_id}` - Detalles del juego
- `POST /games/{game_id}/start` - Iniciar juego

### 5️⃣ NAVEGACIÓN Y ROUTING
**Prioridad:** 🟡 ALTA  
**Tiempo:** 30 minutos  

#### Rutas nuevas
- `/games` - Lista de juegos
- `/games/:gameId` - Sala de espera específica
- `/games/:gameId/play` - Juego en progreso (preparación para Fase 6)

---

## 🎯 CRITERIOS DE ÉXITO

### ✅ Gestión de Juegos
- [ ] Crear juegos con configuración personalizada
- [ ] Ver lista de juegos disponibles con estado actual
- [ ] Unirse y salir de juegos existentes
- [ ] Solo el host puede configurar e iniciar el juego

### ✅ Sala de Espera
- [ ] Ver jugadores unidos en tiempo real
- [ ] Configurar roles disponibles en el juego
- [ ] Iniciar juego cuando hay suficientes jugadores
- [ ] Navegación intuitiva entre vistas

### ✅ Estado y Persistencia
- [ ] Estado del juego se mantiene al navegar
- [ ] Sincronización con backend en tiempo real
- [ ] Manejo de errores y estados de carga
- [ ] Notificaciones de eventos importantes

---

## 🔧 ARQUITECTURA TÉCNICA

### Store de Juegos (Pinia)
```typescript
interface Game {
  id: string
  name: string
  host_id: string
  status: 'waiting' | 'in_progress' | 'finished'
  players: Player[]
  max_players: number
  settings: GameSettings
}

interface GameSettings {
  roles: string[]
  day_duration: number
  night_duration: number
}
```

### Componentes Vue
- **GamesList**: DataTable con PrimeVue para mostrar juegos
- **CreateGameModal**: Dialog con formulario de configuración
- **PlayersList**: Lista dinámica con avatares y estado
- **GameSettings**: Panel de configuración para el host

---

## 🚀 PREPARACIÓN PARA FASE 6

Esta fase establece la base para:
- Sistema de juego en tiempo real (WebSockets)
- Estados de juego (día/noche, votaciones)
- Comunicación entre jugadores
- Lógica de roles especiales

---

## 📊 IMPACTO EN EL PROYECTO

**Al completar esta fase tendremos:**
- 🎮 Gestión completa de juegos funcionando
- 👥 Sistema de salas multiusuario
- ⚙️ Configuración flexible de partidas
- 🔗 Base sólida para el gameplay en tiempo real

**Progreso del proyecto:** 50% → 62.5% (completando 5/8 fases)

---

> **⚡ NOTA:** Esta fase es crítica para la experiencia de usuario. La interfaz debe ser intuitiva y responsive para gestionar múltiples jugadores eficientemente.
