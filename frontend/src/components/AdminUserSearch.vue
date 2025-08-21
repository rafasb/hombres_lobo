<template>
  <div class="card shadow-sm mb-4" style="background: rgba(255, 255, 255, 0.95); backdrop-filter: blur(10px);">
    <div class="card-body">
      <div class="row g-3 align-items-end">
        <div class="col-md-9">
          <label class="form-label fw-semibold">
            <i class="bi bi-search me-1"></i>
            Buscar Usuario
          </label>
          <input 
            v-model="searchModel" 
            type="text" 
            class="form-control form-control-lg" 
            placeholder="Introduce nombre de usuario..." 
          />
        </div>
        <div class="col-md-3">
          <div class="d-grid">
            <button 
              @click="$emit('search')"
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
</template>

<script setup lang="ts">
import { computed } from 'vue'

const props = defineProps<{
  search: string
  loading: boolean
}>()
const emit = defineEmits(['update:search', 'search'])

const searchModel = computed({
  get: () => props.search,
  set: (val: string) => emit('update:search', val)
})
</script>
