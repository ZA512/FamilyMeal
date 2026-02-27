import { defineStore } from 'pinia'

interface AuthState {
  adminToken: string | null
  readerToken: string | null
  membreId: number | null
  username: string | null
}

export const useAuthStore = defineStore('auth', {
  state: (): AuthState => ({
    adminToken: null,
    readerToken: null,
    membreId: null,
    username: null,
  }),

  getters: {
    isAdmin: (state) => !!state.adminToken,
    isReader: (state) => !!state.readerToken,
    isAuthenticated: (state) => !!state.adminToken || !!state.readerToken,
    authHeader: (state): Record<string, string> => {
      if (state.adminToken) return { Authorization: `Bearer ${state.adminToken}` }
      if (state.readerToken) return { Authorization: `Reader ${state.readerToken}` }
      return {}
    },
  },

  actions: {
    initFromCookies() {
      if (typeof window !== 'undefined') {
        this.adminToken = localStorage.getItem('fm_admin_token')
        this.readerToken = localStorage.getItem('fm_reader_token')
        this.membreId = Number(localStorage.getItem('fm_membre_id')) || null
        this.username = localStorage.getItem('fm_username')
      }
    },

    setAdmin(token: string, username: string) {
      this.adminToken = token
      this.username = username
      this.readerToken = null
      if (typeof window !== 'undefined') {
        localStorage.setItem('fm_admin_token', token)
        localStorage.setItem('fm_username', username)
        localStorage.removeItem('fm_reader_token')
        localStorage.removeItem('fm_membre_id')
      }
    },

    setReader(token: string, membreId: number | null) {
      this.readerToken = token
      this.membreId = membreId
      this.adminToken = null
      if (typeof window !== 'undefined') {
        localStorage.setItem('fm_reader_token', token)
        if (membreId) localStorage.setItem('fm_membre_id', String(membreId))
        localStorage.removeItem('fm_admin_token')
        localStorage.removeItem('fm_username')
      }
    },

    updateMembreId(membreId: number, token: string) {
      this.membreId = membreId
      this.readerToken = token
      if (typeof window !== 'undefined') {
        localStorage.setItem('fm_membre_id', String(membreId))
        localStorage.setItem('fm_reader_token', token)
      }
    },

    logout() {
      this.adminToken = null
      this.readerToken = null
      this.membreId = null
      this.username = null
      if (typeof window !== 'undefined') {
        localStorage.removeItem('fm_admin_token')
        localStorage.removeItem('fm_reader_token')
        localStorage.removeItem('fm_membre_id')
        localStorage.removeItem('fm_username')
      }
    },
  },
})
