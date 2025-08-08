#!/bin/bash

# Script para iniciar el servidor FastAPI de Hombres Lobo
# Descripción: Configura el entorno virtual de Python y ejecuta el servidor

# Colores para output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${GREEN}🐺 Iniciando servidor Hombres Lobo...${NC}"

# Directorio del script
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Nombre del entorno virtual
VENV_NAME="venv"
VENV_PATH="$SCRIPT_DIR/$VENV_NAME"

# Función para crear el entorno virtual
create_venv() {
    echo -e "${YELLOW}📦 Creando entorno virtual...${NC}"
    python3 -m venv "$VENV_NAME"
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✅ Entorno virtual creado exitosamente${NC}"
    else
        echo -e "${RED}❌ Error al crear el entorno virtual${NC}"
        exit 1
    fi
}

# Verificar si existe el entorno virtual
if [ ! -d "$VENV_PATH" ]; then
    echo -e "${YELLOW}⚠️  Entorno virtual no encontrado${NC}"
    create_venv
fi

# Activar entorno virtual
echo -e "${YELLOW}🔄 Activando entorno virtual...${NC}"
source "$VENV_PATH/bin/activate"

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Entorno virtual activado${NC}"
else
    echo -e "${RED}❌ Error al activar el entorno virtual${NC}"
    exit 1
fi

# Verificar si requirements.txt existe e instalar dependencias si es necesario
if [ -f "requirements.txt" ]; then
    echo -e "${YELLOW}📋 Verificando dependencias...${NC}"
    
    # Verificar si FastAPI está instalado
    pip show fastapi > /dev/null 2>&1
    if [ $? -ne 0 ]; then
        echo -e "${YELLOW}📦 Instalando dependencias...${NC}"
        pip install -r requirements.txt
        if [ $? -eq 0 ]; then
            echo -e "${GREEN}✅ Dependencias instaladas exitosamente${NC}"
        else
            echo -e "${RED}❌ Error al instalar las dependencias${NC}"
            exit 1
        fi
    else
        echo -e "${GREEN}✅ Dependencias ya están instaladas${NC}"
    fi
else
    echo -e "${RED}❌ Archivo requirements.txt no encontrado${NC}"
    exit 1
fi

# Verificar que el módulo app existe
if [ ! -d "app" ]; then
    echo -e "${RED}❌ Directorio 'app' no encontrado${NC}"
    exit 1
fi

# Configurar variables de entorno si existe archivo .env
if [ -f ".env" ]; then
    echo -e "${YELLOW}🔧 Cargando variables de entorno desde .env${NC}"
    set -o allexport
    source .env
    set +o allexport
fi

# Mostrar información del servidor
echo -e "${GREEN}"
echo "🚀 Iniciando servidor FastAPI..."
echo "📍 Módulo: app.main:app"
echo "🌐 Host: 0.0.0.0"
echo "🔌 Puerto: 8000"
echo "🔄 Recarga automática: Habilitada"
echo "📖 Documentación disponible en: http://localhost:8000/docs"
echo "📋 ReDoc disponible en: http://localhost:8000/redoc"
echo -e "${NC}"

# Ejecutar el servidor
echo -e "${YELLOW}🎯 Ejecutando uvicorn...${NC}"
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

# Capturar la señal de interrupción (Ctrl+C)
trap 'echo -e "\n${YELLOW}🛑 Deteniendo servidor...${NC}"; exit 0' INT

echo -e "${GREEN}👋 Servidor detenido${NC}"
