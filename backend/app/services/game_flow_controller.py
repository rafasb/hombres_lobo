"""
Servicio maestro de flujo de juego que coordina todas las mecánicas y fases.
Este módulo orquesta el flujo completo del juego "Hombres Lobo".
"""

from typing import Dict, List, Any, Optional
from app.database import load_game, save_game
from app.models.game_and_roles import GameStatus, GameRole, Game
from app.services import player_action_service
from app.services.game_flow_service import reset_night_actions
from app.services.user_service import UserService
import logging

logger = logging.getLogger(__name__)


class GameFlowController:
    """
    Controlador maestro del flujo de juego que coordina todas las fases y mecánicas.
    """
    
    def __init__(self):
        # Los handlers se implementan directamente en los métodos process_*_phase
        pass
    
    def process_night_phase(self, game_id: str) -> Dict[str, Any]:
        """
        Procesa completamente una fase nocturna del juego.
        
        Args:
            game_id: ID de la partida
            
        Returns:
            Diccionario con los resultados de la fase nocturna
        """
        game = load_game(game_id)
        if not game or game.status != GameStatus.NIGHT:
            return {"success": False, "error": "Game not found or not in night phase"}
        
        logger.info(f"Processing night phase for game {game_id}, round {game.current_round}")
        
        results = {
            "success": True,
            "round": game.current_round,
            "events": [],
            "deaths": [],
            "transformations": [],
            "notifications": [],
            "next_phase": "day"
        }
        
        # 1. Procesar acciones de hombres lobo
        werewolf_results = self._process_werewolf_actions(game_id)
        if werewolf_results["victim"]:
            results["events"].append({
                "type": "werewolf_attack",
                "victim": werewolf_results["victim"],
                "victim_username": werewolf_results["victim_username"]
            })
        
        # 2. Procesar acciones de la bruja
        witch_results = self._process_witch_actions(game_id)
        if witch_results["healed"]:
            results["events"].append({
                "type": "witch_healing",
                "healed": witch_results["healed"]
            })
        if witch_results["poisoned"]:
            results["events"].append({
                "type": "witch_poison",
                "poisoned": witch_results["poisoned"]
            })
        
        # 3. Resolver muertes finales de la noche
        night_deaths = self._resolve_night_deaths(game_id, werewolf_results, witch_results)
        results["deaths"].extend(night_deaths)
        
        # 4. Procesar consecuencias de muertes
        death_consequences = self._process_death_consequences(game_id, night_deaths)
        results["transformations"].extend(death_consequences["transformations"])
        results["deaths"].extend(death_consequences["additional_deaths"])
        results["notifications"].extend(death_consequences["notifications"])
        
        # 5. Verificar condiciones de victoria
        victory_check = self._check_victory_conditions(game_id)
        if victory_check["game_over"]:
            results["game_over"] = True
            results["winners"] = victory_check["winners"]
            results["victory_type"] = victory_check["victory_type"]
            results["next_phase"] = "finished"
            
            # Cambiar estado del juego a FINISHED
            game = load_game(game_id)
            if game:
                game.status = GameStatus.FINISHED
                save_game(game)
        else:
            # 6. Preparar para la fase diurna
            self._prepare_day_phase(game_id)
        
        logger.info(f"Night phase completed for game {game_id}")
        return results
    
    def process_day_phase(self, game_id: str) -> Dict[str, Any]:
        """
        Procesa completamente una fase diurna del juego.
        
        Args:
            game_id: ID de la partida
            
        Returns:
            Diccionario con los resultados de la fase diurna
        """
        game = load_game(game_id)
        if not game or game.status != GameStatus.DAY:
            return {"success": False, "error": "Game not found or not in day phase"}
        
        logger.info(f"Processing day phase for game {game_id}, round {game.current_round}")
        
        results = {
            "success": True,
            "round": game.current_round,
            "events": [],
            "deaths": [],
            "notifications": [],
            "next_phase": "night"
        }
        
        # 1. Resolver votación diurna
        lynching_result = self._resolve_day_voting(game_id)
        if lynching_result["lynched_player"]:
            results["events"].append({
                "type": "lynching",
                "victim": lynching_result["lynched_player"],
                "victim_username": lynching_result["victim_username"],
                "vote_counts": lynching_result["vote_counts"]
            })
            results["deaths"].append(lynching_result["lynched_player"])
        else:
            results["events"].append({
                "type": "no_lynching",
                "reason": lynching_result["reason"]
            })
        
        # 2. Procesar consecuencias de la muerte por linchamiento
        if lynching_result["lynched_player"]:
            death_consequences = self._process_death_consequences(game_id, [lynching_result["lynched_player"]])
            results["deaths"].extend(death_consequences["additional_deaths"])
            results["notifications"].extend(death_consequences["notifications"])
        
        # 3. Verificar condiciones de victoria
        victory_check = self._check_victory_conditions(game_id)
        if victory_check["game_over"]:
            results["game_over"] = True
            results["winners"] = victory_check["winners"]
            results["victory_type"] = victory_check["victory_type"]
            results["next_phase"] = "finished"
            
            # Cambiar estado del juego a FINISHED
            game = load_game(game_id)
            if game:
                game.status = GameStatus.FINISHED
                save_game(game)
        else:
            # 4. Preparar para la próxima fase nocturna
            self._prepare_night_phase(game_id)
        
        logger.info(f"Day phase completed for game {game_id}")
        return results
    
    def _process_werewolf_actions(self, game_id: str) -> Dict[str, Any]:
        """Procesa las acciones de los hombres lobo."""
        victim_id = player_action_service.get_warewolf_attack_consensus(game_id)
        victim_username = None
        
        if victim_id:
            game: Optional[Game] = load_game(game_id)
            if game:
                for player in game.players:
                    if player == victim_id:
                        victim_usernameObject = UserService.get_user(player)
                        if victim_usernameObject:
                            victim_username = victim_usernameObject.username
                        else:
                            victim_username = "Unknown Player"
                        break
        
        return {
            "victim": victim_id,
            "victim_username": victim_username
        }
    
    def _process_witch_actions(self, game_id: str) -> Dict[str, List[str]]:
        """Procesa las acciones de la bruja."""
        return player_action_service.process_witch_night_actions(game_id)
    
    def _resolve_night_deaths(self, game_id: str, werewolf_results: Dict, witch_results: Dict) -> List[str]:
        """
        Resuelve las muertes de la noche considerando ataques de hombres lobo y acciones de bruja.
        """
        game = load_game(game_id)
        if not game:
            return []
        
        deaths = []
        
        # Procesar ataque de hombres lobo
        if werewolf_results["victim"]:
            victim_id = werewolf_results["victim"]
            # Verificar si la bruja curó a la víctima
            if victim_id not in witch_results["healed"]:
                # La víctima muere
                if victim_id in game.roles:
                    game.roles[victim_id].is_alive = False
                    deaths.append(victim_id)
        
        # Las muertes por veneno ya se procesaron en process_witch_night_actions
        deaths.extend(witch_results["poisoned"])
        
        save_game(game)
        return deaths
    
    def _process_death_consequences(self, game_id: str, dead_players: List[str]) -> Dict[str, List]:
        """
        Procesa todas las consecuencias de las muertes: transformaciones, venganzas, etc.
        """
        consequences = {
            "transformations": [],
            "additional_deaths": [],
            "notifications": []
        }
        
        for dead_player_id in dead_players:
            # 1. Verificar transformación del Niño Salvaje
            transformations = player_action_service.check_wild_child_transformation(game_id, dead_player_id)
            consequences["transformations"].extend(transformations)
            
            # Notificar a hombres lobo sobre nuevos miembros
            for transformation in transformations:
                werewolves = player_action_service.notify_werewolves_of_new_member(
                    game_id, transformation["wild_child_id"]
                )
                consequences["notifications"].append({
                    "type": "new_werewolf",
                    "new_werewolf": transformation["wild_child_id"],
                    "existing_werewolves": werewolves
                })
            
            # 2. Verificar muerte de enamorados
            lover_deaths = player_action_service.check_lovers_death(game_id, dead_player_id)
            consequences["additional_deaths"].extend(lover_deaths)
            
            if lover_deaths:
                consequences["notifications"].append({
                    "type": "lover_death",
                    "original_death": dead_player_id,
                    "lover_deaths": lover_deaths
                })
            
            # 3. Verificar venganza del cazador
            game = load_game(game_id)
            if game and dead_player_id in game.roles:
                role_info = game.roles[dead_player_id]
                if (role_info.role == GameRole.HUNTER and 
                    role_info.can_revenge_kill and 
                    not role_info.has_used_revenge):
                    
                    consequences["notifications"].append({
                        "type": "hunter_revenge_available",
                        "hunter_id": dead_player_id
                    })
            
            # 4. Verificar promoción de sucesor del alguacil
            game = load_game(game_id)
            if game and dead_player_id in game.roles:
                role_info = game.roles[dead_player_id]
                if role_info.role == GameRole.SHERIFF and role_info.successor_id:
                    promoted_game = player_action_service.promote_sheriff_successor(game_id, dead_player_id)
                    if promoted_game:
                        consequences["notifications"].append({
                            "type": "sheriff_succession",
                            "old_sheriff": dead_player_id,
                            "new_sheriff": role_info.successor_id
                        })
        
        return consequences
    
    def _resolve_day_voting(self, game_id: str) -> Dict[str, Any]:
        """
        Resuelve la votación diurna y determina quién es linchado.
        """
        vote_counts = player_action_service.get_day_vote_counts(game_id)
        
        if not vote_counts:
            return {
                "lynched_player": None,
                "victim_username": None,
                "vote_counts": [],
                "reason": "No votes cast"
            }
        
        # Encontrar el jugador con más votos
        max_votes = max(count["vote_count"] for count in vote_counts)
        tied_players = [count for count in vote_counts if count["vote_count"] == max_votes]
        
        lynched_player = None
        victim_username = None
        
        if len(tied_players) == 1:
            # No hay empate
            lynched_player = tied_players[0]["player_id"]
            victim_username = tied_players[0]["username"]
        else:
            # Hay empate, verificar si el alguacil puede desempatar
            tied_player_ids = [player["player_id"] for player in tied_players]
            sheriff_decision = self._handle_sheriff_tiebreak(game_id, tied_player_ids)
            
            if sheriff_decision:
                lynched_player = sheriff_decision["chosen_player"]
                victim_username = sheriff_decision["chosen_username"]
            else:
                return {
                    "lynched_player": None,
                    "victim_username": None,
                    "vote_counts": vote_counts,
                    "reason": "Tie vote with no sheriff tiebreak"
                }
        
        # Marcar al jugador como muerto
        if lynched_player:
            game = load_game(game_id)
            if game and lynched_player in game.roles:
                game.roles[lynched_player].is_alive = False
                save_game(game)
        
        return {
            "lynched_player": lynched_player,
            "victim_username": victim_username,
            "vote_counts": vote_counts,
            "reason": "Lynching successful"
        }
    
    def _handle_sheriff_tiebreak(self, game_id: str, tied_players: List[str]) -> Optional[Dict[str, str]]:
        """
        Maneja el desempate por parte del alguacil.
        """
        # Encontrar al alguacil
        game = load_game(game_id)
        if not game:
            return None
        
        sheriff_id = None
        for player_id, role_info in game.roles.items():
            if role_info.role == GameRole.SHERIFF and role_info.is_alive:
                sheriff_id = player_id
                break
        
        if not sheriff_id:
            return None
        
        # En una implementación real, aquí se notificaría al alguacil para que tome la decisión
        # Por ahora, retornamos None para indicar que se necesita intervención manual
        return None
    
    def _check_victory_conditions(self, game_id: str) -> Dict[str, Any]:
        """
        Verifica todas las condiciones de victoria posibles.
        """
        game = load_game(game_id)
        if not game:
            return {"game_over": False}
        
        # Contar jugadores vivos por bando
        alive_werewolves = 0
        alive_villagers = 0
        alive_players = []
        
        for player_id, role_info in game.roles.items():
            if role_info.is_alive:
                alive_players.append(player_id)
                if role_info.role == GameRole.WAREWOLF:
                    alive_werewolves += 1
                else:
                    alive_villagers += 1
        
        # 1. Verificar victoria de enamorados
        lovers_victory = player_action_service.check_lovers_victory_condition(game_id)
        if lovers_victory:
            return {
                "game_over": True,
                "victory_type": lovers_victory["victory_type"],
                "winners": lovers_victory["winners"]
            }
        
        # 2. Verificar victoria de hombres lobo
        if alive_werewolves >= alive_villagers:
            werewolf_winners = []
            for player_id, role_info in game.roles.items():
                if role_info.is_alive and role_info.role == GameRole.WAREWOLF:
                    username = None
                    for player in game.players:
                        if player == player_id:
                            usernameObject = UserService.get_user(player)
                            if usernameObject:
                                username = usernameObject.username
                            else:
                                username = "Unknown Player"
                            break
                    werewolf_winners.append({"id": player_id, "username": username})
            
            return {
                "game_over": True,
                "victory_type": "werewolves",
                "winners": werewolf_winners
            }
        
        # 3. Verificar victoria de aldeanos
        if alive_werewolves == 0:
            villager_winners = []
            for player_id, role_info in game.roles.items():
                if role_info.is_alive and role_info.role != GameRole.WAREWOLF:
                    username = None
                    for player in game.players:
                        if player == player_id:
                            usernameObject = UserService.get_user(player)
                            if usernameObject:
                                username = usernameObject.username
                            else:
                                username = "Unknown Player"
                            break
                    villager_winners.append({"id": player_id, "username": username})
            
            return {
                "game_over": True,
                "victory_type": "villagers",
                "winners": villager_winners
            }
        
        return {"game_over": False}
    
    def _prepare_day_phase(self, game_id: str):
        """Prepara el juego para la fase diurna."""
        game = load_game(game_id)
        if not game:
            return
        
        game.status = GameStatus.DAY
        
        # Resetear votos diurnos
        game.day_votes = {}
        
        save_game(game)
    
    def _prepare_night_phase(self, game_id: str):
        """Prepara el juego para la próxima fase nocturna."""
        game = load_game(game_id)
        if not game:
            return
        
        game.status = GameStatus.NIGHT
        game.current_round += 1
        
        # Resetear acciones nocturnas de todos los roles
        self._reset_all_night_actions(game_id)
        
        save_game(game)
    
    def _reset_all_night_actions(self, game_id: str):
        """Resetea las acciones nocturnas de todos los roles."""
        # Resetear acciones nocturnas generales
        reset_night_actions(game_id)
        
        # Resetear acciones específicas de cada rol
        player_action_service.reset_seer_night_actions(game_id)
        player_action_service.reset_witch_night_actions(game_id)
        player_action_service.reset_wild_child_night_actions(game_id)
        player_action_service.reset_cupid_night_actions(game_id)
    
    def get_game_state_summary(self, game_id: str) -> Dict[str, Any]:
        """
        Obtiene un resumen completo del estado actual del juego.
        """
        game = load_game(game_id)
        if not game:
            return {"error": "Game not found"}
        
        # Contar jugadores vivos por rol
        role_counts = {}
        alive_players = []
        dead_players = []
        
        for player_id, role_info in game.roles.items():
            role_name = role_info.role.value
            if role_name not in role_counts:
                role_counts[role_name] = {"alive": 0, "dead": 0}
            
            if role_info.is_alive:
                role_counts[role_name]["alive"] += 1
                alive_players.append(player_id)
            else:
                role_counts[role_name]["dead"] += 1
                dead_players.append(player_id)
        
        # Obtener acciones pendientes por fase
        pending_actions = self._get_pending_actions(game_id)
        
        return {
            "game_id": game_id,
            "status": game.status.value,
            "round": game.current_round,
            "total_players": len(game.players),
            "alive_players": len(alive_players),
            "dead_players": len(dead_players),
            "role_counts": role_counts,
            "pending_actions": pending_actions,
            "can_advance_phase": len(pending_actions) == 0
        }
    
    def _get_pending_actions(self, game_id: str) -> List[Dict[str, str]]:
        """
        Obtiene las acciones pendientes según la fase actual del juego.
        """
        game = load_game(game_id)
        if not game:
            return []
        
        pending = []
        
        if game.status == GameStatus.NIGHT:
            # Verificar acciones nocturnas pendientes
            for player_id, role_info in game.roles.items():
                if not role_info.is_alive:
                    continue
                
                # Hombres lobo
                if role_info.role == GameRole.WAREWOLF:
                    if not self._has_werewolf_voted(game_id, player_id):
                        pending.append({"player_id": player_id, "action": "werewolf_attack"})
                
                # Vidente
                elif role_info.role == GameRole.SEER:
                    if not role_info.has_used_vision_tonight:
                        pending.append({"player_id": player_id, "action": "seer_vision"})
                
                # Bruja
                elif role_info.role == GameRole.WITCH:
                    witch_info = player_action_service.get_witch_night_info(game_id, player_id)
                    if witch_info["can_heal"] or witch_info["can_poison"]:
                        pending.append({"player_id": player_id, "action": "witch_actions"})
                
                # Cupido (solo primera noche)
                elif role_info.role == GameRole.CUPID and game.current_round == 1:
                    if player_action_service.can_cupid_choose_lovers(game_id, player_id):
                        pending.append({"player_id": player_id, "action": "cupid_lovers"})
                
                # Niño Salvaje (solo primera noche)
                elif role_info.role == GameRole.WILD_CHILD and game.current_round == 1:
                    if player_action_service.can_wild_child_choose_model(game_id, player_id):
                        pending.append({"player_id": player_id, "action": "wild_child_model"})
        
        elif game.status == GameStatus.DAY:
            # Verificar votos diurnos pendientes
            for player_id, role_info in game.roles.items():
                if role_info.is_alive and player_id not in game.day_votes:
                    pending.append({"player_id": player_id, "action": "day_vote"})
        
        return pending
    
    def _has_werewolf_voted(self, game_id: str, werewolf_id: str) -> bool:
        """Verifica si un hombre lobo ya votó en la fase nocturna."""
        game = load_game(game_id)
        if not game:
            return False
        
        return (werewolf_id in game.night_actions.get("warewolf_attacks", {}))


# Instancia global del controlador
game_flow_controller = GameFlowController()
