<script setup>
import { ref, onMounted } from 'vue'
import LoginForm from './components/LoginForm.vue'
import GamesList from './components/GamesList.vue'
import GameView from './components/GameView.vue'

const currentView = ref('login')
const user = ref(null)
const selectedGame = ref(null)

onMounted(() => {
  // Check if user is already logged in
  const token = localStorage.getItem('access_token')
  const userData = localStorage.getItem('user_data')
  if (token && userData) {
    user.value = JSON.parse(userData)
    currentView.value = 'games'
  }
})

const handleLogin = (userData) => {
  user.value = userData
  currentView.value = 'games'
}

const handleLogout = () => {
  localStorage.removeItem('access_token')
  localStorage.removeItem('user_data')
  user.value = null
  currentView.value = 'login'
}

const selectGame = (game) => {
  selectedGame.value = game
  currentView.value = 'game'
}

const backToGames = () => {
  selectedGame.value = null
  currentView.value = 'games'
}
</script>

<template>
  <div id="app">
    <header v-if="user" class="app-header">
      <h1>🐺 Hombres Lobo</h1>
      <div class="user-info">
        <span>Bienvenido, {{ user.username }}</span>
        <button @click="handleLogout" class="btn btn-secondary">Cerrar Sesión</button>
      </div>
    </header>

    <main class="main-content">
      <LoginForm v-if="currentView === 'login'" @login="handleLogin" />
      <GamesList 
        v-else-if="currentView === 'games'" 
        :user="user"
        @select-game="selectGame" 
      />
      <GameView 
        v-else-if="currentView === 'game'" 
        :game="selectedGame"
        :user="user"
        @back-to-games="backToGames"
      />
    </main>
  </div>
</template>

<style>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: #333;
  min-height: 100vh;
}

#app {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

.app-header {
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(10px);
  padding: 1rem 2rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
  color: white;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
}

.app-header h1 {
  font-size: 1.8rem;
  font-weight: 700;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.main-content {
  flex: 1;
  padding: 2rem;
  display: flex;
  justify-content: center;
  align-items: center;
}

.btn {
  padding: 0.5rem 1rem;
  border: none;
  border-radius: 5px;
  cursor: pointer;
  font-weight: 500;
  transition: all 0.2s;
  text-decoration: none;
  display: inline-block;
}

.btn-primary {
  background: #4CAF50;
  color: white;
}

.btn-primary:hover {
  background: #45a049;
}

.btn-secondary {
  background: rgba(255, 255, 255, 0.2);
  color: white;
  border: 1px solid rgba(255, 255, 255, 0.3);
}

.btn-secondary:hover {
  background: rgba(255, 255, 255, 0.3);
}

.card {
  background: white;
  border-radius: 10px;
  padding: 2rem;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.2);
  max-width: 500px;
  width: 100%;
}

.form-group {
  margin-bottom: 1rem;
}

.form-group label {
  display: block;
  margin-bottom: 0.5rem;
  font-weight: 500;
}

.form-group input {
  width: 100%;
  padding: 0.75rem;
  border: 1px solid #ddd;
  border-radius: 5px;
  font-size: 1rem;
}

.form-group input:focus {
  outline: none;
  border-color: #4CAF50;
  box-shadow: 0 0 0 2px rgba(76, 175, 80, 0.2);
}

.alert {
  padding: 0.75rem;
  border-radius: 5px;
  margin-bottom: 1rem;
}

.alert-error {
  background: #ffebee;
  color: #c62828;
  border: 1px solid #ffcdd2;
}

.alert-success {
  background: #e8f5e8;
  color: #2e7d32;
  border: 1px solid #c8e6c9;
}

@media (max-width: 768px) {
  .main-content {
    padding: 1rem;
  }
  
  .app-header {
    padding: 1rem;
    flex-direction: column;
    gap: 1rem;
    text-align: center;
  }
  
  .user-info {
    flex-direction: column;
    gap: 0.5rem;
  }
}
</style>
