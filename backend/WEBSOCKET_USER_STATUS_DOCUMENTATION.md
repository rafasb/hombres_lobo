# 📡 Documentación WebSocket - Gestión de Estado de Usuarios

## 🎯 Descripción General

El sistema WebSocket ahora incluye funcionalidad completa para gestionar y consultar el estado de los usuarios en tiempo real. Permite cambios automáticos al conectar/desconectar y cambios manuales por parte de usuarios y administradores.

## 🔌 Conexión WebSocket

### URL de Conexión
```
ws://localhost:8000/ws/{game_id}?token={jwt_token}
```

### Parámetros
- `game_id`: ID del juego al que conectarse
- `jwt_token`: Token JWT de autenticación del usuario

### Evento Automático al Conectar
Al conectarse exitosamente, el usuario se marca automáticamente como `connected` y todos los demás usuarios conectados reciben esta notificación:

```json
{
  "type": "user_status_changed",
  "user_id": "uuid-del-usuario",
  "old_status": "active",
  "new_status": "connected",
  "timestamp": "2025-08-09T00:40:08.907970",
  "message": "Usuario {user_id} cambió su estado de 'active' a 'connected'"
}
```

## 📊 Estados de Usuario Disponibles

| Estado | Descripción | Quién puede establecerlo |
|--------|-------------|-------------------------|
| `active` | Usuario activo y disponible | Usuario, Admin |
| `inactive` | Usuario inactivo temporalmente | Usuario, Admin |
| `connected` | Usuario conectado a la aplicación | Usuario, Admin, Automático |
| `disconnected` | Usuario desconectado | Usuario, Admin, Automático |
| `banned` | Usuario bloqueado/baneado | **Solo Admin** |

## 🎮 Cambios Manuales de Estado

### Enviar Cambio de Estado
Para cambiar manualmente el estado, envía este mensaje vía WebSocket:

```json
{
  "type": "update_user_status",
  "status": "inactive",
  "timestamp": 1691544000000
}
```

### Respuesta Exitosa
```json
{
  "type": "success",
  "action": "update_user_status",
  "message": "Estado actualizado de 'connected' a 'inactive'",
  "data": {
    "user_id": "uuid-del-usuario",
    "old_status": "connected",
    "new_status": "inactive",
    "updated_at": "2025-08-08T22:40:11.915599+00:00"
  },
  "timestamp": "2025-08-09T00:40:11.926407"
}
```

### Respuesta de Error (Sin Permisos)
```json
{
  "type": "error",
  "error_code": "INSUFFICIENT_PERMISSIONS",
  "message": "Solo los administradores pueden banear usuarios",
  "details": {},
  "timestamp": "2025-08-09T00:40:19.927276"
}
```

### Respuesta de Error (Estado Inválido)
```json
{
  "type": "error",
  "error_code": "INVALID_STATUS",
  "message": "Estado inválido: estado_inexistente",
  "details": {},
  "timestamp": "2025-08-09T00:40:19.927276"
}
```

## 📡 Notificaciones Automáticas

### Al Conectar Usuario
Todos los usuarios conectados reciben:
```json
{
  "type": "user_status_changed",
  "user_id": "uuid-del-usuario",
  "old_status": "disconnected",
  "new_status": "connected",
  "timestamp": "2025-08-09T00:40:08.907970",
  "message": "Usuario {user_id} cambió su estado de 'disconnected' a 'connected'"
}
```

### Al Desconectar Usuario
Todos los usuarios conectados reciben:
```json
{
  "type": "user_status_changed",
  "user_id": "uuid-del-usuario", 
  "old_status": "connected",
  "new_status": "disconnected",
  "timestamp": "2025-08-09T00:40:08.907970",
  "message": "Usuario {user_id} cambió su estado de 'connected' a 'disconnected'"
}
```

### Al Cambiar Estado Manualmente
Todos los demás usuarios conectados reciben la notificación (excluyendo al usuario que hizo el cambio):
```json
{
  "type": "user_status_changed",
  "user_id": "uuid-del-usuario",
  "old_status": "active",
  "new_status": "inactive", 
  "timestamp": "2025-08-09T00:40:08.907970",
  "message": "Usuario {user_id} cambió su estado de 'active' a 'inactive'"
}
```

## 🔧 Integración en el Frontend

### 1. Conectar WebSocket
```javascript
class GameWebSocket {
  constructor(gameId, token) {
    this.gameId = gameId;
    this.token = token;
    this.ws = null;
    this.userStatuses = new Map(); // Para trackear estados de usuarios
  }

  connect() {
    const wsUrl = `ws://localhost:8000/ws/${this.gameId}?token=${this.token}`;
    this.ws = new WebSocket(wsUrl);
    
    this.ws.onopen = () => {
      console.log('✅ Conectado al WebSocket');
      // El estado se actualiza automáticamente a 'connected'
    };
    
    this.ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      this.handleMessage(data);
    };
    
    this.ws.onclose = () => {
      console.log('🔌 WebSocket desconectado');
      // El estado se actualiza automáticamente a 'disconnected'
    };
  }
}
```

### 2. Manejar Mensajes de Estado
```javascript
handleMessage(data) {
  switch (data.type) {
    case 'user_status_changed':
      this.handleUserStatusChanged(data);
      break;
    case 'success':
      if (data.action === 'update_user_status') {
        this.handleStatusUpdateSuccess(data);
      }
      break;
    case 'error':
      this.handleError(data);
      break;
    case 'system_message':
      console.log('💬 Sistema:', data.message);
      break;
  }
}

handleUserStatusChanged(data) {
  const { user_id, old_status, new_status } = data;
  
  // Actualizar estado en la UI
  this.userStatuses.set(user_id, new_status);
  
  // Actualizar indicadores visuales
  this.updateUserStatusIndicator(user_id, new_status);
  
  // Mostrar notificación si es necesario
  this.showStatusNotification(user_id, old_status, new_status);
}
```

### 3. Cambiar Estado Propio
```javascript
changeMyStatus(newStatus) {
  const message = {
    type: 'update_user_status',
    status: newStatus,
    timestamp: Date.now()
  };
  
  this.ws.send(JSON.stringify(message));
}

// Ejemplos de uso
changeToInactive() {
  this.changeMyStatus('inactive');
}

changeToActive() {
  this.changeMyStatus('active');
}

// Solo para admins
banUser(userId) {
  // Nota: Este cambio se haría vía API REST, no WebSocket
  // ya que es para otro usuario
}
```

### 4. Componente React/Vue de Estado de Usuario
```javascript
// Ejemplo React
const UserStatusIndicator = ({ userId, status, isCurrentUser }) => {
  const [currentStatus, setCurrentStatus] = useState(status);
  
  const statusConfig = {
    'connected': { color: 'green', icon: '🟢', label: 'Conectado' },
    'disconnected': { color: 'red', icon: '🔴', label: 'Desconectado' },
    'active': { color: 'blue', icon: '🟦', label: 'Activo' },
    'inactive': { color: 'orange', icon: '🟠', label: 'Inactivo' },
    'banned': { color: 'black', icon: '⚫', label: 'Baneado' }
  };
  
  const config = statusConfig[currentStatus] || statusConfig['disconnected'];
  
  const handleStatusChange = (newStatus) => {
    if (isCurrentUser) {
      gameWebSocket.changeMyStatus(newStatus);
    }
  };
  
  return (
    <div className="user-status-indicator">
      <span className={`status-icon ${config.color}`}>
        {config.icon}
      </span>
      <span className="status-label">{config.label}</span>
      
      {isCurrentUser && (
        <div className="status-controls">
          <button onClick={() => handleStatusChange('active')}>
            Activo
          </button>
          <button onClick={() => handleStatusChange('inactive')}>
            Inactivo
          </button>
        </div>
      )}
    </div>
  );
};
```

### 5. Lista de Usuarios con Estados
```javascript
// Ejemplo Vue
<template>
  <div class="users-list">
    <div v-for="user in users" :key="user.id" class="user-item">
      <div class="user-info">
        <span class="username">{{ user.username }}</span>
        <UserStatusIndicator 
          :user-id="user.id"
          :status="userStatuses.get(user.id) || 'disconnected'"
          :is-current-user="user.id === currentUserId"
        />
      </div>
    </div>
  </div>
</template>

<script>
export default {
  data() {
    return {
      users: [],
      userStatuses: new Map(),
      currentUserId: null
    }
  },
  
  mounted() {
    // Escuchar cambios de estado vía WebSocket
    this.$gameWebSocket.onUserStatusChanged = (data) => {
      this.userStatuses.set(data.user_id, data.new_status);
      this.$forceUpdate(); // Forzar actualización de la vista
    };
  }
}
</script>
```

## 🎯 Casos de Uso en el Frontend

### 1. Lobby de Juego
```javascript
// Mostrar qué jugadores están conectados
const ConnectedPlayersList = ({ players }) => {
  return (
    <div className="connected-players">
      <h3>Jugadores Conectados</h3>
      {players.filter(p => p.status === 'connected').map(player => (
        <div key={player.id} className="connected-player">
          🟢 {player.username}
        </div>
      ))}
    </div>
  );
};
```

### 2. Durante la Partida
```javascript
// Verificar que jugadores están activos antes de acciones importantes
const canPlayerAct = (playerId) => {
  const status = userStatuses.get(playerId);
  return status === 'connected' || status === 'active';
};

// Mostrar advertencia si jugador está inactivo
if (!canPlayerAct(currentPlayerId)) {
  showNotification("⚠️ Cambia tu estado a 'activo' para participar");
}
```

### 3. Notificaciones Push
```javascript
// Notificar cuando usuarios importantes se conectan
handleUserStatusChanged(data) {
  if (data.new_status === 'connected' && isVipUser(data.user_id)) {
    showNotification(`🎉 ${getUserName(data.user_id)} se ha conectado!`);
  }
}
```

## 📋 API REST Complementaria

Para casos donde WebSocket no sea suficiente, también puedes usar:

### Consultar Estado de Usuario
```javascript
// GET /users/{user_id}
const getUserStatus = async (userId) => {
  const response = await fetch(`/users/${userId}`, {
    headers: { 'Authorization': `Bearer ${token}` }
  });
  const data = await response.json();
  return data.user.status;
};
```

### Cambiar Estado via REST (alternativa)
```javascript
// PUT /users/{user_id}/status
const updateUserStatus = async (userId, status) => {
  const response = await fetch(`/users/${userId}/status`, {
    method: 'PUT',
    headers: { 
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({ status })
  });
  return response.json();
};
```

## ⚡ Consideraciones de Rendimiento

### 1. Throttling de Cambios
```javascript
// Evitar spam de cambios de estado
class StatusManager {
  constructor() {
    this.lastStatusChange = 0;
    this.minInterval = 1000; // 1 segundo mínimo entre cambios
  }
  
  changeStatus(newStatus) {
    const now = Date.now();
    if (now - this.lastStatusChange < this.minInterval) {
      console.warn('⚠️ Esperá un momento antes del próximo cambio');
      return;
    }
    
    this.lastStatusChange = now;
    gameWebSocket.changeMyStatus(newStatus);
  }
}
```

### 2. Cache Local de Estados
```javascript
// Mantener cache local para evitar consultas innecesarias
class UserStatusCache {
  constructor() {
    this.cache = new Map();
    this.lastUpdate = new Map();
    this.maxAge = 30000; // 30 segundos
  }
  
  getStatus(userId) {
    const cached = this.cache.get(userId);
    const lastUpdate = this.lastUpdate.get(userId);
    
    if (cached && lastUpdate && (Date.now() - lastUpdate < this.maxAge)) {
      return cached;
    }
    
    return null; // Necesita actualización
  }
  
  setStatus(userId, status) {
    this.cache.set(userId, status);
    this.lastUpdate.set(userId, Date.now());
  }
}
```

## 🚀 ¡Listo para Integrar!

La documentación está completa y el sistema está listo para integrarse en cualquier frontend. Los permisos funcionan exactamente como describiste:

- ✅ **Usuarios regulares**: Pueden cambiar entre `active`/`inactive`/`connected`/`disconnected`
- ✅ **Solo administradores**: Pueden establecer estado `banned`
- ✅ **Automático**: `connected`/`disconnected` al conectar/desconectar WebSocket

¿Hay algún aspecto específico de la integración que te gustaría que amplíe o algún caso de uso particular que necesites documentar?
