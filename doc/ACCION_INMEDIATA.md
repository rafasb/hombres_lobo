# ⚡ ACCIÓN INMEDIATA REQUERIDA

## 🎯 Resumen Ejecutivo

El proyecto actual está configurado con **Jinja2 templates** (frontend server-side), pero las especificaciones han sido actualizadas para usar **Vue.js 3 SPA**. Se requiere una migración completa de la arquitectura frontend.

## 🚨 Estado Crítico Detectado

### ❌ Problemas Identificados:
1. **Frontend actual:** Jinja2 templates en `/app/templates/` - **OBSOLETO**
2. **Archivos estáticos:** `/app/static/` mezclados con backend - **ARQUITECTURA INCORRECTA**
3. **main.py:** Configurado para servir templates - **DEBE SER API PURA**
4. **TODO.md anterior:** Mencionaba Vue.js pero **NO EXISTE IMPLEMENTACIÓN**

### ✅ Assets Válidos:
- **Backend FastAPI:** ✅ Funcional y completo
- **API endpoints:** ✅ Implementados correctamente
- **Lógica de negocio:** ✅ Sistema completo de Hombres Lobo
- **Base de datos:** ✅ Modelos y persistencia funcionando

---

## 🚀 PLAN DE ACCIÓN INMEDIATO

### **PASO 1: EJECUTAR MIGRACIÓN AUTOMÁTICA**
```bash
cd /home/rafasb/desarrollo/hombres_lobo
./migrate_phase1.sh
```

Este script:
- ✅ Crea backup de seguridad
- ✅ Restructura proyecto en `backend/` y `frontend/`
- ✅ Elimina templates y static obsoletos
- ✅ Mueve archivos a nueva estructura

### **PASO 2: REFACTORIZAR BACKEND (MANUAL)**

**Editar `backend/app/main.py`:**
```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
# ELIMINAR: from fastapi.staticfiles import StaticFiles
# ELIMINAR: from fastapi.templating import Jinja2Templates

app = FastAPI(title="Hombres Lobo API", version="2.0.0")

# AGREGAR: Configuración CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ELIMINAR: app.mount("/static", StaticFiles...)
# ELIMINAR: templates = Jinja2Templates(...)

# Mantener todas las rutas API:
app.include_router(routes_users.router)
app.include_router(routes_games.router)
# ... resto de routers
```

**Actualizar `backend/requirements.txt`:**
```bash
# ELIMINAR línea: jinja2
# AGREGAR línea: fastapi[cors]
```

### **PASO 3: VERIFICAR API FUNCIONA**
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Linux/Mac
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

Probar: http://localhost:8000/docs

### **PASO 4: CREAR FRONTEND VUE.JS**
```bash
cd frontend
npm create vue@latest . --typescript --router --pinia
npm install
npm install axios vuetify@next @vuetify/vite-plugin
npm run dev
```

---

## 📋 CHECKLIST DE MIGRACIÓN

### ✅ Fase 1: Restructuración (HOY)
- [ ] Ejecutar `migrate_phase1.sh`
- [ ] Refactorizar `backend/app/main.py`
- [ ] Actualizar `backend/requirements.txt`
- [ ] Probar API en http://localhost:8000/docs
- [ ] Verificar que endpoints devuelven JSON

### 📋 Fase 2: Frontend Vue.js (SIGUIENTE)
- [ ] Crear proyecto Vue.js 3 en `frontend/`
- [ ] Configurar proxy hacia backend
- [ ] Implementar servicios de API
- [ ] Crear stores de Pinia
- [ ] Desarrollar componentes base

### 📋 Fase 3: Migración Funcional (DESPUÉS)
- [ ] Autenticación JWT
- [ ] Gestión de juegos
- [ ] Interfaz de juego
- [ ] Testing E2E

---

## 🔗 Documentación Completa

- **📄 [ESPECIFICACIONES_Y_PLANIFICACION.md](./doc/ESPECIFICACIONES_Y_PLANIFICACION.md)** - Especificaciones actualizadas
- **📄 [PLANIFICACION_REORIENTACION_FRONTEND.md](./doc/PLANIFICACION_REORIENTACION_FRONTEND.md)** - Plan detallado completo
- **📄 [TODO.md](./doc/TODO.md)** - Lista de tareas actualizada

---

## ⚠️ ADVERTENCIAS

1. **NO eliminar nada sin hacer backup primero**
2. **El script migrate_phase1.sh crea backup automático**
3. **Probar que el backend funciona ANTES de continuar**
4. **La migración es IRREVERSIBLE una vez completada**

---

## 🆘 Si algo sale mal

1. **Restaurar desde backup:**
   ```bash
   rm -rf backend frontend
   cp -r migration_backup/* .
   ```

2. **Contactar para soporte de migración**

3. **Revisar logs y documentación**

---

**🎯 OBJETIVO:** Tener backend API pura funcionando y frontend Vue.js base creado para continuar desarrollo según especificaciones actualizadas.
