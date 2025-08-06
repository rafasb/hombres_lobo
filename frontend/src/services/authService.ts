import axios from 'axios'
import { useAuthStore } from '../stores/authStore'

export async function login(username: string, password: string): Promise<{ access_token?: string; token_type?: string; error?: string }> {
  try {
    const params = new URLSearchParams();
    params.append('username', username);
    params.append('password', password);

    const response = await axios.post('/login', params, {
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' }
    });

    const token = response.data.access_token
    const auth = useAuthStore()
    auth.setToken(token)
    // Obtener perfil tras login
    const profile = await getProfile()
    if (profile && profile.user) {
      auth.setUser(profile.user)
    }
    return { access_token: token, token_type: response.data.token_type }
  } catch (error: any) {
    return { error: error.response?.data?.detail || 'Error de autenticación.' }
  }
}

export async function getProfile(): Promise<{ user?: { id: string; username: string; role: string }; error?: string }> {
  const auth = useAuthStore()
  try {
    const response = await axios.get('/users/me', {
      headers: { Authorization: `Bearer ${auth.token}` }
    })
    // Excluye hashed_password y otros campos innecesarios
    const { id, username, role } = response.data
    return { user: { id, username, role } }
  } catch (error: any) {
    return { error: error.response?.data?.detail || 'Error al obtener perfil.' }
  }
}
