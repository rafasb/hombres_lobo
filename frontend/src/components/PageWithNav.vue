<template>
  <div>
    <NavigationBar :show-admin="showAdmin" @navigate="handleNavigate" />
    <slot />
  </div>
</template>

<script setup lang="ts">
import NavigationBar from './NavigationBar.vue'

interface Props {
  showAdmin?: boolean
}

interface Emits {
  (e: 'navigate', view: string): void
}

const props = defineProps<Props>()
const emit = defineEmits<Emits>()

const showAdmin = props.showAdmin ?? false

const handleNavigate = (view: string) => {
  emit('navigate', view)
}
</script>

<style scoped>
/* no custom styles: this component only composes NavigationBar + slot */
</style>
