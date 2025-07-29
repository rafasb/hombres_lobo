import { createApp } from 'vue'
import { createPinia } from 'pinia'
import PrimeVue from 'primevue/config'

import App from './App.vue'
import router from './router'

// CSS de PrimeVue v4 (estructura actualizada)
import 'primeicons/primeicons.css'

const app = createApp(App)

app.use(createPinia())
app.use(router)
app.use(PrimeVue, {
    // Configuración para PrimeVue 4
    theme: 'none' // Sin tema por ahora, solo funcionalidad básica
})

app.mount('#app')
