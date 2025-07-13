from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from app.api import routes_games, routes_admin, routes_users, routes_players

app = FastAPI()

# Montar archivos estáticos
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Configuración de plantillas Jinja2
templates = Jinja2Templates(directory="app/templates")

# Incluir rutas
app.include_router(routes_users.router)
app.include_router(routes_games.router)
app.include_router(routes_admin.router)
app.include_router(routes_players.router)
