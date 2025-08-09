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

    // La nueva API devuelve una estructura con success, message y los datos del token
    const { access_token, token_type } = response.data
    const auth = useAuthStore()
    auth.setToken(access_token)
    
    // Obtener perfil tras login
    const profile = await getProfile()
    if (profile && profile.user) {
      auth.setUser(profile.user)
      // Informar a la API que el usuario está conectado
      try {
        await axios.put(
          `/users/${profile.user.id}/status`,
          { status: 'connected' },
          { headers: { Authorization: `Bearer ${access_token}` } }
        )
      } catch (e) {
        // No bloquear el login si falla, pero loguear el error
        console.error('No se pudo actualizar el estado del usuario a connected', e)
      }
    }
    return { access_token, token_type }
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
    
    // La nueva API devuelve una estructura con success, message y user
    const { user } = response.data
    // Excluye hashed_password y otros campos innecesarios
    const { id, username, role } = user
    return { user: { id, username, role } }
  } catch (error: any) {
    return { error: error.response?.data?.detail || 'Error al obtener perfil.' }
  }
}
