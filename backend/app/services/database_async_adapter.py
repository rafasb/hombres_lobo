# Adaptador asíncrono para operaciones de base de datos
# Mantiene las operaciones de DB síncronas pero las envuelve para uso async cuando sea necesario

import asyncio
from functools import wraps
from typing import Callable, Any
from concurrent.futures import ThreadPoolExecutor

# Thread pool para operaciones de DB síncronas en contexto async
db_executor = ThreadPoolExecutor(max_workers=4, thread_name_prefix="db_")

def run_in_executor(func: Callable) -> Callable:
    """Decorator para ejecutar funciones síncronas en un executor."""
    @wraps(func)
    async def wrapper(*args, **kwargs) -> Any:
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(db_executor, func, *args, **kwargs)
    return wrapper

# Adapters async para operaciones críticas
@run_in_executor
def save_game_async(game):
    from app.database import save_game
    return save_game(game)

@run_in_executor  
def load_game_async(game_id: str):
    from app.database import load_game
    return load_game(game_id)