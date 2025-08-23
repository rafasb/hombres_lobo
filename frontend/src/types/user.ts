/**
 * Tipos y interfaces relacionados con usuarios
 * Centralización de definiciones para evitar duplicación y mantener consistencia
 */

/**
 * Interfaz base del usuario - campos mínimos requeridos
 */
export interface BaseUser {
  id: string
  username: string
  role: 'admin' | 'player'
}

/**
 * Interfaz completa del usuario con todos los campos del backend
 * Extiende BaseUser para mantener compatibilidad
 */
export interface User extends BaseUser {
  email: string
  status: 'banned' | 'connected' | 'disconnected' | 'in_game'
  in_game: boolean
  game_id: string | null
}

/**
 * Interfaz para usuario en contexto de administración
 * Simplificada para vistas de admin
 */
export interface AdminUser extends BaseUser {
  // Se puede extender con campos específicos de admin si es necesario
}

/**
 * Interfaz para usuario en el store de autenticación
 * Campos mínimos necesarios para el estado de auth
 */
export interface AuthUser extends BaseUser {
  // Se puede extender con campos específicos de auth si es necesario
}

/**
 * Tipo para el rol de usuario
 */
export type UserRole = 'admin' | 'player'

/**
 * Tipo para el estado de usuario
 */
export type UserStatus = 'banned' | 'connected' | 'disconnected' | 'in_game'
