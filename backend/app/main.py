from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from app.api import routes_games, routes_admin, routes_users, routes_players_voting, routes_warewolfs, routes_special_roles, routes_sheriff, routes_hunter, routes_witch, routes_wild_child, routes_cupid, routes_game_flow
from app.websocket.message_handlers import websocket_endpoint

app = FastAPI(
    title="Hombres Lobo API",
    description="API REST para el juego Hombres Lobo - Backend puro para frontend Vue.js",
    version="2.0.0"
)

# Configuración CORS para comunicación con frontend Vue.js
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",  # Vite dev server (Vue.js)
        "http://localhost:5174",  # Nuevo puerto dev server
        "http://localhost:3000",  # Alternative dev port
        "http://127.0.0.1:5173",
        "http://127.0.0.1:5174",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# WebSocket endpoint para tiempo real
@app.websocket("/ws/{game_id}")
async def websocket_game_endpoint(websocket: WebSocket, game_id: str, token: str):
    """Endpoint WebSocket para comunicación en tiempo real del juego"""
    await websocket_endpoint(websocket, game_id, token)

# Incluir rutas
app.include_router(routes_users.router)
app.include_router(routes_games.router)
app.include_router(routes_admin.router)
app.include_router(routes_warewolfs.router)
app.include_router(routes_players_voting.router)
app.include_router(routes_special_roles.router)
app.include_router(routes_sheriff.router)
app.include_router(routes_hunter.router)
app.include_router(routes_witch.router)
app.include_router(routes_wild_child.router)
app.include_router(routes_cupid.router)
app.include_router(routes_game_flow.router)
