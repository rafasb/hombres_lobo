from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

app = FastAPI()

# Montar archivos estáticos
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Configuración de plantillas Jinja2
templates = Jinja2Templates(directory="app/templates")

# Importar rutas (se agregarán en el futuro)
# from app.api import routes_auth, routes_games
# app.include_router(routes_auth.router)
# app.include_router(routes_games.router)
