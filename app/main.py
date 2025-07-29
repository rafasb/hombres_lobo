from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import routes_games, routes_admin, routes_users, routes_players_voting, routes_warewolfs, routes_special_roles, routes_sheriff, routes_hunter, routes_witch, routes_wild_child, routes_cupid, routes_game_flow

app = FastAPI(
    title="Hombres Lobo API",
    description="Backend API for the Hombres Lobo game",
    version="1.0.0"
)

# Configure CORS for frontend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:8080", "http://localhost:5173"],  # Vue.js development servers
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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
