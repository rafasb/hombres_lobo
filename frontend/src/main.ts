import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import { createPinia } from 'pinia'
import { useAuthStore } from './stores/authStore'

// Importar Bootstrap CSS e iconos
import 'bootstrap/dist/css/bootstrap.min.css'
import 'bootstrap-icons/font/bootstrap-icons.css'
import './style.css'

const app = createApp(App)
const pinia = createPinia()

app.use(pinia)
app.use(router)

// Mantener usuario autenticado tras recarga
const auth = useAuthStore()
auth.loadUserFromToken()

app.mount('#app')
