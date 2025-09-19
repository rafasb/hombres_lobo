# 🗄️ Plan de Migración: Centralización de Estado en Base de Datos

## 📋 Resumen Ejecutivo

### 🎯 Objetivo

Migrar toda la gestión de estado de partida desde memoria/servicios temporales hacia la base de datos, simplificando la arquitectura y eliminando dependencias de temporizadores complejos.

### 🚨 Problema Actual

- **Estado fragmentado**: Información crítica reside en [`GameState`](backend/app/services/game_state_service.py), [`GamePhaseController`](backend/app/services/game_phases_service.py) y memoria
- **Temporizadores complejos**: Lógica distribuida entre servicios dificulta mantenimiento
- **Riesgo de pérdida**: Estado en memoria no persiste ante reinicios
- **Inconsistencias**: Múltiples fuentes de verdad generan conflictos

### ✅ Beneficios Esperados

- **Estado único**: Base de datos como única fuente de verdad
- **Persistencia garantizada**: No pérdida de información ante fallos
- **Simplificación**: Eliminación de gestores de estado complejos
- **Escalabilidad**: Preparación para múltiples instancias
- **Debugging**: Trazabilidad completa en base de datos

---

## 🔍 Análisis del Estado Actual

### 📊 Modelos de Datos Actuales

#### [`Game`](backend/app/models/game_and_player.py) - Estado Persistente ✅

```python
class Game(GameBase):
    id: str
    creator_id: str
    player_ids: List[str]  # Lista de jugadores en la partida
    players: Dict[str, PlayerInfo]  # Estado de jugadores con roles
    status: GameStatus
    created_at: datetime
    current_round: int
    is_first_night: bool
    night_actions: Dict[str, Dict[str, str]]
    defeated_players: List[str]
    votes: Dict[str, str]
    # NOTA: connected_players se eliminará - se maneja en ConnectionManager
```

#### 🚨 Información NO Persistente (En Memoria) ✅

**❌ A Migrar a Base de Datos:**

- **Temporizadores activos**: Duración de fases, timeouts automáticos → `phase_duration_seconds`, `next_phase_at`
- **Estado de fases**: Información temporal de [`GamePhaseController`](backend/app/services/game_phases_service.py) → `current_phase`, `phase_start_time`
- **Estado de juego crítico**: Votos, acciones nocturnas temporales → Campos específicos en BD

**✅ Mantener en Memoria (No Persistir):**

- **Eventos pendientes**: Notificaciones WebSocket sin procesar (temporal por naturaleza)
- **Metadata de sesión**: Información de conexiones activas WebSocket (se reconstruye al conectar)
- **Cache de rendimiento**: Datos temporales para optimización
- **Estado de networking**: Información específica de conexiones TCP/WebSocket

### 🏗️ Servicios Problemáticos

#### [`GameState`](backend/app/services/game_state_service.py)

- ❌ **Cache temporal**: `_cached_game_data` se pierde en reinicio
- ❌ **Lógica duplicada**: Wrapper que complica acceso a datos
- ❌ **Estado híbrido**: Mezcla datos persistentes y temporales

#### [`GamePhaseController`](backend/app/services/game_phases_service.py)

- ❌ **Temporizadores**: `asyncio.create_task()` sin persistencia
- ❌ **Estado de fase**: Información crítica solo en memoria
- ❌ **Callbacks complejos**: Lógica distribuida difícil de rastrear

---

## 🎯 Diseño de la Nueva Arquitectura

### 📋 Campos Nuevos en Modelo `Game`

```python
class Game(GameBase):
    # ... campos existentes ...
    
    # 🆕 Gestión de Fases
    current_phase: GamePhase = GamePhase.WAITING
    phase_start_time: Optional[datetime] = None
    phase_duration_seconds: Optional[int] = None
    phase_auto_advance: bool = True
    
    # 🆕 Temporizadores Persistentes
    next_phase_at: Optional[datetime] = None  # Cuándo avanzar automáticamente
    phase_end_actions: List[str] = Field(default_factory=list)  # Acciones al terminar fase
    
    # 🆕 Estado de Votación
    voting_active: bool = False
    voting_start_time: Optional[datetime] = None
    voting_end_time: Optional[datetime] = None
    voting_type: Optional[str] = None  # "lynch", "sheriff", etc.
    
    # 🆕 Acciones Nocturnas Ampliadas
    pending_night_actions: Dict[str, Dict] = Field(default_factory=dict)
    completed_night_actions: List[str] = Field(default_factory=list)
    night_action_deadline: Optional[datetime] = None
    
    # 🆕 Metadata de Juego
    auto_advance_enabled: bool = True
    manual_control: bool = False  # Permite control manual por admin
    game_speed: str = "normal"  # "slow", "normal", "fast"
    
    # 🆕 Estado de Actividad de Jugadores (Solo para gameplay, no conexiones WebSocket)
    last_game_activity: Dict[str, datetime] = Field(default_factory=dict)  # Última acción en el juego
    inactive_players: List[str] = Field(default_factory=list)  # Jugadores inactivos por tiempo
```

### 🏗️ Arquitectura Híbrida: Persistente + Temporal

#### 🗄️ **Información Persistente (Base de Datos)**

- **Estado del juego**: Fases, temporizadores, configuración
- **Acciones de jugadores**: Votos, acciones nocturnas, roles
- **Historial**: Rondas, eliminaciones, eventos críticos
- **Configuración**: Reglas, participantes, metadata de gameplay

#### 💾 **Información Temporal (Memoria)**

- **Conexiones WebSocket**: Estado de conexiones TCP/WebSocket activas
- **Eventos pendientes**: Notificaciones en cola sin procesar
- **Cache de rendimiento**: Datos temporales para optimización
- **Metadata de sesión**: Información específica de conexiones de red

### 🆕 Nuevo Enum para Fases

```python
class GamePhase(str, Enum):
    WAITING = "waiting"
    STARTING = "starting"
    DAY_DISCUSSION = "day_discussion"
    DAY_VOTING = "day_voting"
    NIGHT_ACTIONS = "night_actions"
    NIGHT_RESOLUTION = "night_resolution"
    GAME_OVER = "game_over"
    PAUSED = "paused"
```

### 🏗️ Nueva Arquitectura de Servicios

#### `GameDatabaseService` (Nuevo - Principal)

```python
class GameDatabaseService:
    """Servicio principal para operaciones de base de datos de juego."""
    
    @staticmethod
    def advance_phase(game_id: str) -> Optional[Game]:
        """Avanza la fase del juego y persiste inmediatamente."""
        
    @staticmethod
    def set_phase_timer(game_id: str, duration_seconds: int) -> bool:
        """Establece cuándo debe avanzar automáticamente la fase."""
        
    @staticmethod
    def process_phase_transitions() -> List[str]:
        """Procesa todos los juegos que deben avanzar de fase."""
        
    @staticmethod
    def update_player_activity(game_id: str, user_id: str) -> bool:
        """Actualiza timestamp de última actividad de gameplay (no conexión)."""
```

#### `WebSocketConnectionManager` (Existente - Mantener en Memoria)

```python
class WebSocketConnectionManager:
    """Maneja conexiones WebSocket temporales - NO persistir en BD."""
    
    # ✅ Mantener en memoria
    active_connections: Dict[str, WebSocket]
    game_connections: Dict[str, Set[str]]  
    pending_notifications: Dict[str, List[dict]]
    connection_metadata: Dict[str, dict]  # IP, user-agent, etc.
```

#### `GameAutomationService` (Nuevo - Reemplazo de temporizadores)

```python
class GameAutomationService:
    """Servicio para automatización sin temporizadores asyncio."""
    
    @staticmethod
    async def process_scheduled_actions():
        """Ejecuta acciones programadas cada X segundos."""
        
    @staticmethod
    def schedule_phase_advance(game_id: str, when: datetime):
        """Programa avance de fase usando timestamps."""
```

```python
class GameAutomationService:
    """Servicio para automatización sin temporizadores asyncio."""
    
    @staticmethod
    async def process_scheduled_actions():
        """Ejecuta acciones programadas cada X segundos."""
        
    @staticmethod
    def schedule_phase_advance(game_id: str, when: datetime):
        """Programa avance de fase usando timestamps."""
```

### 🎯 Principios de Separación de Responsabilidades

#### 📦 **PERSISTIR en Base de Datos** (Estado del Juego)

- ✅ **Datos de gameplay**: Roles, votos, acciones, fases
- ✅ **Temporizadores de juego**: Cuándo avanzar fases, deadlines
- ✅ **Historial crítico**: Eliminaciones, rondas, eventos importantes
- ✅ **Configuración de partida**: Reglas, participantes, settings
- ✅ **Estado de jugadores**: Actividad de juego, roles asignados

#### 💾 **MANTENER en Memoria** (Infraestructura Temporal)

- ❌ **Conexiones WebSocket**: Estados de red, sockets TCP
- ❌ **Eventos en cola**: Notificaciones pendientes de envío
- ❌ **Cache de rendimiento**: Datos optimización temporal
- ❌ **Metadata de sesión**: IP, user-agent, tokens temporales
- ❌ **Estado de red**: Latencia, bandwidth, conexiones activas

> **💡 Regla clave**: Si la información se pierde al reiniciar y el juego puede continuar normalmente, debe estar en memoria. Si es crítica para el estado del juego, debe persistir.

---

## 📅 Plan de Migración Detallado

### 🚀 FASE 1: Preparación y Análisis (Día 1)

**Duración:** 1 día  
**Objetivo:** Preparar estructura sin romper funcionalidad actual

#### 1.1 Backup y Análisis

```bash
# Crear backup completo
cp -r backend/app/db_sqlite backend/app/db_sqlite_backup_$(date +%Y%m%d)
cp backend/init_database.py backend/init_database_backup.py
```

#### 1.2 Análisis de Dependencias

- [ ] Inventariar todos los usos de [`GameState`](backend/app/services/game_state_service.py)
- [ ] Mapear temporizadores en [`GamePhaseController`](backend/app/services/game_phases_service.py)
- [ ] Identificar datos críticos no persistentes
- [ ] Crear matriz de compatibilidad

#### 1.3 Crear Modelos Extendidos

```python
# Archivo: backend/app/models/game_extended.py
class GameExtended(Game):
    """Versión extendida temporal para migración."""
    # Nuevos campos aquí
```

#### ✅ Verificación Fase 1

- [ ] Tests backend siguen pasando: `cd backend && pytest -q`
- [ ] Frontend sigue funcionando: `npm run dev`
- [ ] Backup verificado y restaurable

---

### 🗄️ FASE 2: Migración de Base de Datos (Día 2-3)

**Duración:** 2 días  
**Objetivo:** Añadir nuevos campos sin romper estructura actual

#### 2.1 Actualizar Modelo SQLAlchemy

```python
# En backend/app/database.py
class GameDB(Base):
    # ... campos existentes ...
    
    # Nuevos campos con valores por defecto
    current_phase = Column(String, nullable=False, default="waiting")
    phase_start_time = Column(DateTime, nullable=True)
    phase_duration_seconds = Column(Integer, nullable=True)
    phase_auto_advance = Column(Boolean, nullable=False, default=True)
    next_phase_at = Column(DateTime, nullable=True)
    phase_end_actions = Column(SQLiteJSON, nullable=False, default=list)
    
    voting_active = Column(Boolean, nullable=False, default=False)
    voting_start_time = Column(DateTime, nullable=True)
    voting_end_time = Column(DateTime, nullable=True)
    voting_type = Column(String, nullable=True)
    
    pending_night_actions = Column(SQLiteJSON, nullable=False, default=dict)
    completed_night_actions = Column(SQLiteJSON, nullable=False, default=list)
    night_action_deadline = Column(DateTime, nullable=True)
    
    auto_advance_enabled = Column(Boolean, nullable=False, default=True)
    manual_control = Column(Boolean, nullable=False, default=False)
    game_speed = Column(String, nullable=False, default="normal")
    
    connection_metadata = Column(SQLiteJSON, nullable=False, default=dict)
    last_activity_times = Column(SQLiteJSON, nullable=False, default=dict)
```

#### 2.2 Script de Migración

```python
# Archivo: backend/scripts/migrate_game_model.py
def migrate_existing_games():
    """Migra juegos existentes al nuevo modelo."""
    with get_db_session() as db:
        games = db.query(GameDB).all()
        for game in games:
            # Establecer valores por defecto para nuevos campos
            if not hasattr(game, 'current_phase'):
                game.current_phase = game.status  # Mapear status actual
                game.phase_start_time = datetime.utcnow()
                game.auto_advance_enabled = True
                # ... otros campos
        db.commit()
```

#### 2.3 Actualizar Funciones de Conversión

```python
# En backend/app/database.py
def to_pydantic(self) -> Game:
    """Actualizar conversión con nuevos campos."""
    return Game(
        # ... campos existentes ...
        current_phase=GamePhase(self.current_phase),
        phase_start_time=self.phase_start_time,
        # ... nuevos campos
    )
```

#### ✅ Verificación Fase 2

- [ ] Migración ejecuta sin errores
- [ ] Datos existentes preservados
- [ ] Tests de base de datos pasan
- [ ] Rollback funcional disponible

---

### 🔄 FASE 3: Servicios de Transición (Día 4-5)

**Duración:** 2 días  
**Objetivo:** Crear servicios nuevos manteniendo compatibilidad

#### 3.1 Crear GameDatabaseService

```python
# Archivo: backend/app/services/game_database_service.py
class GameDatabaseService:
    @staticmethod
    def get_game_with_lock(game_id: str) -> Optional[Game]:
        """Obtiene juego con lock para modificación segura."""
        
    @staticmethod
    def update_phase(game_id: str, new_phase: GamePhase, 
                    duration_seconds: Optional[int] = None) -> bool:
        """Actualiza fase y establece timer automático."""
        
    @staticmethod
    def get_games_ready_for_phase_advance() -> List[Game]:
        """Obtiene juegos listos para avanzar de fase."""
        
    @staticmethod
    def record_player_action(game_id: str, user_id: str, 
                           action_type: str, action_data: dict) -> bool:
        """Registra acción de jugador en base de datos."""
```

#### 3.2 Crear GameAutomationService

```python
# Archivo: backend/app/services/game_automation_service.py
class GameAutomationService:
    @classmethod
    async def start_automation_loop(cls):
        """Inicia bucle de automatización (reemplazo de temporizadores)."""
        while True:
            await cls.process_all_games()
            await asyncio.sleep(5)  # Verificar cada 5 segundos
            
    @classmethod
    async def process_all_games(cls):
        """Procesa todos los juegos para avance automático."""
        games = GameDatabaseService.get_games_ready_for_phase_advance()
        for game in games:
            await cls.advance_game_phase(game.id)
```

#### 3.3 Integración Gradual

- [ ] Mantener [`GameState`](backend/app/services/game_state_service.py) como wrapper temporal
- [ ] Redirigir operaciones críticas a nuevo servicio
- [ ] Logging detallado para comparar comportamientos

#### ✅ Verificación Fase 3

- [ ] Servicios nuevos funcionan correctamente
- [ ] [`GameState`](backend/app/services/game_state_service.py) sigue operativo
- [ ] No hay degradación de performance
- [ ] WebSocket sigue funcionando

---

### 🔧 FASE 4: Migración de Lógica (Día 6-7)

**Duración:** 2 días  
**Objetivo:** Migrar lógica de temporizadores a base de datos

#### 4.1 Refactorizar Game Flow

```python
# En backend/app/services/game_flow_service.py
def start_day_phase(game_id: str) -> Optional[Game]:
    """Inicia fase de día usando nuevo sistema."""
    return GameDatabaseService.update_phase(
        game_id=game_id,
        new_phase=GamePhase.DAY_DISCUSSION,
        duration_seconds=300  # 5 minutos
    )

def start_night_phase(game_id: str) -> Optional[Game]:
    """Inicia fase de noche usando nuevo sistema."""
    return GameDatabaseService.update_phase(
        game_id=game_id, 
        new_phase=GamePhase.NIGHT_ACTIONS,
        duration_seconds=180  # 3 minutos
    )
```

#### 4.2 Actualizar WebSocket Handlers

```python
# En backend/app/websocket/game_handlers.py  
async def handle_phase_change(websocket: WebSocket, game_id: str, data: dict):
    """Maneja cambio de fase usando base de datos."""
    # Usar GameDatabaseService en lugar de GameState
    result = GameDatabaseService.advance_phase(game_id)
    if result:
        await broadcast_game_update(game_id, result)
```

#### 4.3 Eliminar Temporizadores Asyncio

- [ ] Identificar todos los `asyncio.create_task()`
- [ ] Reemplazar con timestamps en base de datos
- [ ] Actualizar bucle de automatización

#### ✅ Verificación Fase 4

- [ ] Juegos avanzan de fase correctamente
- [ ] Temporizadores funcionan con timestamps
- [ ] WebSocket mantiene funcionalidad
- [ ] Performance no se degrada

---

### 🧹 FASE 5: Limpieza y Simplificación (Día 8-9)

**Duración:** 2 días  
**Objetivo:** Eliminar código obsoleto y simplificar

#### 5.1 Eliminar Servicios Obsoletos

```bash
# Backup y eliminación progresiva
mv backend/app/services/game_state_service.py backend/app/services/deprecated/
mv backend/app/services/game_phases_service.py backend/app/services/deprecated/
```

#### 5.2 Simplificar Game Responses

```python
# En backend/app/services/game_responses_service.py
class GameResponsesService:
    @staticmethod
    def get_game_response_by_id(game_id: str) -> Optional[GameResponse]:
        """Simplificado: obtiene directamente de base de datos."""
        game = GameDatabaseService.get_game(game_id)
        if not game:
            return None
        return GameResponse(
            game_id=game.id,
            name=game.name,
            # ... mapeo directo desde Game
        )
```

#### 5.3 Actualizar Endpoints

- [ ] Simplificar [`routes_game.py`](backend/app/api/routes_game.py)
- [ ] Eliminar dependencias de servicios obsoletos
- [ ] Consolidar lógica en GameDatabaseService

#### ✅ Verificación Fase 5

- [ ] Compilación sin warnings
- [ ] Tests completos pasan
- [ ] No hay imports de servicios eliminados
- [ ] Funcionalidad completa preservada

---

### 🧪 FASE 6: Testing y Validación (Día 10-11)

**Duración:** 2 días  
**Objetivo:** Asegurar robustez del sistema migrado

#### 6.1 Tests de Persistencia

```python
# Archivo: backend/tests/test_persistence_migration.py
def test_game_survives_restart():
    """Verifica que estado se mantiene tras reinicio."""
    # Crear juego, avanzar fase, simular reinicio
    
def test_phase_timers_work():
    """Verifica que temporizadores basados en timestamps funcionan."""
    
def test_concurrent_access():
    """Verifica que acceso concurrente es seguro."""
```

#### 6.2 Tests de Integración

```python
def test_full_game_flow():
    """Prueba flujo completo de juego usando solo base de datos."""
    
def test_websocket_consistency():
    """Verifica que WebSocket y base de datos están sincronizados."""
```

#### 6.3 Performance Testing

- [ ] Medir latencia de operaciones de base de datos
- [ ] Comparar performance antes/después
- [ ] Optimizar queries si es necesario

#### ✅ Verificación Fase 6

- [ ] 100% tests pasan
- [ ] Performance aceptable (< 100ms por operación)
- [ ] Stress testing exitoso
- [ ] Funcionalidad completa verificada

---

### 📚 FASE 7: Documentación y Deploy (Día 12)

**Duración:** 1 día  
**Objetivo:** Documentar y preparar para producción

#### 7.1 Actualizar Documentación

- [ ] Actualizar [`openapi.json`](openapi.json)
- [ ] Documentar nuevos servicios
- [ ] Crear guía de troubleshooting
- [ ] Actualizar README con cambios

#### 7.2 Scripts de Migración para Producción

```python
# Archivo: backend/scripts/production_migration.py
def migrate_production_database():
    """Script seguro para migrar base de datos en producción."""
```

#### 7.3 Preparar Rollback

```python
def rollback_migration():
    """Rollback completo a versión anterior."""
```

#### ✅ Verificación Fase 7

- [ ] Documentación completa
- [ ] Scripts de migración probados
- [ ] Rollback plan verificado
- [ ] Lista para deploy

---

## 🎯 Criterios de Éxito

### ✅ Funcionales

- [ ] **Estado único**: Toda información crítica persiste en base de datos
- [ ] **Sin temporizadores**: Sistema funciona solo con timestamps
- [ ] **Reinicio seguro**: Estado se mantiene tras reinicio completo
- [ ] **Funcionalidad completa**: Todas las características actuales funcionan

### ✅ Técnicos

- [ ] **Performance**: Operaciones < 100ms
- [ ] **Concurrencia**: Acceso seguro multi-usuario
- [ ] **Escalabilidad**: Preparado para múltiples instancias
- [ ] **Mantenibilidad**: Código simplificado y limpio

### ✅ Operacionales

- [ ] **Monitoring**: Logs y métricas adecuadas
- [ ] **Backup**: Estrategia de respaldo robusta
- [ ] **Rollback**: Plan de reversión probado
- [ ] **Documentación**: Guías completas para equipo

---

## 🚨 Riesgos y Mitigaciones

### 🔴 Riesgo Alto: Pérdida de Estado Durante Migración

**Mitigación:**

- Migración incremental con rollback en cada fase
- Backup automático antes de cada cambio
- Tests de persistencia exhaustivos

### 🟡 Riesgo Medio: Degradación de Performance

**Mitigación:**

- Benchmarking antes/después de cada fase
- Optimización de queries críticas
- Índices de base de datos apropiados

### 🟡 Riesgo Medio: Incompatibilidad con Frontend

**Mitigación:**

- Mantener APIs existentes durante transición
- Versionado de endpoints si es necesario
- Tests de integración frontend-backend

---

## 📊 Timeline y Recursos

### 📅 Cronograma

```table
Día 1-2:  Preparación y migración BD     [2 días]
Día 3-5:  Servicios de transición        [3 días] 
Día 6-8:  Migración de lógica            [3 días]
Día 9-10: Limpieza y simplificación      [2 días]
Día 11:   Testing y validación           [1 día]
Día 12:   Documentación y deploy         [1 día]
─────────────────────────────────────────────────
TOTAL:    12 días laborables              [~2.5 semanas]
```

### 👥 Recursos Necesarios

- **Desarrollador Backend Senior**: 100% tiempo
- **DevOps/DBA**: 25% tiempo (soporte migración BD)
- **QA/Testing**: 25% tiempo (validación y tests)

---

## 🔄 Plan de Rollback

### 🚨 Activadores de Rollback

- Tests de regresión fallan > 20%
- Performance degradada > 50%
- Pérdida de funcionalidad crítica
- Errores de corrupción de datos

### 📋 Procedimiento de Rollback

1. **Parar aplicación**: `systemctl stop hombres_lobo_backend`
2. **Restaurar BD**: `cp db_sqlite_backup/* db_sqlite/`
3. **Revertir código**: `git revert --mainline 1 <merge_commit>`
4. **Verificar**: Ejecutar suite de tests
5. **Reiniciar**: `systemctl start hombres_lobo_backend`

---

## 📈 Beneficios Post-Migración

### 🎯 Inmediatos

- **Confiabilidad**: No pérdida de estado ante fallos
- **Simplicidad**: Código más mantenible
- **Debugging**: Trazabilidad completa

### 🚀 A Largo Plazo

- **Escalabilidad**: Múltiples instancias backend
- **Analytics**: Análisis de datos de partidas
- **Recovery**: Recuperación ante desastres
- **Features**: Nuevas funcionalidades más fáciles

---

## 📞 Contacto y Revisiones

### 👥 Equipo de Migración

- **Lead**: Desarrollador Backend Senior
- **Review**: Team Lead / Arquitecto
- **Support**: DevOps Engineer

### 📅 Checkpoints de Revisión

- **Día 3**: Revisión migración BD
- **Día 6**: Revisión servicios de transición  
- **Día 9**: Revisión eliminación temporizadores
- **Día 12**: Revisión final y go/no-go para deploy

---

> **🎯 OBJETIVO FINAL:** Transformar la aplicación de un sistema híbrido memoria/BD a una arquitectura completamente basada en base de datos, garantizando persistencia, simplicidad y escalabilidad.

**Estado:** 📋 **PENDIENTE DE APROBACIÓN**  
**Prioridad:** 🔴 **ALTA** (Arquitectura crítica)  
**Estimación:** 12 días laborables  
**Riesgo:** 🟡 **MEDIO** (Migración controlada)
