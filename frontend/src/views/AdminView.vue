<template>
  <div class="min-vh-100" style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);">
    <!-- Navegación común -->
    <NavigationBar 
      :show-admin="true"
      @navigate="handleNavigation"
    />
    
    <!-- Contenido principal -->
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
          <div class="card shadow-sm mb-4" style="background: rgba(255, 255, 255, 0.95); backdrop-filter: blur(10px);">
            <div class="card-body">
              <div class="row g-3 align-items-end">
                <div class="col-md-9">
                  <label class="form-label fw-semibold">
                    <i class="bi bi-search me-1"></i>
                    Buscar Usuario
                  </label>
                  <input 
                    v-model="search" 
                    type="text" 
                    class="form-control form-control-lg" 
                    placeholder="Introduce nombre de usuario..." 
                  />
                </div>
                <div class="col-md-3">
                  <div class="d-grid">
                    <button 
                      @click="fetchUsersList"
                      class="btn btn-primary btn-lg"
                      :disabled="loading"
                    >
                      <span v-if="loading" class="spinner-border spinner-border-sm me-2"></span>
                      <i v-else class="bi bi-search me-2"></i>
                      {{ loading ? 'Buscando...' : 'Buscar' }}
                    </button>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- Estados de carga y error -->
          <div v-if="loading && !users.length" class="text-center py-5">
            <div class="card shadow-sm" style="background: rgba(255, 255, 255, 0.95); backdrop-filter: blur(10px);">
              <div class="card-body py-5">
                <div class="spinner-border text-primary" style="width: 3rem; height: 3rem;"></div>
                <p class="text-muted mt-3">Cargando usuarios...</p>
              </div>
            </div>
          </div>

          <div v-if="error" class="alert alert-danger" style="background: rgba(220, 53, 69, 0.1); backdrop-filter: blur(10px); border: 1px solid rgba(220, 53, 69, 0.3);">
            <i class="bi bi-exclamation-triangle me-2"></i>
            <strong>Error:</strong> {{ error }}
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
              <!-- Vista de tabla para desktop -->
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
                            @click="toggleRole(user)"
                            class="btn btn-sm"
                            :class="user.role === 'admin' ? 'btn-outline-warning' : 'btn-outline-success'"
                          >
                            <i :class="user.role === 'admin' ? 'bi bi-arrow-down-circle' : 'bi bi-arrow-up-circle'"></i>
                            {{ user.role === 'admin' ? 'Degradar' : 'Promover' }}
                          </button>
                          <button 
                            @click="deleteUserHandler(user)"
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

              <!-- Vista de cards para móvil -->
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
                        @click="toggleRole(user)"
                        class="btn btn-sm"
                        :class="user.role === 'admin' ? 'btn-outline-warning' : 'btn-outline-success'"
                      >
                        <i :class="user.role === 'admin' ? 'bi bi-arrow-down-circle' : 'bi bi-arrow-up-circle'"></i>
                        {{ user.role === 'admin' ? 'Degradar' : 'Promover' }}
                      </button>
                      <button 
                        @click="deleteUserHandler(user)"
                        class="btn btn-sm btn-outline-danger"
                      >
                        <i class="bi bi-trash"></i>
                        Eliminar
                      </button>
                    </div>
                  </div>
                </div>
              </div>
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
import NavigationBar from '../components/NavigationBar.vue'
import { useAdminComposable } from '../composables/useAdmin.ts'
import { useNavigation } from '../composables/useNavigation'

const {
  users,
  search,
  loading,
  error,
  fetchUsersList,
  deleteUserHandler,
  toggleRole
} = useAdminComposable()

const { handleNavigation } = useNavigation()
</script>
