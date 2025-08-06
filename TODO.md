# 📋 TODO - Proyecto Hombres Lobo

## 🎯 Estado General del Proyecto
**Progreso actual:** 62.5% (5/8 fases completadas)
**Última actualización:** 30 de julio de 2025

---

## ✅ FASES COMPLETADAS

### ✅ FASE 1: Configuración Inicial (COMPLETADA)
- ✅ Estructura del proyecto
- ✅ Configuración de dependencias
- ✅ Setup inicial de FastAPI
- ❌ Setup inicial de Vue.js 3 y VITE. 

### ✅ FASE 2: Base de Datos y Autenticación (COMPLETADA)
- ✅ Modelos de base de datos
- ✅ Sistema de autenticación JWT
- ✅ Endpoints de usuario
- ✅ Middleware de seguridad

### ❌ FASE 3: Frontend Base (PENDIENTE)
- ❌ Configuración de Vue.js 3 + VITE + TypeScript
- ❌ Sistema de routing
- ❌ Store de autenticación con Pinia
- ❌ Componentes base de UI

### ❌ FASE 4: Interfaz de Usuario (PENDIENTE)
- ❌ Login y registro
- ❌ Dashboard principal
- ❌ Navegación y layouts
- ❌ Sistema de notificaciones

### ❌ FASE 5: Gestión de Juegos (PENDIENTE)
**Estado:** ❌ PENDIENTE

#### ❌ Componentes Implementados:
- ❌ `GameStore` - Store completo con Pinia
- ❌ `GamesView` - Lista principal de juegos
- ❌ `GamesList` - DataTable responsive con filtros
- ❌ `CreateGameModal` - Modal de creación con validación
- ❌ `GameLobbyView` - Sala de espera del juego
- ❌ `PlayersList` - Lista de jugadores con avatares
- ❌ `GameSettings` - Panel de configuración avanzada

#### ❌ Funcionalidades Implementadas:
- ❌ Crear juegos con configuración personalizada
- ❌ Lista de juegos con filtros y búsqueda
- ❌ Unirse/salir de juegos
- ❌ Sala de espera con jugadores en tiempo real
- ❌ Configuración de roles y reglas
- ❌ Auto-refresh cada 5 segundos
- ❌ Responsive design completo
- ❌ Sistema de notificaciones integrado

#### ❌ Rutas Implementadas:
- ❌ `/games` - Lista de juegos
- ❌ `/games/:gameId` - Sala de espera específica
- ❌ `/games/:gameId/view` - Vista del juego (solo lectura)

---

## 🔄 FASES PENDIENTES

### 🚀 FASE 6: Sistema de Juego en Tiempo Real
**Prioridad:** 🔴 CRÍTICA
**Estado:** 📋 PLANIFICADA
**Tiempo estimado:** 4-5 días

#### Objetivos principales:
- [ ] Implementar WebSockets para comunicación en tiempo real
- [ ] Sistema de estados de juego (día/noche)
- [ ] Lógica de votaciones
- [ ] Chat en vivo durante el juego
- [ ] Acciones de roles especiales
- [ ] Sistema de turnos y fases

#### Componentes a desarrollar:
- [ ] `GamePlayView` - Vista principal del juego activo
- [ ] `VotingPanel` - Panel de votación
- [ ] `ChatComponent` - Chat en tiempo real
- [ ] `RoleActions` - Acciones específicas por rol
- [ ] `GamePhases` - Manejo de fases día/noche
- [ ] WebSocket service para tiempo real

### 🎭 FASE 7: Roles Especiales
**Prioridad:** 🟡 ALTA
**Estado:** 🔄 PENDIENTE
**Tiempo estimado:** 3-4 días

#### Objetivos principales:
- [ ] Implementar lógica de roles especiales
- [ ] Acciones nocturnas de los roles
- [ ] Sistema de habilidades especiales
- [ ] Condiciones de victoria específicas

#### Roles a implementar:
- [ ] Hombre Lobo - Eliminación nocturna
- [ ] Vidente - Visión de roles
- [ ] Bruja - Pociones de vida/muerte
- [ ] Cazador - Venganza al morir
- [ ] Cupido - Crear parejas de amantes
- [ ] Sheriff - Voto doble
- [ ] Niño Salvaje - Transformación

### 🏆 FASE 8: Finalización y Pulido
**Prioridad:** 🟢 MEDIA
**Estado:** 🔄 PENDIENTE
**Tiempo estimado:** 2-3 días

#### Objetivos principales:
- [ ] Estadísticas de juego
- [ ] Historial de partidas
- [ ] Sistema de puntuación
- [ ] Optimización de performance
- [ ] Testing completo
- [ ] Documentación final

---

## 📊 MÉTRICAS DEL PROYECTO

### Cobertura de funcionalidades:
- **Autenticación:** ❌ 0%
- **Gestión de usuarios:** ❌ 0%
- **Gestión de juegos:** ❌ 0%
- **Gameplay en tiempo real:** ❌ 0%
- **Roles especiales:** ❌ 0%
- **Sistema de puntuación:** ❌ 0%

---

## 🚀 ENTORNO DE DESARROLLO

### Frontend (Vue.js 3):
- **Servidor:** http://localhost:5173/
- **Estado:** ❌ NO OPERATIVO
- **Framework:** VITE + Vue.js 3 + TypeScript
- **UI:** CSS puros, un fichero por vista.

### Backend (FastAPI):
- **Servidor:** http://localhost:8000/
- **Estado:** ✅ OPERATIVO
- **Documentación API:** http://localhost:8000/docs

---

## 📝 NOTAS IMPORTANTES

- **Responsive design** - Compatible con móviles y tablets

