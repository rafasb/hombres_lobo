# 📊 FASE 1 - Análisis de Dependencias Completo

**Fecha:** 19 Septiembre 2025  
**Estado:** ✅ COMPLETADO  
**Backup:** `backups/migration_fase1_20250919_2339/`

---

## 🗄️ 1. Backup Completado

✅ **Archivos respaldados:**
- `backend/app/db_sqlite/` → Base de datos SQLite completa
- `backend/init_database.py` → Script de inicialización DB
- `backend/app/database.py` → Módulo principal de BD

---

## 🔍 2. Inventario de GameState

### 📍 **Ubicaciones principales:**
- **Definición**: `backend/app/services/game_state_service.py` (línea 16)
- **Manager**: `backend/app/services/game_state_service.py` (línea 158)
- **Instancia global**: `game_state_manager` (línea 304)

### 🌐 **Archivos que usan GameState:**

#### 🔧 **API Routes:**
- `backend/app/api/routes_game.py` (comentados - líneas 77, 79, 141, 143)

#### 🌐 **WebSocket Handlers:**
- `backend/app/websocket/game_handlers.py` (importa y usa activamente)
- `backend/app/websocket/user_status_handlers.py` (4 usos de game_state_manager)
- `backend/app/websocket/websocket_endpoint.py` (3 importaciones dinámicas)

#### 📋 **Modelos y Servicios:**
- `backend/app/models/game_responses.py` (referencias en comentarios)
- `backend/app/services/game_responses_service.py` (documentación)

---

## ⏰ 3. Inventario de Temporizadores

### 🚨 **Temporizadores Críticos a Migrar:**

#### 🎮 **GamePhaseController** (`game_phases_service.py`):
```python
# Línea 61: Definición
self.phase_timer_task: Optional[asyncio.Task] = None

# Línea 117: Creación de timer
self.phase_timer_task = asyncio.create_task(
    self._handle_phase_timeout(duration_minutes * 60)
)

# Líneas 94-96, 231-233: Cancelación de timers
if self.phase_timer_task:
    self.phase_timer_task.cancel()
    self.phase_timer_task = None
```

#### 🎯 **GameState** (`game_state_service.py`):
```python
# Línea 28: Definición
self.phase_timer_task = None

# Línea 155: Uso indirecto
asyncio.create_task(self.phase_controller.change_phase(game_phase, force=True))

# Líneas 297-298: Cancelación
if game_state.phase_timer_task:
    game_state.phase_timer_task.cancel()
```

#### 🌐 **ConnectionManager** (`connection_manager.py`):
```python
# Línea 113: Heartbeat (NO migrar - mantener en memoria)
self.heartbeat_task = asyncio.create_task(self._heartbeat_loop())
```

---

## 📋 4. Matriz de Dependencias

### 🔄 **Flujo de Dependencias Crítico:**

```
WebSocket Events → game_state_manager → GameState → GamePhaseController → asyncio timers
                ↓                    ↓            ↓
            WebSocket notify    Cache datos    Fase temporal
```

### 🎯 **Componentes a Migrar (Orden de prioridad):**

1. **ALTA**: `GamePhaseController` temporizadores → Timestamps DB
2. **ALTA**: `GameState` datos temporales → Campos persistentes  
3. **MEDIA**: `game_state_manager` cache → Funciones DB directas
4. **BAJA**: WebSocket handlers → Actualizar imports

### ✅ **Componentes NO migrar (mantener memoria):**

1. **ConnectionManager heartbeat** - Infraestructura de red
2. **WebSocket connection pools** - Estado temporal conexiones
3. **Pending notifications queue** - Cola temporal eventos

---

## 🚧 5. Riesgos Identificados

### 🔴 **Alto Riesgo:**
- **Temporizadores activos**: Cancelar incorrectamente puede dejar juegos "colgados"
- **Estado híbrido temporal**: Inconsistencias durante transición

### 🟡 **Medio Riesgo:**
- **Referencias circulares**: GameState ↔ GamePhaseController
- **WebSocket sync**: Mantener notificaciones durante migración

### 🟢 **Bajo Riesgo:**
- **Database schema**: Cambios son aditivos (no destructivos)
- **API compatibility**: Endpoints mantienen interfaz

---

## 📝 6. Siguiente Pasos - FASE 2

### 🎯 **Preparar para Migración BD:**

1. **Crear GameExtended** con nuevos campos
2. **Script migración** para datos existentes  
3. **Tests de compatibilidad** antes/después
4. **Rollback procedures** verificados

### ⚡ **Orden de Eliminación (FASE 5):**

```
1. GamePhaseController.phase_timer_task
2. GameState.phase_timer_task  
3. GameState._cached_game_data
4. game_state_manager.active_game_states
5. Cleanup imports obsoletos
```

---

**✅ FASE 1 COMPLETADA**  
**🎯 Listo para FASE 2: Migración de Base de Datos**