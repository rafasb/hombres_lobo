# 📋 Planificación Global del Proyecto - Hombres Lobo

## 🎯 Objetivo General
Migrar de una aplicación monolítica con templates Jinja2 a una arquitectura moderna con:
- **Backend:** FastAPI (API REST pura)
- **Frontend:** Vue.js 3 SPA con TypeScript y PrimeVue

## 📊 Progreso General
**Estado actual:** 3/8 fases completadas (37.5%)  
**Tiempo invertido:** 2 días  
**Tiempo estimado restante:** 14-23 días

---

## 🚀 FASES DEL PROYECTO

### ✅ FASE 1: RESTRUCTURACIÓN BACKEND (COMPLETADA)
**Duración:** 1 día | **Completado:** 29 Jul 2025

#### Objetivos
- Separar backend del frontend
- Eliminar dependencias de Jinja2
- Configurar API REST pura

#### Tareas Completadas
- [x] Crear estructura `/backend/` y `/frontend/`
- [x] Mover código backend a nueva estructura
- [x] Eliminar `/app/templates/` y `/app/static/`
- [x] Refactorizar `main.py` (eliminar Jinja2, añadir CORS)
- [x] Actualizar `requirements.txt`
- [x] Verificar API funcionando en puerto 8000

---

### ✅ FASE 2: INSTALACIÓN FRONTEND VUE.JS (COMPLETADA)
**Duración:** 1 día | **Completado:** 29 Jul 2025

#### Objetivos
- Crear proyecto Vue.js 3 con TypeScript
- Instalar stack tecnológico completo
- Verificar funcionamiento básico

#### Tareas Completadas
- [x] Crear proyecto Vue.js 3 con `npm create vue@latest`
- [x] Instalar PrimeVue + PrimeIcons + PrimeFlex
- [x] Instalar Axios para comunicación HTTP
- [x] Configurar TypeScript y Vite
- [x] Verificar dev server funcionando en puerto 5173

---

### ✅ FASE 3: CONFIGURACIONES BASE (COMPLETADA)
**Duración:** 1 día | **Completado:** 29 Jul 2025

#### Objetivos ✅
- Configurar PrimeVue en el frontend
- Establecer comunicación con backend
- Crear servicios API base

#### Tareas Completadas
- [x] Configurar PrimeVue en `main.ts` (sin errores)
- [x] Configurar proxy backend en `vite.config.ts` 
- [x] Crear servicios API base (`api.ts`) con interceptors JWT
- [x] Crear estructura de carpetas profesional
- [x] **Probar comunicación frontend-backend: ¡EXITOSA!**

---

### � FASE 4: AUTENTICACIÓN (EN PROGRESO)
**Duración:** 2-3 días | **Estado:** Próximo paso inmediato

#### Objetivos
- Implementar login/register en frontend
- Configurar JWT token management
- Crear guards de navegación

#### Tareas
- [ ] Crear componentes de autenticación
- [ ] Implementar stores de autenticación
- [ ] Configurar interceptors de Axios
- [ ] Crear guards de Vue Router
- [ ] Integrar con endpoints de backend

---

### 📋 FASE 5: GESTIÓN DE JUEGOS (PENDIENTE)
**Duración:** 3-4 días

#### Objetivos
- Crear interfaces para gestión de juegos
- Implementar lobby y salas de espera
- Conectar con endpoints de backend

#### Tareas
- [ ] Crear vistas de gestión de juegos
- [ ] Implementar componentes de lobby
- [ ] Crear formularios de creación de juegos
- [ ] Integrar con API de juegos
- [ ] Implementar estados reactivos

---

### 📋 FASE 6: INTERFAZ DE JUEGO (PENDIENTE)
**Duración:** 5-7 días

#### Objetivos
- Crear interfaz completa del juego
- Implementar todos los roles especiales
- Gestionar fases del juego

#### Tareas
- [ ] Crear componentes de fases del juego
- [ ] Implementar componentes por rol
- [ ] Crear sistema de votaciones
- [ ] Implementar timers y eventos
- [ ] Integrar con lógica de backend

---

### 📋 FASE 7: FUNCIONALIDADES AVANZADAS (PENDIENTE)
**Duración:** 3-4 días

#### Objetivos
- Optimizar UX/UI
- Implementar funcionalidades premium
- Añadir responsive design completo

#### Tareas
- [ ] Implementar WebSockets (opcional)
- [ ] Crear animaciones y transiciones
- [ ] Optimizar para móviles
- [ ] Implementar notificaciones
- [ ] Crear sistema de temas

---

### 📋 FASE 8: TESTING Y OPTIMIZACIÓN (PENDIENTE)
**Duración:** 2-3 días

#### Objetivos
- Asegurar calidad del código
- Optimizar performance
- Preparar para producción

#### Tareas
- [ ] Crear tests unitarios
- [ ] Implementar tests E2E
- [ ] Optimizar bundle size
- [ ] Configurar build de producción
- [ ] Documentar deployment

---

## 🏗️ Arquitectura Final

### Backend (Puerto 8000)
```
backend/
├── app/
│   ├── main.py          # FastAPI + CORS
│   ├── api/             # Endpoints REST
│   ├── models/          # Modelos Pydantic
│   ├── services/        # Lógica de negocio
│   └── database.py      # Persistencia
└── requirements.txt     # Dependencias Python
```

### Frontend (Puerto 5173)
```
frontend/
├── src/
│   ├── main.ts          # Punto entrada + PrimeVue
│   ├── components/      # Componentes reutilizables
│   ├── views/           # Páginas principales
│   ├── stores/          # Estado global (Pinia)
│   ├── services/        # Servicios API
│   ├── router/          # Enrutamiento
│   └── types/           # Tipos TypeScript
└── package.json         # Dependencias Node.js
```

---

## 🔧 Stack Tecnológico

### Backend
- **FastAPI** - Framework API REST
- **Uvicorn** - Servidor ASGI
- **Pydantic** - Validación de datos
- **JWT** - Autenticación
- **CORS** - Comunicación con frontend

### Frontend
- **Vue.js 3** - Framework principal
- **TypeScript** - Tipado estático
- **PrimeVue** - Componentes UI
- **Pinia** - State management
- **Vue Router 4** - Enrutamiento
- **Axios** - Cliente HTTP
- **Vite** - Build tool

---

## 📊 Criterios de Éxito

### Técnicos
- [ ] Arquitectura completamente separada
- [ ] API REST pura sin dependencias frontend
- [ ] SPA Vue.js 3 completamente funcional
- [ ] Autenticación JWT segura
- [ ] Responsive design mobile-first
- [ ] Tests unitarios y E2E pasando

### Funcionales
- [ ] Sistema completo de Hombres Lobo
- [ ] Todos los roles especiales funcionando
- [ ] Gestión completa de partidas
- [ ] Interfaz intuitiva y moderna
- [ ] Performance optimizada

---

## 📅 Cronograma Resumido

| Fase | Estado | Duración | Fecha Objetivo |
|------|--------|----------|----------------|
| 1-3 | ✅ Completadas | 2 días | 29 Jul 2025 |
| 4 | 🔄 En progreso | 2-3 días | 1 Ago 2025 |
| 5 | 📋 Pendiente | 3-4 días | 5 Ago 2025 |
| 6 | 📋 Pendiente | 5-7 días | 12 Ago 2025 |
| 7-8 | 📋 Pendientes | 5-7 días | 19 Ago 2025 |

**Entrega estimada:** 19 Agosto 2025
