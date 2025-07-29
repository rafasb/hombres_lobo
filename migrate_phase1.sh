#!/bin/bash
# Migración Fase 1: Restructuración y Limpieza Frontend
# Ejecutar desde el directorio raíz del proyecto

set -e  # Terminar si hay errores

echo "🚀 Iniciando migración Fase 1: Restructuración Frontend"
echo "======================================================="

# Crear backup antes de la migración
echo "📦 Creando backup del estado actual..."
mkdir -p migration_backup
cp -r app migration_backup/
cp -r tests migration_backup/
cp requirements.txt migration_backup/
cp .env migration_backup/ 2>/dev/null || echo "No .env file found"
cp .env.example migration_backup/ 2>/dev/null || echo "No .env.example file found"
echo "✅ Backup creado en migration_backup/"

# Crear nueva estructura de directorios
echo "📁 Creando nueva estructura backend/frontend..."
mkdir -p backend
mkdir -p frontend

# Mover archivos del backend a nueva estructura
echo "🔄 Moviendo backend a nueva estructura..."
mv app backend/
mv tests backend/
mv requirements.txt backend/

# Mover archivos de configuración del backend
mv .env backend/ 2>/dev/null || echo "No .env file to move"
mv .env.example backend/ 2>/dev/null || echo "No .env.example file to move"

echo "🗑️ Eliminando archivos frontend obsoletos..."
# Eliminar templates y static del backend
rm -rf backend/app/templates
rm -rf backend/app/static

echo "✅ Estructura migrada:"
echo "├── backend/"
echo "│   ├── app/"
echo "│   ├── tests/"
echo "│   └── requirements.txt"
echo "├── frontend/ (vacío - para Vue.js)"
echo "└── migration_backup/ (backup seguridad)"

echo ""
echo "🔧 PRÓXIMOS PASOS MANUALES:"
echo "1. Editar backend/app/main.py para eliminar Jinja2 y static files"
echo "2. Agregar CORS middleware"
echo "3. Actualizar imports si es necesario"
echo "4. Eliminar 'jinja2' de backend/requirements.txt"
echo "5. Probar que la API funciona: cd backend && uvicorn app.main:app --reload"
echo ""
echo "📚 Consultar doc/PLANIFICACION_REORIENTACION_FRONTEND.md para más detalles"
