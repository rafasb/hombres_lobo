<template>
  <div class="table-responsive d-none d-md-block">
    <table class="table table-hover table-striped mb-0">
      <thead class="table-dark">
        <tr>
          <th scope="col">
            <i class="bi bi-person me-1"></i>
            Usuario
          </th>
          <th scope="col">
            <i class="bi bi-hash me-1"></i>
            ID
          </th>
          <th scope="col">
            <i class="bi bi-shield me-1"></i>
            Rol
          </th>
          <th scope="col" class="text-center">
            <i class="bi bi-gear me-1"></i>
            Acciones
          </th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="user in users" :key="user.id">
          <td class="fw-medium">{{ user.username }}</td>
          <td class="text-muted">#{{ user.id }}</td>
          <td>
            <span 
              class="badge"
              :class="user.role === 'admin' ? 'bg-success' : 'bg-secondary'"
            >
              <i :class="user.role === 'admin' ? 'bi bi-shield-check' : 'bi bi-person'"></i>
              {{ user.role === 'admin' ? 'Administrador' : 'Jugador' }}
            </span>
          </td>
          <td>
            <div class="btn-group" role="group">
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
          </td>
        </tr>
      </tbody>
    </table>
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
