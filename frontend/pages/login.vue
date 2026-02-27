<template>
  <div class="min-h-screen bg-emerald-50 flex items-center justify-center p-4">
    <div class="bg-white rounded-2xl shadow-lg p-8 w-full max-w-sm">
      <div class="text-center mb-6">
        <div class="text-5xl mb-3">🍽️</div>
        <h1 class="text-2xl font-bold text-gray-800">FamilyMeal</h1>
        <p class="text-sm text-gray-500 mt-1">Espace administrateur</p>
      </div>

      <form @submit.prevent="submit" class="space-y-4">
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Identifiant</label>
          <input
            v-model="form.username"
            type="text"
            autocomplete="username"
            required
            class="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-emerald-400"
          />
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Mot de passe</label>
          <input
            v-model="form.password"
            type="password"
            autocomplete="current-password"
            required
            class="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-emerald-400"
          />
        </div>

        <div v-if="error" class="text-sm text-red-600 bg-red-50 rounded-lg px-3 py-2">
          {{ error }}
        </div>

        <button
          type="submit"
          :disabled="loading"
          class="w-full bg-emerald-600 hover:bg-emerald-700 text-white font-semibold py-2 rounded-lg transition disabled:opacity-50"
        >
          {{ loading ? 'Connexion…' : 'Se connecter' }}
        </button>
      </form>

      <div class="text-center mt-4">
        <NuxtLink to="/lecteur-login" class="text-xs text-emerald-600 hover:underline">
          Accès lecteur →
        </NuxtLink>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useAuthStore } from '~/stores/auth'
import { useApi } from '~/composables/useApi'

definePageMeta({ layout: false })

const auth = useAuthStore()
const api = useApi()

const form = reactive({ username: '', password: '' })
const loading = ref(false)
const error = ref('')

async function submit() {
  loading.value = true
  error.value = ''
  try {
    const data = await api.post('/auth/admin/login/', form)
    auth.setAdmin(data.access, data.username)
    navigateTo('/admin')
  } catch (e: any) {
    error.value = e?.data?.detail || 'Identifiant ou mot de passe incorrect.'
  } finally {
    loading.value = false
  }
}
</script>
