import axios from 'axios'

// Create axios instance with base configuration
const api = axios.create({
  baseURL: process.env.NODE_ENV === 'production' ? '/api' : 'http://localhost:8000',
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Request interceptor to add authentication token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// Response interceptor to handle errors
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Clear token and redirect to login
      localStorage.removeItem('access_token')
      window.location.href = '/login'
    }
    return Promise.reject(error)
  }
)

// Auth API
export const authAPI = {
  login: (username, password) => {
    const formData = new FormData()
    formData.append('username', username)
    formData.append('password', password)
    return api.post('/login', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    })
  },
  register: (username, email, password) => {
    const formData = new FormData()
    formData.append('username', username)
    formData.append('email', email)
    formData.append('password', password)
    return api.post('/register', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    })
  },
}

// Games API
export const gamesAPI = {
  createGame: (data) => api.post('/games', data),
  getGames: () => api.get('/games'),
  getGame: (gameId) => api.get(`/games/${gameId}`),
  joinGame: (gameId, data) => api.post(`/games/${gameId}/join`, data),
  startGame: (gameId) => api.post(`/games/${gameId}/start`),
}

// Users API
export const usersAPI = {
  getUser: (userId) => api.get(`/users/${userId}`),
  updateUser: (userId, data) => api.put(`/users/${userId}`, data),
}

// Game Actions API
export const gameActionsAPI = {
  vote: (gameId, data) => api.post(`/games/${gameId}/vote`, data),
  werewolfVote: (gameId, data) => api.post(`/games/${gameId}/werewolf-vote`, data),
  seerInvestigate: (gameId, data) => api.post(`/games/${gameId}/seer-investigate`, data),
  witchHeal: (gameId, data) => api.post(`/games/${gameId}/witch-heal`, data),
  witchPoison: (gameId, data) => api.post(`/games/${gameId}/witch-poison`, data),
  hunterShoot: (gameId, data) => api.post(`/games/${gameId}/hunter-shoot`, data),
  cupidChooseLovers: (gameId, data) => api.post(`/games/${gameId}/cupid-choose-lovers`, data),
  wildChildChooseModel: (gameId, data) => api.post(`/games/${gameId}/wild-child-choose-model`, data),
}

export default api