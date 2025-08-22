import api from './api'
import { extractErrorMessage } from './errorHelper'

export async function register(username: string, email: string, password: string): Promise<{ success?: boolean; error?: string }> {
  try {
    const params = new URLSearchParams();
    params.append('username', username);
    params.append('email', email);
    params.append('password', password);

    const response = await api.post('/register', params, {
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' }
    });

    // La nueva API devuelve una estructura con success, message y user
    return { success: response.data.success || true }
  } catch (error: unknown) {
    const msg = extractErrorMessage(error, 'Error al registrar usuario.')
    return { error: msg }
  }
}
