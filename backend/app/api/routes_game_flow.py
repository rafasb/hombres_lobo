"""
Rutas de la API para el control de flujo de juego.
"""

from fastapi import APIRouter, HTTPException, Depends

from app.core.dependencies import get_current_user
from app.models.user import User
from app.models.game_and_player import GameStatus, Roles
from app.services.game_flow_controller import game_flow_controller
from app.services.witch_action_service import get_witch_night_info
from app.services.cupid_action_service import can_cupid_choose_lovers, get_cupid_status, get_lovers_status
from app.services.wild_child_action_service import can_wild_child_choose_model, get_wild_child_status

router = APIRouter(prefix="/game-flow", tags=["game-flow"])


@router.post("/process-night/{game_id}")
async def process_night_phase(
    game_id: str,
    current_user: User = Depends(get_current_user)
):
    """
    Procesa completamente una fase nocturna del juego.
    Solo accesible por administradores o el creador del juego.
    """
    # En una implementación real, verificaríamos permisos aquí
    results = game_flow_controller.process_night_phase(game_id)
    
    if not results["success"]:
        raise HTTPException(
            status_code=400,
            detail=results.get("error", "Error processing night phase")
        )
    
    return {
        "success": True,
        "message": "Night phase processed successfully",
        "results": results
    }


@router.post("/process-day/{game_id}")
async def process_day_phase(
    game_id: str,
    current_user: User = Depends(get_current_user)
):
    """
    Procesa completamente una fase diurna del juego.
    Solo accesible por administradores o el creador del juego.
    """
    # En una implementación real, verificaríamos permisos aquí
    results = game_flow_controller.process_day_phase(game_id)
    
    if not results["success"]:
        raise HTTPException(
            status_code=400,
            detail=results.get("error", "Error processing day phase")
        )
    
    return {
        "success": True,
        "message": "Day phase processed successfully",
        "results": results
    }


@router.get("/game-state/{game_id}")
async def get_game_state_summary(
    game_id: str,
    current_user: User = Depends(get_current_user)
):
    """
    Obtiene un resumen completo del estado actual del juego.
    """
    summary = game_flow_controller.get_game_state_summary(game_id)
    
    if "error" in summary:
        raise HTTPException(
            status_code=404,
            detail=summary["error"]
        )
    
    return {
        "success": True,
        "message": "Game state summary retrieved",
        "summary": summary
    }


@router.get("/pending-actions/{game_id}")
async def get_pending_actions(
    game_id: str,
    current_user: User = Depends(get_current_user)
):
    """
    Obtiene las acciones pendientes para la fase actual del juego.
    """
    summary = game_flow_controller.get_game_state_summary(game_id)
    
    if "error" in summary:
        raise HTTPException(
            status_code=404,
            detail=summary["error"]
        )
    
    return {
        "success": True,
        "message": "Pending actions retrieved",
        "pending_actions": summary["pending_actions"],
        "can_advance_phase": summary["can_advance_phase"],
        "current_phase": summary["status"],
        "round": summary["round"]
    }


@router.post("/auto-advance/{game_id}")
async def auto_advance_phase(
    game_id: str,
    current_user: User = Depends(get_current_user)
):
    """
    Avanza automáticamente a la siguiente fase si no hay acciones pendientes.
    Solo accesible por administradores o el creador del juego.
    """
    # Verificar estado actual
    summary = game_flow_controller.get_game_state_summary(game_id)
    
    if "error" in summary:
        raise HTTPException(
            status_code=404,
            detail=summary["error"]
        )
    
    if not summary["can_advance_phase"]:
        raise HTTPException(
            status_code=400,
            detail=f"Cannot advance phase. Pending actions: {len(summary['pending_actions'])}"
        )
    
    # Procesar la fase actual
    if summary["status"] == "night":
        results = game_flow_controller.process_night_phase(game_id)
    elif summary["status"] == "day":
        results = game_flow_controller.process_day_phase(game_id)
    else:
        raise HTTPException(
            status_code=400,
            detail=f"Cannot process phase: {summary['status']}"
        )
    
    if not results["success"]:
        raise HTTPException(
            status_code=400,
            detail=results.get("error", "Error advancing phase")
        )
    
    return {
        "success": True,
        "message": f"Phase advanced from {summary['status']} to {results.get('next_phase', 'unknown')}",
        "results": results
    }


@router.get("/player-role-info/{game_id}")
async def get_player_role_info(
    game_id: str,
    current_user: User = Depends(get_current_user)
):
    """
    Obtiene información específica del rol del jugador actual.
    """
    from app.database import load_game
    
    game = load_game(game_id)
    if not game:
        raise HTTPException(status_code=404, detail="Game not found")
    
    if current_user.id not in game.players:
        raise HTTPException(status_code=403, detail="You are not part of this game")
    
    role_info = game.players[current_user.id]
    
    # Información básica del rol
    response = {
        "success": True,
        "player_id": current_user.id,
        "username": current_user.username,
        "role": role_info.role.value,
        "is_alive": role_info.is_alive,
        "game_status": game.status.value,
        "round": game.current_round,
        "available_actions": []
    }
    
    # Agregar acciones disponibles según el rol y fase
    if role_info.is_alive:
        if game.status == GameStatus.NIGHT:
            if role_info.role == Roles.WAREWOLF:
                response["available_actions"].append("werewolf_attack")
            elif role_info.role == Roles.SEER and not role_info.has_acted_tonight:
                response["available_actions"].append("seer_vision")
            elif role_info.role == Roles.WITCH:
                witch_info = get_witch_night_info(game_id, current_user.id)
                if witch_info["can_heal"]:
                    response["available_actions"].append("witch_heal")
                if witch_info["can_poison"]:
                    response["available_actions"].append("witch_poison")
            elif role_info.role == Roles.CUPID and game.current_round == 1:
                if can_cupid_choose_lovers(game_id, current_user.id):
                    response["available_actions"].append("cupid_choose_lovers")
            elif role_info.role == Roles.WILD_CHILD and game.current_round == 1:
                if can_wild_child_choose_model(game_id, current_user.id):
                    response["available_actions"].append("wild_child_choose_model")
                    
        elif game.status == GameStatus.DAY:
            if current_user.id not in game.day_votes:
                response["available_actions"].append("day_vote")
    
    # Información específica del rol
    if role_info.role == Roles.SEER:
        response["role_specific"] = {
            "has_used_vision_tonight": role_info.has_acted_tonight or False
        }
    elif role_info.role == Roles.WITCH:
        response["role_specific"] = {
            "has_healing_potion": role_info.has_healing_potion or False,
            "has_poison_potion": role_info.has_poison_potion or False
        }
    elif role_info.role == Roles.WILD_CHILD:
        status = get_wild_child_status(game_id, current_user.id)
        response["role_specific"] = status
    elif role_info.role == Roles.CUPID:
        status = get_cupid_status(game_id, current_user.id)
        response["role_specific"] = status
    elif role_info.role == Roles.SHERIFF:
        response["role_specific"] = {
            "has_double_vote": role_info.has_double_vote or False,
            "can_break_ties": role_info.can_break_ties or False,
            "successor_id": role_info.successor_id
        }
    elif role_info.role == Roles.HUNTER:
        response["role_specific"] = {
            "can_revenge_kill": role_info.can_revenge_kill or False,
            "has_used_revenge": role_info.has_acted_tonight or False
        }
    
    # Información de enamorado
    if role_info.lover_partner_id != '':
        lovers_status = get_lovers_status(game_id, current_user.id)
        response["lovers_info"] = lovers_status
    
    return response


@router.get("/game-history/{game_id}")
async def get_game_history(
    game_id: str,
    current_user: User = Depends(get_current_user)
):
    """
    Obtiene el historial de eventos del juego.
    (Placeholder - requeriría un sistema de logging de eventos)
    """
    # En una implementación completa, esto devolvería el historial de eventos
    return {
        "success": True,
        "message": "Game history feature not yet implemented",
        "history": []
    }
