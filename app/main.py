from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from app.api import routes_games, routes_admin, routes_users, routes_players_voting, routes_warewolfs, routes_special_roles, routes_sheriff, routes_hunter, routes_witch

app = FastAPI()

# Montar archivos estáticos
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Configuración de plantillas Jinja2
templates = Jinja2Templates(directory="app/templates")

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
