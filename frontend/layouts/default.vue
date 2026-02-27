<template>
  <div class="min-h-screen bg-gray-50">
    <!-- Header lecteur -->
    <header class="bg-white shadow-sm border-b border-gray-200">
      <div class="max-w-5xl mx-auto px-4 py-3 flex items-center justify-between">
        <div class="flex items-center gap-2">
          <span class="text-2xl">🍽️</span>
          <span class="font-bold text-xl text-emerald-700">FamilyMeal</span>
        </div>
        <div class="flex items-center gap-3">
          <span v-if="membrePrenom" class="text-sm text-gray-600">
            Bonjour <strong>{{ membrePrenom }}</strong>
          </span>
          <button @click="logout" class="text-sm text-gray-500 hover:text-red-500 transition">
            Déconnexion
          </button>
        </div>
      </div>
    </header>

    <main class="max-w-5xl mx-auto px-4 py-6">
      <slot />
    </main>
  </div>
</template>

<script setup lang="ts">
import { useAuthStore } from '~/stores/auth'
import { useApi } from '~/composables/useApi'

const auth = useAuthStore()
const api = useApi()

const membrePrenom = ref<string | null>(null)

onMounted(async () => {
  auth.initFromCookies()
  if (auth.membreId) {
    try {
      const membre = await api.get<{ prenom: string }>(`/membres/${auth.membreId}/`)
      membrePrenom.value = membre.prenom
    } catch {}
  }
})

function logout() {
  auth.logout()
  navigateTo('/lecteur-login')
}
</script>
