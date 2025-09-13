

 # Notificar a otros en la room (user_id ya fue obtenido arriba)
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
