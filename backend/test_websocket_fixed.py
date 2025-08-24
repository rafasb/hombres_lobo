import json
import os
from pathlib import Path

import pytest


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def read_text_rel(path: str) -> str:
    p = PROJECT_ROOT.joinpath(path)
    assert p.exists(), f"Fichero esperado inexistente: {p}"
    return p.read_text(encoding="utf-8")


def exists_rel(path: str) -> bool:
    return PROJECT_ROOT.joinpath(path).exists()


def load_json_rel(path: str):
    p = PROJECT_ROOT.joinpath(path)
    assert p.exists(), f"Fichero JSON inexistente: {p}"
    return json.loads(p.read_text(encoding="utf-8"))


@pytest.mark.asyncio
async def test_todo_plan_contains_mandatory_tasks():
    """Verifica que Docs/TODO.md contiene las entradas principales de la migración WS->REST+Pinia."""
    text = read_text_rel("Docs/TODO.md")
    assert "get_game_status" in text, "Falta 'get_game_status' en Docs/TODO.md"
    assert "join_game" in text, "Falta 'join_game' en Docs/TODO.md"
    assert "heartbeat" in text, "Falta 'heartbeat' en Docs/TODO.md"
    # Comprobaciones relacionadas con stores y archivos mencionados
    assert "frontend/src/stores/user.ts" in text or "frontend/src/stores/player.ts" in text


@pytest.mark.asyncio
async def test_important_backend_handlers_exist():
    """Verifica que los handlers/servicios backend referenciados en la planificación existen."""
    assert exists_rel("backend/app/websocket/connection_manager.py"), "connection_manager.py no encontrado"
    assert exists_rel("backend/app/websocket/game_handlers.py"), "game_handlers.py no encontrado"
    assert exists_rel("backend/app/services/game_state_service.py"), "game_state_service.py no encontrado"


@pytest.mark.asyncio
async def test_openapi_document_contains_game_status_endpoint():
    """Comprueba que openapi.json define el endpoint esperado para status de partidas."""
    data = load_json_rel("openapi.json")
    paths = data.get("paths", {})
    # Se busca una ruta explícita usada en la documentación: /games/{game_id}/status
    candidates = [p for p in paths.keys() if "games" in p and "status" in p]
    assert candidates, f"No se encontró ruta 'games...status' en openapi.json (paths keys: {list(paths.keys())[:10]})"


@pytest.mark.asyncio
async def test_frontend_ws_spec_exists_and_mentions_heartbeat():
    """Verifica que la especificación WS del frontend/documentación menciona 'heartbeat' y 'join_game'."""
    # Revisar tanto la especificación en frontend como la documentación rápida
    found = False
    for candidate in [
        "frontend/src/websocket/copilot-ws-messages.md",
        "backend/app/websocket/copilot-ws-messages.md",
        "Docs/WEBSOCKET_QUICK_REFERENCE.md",
        "Docs/WEBSOCKET_DOCUMENTATION.md",
    ]:
        p = PROJECT_ROOT.joinpath(candidate)
        if p.exists():
            text = p.read_text(encoding="utf-8")
            if "heartbeat" in text and "join_game" in text:
                found = True
                break
    assert found, "No se encontró especificación WS que contenga 'heartbeat' y 'join_game' en las rutas esperadas."


@pytest.mark.asyncio
async def test_integration_test_placeholder_exists():
    """Confirma que existe un test de integración WS (para referencia y CI)."""
    assert exists_rel("backend/test_websocket_status.py"), "Falta backend/test_websocket_status.py; debería existir según planificación"