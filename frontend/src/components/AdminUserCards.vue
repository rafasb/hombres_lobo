<template>
  <div class="d-block d-md-none p-3">
    <div v-for="user in users" :key="user.id" class="card mb-3" style="background: rgba(255, 255, 255, 0.9);">
      <div class="card-body">
        <div class="d-flex justify-content-between align-items-start mb-2">
          <div>
            <h6 class="card-title mb-1">
              <i class="bi bi-person me-1"></i>
              {{ user.username }}
            </h6>
            <small class="text-muted">ID: #{{ user.id }}</small>
          </div>
          <span 
            class="badge"
            :class="user.role === 'admin' ? 'bg-success' : 'bg-secondary'"
          >
            {{ user.role === 'admin' ? 'Admin' : 'Jugador' }}
          </span>
        </div>
        <div class="btn-group w-100" role="group">
          <button 
            @click="$emit('toggle-role', user)"
            class="btn btn-sm"
            :class="user.role === 'admin' ? 'btn-outline-warning' : 'btn-outline-success'"
          >
            <i :class="user.role === 'admin' ? 'bi bi-arrow-down-circle' : 'bi bi-arrow-up-circle'"></i>
            {{ user.role === 'admin' ? 'Degradar' : 'Promover' }}
          </button>
          <button 
            @click="$emit('delete', user)"
            class="btn btn-sm btn-outline-danger"
          >
            <i class="bi bi-trash"></i>
            Eliminar
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
interface UserSimple {
  id: string
  username: string
  role: 'admin' | 'player'
}

defineProps<{
  users: UserSimple[]
}>()

defineEmits(['toggle-role', 'delete'])
</script>
