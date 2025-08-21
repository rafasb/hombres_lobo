<template>
  <div class="min-vh-100" style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);">
    <!-- Navegación común -->
    <NavigationBar 
      :show-admin="true"
      @navigate="handleNavigation"
    />
    <div class="container-lg py-4">
      <div class="row">
        <div class="col-12">
          <!-- Header -->
          <div class="card shadow-sm mb-4" style="background: rgba(255, 255, 255, 0.95); backdrop-filter: blur(10px);">
            <div class="card-body">
              <div class="d-flex align-items-center">
                <div class="me-3">
                  <i class="bi bi-people-fill text-primary" style="font-size: 2.5rem;"></i>
                </div>
                <div>
                  <h2 class="mb-1 text-primary fw-bold">Administración de Usuarios</h2>
                  <p class="text-muted mb-0">Gestiona los usuarios del sistema</p>
                </div>
              </div>
            </div>
          </div>
          <!-- Búsqueda -->
          <AdminUserSearch
            :search="search"
            :loading="loading"
            @update:search="val => search = val"
            @search="fetchUsersList"
          />
          <!-- Control de acceso y errores -->
          <AdminUserError v-if="localError" :error="localError" />
          <div v-else>
            <div v-if="loading && !users.length" class="text-center py-5">
              <div class="card shadow-sm" style="background: rgba(255, 255, 255, 0.95); backdrop-filter: blur(10px);">
                <div class="card-body py-5">
                  <div class="spinner-border text-primary" style="width: 3rem; height: 3rem;"></div>
                  <p class="text-muted mt-3">Cargando usuarios...</p>
                </div>
              </div>
            </div>
            <AdminUserError v-else-if="error" :error="error" />
          </div>
          <!-- Tabla de usuarios -->
          <div v-if="users.length" class="card shadow-sm" style="background: rgba(255, 255, 255, 0.95); backdrop-filter: blur(10px);">
            <div class="card-header bg-primary text-white">
              <h5 class="mb-0">
                <i class="bi bi-list-ul me-2"></i>
                Lista de Usuarios ({{ users.length }})
              </h5>
            </div>
            <div class="card-body p-0">
              <!-- Vista de tabla para desktop extraída a componente -->
              <AdminUserTable
                v-if="users.length"
                :users="users"
                @toggle-role="confirmAndToggleRole"
                @delete="confirmAndDelete"
              />
              <!-- Vista de cards para móvil extraída a componente -->
              <AdminUserCards
                v-if="users.length"
                :users="users"
                @toggle-role="confirmAndToggleRole"
                @delete="confirmAndDelete"
              />
            </div>
          </div>
          <!-- Estado vacío -->
          <div v-else-if="!loading && !error" class="text-center py-5">
            <div class="card shadow-sm" style="background: rgba(255, 255, 255, 0.95); backdrop-filter: blur(10px);">
              <div class="card-body py-5">
                <div class="mb-4">
                  <i class="bi bi-inbox text-muted" style="font-size: 4rem;"></i>
                </div>
                <h5 class="text-muted">No hay usuarios para mostrar</h5>
                <p class="text-muted">Realiza una búsqueda para encontrar usuarios</p>
                <button 
                  @click="fetchUsersList" 
                  class="btn btn-primary"
                >
                  <i class="bi bi-arrow-clockwise me-1"></i>
                  Actualizar
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { onMounted, ref } from 'vue'
import NavigationBar from '../components/NavigationBar.vue'
import AdminUserError from '../components/AdminUserError.vue'
import AdminUserCards from '../components/AdminUserCards.vue'
import AdminUserTable from '../components/AdminUserTable.vue'
import AdminUserSearch from '../components/AdminUserSearch.vue'
import { useAdminComposable } from '../composables/useAdmin.ts'
import { useNavigation } from '../composables/useNavigation'
import { useProfile } from '../composables/useProfile'

const {
  users,
  search,
  loading,
  error,
  fetchUsersList,
  deleteUserHandler,
  toggleRole
} = useAdminComposable()

const { isAdmin } = useProfile()

const { handleNavigation } = useNavigation()

const localError = ref('')

interface User {
  id: string
  username: string
  role: 'admin' | 'player'
}

function confirmAndDelete(user: User): void {
  if (confirm(`¿Estás seguro de que deseas eliminar al usuario ${user.username}?`)) {
    deleteUserHandler(user)
  }
}

function confirmAndToggleRole(user: User) {
  const newRole = user.role === 'admin' ? 'player' : 'admin'
  if (confirm(`¿Estás seguro de que deseas cambiar el rol de ${user.username} a ${newRole}?`)) {
    toggleRole(user, newRole)
  }
}

onMounted(async () => {
  if (isAdmin) {
    fetchUsersList()
  } else {
    localError.value = 'No tienes permisos de administrador para ver esta página'
  }
})
</script>
