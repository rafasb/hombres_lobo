# Plan de Migración:
1. Expandir Game con los campos necesarios para evitar que exista un estado de la partida en memoria no almacenado en la base de datos.
2. Actualizar base de datos para incluir nuevos campos del modelo Game
3. Refactorizar GameState para ser solo un wrapper de servicios
4. Actualizar GameFlowController para usar Game directamente