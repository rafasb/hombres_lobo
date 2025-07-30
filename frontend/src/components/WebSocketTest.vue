<template>
  <div class="websocket-test">
    <Card>
      <template #title>
        <div class="flex align-items-center gap-2">
          <i class="pi pi-wifi"></i>
          Test WebSocket
        </div>
      </template>

      <template #content>
        <div class="flex flex-column gap-3">
          <!-- Connection status -->
          <div class="field">
            <label>Estado de Conexión:</label>
            <Tag
              :value="connectionStatus"
              :severity="connectionSeverity"
              :icon="connectionIcon"
            />
            <small v-if="connectionError" class="text-red-500 block">
              Error: {{ connectionError }}
            </small>
          </div>

          <!-- Game ID input -->
          <div class="field">
            <label for="gameId">Game ID:</label>
            <InputText
              id="gameId"
              v-model="testGameId"
              placeholder="Ingresa un Game ID"
              :disabled="isConnected"
            />
          </div>

          <!-- Actions -->
          <div class="flex gap-2">
            <Button
              v-if="!isConnected"
              label="Conectar"
              icon="pi pi-link"
              @click="connect"
              :loading="isConnecting"
              :disabled="!testGameId"
              class="p-button-success"
            />
            <Button
              v-if="isConnected"
              label="Desconectar"
              icon="pi pi-times"
              @click="disconnect"
              class="p-button-danger"
            />
            <Button
              v-if="isConnected"
              label="Test Status"
              icon="pi pi-question"
              @click="testStatus"
              class="p-button-info"
            />
          </div>

          <!-- Messages log -->
          <div v-if="messages.length > 0" class="field">
            <label>Mensajes WebSocket:</label>
            <div class="messages-log">
              <div
                v-for="(msg, index) in messages"
                :key="index"
                class="message-item"
                :class="msg.type"
              >
                <small class="text-500">{{ msg.timestamp }}</small>
                <div class="message-content">
                  <strong>{{ msg.direction }}:</strong> {{ msg.content }}
                </div>
              </div>
            </div>
          </div>
        </div>
      </template>
    </Card>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { useGameWebSocket } from '@/composables/useGameWebSocket'
import { useAuthStore } from '@/stores/auth'

// PrimeVue components
import Card from 'primevue/card'
import Button from 'primevue/button'
import InputText from 'primevue/inputtext'
import Tag from 'primevue/tag'

const authStore = useAuthStore()
const { isConnected, isConnecting, connectionError, connectToGame, disconnect: disconnectWS, getStatus } = useGameWebSocket()

// Local state
const testGameId = ref('test-game-123')
const messages = ref<Array<{
  timestamp: string,
  direction: 'SENT' | 'RECEIVED',
  content: string,
  type: 'sent' | 'received'
}>>([])

// Computed
const connectionStatus = computed(() => {
  if (isConnecting) return 'Conectando...'
  if (isConnected) return 'Conectado'
  if (connectionError) return 'Error'
  return 'Desconectado'
})

const connectionSeverity = computed(() => {
  if (isConnecting) return 'info'
  if (isConnected) return 'success'
  if (connectionError) return 'danger'
  return 'secondary'
})

const connectionIcon = computed(() => {
  if (isConnecting) return 'pi pi-spin pi-spinner'
  if (isConnected) return 'pi pi-check-circle'
  if (connectionError) return 'pi pi-times-circle'
  return 'pi pi-circle'
})

// Methods
const connect = async () => {
  if (!testGameId.value) return

  addMessage('SENT', `Conectando a juego: ${testGameId.value}`)

  try {
    const success = await connectToGame(testGameId.value)
    if (success) {
      addMessage('RECEIVED', 'Conexión WebSocket establecida')
    } else {
      addMessage('RECEIVED', 'Error en la conexión')
    }
  } catch (error) {
    addMessage('RECEIVED', `Error: ${error}`)
  }
}

const disconnect = () => {
  disconnectWS()
  addMessage('SENT', 'Desconectando...')
  addMessage('RECEIVED', 'Desconectado')
}

const testStatus = () => {
  const success = getStatus()
  if (success) {
    addMessage('SENT', 'Solicitando estado del juego')
  } else {
    addMessage('RECEIVED', 'Error enviando solicitud de estado')
  }
}

const addMessage = (direction: 'SENT' | 'RECEIVED', content: string) => {
  messages.value.push({
    timestamp: new Date().toLocaleTimeString(),
    direction,
    content,
    type: direction === 'SENT' ? 'sent' : 'received'
  })

  // Mantener solo los últimos 20 mensajes
  if (messages.value.length > 20) {
    messages.value = messages.value.slice(-20)
  }
}
</script>

<style scoped>
.websocket-test {
  max-width: 600px;
  margin: 2rem auto;
}

.field {
  margin-bottom: 1rem;
}

.field label {
  display: block;
  margin-bottom: 0.5rem;
  font-weight: 600;
  color: var(--text-color);
}

.messages-log {
  max-height: 300px;
  overflow-y: auto;
  border: 1px solid var(--surface-border);
  border-radius: 4px;
  padding: 1rem;
  background: var(--surface-50);
}

.message-item {
  margin-bottom: 0.5rem;
  padding: 0.5rem;
  border-radius: 4px;
  border-left: 3px solid var(--surface-300);
}

.message-item.sent {
  background: var(--blue-50);
  border-left-color: var(--blue-500);
}

.message-item.received {
  background: var(--green-50);
  border-left-color: var(--green-500);
}

.message-content {
  margin-top: 0.25rem;
  font-size: 0.9rem;
}
</style>
