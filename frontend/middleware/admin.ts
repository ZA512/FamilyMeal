import { useAuthStore } from '~/stores/auth'

export default defineNuxtRouteMiddleware(() => {
  const auth = useAuthStore()
  auth.initFromCookies()
  if (!auth.isAdmin) {
    return navigateTo('/login')
  }
})
