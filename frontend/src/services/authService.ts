import api from './api'
import { extractErrorMessage } from './errorHelper'
import { useAuthStore } from '../stores/authStore'

export async function login(username: string, password: string): Promise<{ access_token?: string; token_type?: string; error?: string }> {
  try {
    const params = new URLSearchParams();
    params.append('username', username);
    params.append('password', password);

    const response = await api.post('/login', params, {
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' }
    });

    // La nueva API devuelve una estructura con success, message y los datos del token
    const { access_token, token_type } = response.data
    const auth = useAuthStore()
    auth.setToken(access_token)
    
    // Obtener perfil tras login
    const profile = await getProfile()
    if (profile && profile.user) {
      // Hacer casting del usuario para asegurar que el role sea del tipo correcto
      auth.setUser({
        id: profile.user.id,
        username: profile.user.username,
        role: profile.user.role as 'admin' | 'player'
      })
      // Informar a la API que el usuario está conectado
      try {
          await api.put(
            `/users/${profile.user.id}/status`,
            { status: 'connected' }
          )
        } catch (e) {
        // No bloquear el login si falla, pero loguear el error
        console.error('No se pudo actualizar el estado del usuario a connected', e)
      }
    }
    return { access_token, token_type }
  } catch (error: unknown) {
    return { error: extractErrorMessage(error, 'Error de autenticación.') }
  }
}

export async function getProfile(): Promise<{ user?: { id: string; username: string; role: string }; error?: string }> {
  try {
    const response = await api.get('/users/me')
    
    // La nueva API devuelve una estructura con success, message y user
    const { user } = response.data
    // Excluye hashed_password y otros campos innecesarios
    const { id, username, role } = user
    return { user: { id, username, role } }
  } catch (error: unknown) {
    return { error: extractErrorMessage(error, 'Error al obtener perfil.') }
  }
}
