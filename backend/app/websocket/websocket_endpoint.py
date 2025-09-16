'''
Este módulo se encarga de manejar el endpoint principal de WebSocket,
incluyendo autenticación, gestión de conexiones, recepción y envío de mensajes,
y actualización automática del estado de los usuarios.
'''
from fastapi import WebSocket, WebSocketDisconnect
from datetime import datetime
import json
import logging

from app.websocket.connection_manager import connection_manager
from app.core.security import verify_access_token
from app.websocket.user_status_handlers import user_status_handler
from app.services.game_responses_service import GameResponsesService

from app.websocket.messages_types import (
    MessageType, ErrorCode,
    WebSocketMessageV2, WsSystemMessage, SystemMessageType
)

from app.websocket.message_handlers import message_handler


logger = logging.getLogger(__name__)

async def websocket_endpoint(websocket: WebSocket, game_id: str, token: str) -> None:
    """Endpoint principal de WebSocket"""
    connection_id = None
    user_id = None
    
    try:
        logger.info(f"Intentando conectar WebSocket para juego {game_id}")
        logger.info(f"Token recibido: {token[:50]}...")
        print(f"Intentando conectar WebSocket para juego {game_id}")
        print(f"Token recibido: {token[:50]}...")
        
        # Verificar token de autenticación
        payload = verify_access_token(token)
        logger.info(f"Payload del token: {payload}")
        
        if not payload:
            logger.error("Token inválido - cerrando conexión")
            try:
                await websocket.close(code=4001, reason="Token inválido")
            except Exception:
                pass  # Si ya está cerrado, ignorar el error
            return
        
        user_id = payload.get("user_id")
        if not user_id:
            # Intentar con 'sub' como alternativa
            user_id = payload.get("sub")
            
        logger.info(f"User ID extraído: {user_id}")
        
        if not user_id:
            logger.error("Usuario no encontrado en token - cerrando conexión")
            try:
                await websocket.close(code=4001, reason="Usuario no encontrado en token")
            except Exception:
                pass  # Si ya está cerrado, ignorar el error
            return
        
        # Conectar usuario
        connection_id = await connection_manager.connect(websocket, user_id, game_id)
        logger.info(f"Usuario {user_id} conectado al juego {game_id} con conexión {connection_id}")
        
        # Actualizar estado del usuario a 'connected' automáticamente
        try:
            await user_status_handler.auto_update_status_on_connect(user_id)
        except Exception as e:
            logger.warning(f"Error actualizando estado a conectado para {user_id}: {e}")
        
        # Sincronizar estado de connected_players con ConnectionManager
        try:
            from app.services.game_state_service import game_state_manager
            actual_connected_users = connection_manager.get_game_users(game_id)
            await game_state_manager.sync_connected_players_with_connection_manager(game_id, actual_connected_users)
            logger.info(f"Sincronizados connected_players para {game_id}: {actual_connected_users}")
            print(f"Sincronizados connected_players para {game_id}: {actual_connected_users}")
        except Exception as e:
            logger.warning(f"Error sincronizando connected_players para {game_id}: {e}")
            print(f"Error sincronizando connected_players para {game_id}: {e}")
        
        # Enviar mensaje de bienvenida usando SystemMessage
        welcome_message = WsSystemMessage(
            type=MessageType.SYSTEM_MESSAGE,
            data=f"Conectado al juego {game_id}",
            message_key=SystemMessageType.CONNECTED_TO_GAME,
            params={"game_id": game_id},
            timestamp=datetime.now()
        )
        
        await connection_manager.send_personal_message(
            connection_id,
            welcome_message
        )

        # Enviar datos de la partida usando GameResponse
        # ESTE (GAME_STATUS) ES EL ÚNICO MENSAJE QUE ESTÁ BIEN FORMATEADO EN LOS ENVÍOS, 
        # JUNTO CON EL MENSAJE DE HEARTBEAT. 
        # TODO: Revisar el formato del resto de mensajes, idealmente migrar a WebSocketMessageV2
        # y contener la información dentro de data.
        try:
            game_response = GameResponsesService.get_game_response_by_id(game_id)
            if game_response:
                game_data_message = WebSocketMessageV2(
                    type=MessageType.GAME_STATUS,
                    data=game_response.dict(),
                    timestamp=datetime.now()
                )
                
                await connection_manager.send_personal_message(
                    connection_id,
                    game_data_message
                )
                logger.info(f"Datos de partida enviados a usuario {user_id} en juego {game_id}")
                print(f"Datos de partida enviados a usuario {user_id} en juego {game_id}")
            else:
                logger.warning(f"No se pudieron obtener datos de la partida {game_id} para usuario {user_id}")
                print(f"No se pudieron obtener datos de la partida {game_id} para usuario {user_id}")
        except Exception as e:
            logger.error(f"Error enviando datos de partida a {user_id}: {e}")
            print(f"Error enviando datos de partida a {user_id}: {e}")
        # Loop principal de mensajes
        # Los únicos mensajes que se pueden recibir son de HEARTBEAT

        while True:
            try:
                # Recibir mensaje
                data = await websocket.receive_text()
                # Log raw incoming message
                logger.info(f"RAW RECV <- connection_id={connection_id} raw={data}")
                message_data = json.loads(data)
                
                # Procesar mensaje
                await message_handler.handle_message(connection_id, message_data)
                
            except WebSocketDisconnect:
                # Manejar desconexión - la limpieza se hace en finally
                logger.info(f"WebSocket desconectado para conexión {connection_id}")
                print(f"WebSocket desconectado para conexión {connection_id}")
                break
            except json.JSONDecodeError:
                await message_handler.send_error(
                    connection_id,
                    ErrorCode.INVALID_MESSAGE,
                    "Formato JSON inválido"
                )
            except Exception as e:
                logger.error(f"Error en websocket loop: {e}")
                await message_handler.send_error(
                    connection_id,
                    ErrorCode.INTERNAL_ERROR,
                    "Error interno del servidor"
                )
                
    except WebSocketDisconnect: 
        if user_id:
            try:
                await user_status_handler.auto_update_status_on_disconnect(user_id)
                from app.services.game_state_service import game_state_manager
                # Sincronizar estado de connected_players después de la desconexión
                actual_connected_users = connection_manager.get_game_users(game_id)
                await game_state_manager.sync_connected_players_with_connection_manager(game_id, actual_connected_users)
            except Exception as e:
                logger.warning(f"Error actualizando estado de usuario a desconectado: {e}")

    except Exception as e:
        logger.error(f"Error en websocket endpoint: {e}")
        try:
            if websocket.client_state.name != "DISCONNECTED":
                await websocket.close(code=4000, reason="Error interno")
        except Exception:
            pass  # Si ya está cerrado, ignorar el error
    finally:
        # Limpiar conexión y actualizar estado
        if connection_id:
            # Obtener user_id antes de desconectar si no lo tenemos ya
            if not user_id:
                user_id = connection_manager.connection_users.get(connection_id)
            
            # Desconectar la conexión
            await connection_manager.disconnect(connection_id)
            
            # Actualizar estado del usuario a 'disconnected' automáticamente
            if user_id:
                try:
                    await user_status_handler.auto_update_status_on_disconnect(user_id)
                except Exception as e:
                    logger.warning(f"Error actualizando estado a desconectado para {user_id}: {e}")
                
                # Sincronizar estado de connected_players después de la desconexión
                try:
                    from app.services.game_state_service import game_state_manager
                    actual_connected_users = connection_manager.get_game_users(game_id)
                    await game_state_manager.sync_connected_players_with_connection_manager(game_id, actual_connected_users)
                except Exception as e:
                    logger.warning(f"Error sincronizando connected_players tras desconexión: {e}")
            
            # Limpiar recursos finales
            await connection_manager.cleanup_after_disconnect()
            logger.info(f"Conexión {connection_id} desconectada")
