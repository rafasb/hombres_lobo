import os
import json
from typing import Any

# Configuración y conexión a la base de datos

# Directorio donde se almacenarán los ficheros JSON
DB_DIR = os.path.join(os.path.dirname(__file__), 'db_json')

# Crear el directorio si no existe
os.makedirs(DB_DIR, exist_ok=True)

def get_json_path(filename: str) -> str:
    """Devuelve la ruta absoluta de un fichero JSON en la base de datos."""
    return os.path.join(DB_DIR, f"{filename}.json")

def save_json(filename: str, data: Any) -> None:
    """Guarda datos en un fichero JSON."""
    with open(get_json_path(filename), 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def load_json(filename: str) -> Any:
    """Carga datos de un fichero JSON. Devuelve None si no existe."""
    path = get_json_path(filename)
    if not os.path.exists(path):
        return None
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)
