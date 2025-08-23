# 🎭 FASE 7: Roles Especiales y Acciones Nocturnas
## 📊 PROGRESO: 0/5 PASOS COMPLETADOS (0%)

## 🎯 Objetivo
Implementar roles especiales con acciones nocturnas únicas, sistema de habilidades especiales y mecánicas avanzadas como amantes y transformaciones.

## 📋 PASOS PENDIENTES

### 1️⃣ SISTEMA BASE DE ROLES
**Prioridad:** 🔴 CRÍTICA  
**Tiempo:** 1.5 días

#### 1.1 Role Engine Backend
**Archivo:** `backend/app/services/role_service.py`
- [ ] Definición de roles base (Aldeano, Lobo, Vidente, Bruja, etc.)
- [ ] Sistema de habilidades por rol
- [ ] Validación de acciones según rol
- [ ] Asignación automática de roles al iniciar juego

#### 1.2 Night Actions System
**Archivo:** `backend/app/services/night_actions_service.py`
- [ ] Registro de acciones nocturnas por jugador
- [ ] Resolución de acciones en orden de prioridad
- [ ] Conflictos y resolución (múltiples acciones sobre mismo objetivo)
- [ ] Sistema de cooldown para habilidades

### 2️⃣ ROLES BÁSICOS IMPLEMENTADOS
**Prioridad:** 🔴 CRÍTICA  
**Tiempo:** 2 días

#### 2.1 Roles de Mafia
- [ ] **Hombre Lobo** - Eliminar jugador cada noche
- [ ] **Lobo Alfa** - Eliminar + inmunidad primera noche
- [ ] **Joven Lobo** - Eliminar cada 2 noches

#### 2.2 Roles de Pueblo
- [ ] **Aldeano** - Solo votar de día
- [ ] **Vidente** - Ver rol de jugador cada noche
- [ ] **Bruja** - Pociones de vida y muerte (1 uso cada una)
- [ ] **Cazador** - Al morir, mata a otro jugador
- [ ] **Cupido** - Primera noche, crea pareja de amantes

### 3️⃣ ACCIONES NOCTURNAS EN TIEMPO REAL
**Prioridad:** 🔴 CRÍTICA  
**Tiempo:** 1 día

#### 3.1 Night Phase WebSocket
**Archivo:** `backend/app/websocket/night_handlers.py`
- [ ] Handlers para acciones específicas por rol
- [ ] Validación de permisos (solo roles específicos)
- [ ] Notificación de acciones disponibles
- [ ] Timer para acciones nocturnas

#### 3.2 Frontend Night Actions
**Archivo:** `frontend/src/components/game/NightActionsPanel.vue`
- [ ] Panel de acciones según rol del jugador
- [ ] Selección de objetivos válidos
- [ ] Confirmación de acciones
- [ ] Estados: esperando, acción realizada, resolviendo

### 4️⃣ MECÁNICAS ESPECIALES
**Prioridad:** 🟡 ALTA  
**Tiempo:** 1.5 días

#### 4.1 Sistema de Amantes (Cupido)
- [ ] Creación de vínculo entre 2 jugadores
- [ ] Si uno muere, el otro también muere
- [ ] Victoria especial si solo quedan los amantes

#### 4.2 Sistema de Transformaciones
- [ ] **Niño Salvaje** - Se convierte en lobo si muere su modelo
- [ ] **Defensor del Pueblo** - Revelado al morir
- [ ] Cambios de rol durante partida

#### 4.3 Habilidades Especiales
- [ ] **Protección** (Bruja, Defensor) - Inmunidad temporal
- [ ] **Investigación** (Vidente, Detective) - Información sobre otros
- [ ] **Venganza** (Cazador) - Acción tras muerte

### 5️⃣ INTERFAZ DE ROLES
**Prioridad:** 🟡 ALTA  
**Tiempo:** 1 día

#### 5.1 Role Display Component
**Archivo:** `frontend/src/components/game/RoleCard.vue`
- [ ] Carta de rol personal con descripción
- [ ] Lista de habilidades disponibles
- [ ] Estado de habilidades (usadas/disponibles)
- [ ] Tutorial contextual por rol

#### 5.2 Actions Panel
**Archivo:** `frontend/src/components/game/RoleActionsPanel.vue`
- [ ] Panel de acciones específicas por rol
- [ ] Target selection para habilidades
- [ ] Cooldowns y limitaciones visuales
- [ ] Confirmación de acciones críticas

---

## 🎭 DEFINICIÓN DE ROLES

### 🐺 ROLES DE MAFIA

#### Hombre Lobo
- **Habilidad:** Eliminar un jugador cada noche
- **Victoria:** Igualar o superar en número a los aldeanos
- **Especial:** Conoce a otros lobos

#### Lobo Alfa  
- **Habilidad:** Eliminar + inmunidad primera noche
- **Victoria:** Igualar o superar en número a los aldeanos
- **Especial:** Lidera la manada, voto doble en eliminaciones nocturnas

### 👥 ROLES DE PUEBLO

#### Aldeano
- **Habilidad:** Solo votación diurna
- **Victoria:** Eliminar todos los lobos
- **Especial:** Ninguna

#### Vidente
- **Habilidad:** Ver rol de un jugador cada noche
- **Victoria:** Eliminar todos los lobos
- **Especial:** Información privilegiada

#### Bruja
- **Habilidad:** Poción de vida (salvar) y muerte (matar) - 1 uso cada una
- **Victoria:** Eliminar todos los lobos
- **Especial:** Puede salvar la víctima de los lobos

#### Cazador
- **Habilidad:** Al morir, elimina a otro jugador
- **Victoria:** Eliminar todos los lobos
- **Especial:** Venganza desde la tumba

#### Cupido
- **Habilidad:** Primera noche, designa 2 amantes
- **Victoria:** Eliminar todos los lobos O solo amantes vivos
- **Especial:** Crea condición de victoria alternativa

### 🔮 ROLES ESPECIALES

#### Niño Salvaje
- **Habilidad:** Elige modelo primera noche, se convierte en lobo si modelo muere
- **Victoria:** Aldeanos (inicial) / Lobos (tras transformación)
- **Especial:** Cambio de bando dinámico

#### Defensor del Pueblo
- **Habilidad:** Al morir, su rol se revela a todos
- **Victoria:** Eliminar todos los lobos
- **Especial:** Información post-mortem

---

## 🎯 SISTEMA DE PRIORIDADES NOCTURNAS

### Orden de Resolución:
1. **Protecciones** (Bruja - Poción de vida, Defensor)
2. **Investigaciones** (Vidente, Detective)
3. **Transformaciones** (Niño Salvaje check)
4. **Eliminaciones** (Lobos, Bruja - Poción de muerte)
5. **Resolución de muertes** (Amantes, Cazador)

### Conflictos:
- **Múltiples protecciones:** La primera tiene prioridad
- **Eliminar + Proteger mismo objetivo:** Protección gana
- **Cazador + Amantes:** Se resuelven en cadena

---

## 🔧 ARQUITECTURA TÉCNICA

### Backend Role System
```
backend/app/
├── services/
│   ├── role_service.py          # Motor de roles
│   ├── night_actions_service.py # Acciones nocturnas
│   ├── ability_service.py       # Sistema de habilidades
│   └── transformation_service.py # Cambios de rol
├── models/
│   ├── roles.py                 # Definiciones de roles
│   ├── abilities.py             # Habilidades específicas
│   └── night_actions.py         # Acciones nocturnas
└── websocket/
    └── night_handlers.py        # Handlers WebSocket nocturnos
```

### Frontend Role Interface
```
frontend/src/
├── components/game/
│   ├── RoleCard.vue             # Carta de rol personal
│   ├── RoleActionsPanel.vue     # Panel de acciones
│   ├── NightActionsPanel.vue    # Acciones nocturnas
│   ├── TargetSelector.vue       # Selector de objetivos
│   └── AbilityButton.vue        # Botones de habilidades
├── composables/
│   ├── useRole.ts               # Lógica de rol
│   ├── useNightActions.ts       # Acciones nocturnas
│   └── useAbilities.ts          # Sistema de habilidades
└── stores/
    └── role-game.ts             # Estado de roles
```

---

## 📊 IMPACTO EN EL PROYECTO

**Al completar esta fase tendremos:**
- 🎭 Sistema completo de roles especiales
- 🌙 Acciones nocturnas en tiempo real
- 💫 Mecánicas avanzadas (amantes, transformaciones)
- 🎯 Gameplay rico y variado
- 🔮 Base para expansiones futuras

**Progreso del proyecto:** 87.5% → 97.5%

---

## 🚀 PREPARACIÓN PARA FASE 8

Esta fase prepara para:
- Sistema de estadísticas y ranking
- Modo espectador
- Replays de partidas
- Tournaments y competiciones

---

> **🎯 OBJETIVO:** Sistema completo de roles especiales funcional
> 
> **🏁 RESULTADO ESPERADO:** Partidas con roles únicos, acciones nocturnas y mecánicas especiales
