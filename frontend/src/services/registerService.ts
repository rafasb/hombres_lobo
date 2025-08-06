import axios from 'axios'

export async function register(username: string, email: string, password: string): Promise<{ success?: boolean; error?: string }> {
  try {
    const params = new URLSearchParams();
    params.append('username', username);
    params.append('email', email);
    params.append('password', password);

    await axios.post('/register', params, {
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' }
    });

    return { success: true }
  } catch (error: any) {
    let errorMessage = 'Error al registrar usuario.'
    if (error.response?.data?.detail) {
      if (typeof error.response.data.detail === 'string') {
        errorMessage = error.response.data.detail
      } else if (Array.isArray(error.response.data.detail)) {
        errorMessage = error.response.data.detail[0]?.msg || errorMessage
      }
    }
    return { error: errorMessage }
  }
}
