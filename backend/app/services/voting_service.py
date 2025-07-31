"""
Sistema de Votaciones para el juego Hombres Lobo
Maneja votaciones diurnas, conteo de votos, empates y eliminaciones
"""
from typing import Dict, List, Optional, Set, Tuple
from datetime import datetime
from enum import Enum
import logging
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)

class VoteType(str, Enum):
    """Tipos de votación"""
    DAY_VOTE = "day_vote"           # Votación diurna general
    SHERIFF_ELECTION = "sheriff_election"  # Elección de alguacil
    TIE_BREAKER = "tie_breaker"     # Desempate del alguacil
    # Futuro: WEREWOLF_VOTE = "werewolf_vote"  # Votación nocturna lobos

class VoteStatus(str, Enum):
    """Estados de una votación"""
    PENDING = "pending"     # Esperando que se abra
    ACTIVE = "active"       # Abierta para votar
    CLOSED = "closed"       # Cerrada, contando votos
    FINISHED = "finished"   # Completada con resultado

@dataclass
class Vote:
    """Representa un voto individual"""
    voter_id: str
    target_id: str
    timestamp: datetime = field(default_factory=datetime.now)
    vote_weight: int = 1  # Para futuro: voto doble del alguacil

@dataclass 
class VotingSession:
    """Sesión de votación"""
    game_id: str
    vote_type: VoteType
    status: VoteStatus = VoteStatus.PENDING
    eligible_voters: Set[str] = field(default_factory=set)  # Jugadores que pueden votar
    vote_targets: Set[str] = field(default_factory=set)     # Jugadores por los que se puede votar
    votes: Dict[str, Vote] = field(default_factory=dict)    # voter_id -> Vote
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    duration_seconds: int = 120  # 2 minutos por defecto
    result: Optional[str] = None  # ID del jugador eliminado
    is_tie: bool = False
    
    def get_vote_counts(self) -> Dict[str, int]:
        """Obtener conteo de votos por target"""
        counts = {}
        for vote in self.votes.values():
            target = vote.target_id
            counts[target] = counts.get(target, 0) + vote.vote_weight
        return counts
    
    def get_leading_candidates(self) -> List[Tuple[str, int]]:
        """Obtener candidatos con más votos (ordenados)"""
        counts = self.get_vote_counts()
        if not counts:
            return []
        
        # Ordenar por votos (descendente) y luego por ID (para consistencia)
        sorted_candidates = sorted(
            counts.items(),
            key=lambda x: (-x[1], x[0])
        )
        return sorted_candidates
    
    def get_winner(self) -> Optional[str]:
        """Determinar ganador de la votación"""
        candidates = self.get_leading_candidates()
        if not candidates:
            return None
        
        # Verificar si hay empate
        top_votes = candidates[0][1]
        tied_candidates = [c for c, v in candidates if v == top_votes]
        
        if len(tied_candidates) > 1:
            self.is_tie = True
            return None  # Empate, necesita resolución
        
        self.is_tie = False
        return candidates[0][0]  # Ganador claro

class VotingService:
    """Servicio principal de votaciones"""
    
    def __init__(self):
        # game_id -> VotingSession
        self.active_sessions: Dict[str, VotingSession] = {}
        # Para callbacks de eventos
        self.vote_callbacks: List = []
        self.result_callbacks: List = []
    
    def add_vote_callback(self, callback):
        """Agregar callback para cuando se emite un voto"""
        self.vote_callbacks.append(callback)
    
    def add_result_callback(self, callback):
        """Agregar callback para cuando una votación termina"""
        self.result_callbacks.append(callback)
    
    async def create_voting_session(
        self,
        game_id: str,
        vote_type: VoteType,
        eligible_voters: List[str],
        vote_targets: List[str],
        duration_seconds: int = 120
    ) -> VotingSession:
        """Crear nueva sesión de votación"""
        logger.info(f"Creando sesión de votación {vote_type} para juego {game_id}")
        
        session = VotingSession(
            game_id=game_id,
            vote_type=vote_type,
            eligible_voters=set(eligible_voters),
            vote_targets=set(vote_targets),
            duration_seconds=duration_seconds
        )
        
        self.active_sessions[game_id] = session
        return session
    
    async def start_voting_session(self, game_id: str) -> bool:
        """Iniciar sesión de votación"""
        if game_id not in self.active_sessions:
            logger.error(f"No hay sesión de votación para juego {game_id}")
            return False
        
        session = self.active_sessions[game_id]
        if session.status != VoteStatus.PENDING:
            logger.error(f"Sesión de votación {game_id} no está en estado PENDING")
            return False
        
        session.status = VoteStatus.ACTIVE
        session.start_time = datetime.now()
        
        logger.info(f"Votación iniciada para juego {game_id} - Duración: {session.duration_seconds}s")
        return True
    
    async def cast_vote(
        self,
        game_id: str,
        voter_id: str,
        target_id: str,
        vote_weight: int = 1
    ) -> Tuple[bool, str]:
        """Emitir un voto"""
        if game_id not in self.active_sessions:
            return False, "No hay votación activa"
        
        session = self.active_sessions[game_id]
        
        # Validaciones
        if session.status != VoteStatus.ACTIVE:
            return False, "La votación no está activa"
        
        if voter_id not in session.eligible_voters:
            return False, "No tienes derecho a voto"
        
        if target_id not in session.vote_targets:
            return False, "Objetivo de voto inválido"
        
        # Registrar voto (sobreescribe voto anterior si existe)
        vote = Vote(
            voter_id=voter_id,
            target_id=target_id,
            vote_weight=vote_weight
        )
        
        old_vote = session.votes.get(voter_id)
        session.votes[voter_id] = vote
        
        # Notificar callbacks
        for callback in self.vote_callbacks:
            try:
                if hasattr(callback, '__call__'):
                    await callback(game_id, voter_id, target_id, old_vote)
            except Exception as e:
                logger.error(f"Error en vote callback: {e}")
        
        logger.info(f"Voto registrado: {voter_id} -> {target_id} en juego {game_id}")
        return True, "Voto registrado"
    
    async def close_voting_session(self, game_id: str) -> bool:
        """Cerrar sesión de votación y calcular resultado"""
        if game_id not in self.active_sessions:
            return False
        
        session = self.active_sessions[game_id]
        if session.status != VoteStatus.ACTIVE:
            return False
        
        session.status = VoteStatus.CLOSED
        session.end_time = datetime.now()
        
        # Calcular resultado
        winner = session.get_winner()
        session.result = winner
        session.status = VoteStatus.FINISHED
        
        # Notificar callbacks
        for callback in self.result_callbacks:
            try:
                if hasattr(callback, '__call__'):
                    await callback(game_id, session)
            except Exception as e:
                logger.error(f"Error en result callback: {e}")
        
        logger.info(f"Votación cerrada para juego {game_id} - Resultado: {winner} (Empate: {session.is_tie})")
        return True
    
    def get_voting_session(self, game_id: str) -> Optional[VotingSession]:
        """Obtener sesión de votación activa"""
        return self.active_sessions.get(game_id)
    
    def get_voting_status(self, game_id: str) -> Dict:
        """Obtener estado de la votación para cliente"""
        session = self.get_voting_session(game_id)
        if not session:
            return {"status": "no_voting", "message": "No hay votación activa"}
        
        vote_counts = session.get_vote_counts()
        leading_candidates = session.get_leading_candidates()
        
        # Tiempo restante
        time_remaining = None
        if session.start_time and session.status == VoteStatus.ACTIVE:
            elapsed = (datetime.now() - session.start_time).total_seconds()
            time_remaining = max(0, session.duration_seconds - elapsed)
        
        return {
            "status": session.status.value,
            "vote_type": session.vote_type.value,
            "vote_counts": vote_counts,
            "leading_candidates": leading_candidates,
            "total_votes": len(session.votes),
            "eligible_voters": len(session.eligible_voters),
            "time_remaining": time_remaining,
            "is_tie": session.is_tie,
            "result": session.result
        }
    
    async def cleanup_session(self, game_id: str):
        """Limpiar sesión de votación terminada"""
        if game_id in self.active_sessions:
            del self.active_sessions[game_id]
            logger.info(f"Sesión de votación {game_id} eliminada")

# Instancia global del servicio de votaciones
voting_service = VotingService()
