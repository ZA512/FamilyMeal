import { useAuthStore } from '~/stores/auth'

export function useApi() {
  const config = useRuntimeConfig()
  const auth = useAuthStore()
  const baseURL = config.public.apiBase

  async function request<T>(path: string, options: RequestInit = {}): Promise<T> {
    const res = await fetch(`${baseURL}${path}`, {
      ...options,
      headers: {
        'Content-Type': 'application/json',
        ...auth.authHeader,
        ...(options.headers as Record<string, string> || {}),
      },
    })
    if (res.status === 401) {
      auth.logout()
      navigateTo('/login')
      throw new Error('Non authentifié')
    }
    if (!res.ok) {
      const error = await res.json().catch(() => ({ detail: `Erreur ${res.status}` }))
      // 403 avec message de token invalide → jeton expiré ou corrompu, forcer re-login
      if (res.status === 403 && typeof error.detail === 'string' && error.detail.toLowerCase().includes('jeton')) {
        auth.logout()
        navigateTo('/login')
        throw new Error('Session expirée, veuillez vous reconnecter.')
      }
      throw new Error(error.detail || JSON.stringify(error))
    }
    if (res.status === 204) return undefined as T
    return res.json()
  }

  return {
    get: <T>(path: string) => request<T>(path),
    post: <T>(path: string, body: unknown) =>
      request<T>(path, { method: 'POST', body: JSON.stringify(body) }),
    put: <T>(path: string, body: unknown) =>
      request<T>(path, { method: 'PUT', body: JSON.stringify(body) }),
    patch: <T>(path: string, body: unknown) =>
      request<T>(path, { method: 'PATCH', body: JSON.stringify(body) }),
    del: <T>(path: string) => request<T>(path, { method: 'DELETE' }),
  }
}
