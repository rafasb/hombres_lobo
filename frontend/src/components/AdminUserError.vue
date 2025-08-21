<template>
  <div v-if="error" class="alert alert-danger" style="background: rgba(220, 53, 69, 0.1); backdrop-filter: blur(10px); border: 1px solid rgba(220, 53, 69, 0.3);">
    <i class="bi bi-exclamation-triangle me-2"></i>
    <strong>Error:</strong> {{ error }}
  </div>
</template>

<script setup lang="ts">
defineProps<{
  error: string
}>()
</script>
