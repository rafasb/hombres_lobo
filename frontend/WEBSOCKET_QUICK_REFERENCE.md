# 🚀 Referencia Rápida - WebSocket Estados de Usuario

## 📡 Conexión
```javascript
ws://localhost:8000/ws/{game_id}?token={jwt_token}
```

## 📊 Estados Disponibles
- `active` - Usuario activo (Usuario/Admin)
- `inactive` - Usuario inactivo (Usuario/Admin) 
- `connected` - Conectado (Usuario/Admin/Auto)
- `disconnected` - Desconectado (Usuario/Admin/Auto)
- `banned` - Baneado (**Solo Admin**)

## 📤 Cambiar Estado (Enviar)
```json
{
  "type": "update_user_status",
  "status": "inactive"
}
```

## 📥 Respuesta Éxito (Recibir)
```json
{
  "type": "success",
  "action": "update_user_status",
  "message": "Estado actualizado de 'connected' a 'inactive'",
  "data": {
    "user_id": "uuid",
    "old_status": "connected",
    "new_status": "inactive",
    "updated_at": "2025-08-08T22:40:11.915599+00:00"
  }
}
```

## 📥 Notificación a Otros (Recibir)
```json
{
  "type": "user_status_changed",
  "user_id": "uuid",
  "old_status": "connected",
  "new_status": "in_game",
  "message": "Usuario uuid cambió su estado de 'connected' a 'in_game'"
}
```

## ❌ Error Sin Permisos (Recibir)
```json
{
  "type": "error",
  "error_code": "INSUFFICIENT_PERMISSIONS",
  "message": "Solo los administradores pueden banear usuarios"
}
```

## 🔧 JavaScript Rápido
```javascript
// Conectar
const ws = new WebSocket(`ws://localhost:8000/ws/game123?token=${token}`);

// Enviar cambio
ws.send(JSON.stringify({
  type: 'update_user_status',
  status: 'inactive'
}));

// Escuchar cambios
ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  if (data.type === 'user_status_changed') {
    updateUserUI(data.user_id, data.new_status);
  }
};
```

## 🤖 Automático
- **Al conectar WebSocket** → `connected`
- **Al desconectar WebSocket** → `disconnected`
