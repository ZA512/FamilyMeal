<template>
  <div class="min-h-screen bg-emerald-50 flex items-center justify-center p-4">
    <div class="bg-white rounded-2xl shadow-lg p-8 w-full max-w-sm">
      <div class="text-center mb-6">
        <div class="text-5xl mb-3">🍽️</div>
        <h1 class="text-2xl font-bold text-gray-800">FamilyMeal</h1>
        <p class="text-sm text-gray-500 mt-1">Espace famille</p>
      </div>

      <!-- Étape 1 : mot de passe partagé -->
      <div v-if="step === 1">
        <form @submit.prevent="submitPassword" class="space-y-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Mot de passe famille</label>
            <input
              v-model="password"
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
            {{ loading ? 'Vérification…' : 'Continuer' }}
          </button>
        </form>
      </div>

      <!-- Étape 2 : choix du membre -->
      <div v-else-if="step === 2">
        <p class="text-sm text-gray-600 mb-4 text-center">Qui es-tu ?</p>
        <div class="space-y-2">
          <button
            v-for="membre in membres"
            :key="membre.id"
            @click="choisirMembre(membre)"
            :disabled="loadingMembre === membre.id"
            class="w-full flex items-center gap-3 border-2 rounded-xl px-4 py-3 text-left hover:border-emerald-500 transition disabled:opacity-50"
            :style="{ borderColor: membre.couleur || '#d1d5db' }"
          >
            <span
              class="w-8 h-8 rounded-full flex items-center justify-center text-white font-bold text-sm flex-shrink-0"
              :style="{ backgroundColor: membre.couleur || '#6b7280' }"
            >
              {{ membre.prenom.charAt(0).toUpperCase() }}
            </span>
            <span class="font-medium text-gray-800">{{ membre.prenom }}</span>
          </button>
        </div>
        <button @click="step = 1" class="text-xs text-gray-400 hover:text-gray-600 mt-4 w-full text-center">
          ← Retour
        </button>
      </div>

      <div class="text-center mt-6">
        <NuxtLink to="/login" class="text-xs text-gray-400 hover:text-emerald-600">
          Accès administrateur →
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

const step = ref(1)
const password = ref('')
const loading = ref(false)
const loadingMembre = ref<number | null>(null)
const error = ref('')
const membres = ref<any[]>([])

async function submitPassword() {
  loading.value = true
  error.value = ''
  try {
    const data = await api.post('/auth/lecteur/login/', { mot_de_passe: password.value })
    // Store provisional token (no membre yet) and load members
    auth.setReader(data.access, null)
    const list = await api.get('/membres/')
    membres.value = list
    step.value = 2
  } catch (e: any) {
    error.value = e?.data?.detail || 'Mot de passe incorrect.'
  } finally {
    loading.value = false
  }
}

async function choisirMembre(membre: any) {
  loadingMembre.value = membre.id
  try {
    const data = await api.post('/auth/lecteur/choisir-membre/', { membre_id: membre.id })
    auth.setReader(data.access, data.membre_id)
    navigateTo('/planning')
  } catch (e: any) {
    error.value = 'Erreur lors de la sélection du membre.'
  } finally {
    loadingMembre.value = null
  }
}
</script>
