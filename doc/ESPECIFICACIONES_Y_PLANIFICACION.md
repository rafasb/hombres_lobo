# Especificaciones y Planificación del Proyecto: Aplicación Web "Hombres Lobo"

## 1. Descripción General
La aplicación web "Hombres Lobo" será una plataforma orientada a dispositivos móviles que permitirá a los usuarios interactuar con funcionalidades específicas a través de una interfaz web moderna y responsiva. El backend estará desarrollado en Python utilizando FastAPI como API REST, mientras que el frontend será una Single Page Application (SPA) desarrollada con Vue.js 3 y componentes UI modernos para asegurar una experiencia de usuario óptima en móviles.

## 2. Tecnologías a Utilizar
### Backend:
- **Framework:** Python 3.x, FastAPI
- **API:** REST API con documentación automática (OpenAPI/Swagger)
- **Servidor Web:** Uvicorn
- **Gestión de dependencias:** pip, requirements.txt
- **Modelado y validación de datos:** Pydantic
- **Autenticación:** JWT (JSON Web Tokens)
- **CORS:** FastAPI CORS middleware para comunicación frontend-backend

### Frontend:
- **Framework:** Vue.js 3 (Composition API)
- **Build Tool:** Vite
- **UI Framework:** Vuetify 3 o PrimeVue (componentes mobile-first)
- **State Management:** Pinia (para gestión de estado global)
- **Router:** Vue Router 4
- **HTTP Client:** Axios
- **Desarrollo:** Node.js, npm/yarn

### Despliegue:
- **Backend:** Docker, Gunicorn/Uvicorn
- **Frontend:** Build estático servido por Nginx o CDN
- **Arquitectura:** Separación completa frontend/backend

## 3. Estructura del Proyecto (Detallada)

```
/ (raíz del proyecto)
│
├── backend/                  # Aplicación FastAPI (API REST)
│   ├── app/
│   │   ├── main.py          # Punto de entrada FastAPI, configuración CORS
│   │   ├── core/            # Configuración central y utilidades
│   │   │   ├── config.py    # Configuración general (variables de entorno, settings)
│   │   │   ├── security.py  # JWT, autenticación y autorización
│   │   │   └── dependencies.py # Dependencias reutilizables para rutas
│   │   ├── api/             # Rutas API REST
│   │   │   ├── __init__.py
│   │   │   ├── routes_auth.py    # Endpoints de autenticación (JWT)
│   │   │   ├── routes_users.py   # Endpoints de usuarios
│   │   │   ├── routes_games.py   # Endpoints de gestión de partidas
│   │   │   └── routes_admin.py   # Endpoints de administración
│   │   ├── models/          # Modelos de datos (Pydantic)
│   │   │   ├── __init__.py
│   │   │   ├── user.py      # Modelo de usuario
│   │   │   ├── game.py      # Modelo de partida
│   │   │   └── auth.py      # Modelos de autenticación (login, register, tokens)
│   │   ├── services/        # Lógica de negocio
│   │   │   ├── __init__.py
│   │   │   ├── user_service.py   # Lógica relacionada con usuarios
│   │   │   ├── game_service.py   # Lógica relacionada con partidas
│   │   │   └── auth_service.py   # Lógica de autenticación y JWT
│   │   └── database.py      # Configuración y conexión a la base de datos
│   ├── tests/               # Pruebas backend
│   │   ├── __init__.py
│   │   ├── test_auth.py
│   │   ├── test_users.py
│   │   ├── test_games.py
│   │   └── ...
│   └── requirements.txt     # Dependencias Python
│
├── frontend/                # Aplicación Vue.js 3
│   ├── public/             # Archivos públicos estáticos
│   │   ├── index.html      # HTML base
│   │   └── favicon.ico
│   ├── src/
│   │   ├── main.js         # Punto de entrada Vue
│   │   ├── App.vue         # Componente raíz
│   │   ├── components/     # Componentes reutilizables
│   │   │   ├── common/     # Componentes comunes (Header, Footer, etc.)
│   │   │   ├── auth/       # Componentes de autenticación
│   │   │   ├── games/      # Componentes de partidas
│   │   │   └── ui/         # Componentes UI específicos
│   │   ├── views/          # Páginas/Vistas principales
│   │   │   ├── HomeView.vue
│   │   │   ├── LoginView.vue
│   │   │   ├── RegisterView.vue
│   │   │   ├── GamesView.vue
│   │   │   └── GameView.vue
│   │   ├── router/         # Configuración de rutas
│   │   │   └── index.js
│   │   ├── stores/         # Estado global (Pinia)
│   │   │   ├── auth.js     # Store de autenticación
│   │   │   ├── games.js    # Store de partidas
│   │   │   └── user.js     # Store de usuario
│   │   ├── services/       # Servicios para comunicación con API
│   │   │   ├── api.js      # Configuración Axios
│   │   │   ├── authService.js
│   │   │   ├── userService.js
│   │   │   └── gameService.js
│   │   ├── composables/    # Composables Vue 3
│   │   │   ├── useAuth.js
│   │   │   └── useApi.js
│   │   ├── assets/         # Assets (CSS, imágenes, etc.)
│   │   │   ├── css/
│   │   │   ├── images/
│   │   │   └── icons/
│   │   └── utils/          # Utilidades y helpers
│   │       ├── constants.js
│   │       └── helpers.js
│   ├── package.json        # Dependencias Node.js
│   ├── vite.config.js      # Configuración Vite
│   └── ...
│
├── docs/                   # Documentación del proyecto
├── docker-compose.yml      # Orquestación de contenedores (opcional)
├── README.md              # Documentación principal
└── ...
```

### Explicación de la estructura y buenas prácticas:
- **Arquitectura separada:** Frontend y backend completamente independientes, comunicándose por API REST.
- **Separación de responsabilidades:** Cada carpeta y archivo tiene una función clara.
- **Principios SOLID:**
  - *Single Responsibility:* Cada módulo/servicio/componente tiene una única responsabilidad.
  - *Open/Closed:* Los servicios, componentes y rutas pueden extenderse sin modificar código existente.
  - *Dependency Inversion:* Las dependencias se inyectan y abstraen.
- **Vue.js 3 Best Practices:**
  - *Composition API:* Para mejor reutilización de lógica y TypeScript support.
  - *Componentes pequeños y reutilizables:* Principio de componente único.
  - *Estado centralizado:* Pinia para gestión de estado global.
  - *Separación de concerns:* Servicios para API, composables para lógica reutilizable.
- **Escalabilidad:** Permite añadir nuevas funcionalidades sin romper la estructura.
- **Testabilidad:** Pruebas separadas para frontend y backend.
- **Desarrollo independiente:** Frontend y backend pueden desarrollarse en paralelo.

> Esta arquitectura facilita el mantenimiento, la colaboración y la extensión del proyecto, además de permitir despliegues independientes.

## 4. Funcionalidades Principales
- **API REST completa** (autenticación JWT, CRUD de usuarios y partidas)
- **SPA Vue.js** con navegación fluida y reactiva
- **Autenticación de usuarios** (registro, login, logout con JWT)
- **Gestión de partidas** (crear, unirse, listar, tiempo real)
- **Interfaz de usuario responsiva** (optimizada para móviles con componentes UI modernos)
- **Estado reactivo** (gestión de estado global con Pinia)
- **Panel de administración** (opcional, con roles y permisos)
- **Comunicación en tiempo real** (WebSockets para actualizaciones en vivo)

## 5. Planificación y Fases
### Fase 1: Configuración Inicial
- Crear estructura de carpetas separada (backend/frontend)
- Configurar entorno backend (Python virtual env, FastAPI)
- Configurar entorno frontend (Node.js, Vue.js 3, Vite)
- Configurar CORS y comunicación entre ambos

### Fase 2: Desarrollo Backend (API REST)
- Definir modelos de datos (Pydantic)
- Implementar autenticación JWT
- Implementar endpoints API REST
- Documentación automática con OpenAPI/Swagger
- Pruebas unitarias backend

### Fase 3: Desarrollo Frontend Base
- Configurar Vue.js 3 con Composition API
- Configurar router y estado global (Pinia)
- Crear componentes base y layout responsivo
- Configurar servicios para comunicación con API
- Implementar autenticación en frontend

### Fase 4: Desarrollo de Funcionalidades
- Vistas de autenticación (login, registro)
- Gestión de partidas (crear, listar, unirse)
- Componentes específicos del juego
- Integración de estado reactivo
- Pruebas de componentes Vue

### Fase 5: Integración y Optimización
- Integración completa frontend-backend
- Optimización de rendimiento (lazy loading, code splitting)
- Pruebas end-to-end
- Ajustes de UX/UI para móviles
- WebSockets para tiempo real (opcional)

### Fase 6: Despliegue
- Build de producción del frontend
- Configuración de servidor backend
- Dockerización (opcional)
- Configuración de proxy/nginx
- Documentación final

## 6. Consideraciones de Diseño
- **Mobile-first:** Todo el diseño debe priorizar la experiencia en móviles.
- **SPA Performance:** Optimización de carga inicial y lazy loading de componentes.
- **Seguridad:** JWT tokens, validación en frontend y backend, CORS configurado.
- **Escalabilidad:** Arquitectura separada permite escalado independiente.
- **Estado Reactivo:** Uso de Pinia para gestión de estado predecible y debuggeable.
- **Componentes Reutilizables:** UI consistente con componentes modulares.
- **API First:** Backend como API REST pura, sin dependencia del frontend.

## 7. Próximos Pasos
1. Reestructurar proyecto actual para separar backend/frontend.
2. Migrar código backend actual a estructura API REST.
3. Crear proyecto Vue.js 3 desde cero.
4. Configurar comunicación entre ambos.
5. Migrar funcionalidades existentes a la nueva arquitectura.

---

> **Nota:** Esta planificación es una guía inicial y puede ajustarse según las necesidades del proyecto y el feedback recibido durante el desarrollo.
